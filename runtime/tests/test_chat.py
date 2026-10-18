from dataclasses import replace
import hashlib
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from byterex_chat.cli import chat_loop, check_environment, main, respond
from byterex_chat.backend import ContextBudgetExceeded
from byterex_chat.config import ChatConfig, RUNTIME_VERSION
from byterex_chat.litert_backend import LiteRTBackend


class FakeBackend:
    def __init__(self, pieces=("こんにちは", "。")):
        self.pieces = pieces
        self.prompts = []
        self.resets = 0
        self.cancelled = 0

    def stream(self, text):
        self.prompts.append(text)
        for piece in self.pieces:
            if isinstance(piece, BaseException):
                raise piece
            yield piece

    def reset(self):
        self.resets += 1

    def cancel(self):
        self.cancelled += 1

    def close(self):
        pass


class ConfigSetup:
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.model = root / "model.litertlm"
        self.model.write_bytes(b"unit-test model, not a real model")
        self.config = ChatConfig(self.model, root / "cache")


class ConfigTest(ConfigSetup, unittest.TestCase):
    def test_model_and_defaults(self):
        self.config.validate()
        self.assertEqual(self.config.max_output_tokens, 128)
        self.assertEqual(self.config.threads, 4)

    def test_empty_and_lfs_pointer_rejected(self):
        for data in (b"", b"version https://git-lfs.github.com/spec/v1\n"):
            self.model.write_bytes(data)
            with self.assertRaises(ValueError):
                self.config.validate()

    def test_missing_file_and_wrong_extension_rejected(self):
        for name in ("missing.litertlm", "model.gguf"):
            with self.assertRaises(ValueError):
                replace(self.config, model_path=self.model.parent / name).validate()

    def test_limits(self):
        for change in ({"threads": 0}, {"threads": 5}, {"max_turns": 0},
                       {"max_output_tokens": 0}, {"max_input_chars": 0},
                       {"context_tokens": 512, "max_output_tokens": 512}):
            with self.assertRaises(ValueError):
                replace(self.config, **change).validate()

    def test_sha(self):
        with self.assertRaises(ValueError):
            self.config.verify_model()
        digest = hashlib.sha256(self.model.read_bytes()).hexdigest()
        with patch("byterex_chat.config.MODEL_SHA256", digest):
            self.config.verify_model()


class ChatTest(ConfigSetup, unittest.TestCase):
    def run_chat(self, backend, inputs=(), prompt=None, **options):
        output, error = io.StringIO(), io.StringIO()
        iterator = iter(inputs)
        def next_input(_):
            try:
                return next(iterator)
            except StopIteration:
                raise EOFError from None
        status = chat_loop(
            backend, self.config, prompt=prompt, input_fn=next_input,
            output=output, error=error, **options
        )
        return status, output.getvalue(), error.getvalue()

    def test_japanese_one_shot(self):
        backend = FakeBackend()
        status, output, _ = self.run_chat(backend, prompt="こんにちは")
        self.assertEqual(status, 0)
        self.assertEqual(output, "こんにちは。\n")
        self.assertEqual(backend.prompts, ["こんにちは"])

    def test_empty_and_long_inputs_not_sent(self):
        backend = FakeBackend()
        status, _, _ = self.run_chat(backend, inputs=["", "あ" * 401, "/quit"])
        self.assertEqual(status, 0)
        self.assertEqual(backend.prompts, [])

    def test_long_or_empty_one_shot_rejected(self):
        for prompt in ("", " " * 5, "あ" * 401):
            backend = FakeBackend()
            status, _, _ = self.run_chat(backend, prompt=prompt)
            self.assertEqual(status, 2)
            self.assertEqual(backend.prompts, [])

    def test_reset_is_explicit_and_turns_bounded(self):
        backend = FakeBackend()
        status, _, error = self.run_chat(
            backend, inputs=["a", "b", "c", "d", "blocked", "/reset", "e", "/quit"]
        )
        self.assertEqual(status, 0)
        self.assertEqual(backend.prompts, ["a", "b", "c", "d", "e"])
        self.assertEqual(backend.resets, 1)
        self.assertIn("会話回数の上限", error)

    def test_interruption_cancels_and_exits(self):
        backend = FakeBackend(("途中", KeyboardInterrupt()))
        status, output, _ = self.run_chat(backend, prompt="質問")
        self.assertEqual(status, 130)
        self.assertEqual(backend.cancelled, 1)
        self.assertEqual(output, "途中\n")

    def test_error_never_retries_or_falls_back(self):
        backend = FakeBackend((RuntimeError("native failure"),))
        status, _, error = self.run_chat(backend, prompt="質問")
        self.assertEqual(status, 1)
        self.assertEqual(len(backend.prompts), 1)
        self.assertEqual(backend.cancelled, 1)
        self.assertIn("native failure", error)

    def test_no_answer_is_not_success(self):
        status, _, _ = self.run_chat(FakeBackend(()), prompt="質問")
        self.assertEqual(status, 1)

    def test_context_rejection_allows_explicit_reset(self):
        backend = FakeBackend((ContextBudgetExceeded("/reset"),))
        status, _, error = self.run_chat(backend, inputs=["質問", "/reset", "/quit"])
        self.assertEqual(status, 0)
        self.assertEqual(backend.resets, 1)
        self.assertIn("/reset", error)

    def test_metrics_are_first_text_not_token_claim(self):
        output, error = io.StringIO(), io.StringIO()
        ticks = iter([1.0, 1.25, 2.0])
        respond(FakeBackend(("", "あ", "いう")), "private", output, error, True,
                clock=lambda: next(ticks))
        record = json.loads(error.getvalue())
        self.assertEqual(record["first_text_ms"], 250.0)
        self.assertEqual(record["elapsed_ms"], 1000.0)
        self.assertEqual(record["output_characters"], 3)
        self.assertNotIn("private", error.getvalue())
        self.assertNotIn("tokens", record)

    def test_default_metrics_off(self):
        _, _, error = self.run_chat(FakeBackend(), prompt="質問")
        self.assertEqual(error, "")


