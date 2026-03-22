"""Utilities for working with FastMCP Context from sync tool functions."""

from __future__ import annotations

from fastmcp import Context
from server.adapters.mcp.session_state import (
    get_session_phase,
    get_session_value,
    set_session_phase,
    set_session_value,
)


def ctx_info(ctx: Context, message: str) -> None:
    """Best-effort INFO message to the connected MCP client."""

    try:
        ctx.info(message)
    except Exception:
        return


def ctx_warning(ctx: Context, message: str) -> None:
    """Best-effort WARNING message to the connected MCP client."""

    try:
        ctx.warning(message)
    except Exception:
        return


def ctx_error(ctx: Context, message: str) -> None:
    """Best-effort ERROR message to the connected MCP client."""

    try:
        ctx.error(message)
    except Exception:
        return


def ctx_progress(
    ctx: Context,
    progress: float,
    total: float | None = None,
    message: str | None = None,
) -> None:
    """Best-effort progress reporting for long-running interactions."""

    try:
        ctx.report_progress(progress=progress, total=total, message=message)
    except Exception:
        return


__all__ = [
    "ctx_error",
    "ctx_info",
    "ctx_progress",
    "ctx_warning",
    "get_session_phase",
    "get_session_value",
    "set_session_phase",
    "set_session_value",
]
