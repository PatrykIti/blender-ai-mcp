# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Helpers for session-scoped MCP state."""

from __future__ import annotations

from fastmcp import Context

SESSION_PHASE_KEY = "phase"
DEFAULT_SESSION_PHASE = "bootstrap"


def get_session_value(ctx: Context, key: str, default=None):
    """Read a session-scoped value with a default fallback."""

    try:
        value = ctx.get_state(key)
    except Exception:
        return default
    return default if value is None else value


def set_session_value(ctx: Context, key: str, value, *, serializable: bool = True) -> None:
    """Write a session-scoped value without failing the tool call."""

    try:
        ctx.set_state(key, value, serializable=serializable)
    except Exception:
        return


def get_session_phase(ctx: Context) -> str:
    """Return the canonical session phase, defaulting to bootstrap."""

    return str(get_session_value(ctx, SESSION_PHASE_KEY, DEFAULT_SESSION_PHASE))


def set_session_phase(ctx: Context, phase: str) -> None:
    """Store the canonical session phase."""

    set_session_value(ctx, SESSION_PHASE_KEY, phase)
