"""Text-only boundary; future runtimes can implement the same interface.

There is intentionally no tool-execution, camera, audio, or motor-control API.
"""

from collections.abc import Iterator
from typing import Protocol


class ContextBudgetExceeded(ValueError):
    """Input rejected before generation; the existing conversation is intact."""


class ChatBackend(Protocol):
    def reset(self) -> None:
        """Start an empty conversation with the configured system instruction."""
        ...

    def stream(self, text: str) -> Iterator[str]:
        """Yield final-answer text only, never reasoning or tool calls."""
        ...

    def cancel(self) -> None:
        """Cancel active generation before closing its conversation."""
        ...

    def close(self) -> None:
        """Release conversation and engine resources."""
        ...
