"""Terminal-only Japanese chat; no listener, network client, or device access."""

import argparse
from collections.abc import Callable, Sequence
from importlib import metadata
import json
from pathlib import Path
import platform
import sys
from time import perf_counter
from typing import TextIO

from .backend import ChatBackend, ContextBudgetExceeded
from .config import ChatConfig, RUNTIME_VERSION


def check_environment() -> None:
    if sys.version_info < (3, 10):
        raise ValueError("Python 3.10 以上が必要です。")
    if platform.system() != "Linux" or platform.machine().lower() not in {
        "aarch64", "arm64"
    }:
        raise ValueError("この初期実装の対象は 64-bit Linux / ARM64 の Raspberry Pi です。")
    libc, version = platform.libc_ver()
    if libc != "glibc":
        raise ValueError("glibc 2.27 以上の Linux が必要です。")
    try:
        glibc = tuple(int(part) for part in version.split(".")[:2])
    except ValueError as exc:
        raise ValueError("glibc のバージョンを確認できません。") from exc
    if glibc < (2, 27):
        raise ValueError("glibc 2.27 以上が必要です。")
    try:
        installed = metadata.version("litert-lm-api")
    except metadata.PackageNotFoundError as exc:
        raise ValueError("先に python -m pip install -r requirements.txt を実行してください。") from exc
    if installed != RUNTIME_VERSION:
        raise ValueError(
            f"litert-lm-api=={RUNTIME_VERSION} が必要です (現在 {installed})。"
        )


def emit_metrics(error: TextIO, **values: object) -> None:
    # Do not include prompts or responses in diagnostics.
    print(json.dumps(values, ensure_ascii=False), file=error, flush=True)


def respond(
    backend: ChatBackend,
    text: str,
    output: TextIO,
    error: TextIO,
    metrics: bool,
    clock: Callable[[], float] = perf_counter,
) -> None:
    start = clock()
    first_text_ms: float | None = None
    characters = 0
    try:
        for piece in backend.stream(text):
            if not piece:
                continue
            if first_text_ms is None:
                first_text_ms = round((clock() - start) * 1000, 1)
            print(piece, end="", file=output, flush=True)
            characters += len(piece)
    except BaseException:
        # The caller closes the failed/interrupted conversation. Do not reuse
        # partially generated history or silently retry a possibly accepted turn.
        backend.cancel()
        raise
    finally:
        print(file=output, flush=True)
    if metrics:
        emit_metrics(
            error,
            event="response",
            first_text_ms=first_text_ms,
            elapsed_ms=round((clock() - start) * 1000, 1),
            output_characters=characters,
        )
    if characters == 0:
        raise RuntimeError("応答テキストがありません。新しい会話で再実行してください。")


def chat_loop(
    backend: ChatBackend,
    config: ChatConfig,
    *,
    prompt: str | None = None,
    metrics: bool = False,
    input_fn: Callable[[str], str] = input,
    output: TextIO = sys.stdout,
    error: TextIO = sys.stderr,
) -> int:
    turns = 0
    single_turn = prompt is not None
    if not single_turn:
        print("Byterex CPU chat: /reset で履歴を消去、/quit で終了。", file=error)
    while True:
        try:
            text = prompt if single_turn else input_fn("あなた > ")
        except (EOFError, KeyboardInterrupt):
            print(file=error)
            return 0
        assert text is not None
        text = text.strip()
        if not single_turn and text == "/quit":
            return 0
        if not single_turn and text == "/reset":
            backend.reset()
            turns = 0
            print("会話をリセットしました。", file=error)
            continue
        if not text:
            if single_turn:
                print("質問を入力してください。", file=error)
                return 2
            continue
        if len(text) > config.max_input_chars:
            print(f"入力は {config.max_input_chars} 文字以内にしてください。", file=error)
            if single_turn:
                return 2
            continue
        if turns >= config.max_turns:
            print("会話回数の上限です。/reset で新しい会話を始めてください。", file=error)
            continue
        try:
            respond(backend, text, output, error, metrics)
        except ContextBudgetExceeded as exc:
            print(str(exc), file=error)
            if single_turn:
                return 1
            continue
        except KeyboardInterrupt:
            # End the process after cancellation; never reuse partial history.
            print("生成を中断しました。終了します。", file=error)
            return 130
        except Exception as exc:
            print(f"推論に失敗しました: {exc}", file=error)
            # Fail closed: no alternate model, accelerator, or cloud service.
            return 1
        turns += 1
        if single_turn:
            return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Byterex: Pi CPU 日本語テキストチャット")
    result.add_argument("--model", type=Path, required=True, help="ローカル .litertlm ファイル")
    result.add_argument("--cache-dir", type=Path, default=Path.home() / ".cache/byterex/litert-lm")
    result.add_argument("--threads", type=int, default=4)
    result.add_argument("--context-tokens", type=int, default=2048)
    result.add_argument("--max-output-tokens", type=int, default=128)
    result.add_argument("--max-input-chars", type=int, default=400)
    result.add_argument("--max-turns", type=int, default=4)
    mode = result.add_mutually_exclusive_group()
    mode.add_argument("--prompt", help="1回だけ質問して終了")
    mode.add_argument("--check", action="store_true", help="前提条件だけ検証。モデルはロードしない")
    result.add_argument("--verify-model", action="store_true", help="固定モデルの SHA256 を全件検証")
    result.add_argument("--metrics", action="store_true", help="実行時間と出力文字数を標準エラーに表示")
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    config = ChatConfig(
        model_path=args.model.expanduser().resolve(),
        cache_dir=args.cache_dir.expanduser().resolve(),
        threads=args.threads,
        context_tokens=args.context_tokens,
        max_output_tokens=args.max_output_tokens,
        max_input_chars=args.max_input_chars,
        max_turns=args.max_turns,
    )
    backend = None
    try:
        config.validate()
        if args.prompt is not None and (
            not args.prompt.strip() or len(args.prompt.strip()) > config.max_input_chars
        ):
            raise ValueError(f"質問は 1〜{config.max_input_chars} 文字で指定してください。")
        check_environment()
        if args.verify_model:
            config.verify_model()
        from .litert_backend import LiteRTBackend
        # Import native bindings too, so --check detects missing shared libraries.
        LiteRTBackend.check_import()
        if args.check:
            print(f"前提条件OK: ARM64 Linux / LiteRT-LM {RUNTIME_VERSION} / CPU")
            print("モデルのロード・推論・Piの速度は未確認です。")
            if args.verify_model:
                print("固定 Gemma 4 E2B モデルの SHA256 一致。")
            else:
                print("モデルの同一性は未検証です。初回は --verify-model を付けてください。")
            return 0
        print("Gemma 4 E2B を CPU で読み込んでいます…", file=sys.stderr, flush=True)
        start = perf_counter()
        backend = LiteRTBackend(config)
        if args.metrics:
            emit_metrics(sys.stderr, event="load", elapsed_ms=round((perf_counter() - start) * 1000, 1))
        return chat_loop(backend, config, prompt=args.prompt, metrics=args.metrics)
    except KeyboardInterrupt:
        print("中断しました。", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"起動できません: {exc}", file=sys.stderr)
        return 1
    finally:
        if backend is not None:
            backend.close()
