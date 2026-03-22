# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Registry for MCP task bookkeeping and addon job identity mapping."""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from time import time

from server.adapters.mcp.tasks.progress import (
    BackgroundProgressSnapshot,
    build_progress_snapshot,
)


BackgroundJobStatus = str


@dataclass(frozen=True)
class BackgroundJobRecord:
    """Tracked state for one MCP background task and its backend job."""

    task_id: str
    tool_name: str
    backend_kind: str
    backend_job_id: str | None = None
    status: BackgroundJobStatus = "queued"
    progress: BackgroundProgressSnapshot = field(default_factory=BackgroundProgressSnapshot)
    cancelled: bool = False
    result_ref: str | None = None
    error: str | None = None
    created_at: float = field(default_factory=time)
    updated_at: float = field(default_factory=time)

    def to_dict(self) -> dict[str, object]:
        """Serialize the record into stable diagnostics."""

        return {
            "task_id": self.task_id,
            "tool_name": self.tool_name,
            "backend_kind": self.backend_kind,
            "backend_job_id": self.backend_job_id,
            "status": self.status,
            "progress": self.progress.to_dict(),
            "cancelled": self.cancelled,
            "result_ref": self.result_ref,
            "error": self.error,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class BackgroundJobRegistry:
    """Thread-safe registry keyed by FastMCP ``task_id``."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._jobs: dict[str, BackgroundJobRecord] = {}

    def register(self, *, task_id: str, tool_name: str, backend_kind: str) -> BackgroundJobRecord:
        """Create or replace the tracked state for a background task."""

        record = BackgroundJobRecord(
            task_id=task_id,
            tool_name=tool_name,
            backend_kind=backend_kind,
        )
        with self._lock:
            self._jobs[task_id] = record
        return record

    def bind_backend_job(self, task_id: str, backend_job_id: str) -> BackgroundJobRecord | None:
        """Attach the addon/server-local job identity to an existing task record."""

        return self._update(
            task_id,
            backend_job_id=backend_job_id,
            status="running",
        )

    def update_progress(
        self,
        task_id: str,
        *,
        current: float,
        total: float | None = None,
        message: str | None = None,
        status: BackgroundJobStatus | None = None,
    ) -> BackgroundJobRecord | None:
        """Update progress bookkeeping for a tracked task."""

        updates = {
            "progress": build_progress_snapshot(current=current, total=total, message=message),
        }
        if status is not None:
            updates["status"] = status
        return self._update(task_id, **updates)

    def mark_completed(self, task_id: str, *, result_ref: str | None = None) -> BackgroundJobRecord | None:
        """Mark a task as completed and optionally attach a stable result reference."""

        return self._update(
            task_id,
            status="completed",
            result_ref=result_ref,
            cancelled=False,
            error=None,
        )

    def mark_failed(self, task_id: str, error: str) -> BackgroundJobRecord | None:
        """Mark a task as failed."""

        return self._update(
            task_id,
            status="failed",
            error=error,
        )

    def mark_cancelled(self, task_id: str, *, error: str | None = None) -> BackgroundJobRecord | None:
        """Mark a task as cancelled."""

        return self._update(
            task_id,
            status="cancelled",
            cancelled=True,
            error=error,
        )

    def get(self, task_id: str) -> BackgroundJobRecord | None:
        """Return the tracked record for a task id."""

        with self._lock:
            return self._jobs.get(task_id)

    def list(self) -> tuple[BackgroundJobRecord, ...]:
        """Return all tracked jobs in insertion order."""

        with self._lock:
            return tuple(self._jobs.values())

    def clear(self) -> None:
        """Remove all tracked jobs."""

        with self._lock:
            self._jobs.clear()

    def _update(self, task_id: str, **changes) -> BackgroundJobRecord | None:
        with self._lock:
            current = self._jobs.get(task_id)
            if current is None:
                return None

            updated = BackgroundJobRecord(
                task_id=current.task_id,
                tool_name=changes.get("tool_name", current.tool_name),
                backend_kind=changes.get("backend_kind", current.backend_kind),
                backend_job_id=changes.get("backend_job_id", current.backend_job_id),
                status=changes.get("status", current.status),
                progress=changes.get("progress", current.progress),
                cancelled=changes.get("cancelled", current.cancelled),
                result_ref=changes.get("result_ref", current.result_ref),
                error=changes.get("error", current.error),
                created_at=current.created_at,
                updated_at=time(),
            )
            self._jobs[task_id] = updated
            return updated


_JOB_REGISTRY = BackgroundJobRegistry()


def get_background_job_registry() -> BackgroundJobRegistry:
    """Return the shared background job registry."""

    return _JOB_REGISTRY


def reset_background_job_registry_for_tests() -> None:
    """Clear shared registry state between tests."""

    _JOB_REGISTRY.clear()
