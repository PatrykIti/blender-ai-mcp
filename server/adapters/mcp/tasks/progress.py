# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Progress snapshots for MCP background job tracking."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BackgroundProgressSnapshot:
    """Progress state tracked for a background-capable task."""

    current: float = 0.0
    total: float | None = None
    message: str | None = None

    @property
    def ratio(self) -> float | None:
        """Return progress ratio when ``total`` is available and valid."""

        if self.total is None or self.total <= 0:
            return None
        return max(0.0, min(1.0, float(self.current) / float(self.total)))

    def to_dict(self) -> dict[str, float | str | None]:
        """Serialize the snapshot into a diagnostics-friendly dict."""

        return {
            "current": self.current,
            "total": self.total,
            "message": self.message,
            "ratio": self.ratio,
        }


def build_progress_snapshot(
    current: float,
    total: float | None = None,
    message: str | None = None,
) -> BackgroundProgressSnapshot:
    """Build a normalized progress snapshot."""

    return BackgroundProgressSnapshot(
        current=float(current),
        total=float(total) if total is not None else None,
        message=message,
    )
