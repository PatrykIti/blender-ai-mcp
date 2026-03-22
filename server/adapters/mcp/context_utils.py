"""Utilities for working with FastMCP Context from sync tool functions."""

from __future__ import annotations

import asyncio
import inspect

from fastmcp import Context
from mcp.types import ClientCapabilities, SamplingCapability, SamplingToolsCapability

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


def ctx_request_id(ctx: Context) -> str | None:
    """Best-effort request-id lookup for request-bound adapter helpers."""

    try:
        request_id = getattr(ctx, "request_id", None)
    except Exception:
        return None

    if callable(request_id):
        try:
            request_id = request_id()
        except Exception:
            return None

    if request_id is None:
        return None

    try:
        value = str(request_id)
    except Exception:
        return None

    return value or None


def ctx_sampling_capability(
    ctx: Context,
    *,
    needs_tools: bool = False,
) -> tuple[bool, str | None, str | None]:
    """Return whether the active MCP request can use sampling."""

    try:
        fastmcp = ctx.fastmcp
        session = ctx.session
    except Exception:
        return False, "unavailable", "sampling_context_unavailable"

    try:
        has_sampling = session.check_client_capability(capability=ClientCapabilities(sampling=SamplingCapability()))
        has_tools_capability = session.check_client_capability(
            capability=ClientCapabilities(sampling=SamplingCapability(tools=SamplingToolsCapability()))
        )
    except Exception:
        has_sampling = False
        has_tools_capability = False

    behavior = getattr(fastmcp, "sampling_handler_behavior", None)
    handler = getattr(fastmcp, "sampling_handler", None)

    if behavior == "always":
        if handler is None:
            return False, "unavailable", "sampling_handler_missing"
        return True, "fallback_handler", None

    client_sufficient = has_sampling and (not needs_tools or has_tools_capability)

    if behavior == "fallback":
        if client_sufficient:
            return True, "client", None
        if handler is not None:
            return True, "fallback_handler", None
        if needs_tools and has_sampling and not has_tools_capability:
            return False, "unavailable", "sampling_tools_capability_missing"
        return False, "unavailable", "sampling_capability_missing"

    if behavior not in {None, "always", "fallback"}:
        return False, "unavailable", "invalid_sampling_handler_behavior"

    if not has_sampling:
        return False, "unavailable", "sampling_capability_missing"

    if needs_tools and not has_tools_capability:
        return False, "unavailable", "sampling_tools_capability_missing"

    return True, "client", None


__all__ = [
    "ctx_error",
    "ctx_info",
    "ctx_progress",
    "ctx_request_id",
    "ctx_sampling_capability",
    "ctx_warning",
    "get_session_phase",
    "get_session_value",
    "set_session_phase",
    "set_session_value",
]
