# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Canonical session phase model for adaptive FastMCP surfaces."""

from __future__ import annotations

from enum import StrEnum


class SessionPhase(StrEnum):
    """Canonical phase vocabulary for FastMCP surface adaptation."""

    BOOTSTRAP = "bootstrap"
    PLANNING = "planning"
    WORKFLOW_RESOLUTION = "workflow_resolution"
    BUILD = "build"
    INSPECT_VALIDATE = "inspect_validate"
    REPAIR = "repair"
    EXPORT_HANDOFF = "export_handoff"


FIRST_PASS_ACTIVE_PHASES: tuple[SessionPhase, ...] = (
    SessionPhase.BOOTSTRAP,
    SessionPhase.PLANNING,
    SessionPhase.BUILD,
    SessionPhase.INSPECT_VALIDATE,
)


def coerce_session_phase(value: str | SessionPhase | None) -> SessionPhase:
    """Coerce arbitrary stored phase values onto the canonical vocabulary."""

    if isinstance(value, SessionPhase):
        return value

    if value is None:
        return SessionPhase.BOOTSTRAP

    try:
        return SessionPhase(str(value))
    except ValueError:
        return SessionPhase.BOOTSTRAP