class FakeText:
    def __init__(self, text):
        self.text = text


class FakeConversation:
    def __init__(self, config):
        self.config = config
        self.closed = 0
        self.cancelled = 0
        self.requests = []
        self.token_count = 0

    def render_message_to_string(self, text):
        return "system and template: " + text

    def send_message_async(self, text, *, max_output_tokens):
        self.requests.append((text, max_output_tokens))
        return iter([
            SimpleNamespace(contents=[FakeText("回答"), object()], channels={"thought": "hidden"}),
            SimpleNamespace(contents=[FakeText("です。")], channels={}),
        ])

    def cancel_process(self):
        self.cancelled += 1

    def close(self):
        self.closed += 1


class FakeEngine:
    def __init__(self, model_path, *, backend, max_num_tokens, cache_dir,
                 vision_backend, audio_backend, enable_speculative_decoding):
        self.options = locals().copy()
        self.closed = 0
        self.conversations = []

    def create_conversation(self, *, messages, sampler_config, thinking_config,
                            max_output_tokens, tools, automatic_tool_calling):
        conversation = FakeConversation(locals().copy())
        self.conversations.append(conversation)
        return conversation

    def tokenize(self, text):
        return list(range(len(text)))

    def close(self):
        self.closed += 1


def fake_sdk():
    return SimpleNamespace(
        Engine=FakeEngine,
        Backend=SimpleNamespace(CPU=lambda *, thread_count: ("CPU", thread_count)),
        Message=SimpleNamespace(system=lambda text: ("system", text)),
        Content=SimpleNamespace(Text=FakeText),
        SamplerConfig=lambda **kwargs: kwargs,
        ThinkingConfig=lambda **kwargs: kwargs,
        LogSeverity=SimpleNamespace(ERROR=3),
        set_min_log_severity=lambda _: None,
    )


