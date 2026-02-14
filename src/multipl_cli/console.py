from __future__ import annotations

from rich.console import Console

_training_mode = False


def set_training_mode(enabled: bool) -> None:
    global _training_mode
    _training_mode = enabled


class MultiplConsole(Console):
    def print(self, *objects, **kwargs):  # type: ignore[override]
        if not _training_mode:
            super().print(*objects, **kwargs)
            return

        if not objects:
            super().print("[TRAINING]", **kwargs)
            return

        first, *rest = objects
        if isinstance(first, str):
            super().print(f"[TRAINING] {first}", *rest, **kwargs)
            return
        super().print("[TRAINING]", *objects, **kwargs)


console = MultiplConsole()
