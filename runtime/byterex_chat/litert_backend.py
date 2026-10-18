"""Adapter for the pinned official LiteRT-LM 0.18.0 Python API."""

from collections.abc import Iterator
import importlib
from typing import Any

from .backend import ContextBudgetExceeded
from .config import ChatConfig, SYSTEM_PROMPT


class LiteRTBackend:
    @staticmethod
    def check_import() -> None:
        sdk = importlib.import_module("litert_lm")
        # The library is loaded lazily. This public native call verifies loading
        # without allocating an Engine or opening the model.
        sdk.set_min_log_severity(sdk.LogSeverity.ERROR)

    def __init__(self, config: ChatConfig, *, sdk: Any = None):
        self.config = config
        self._sdk = sdk if sdk is not None else importlib.import_module("litert_lm")
        self._engine = None
        self._conversation = None
        self._stream = None
        config.cache_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        self._sdk.set_min_log_severity(self._sdk.LogSeverity.ERROR)
        self._engine = self._sdk.Engine(
            str(config.model_path),
            backend=self._sdk.Backend.CPU(thread_count=config.threads),
            max_num_tokens=config.context_tokens,
            cache_dir=str(config.cache_dir),
            vision_backend=None,
            audio_backend=None,
            enable_speculative_decoding=False,
        )
        try:
            self.reset()
        except BaseException:
            self._engine.close()
            self._engine = None
            raise

    def reset(self) -> None:
        if self._engine is None:
            raise RuntimeError("バックエンドは終了しています。")
        self.cancel()
        if self._conversation is not None:
            self._conversation.close()
            self._conversation = None
        self._conversation = self._engine.create_conversation(
            messages=[self._sdk.Message.system(SYSTEM_PROMPT)],
            sampler_config=self._sdk.SamplerConfig(
                top_k=40, top_p=0.9, temperature=0.7, seed=42
            ),
            thinking_config=self._sdk.ThinkingConfig(
                enable_thinking=False, thinking_token_budget=0
            ),
            max_output_tokens=self.config.max_output_tokens,
            tools=[],
            automatic_tool_calling=False,
        )

    def stream(self, text: str) -> Iterator[str]:
        if self._conversation is None:
            raise RuntimeError("会話が初期化されていません。")
        if self._stream is not None:
            raise RuntimeError("同時に複数の生成はできません。")
        # v0.18.0 renders the preface on the first turn and only the suffix later.
        # This is suitable only for our complete strings at an idle conversation;
        # do not reuse it with partial-message or tool-call continuation APIs.
        rendered = self._conversation.render_message_to_string(text)
        if not rendered:
            raise RuntimeError("入力をモデルの会話形式に変換できませんでした。")
        required = (
            self._conversation.token_count
            + len(self._engine.tokenize(rendered))
            + self.config.max_output_tokens
            + 32
        )
        if required > self.config.context_tokens:
            raise ContextBudgetExceeded(
                "コンテキストの空きが不足しています。入力を短くするか /reset してください。"
            )
        self._stream = self._conversation.send_message_async(
            text, max_output_tokens=self.config.max_output_tokens
        )
        # Preserve the native iterator on interruption so cancel() can drain it.
        # The official CLI uses cancel_process() followed by iterator draining.
        for chunk in self._stream:
            for content in chunk.contents:
                if isinstance(content, self._sdk.Content.Text):
                    yield content.text
        self._stream = None

    def cancel(self) -> None:
        stream = self._stream
        if stream is None or self._conversation is None:
            return
        self._conversation.cancel_process()
        try:
            for _ in stream:
                pass
        finally:
            self._stream = None

    def close(self) -> None:
        try:
            self.cancel()
        finally:
            try:
                if self._conversation is not None:
                    self._conversation.close()
            finally:
                self._conversation = None
                if self._engine is not None:
                    self._engine.close()
                    self._engine = None
