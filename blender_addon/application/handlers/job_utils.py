"""Utilities shared by addon-side background job handlers."""

from __future__ import annotations

from typing import Callable


class JobCancelledError(RuntimeError):
    """Raised when a background addon job is cancelled cooperatively."""


def raise_if_cancelled(is_cancelled: Callable[[], bool] | None) -> None:
    """Abort the current job when cooperative cancellation was requested."""

    if is_cancelled is not None and is_cancelled():
        raise JobCancelledError("Background job cancelled")
