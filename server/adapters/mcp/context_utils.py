"""Utilities for working with FastMCP Context from sync tool functions."""

from __future__ import annotations

import asyncio
import inspect

from fastmcp import Context
from server.adapters.mcp.session_state import (
    get_session_phase,
    get_session_value,
    set_session_phase,
    set_session_value,
)


def _fire_and_forget(result) -> None:
    """Await async FastMCP context operations when possible, else degrade silently."""

    if not inspect.isawaitable(result):
        return

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return

    loop.create_task(result)


def ctx_info(ctx: Context, message: str) -> None:
    """Best-effort INFO message to the connected MCP client."""

    try:
        _fire_and_forget(ctx.info(message))
    except Exception:
        return


def ctx_warning(ctx: Context, message: str) -> None:
    """Best-effort WARNING message to the connected MCP client."""

    try:
        _fire_and_forget(ctx.warning(message))
    except Exception:
        return


def ctx_error(ctx: Context, message: str) -> None:
    """Best-effort ERROR message to the connected MCP client."""

    try:
        _fire_and_forget(ctx.error(message))
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
        _fire_and_forget(ctx.report_progress(progress=progress, total=total, message=message))
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