class BackendTest(ConfigSetup, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.backend = LiteRTBackend(self.config, sdk=fake_sdk())
        self.addCleanup(self.backend.close)

    def test_cpu_only_and_fixed_resource_limits(self):
        engine = self.backend._engine
        self.assertEqual(engine.options["backend"], ("CPU", 4))
        self.assertEqual(engine.options["max_num_tokens"], 2048)
        self.assertIsNone(engine.options["vision_backend"])
        self.assertIsNone(engine.options["audio_backend"])
        self.assertFalse(engine.options["enable_speculative_decoding"])
        options = self.backend._conversation.config
        self.assertFalse(options["automatic_tool_calling"])
        self.assertEqual(options["tools"], [])
        self.assertEqual(options["thinking_config"],
                         {"enable_thinking": False, "thinking_token_budget": 0})

    def test_stream_only_answer_text_and_enforce_token_cap(self):
        self.assertEqual(list(self.backend.stream("質問")), ["回答", "です。"])
        self.assertEqual(self.backend._conversation.requests, [("質問", 128)])
        self.assertIsNone(self.backend._stream)

    def test_cancel_drains_iterator(self):
        stream = self.backend.stream("質問")
        self.assertEqual(next(stream), "回答")
        conversation = self.backend._conversation
        self.backend.cancel()
        self.assertEqual(conversation.cancelled, 1)
        self.assertIsNone(self.backend._stream)
        stream.close()

    def test_context_budget_rejects_before_generation(self):
        self.backend._conversation.token_count = 2000
        with self.assertRaises(ContextBudgetExceeded):
            list(self.backend.stream("質問"))
        self.assertEqual(self.backend._conversation.requests, [])
        self.assertIsNone(self.backend._stream)

    def test_empty_prompt_render_rejected(self):
        self.backend._conversation.render_message_to_string = lambda _: ""
        with self.assertRaises(RuntimeError):
            list(self.backend.stream("質問"))
        self.assertEqual(self.backend._conversation.requests, [])

    def test_overlapping_generation_rejected(self):
        stream = self.backend.stream("first")
        next(stream)
        with self.assertRaises(RuntimeError):
            list(self.backend.stream("second"))
        self.backend.cancel()
        stream.close()

    def test_check_import_makes_native_call_without_engine(self):
        sdk = fake_sdk()
        called = []
        sdk.set_min_log_severity = called.append
        with patch("byterex_chat.litert_backend.importlib.import_module", return_value=sdk):
            LiteRTBackend.check_import()
        self.assertEqual(called, [sdk.LogSeverity.ERROR])

    def test_reset_closes_old_conversation(self):
        old = self.backend._conversation
        self.backend.reset()
        self.assertEqual(old.closed, 1)
        self.assertIsNot(self.backend._conversation, old)

    def test_close_idempotent(self):
        engine = self.backend._engine
        conversation = self.backend._conversation
        self.backend.close()
        self.backend.close()
        self.assertEqual(engine.closed, 1)
        self.assertEqual(conversation.closed, 1)

    def test_failed_conversation_creation_closes_engine(self):
        sdk = fake_sdk()
        captured = []
        class BrokenEngine(FakeEngine):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                captured.append(self)
            def create_conversation(self, **kwargs):
                raise RuntimeError("conversation failure")
        sdk.Engine = BrokenEngine
        with self.assertRaises(RuntimeError):
            LiteRTBackend(self.config, sdk=sdk)
        self.assertEqual(captured[0].closed, 1)


class EnvironmentTest(unittest.TestCase):
    def test_platform_and_version_validation(self):
        with patch("byterex_chat.cli.platform.system", return_value="Linux"), \
             patch("byterex_chat.cli.platform.machine", return_value="aarch64"), \
             patch("byterex_chat.cli.platform.libc_ver", return_value=("glibc", "2.36")), \
             patch("byterex_chat.cli.metadata.version", return_value=RUNTIME_VERSION):
            check_environment()
            with patch("byterex_chat.cli.metadata.version", return_value="0.17.0"):
                with self.assertRaises(ValueError):
                    check_environment()
            with patch("byterex_chat.cli.platform.machine", return_value="armv7l"):
                with self.assertRaises(ValueError):
                    check_environment()
            with patch("byterex_chat.cli.platform.libc_ver", return_value=("glibc", "2.26")):
                with self.assertRaises(ValueError):
                    check_environment()

    def test_missing_model_fails_before_native_import(self):
        with patch("sys.stderr", new_callable=io.StringIO), \
             patch("byterex_chat.cli.check_environment") as check:
            self.assertEqual(main(["--model", "/not-found/model.litertlm"]), 1)
            check.assert_not_called()


if __name__ == "__main__":
    unittest.main()
