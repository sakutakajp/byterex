"""Small, explicit limits for the first Raspberry Pi CPU experiment."""

from dataclasses import dataclass
from pathlib import Path
import hashlib

RUNTIME_VERSION = "0.18.0"
MODEL_FILENAME = "gemma-4-E2B-it.litertlm"
MODEL_REPOSITORY = "litert-community/gemma-4-E2B-it-litert-lm"
MODEL_REVISION = "b3ca0d2f076785a8f4b2219ddbd2bdb99954eae1"
MODEL_SHA256 = "181938105e0eefd105961417e8da75903eacda102c4fce9ce90f50b97139a63c"
SYSTEM_PROMPT = (
    "あなたはByterexの会話アシスタントです。日本語で簡潔に、原則1〜2文で答えてください。"
    "現在はテキスト会話のみです。カメラ、マイク、ロボット、外部ツールにはアクセスできません。"
    "実行していない操作を実行したと言わないでください。"
)


@dataclass(frozen=True)
class ChatConfig:
    model_path: Path
    cache_dir: Path
    threads: int = 4
    context_tokens: int = 2048
    max_output_tokens: int = 128
    max_input_chars: int = 400
    max_turns: int = 4

    def validate(self) -> None:
        limits = (
            ("threads", self.threads, 1, 4),
            ("context_tokens", self.context_tokens, 512, 32768),
            ("max_output_tokens", self.max_output_tokens, 1, 512),
            ("max_input_chars", self.max_input_chars, 1, 4000),
            ("max_turns", self.max_turns, 1, 20),
        )
        for name, value, low, high in limits:
            if not low <= value <= high:
                raise ValueError(f"{name} は {low}〜{high} の範囲で指定してください。")
        if self.max_output_tokens >= self.context_tokens:
            raise ValueError("出力上限はコンテキスト上限より小さくしてください。")
        if self.model_path.suffix != ".litertlm":
            raise ValueError("モデルには .litertlm ファイルを指定してください。")
        if not self.model_path.is_file():
            raise ValueError(f"モデルが見つかりません: {self.model_path}")
        with self.model_path.open("rb") as model:
            header = model.read(128)
        if not header:
            raise ValueError("モデルが空です。ダウンロードを確認してください。")
        if header.startswith(b"version https://git-lfs.github.com/spec/v1"):
            raise ValueError("モデル本体ではなく Git LFS ポインタです。")

    def verify_model(self) -> None:
        """Optional full-file integrity check, kept outside load-time metrics."""
        digest = hashlib.sha256()
        with self.model_path.open("rb") as model:
            for block in iter(lambda: model.read(1024 * 1024), b""):
                digest.update(block)
        if digest.hexdigest() != MODEL_SHA256:
            raise ValueError("モデルの SHA256 が固定した Gemma 4 E2B と一致しません。")
