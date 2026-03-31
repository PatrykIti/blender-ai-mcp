# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""In-memory result storage for background-capable task bookkeeping."""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from time import time
from typing import Any


@dataclass(frozen=True)
class BackgroundResultRecord:
    """Stored result metadata for a completed background task."""

    result_ref: str
    task_id: str
    tool_name: str
    payload: Any
    created_at: float = field(default_factory=time)


class BackgroundResultStore:
    """Thread-safe in-memory result store keyed by stable ``result_ref``."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._results: dict[str, BackgroundResultRecord] = {}

    def put(self, *, task_id: str, tool_name: str, payload: Any) -> BackgroundResultRecord:
        """Store a completed result and return its stable reference."""

        record = BackgroundResultRecord(
            result_ref=f"task-result:{task_id}",
            task_id=task_id,
            tool_name=tool_name,
            payload=payload,
        )
        with self._lock:
            self._results[record.result_ref] = record
        return record

    def get(self, result_ref: str) -> BackgroundResultRecord | None:
        """Return a stored result by reference."""

        with self._lock:
            return self._results.get(result_ref)

    def clear(self) -> None:
        """Remove all stored results."""

        with self._lock:
            self._results.clear()


_RESULT_STORE = BackgroundResultStore()


def get_background_result_store() -> BackgroundResultStore:
    """Return the shared background result store."""

    return _RESULT_STORE


def reset_background_result_store_for_tests() -> None:
    """Clear the shared result store between tests."""

    _RESULT_STORE.clear()
