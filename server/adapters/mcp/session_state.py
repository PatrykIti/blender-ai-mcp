# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Helpers for session-scoped MCP state."""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import Awaitable

from fastmcp import Context

SESSION_PHASE_KEY = "phase"
DEFAULT_SESSION_PHASE = "bootstrap"
_MISSING = object()


def _get_prefixed_state_key(ctx: Context, key: str) -> str | None:
    try:
        make_state_key = getattr(ctx, "_make_state_key", None)
        if callable(make_state_key):
            return make_state_key(key)
    except Exception:
        return None
    return None


def _get_request_state_value(ctx: Context, key: str, default=_MISSING):
    prefixed_key = _get_prefixed_state_key(ctx, key)
    request_state = getattr(ctx, "_request_state", None)
    if prefixed_key is None or not isinstance(request_state, dict):
        return default
    return request_state.get(prefixed_key, default)


def _mirror_request_state_value(ctx: Context, key: str, value) -> None:
    prefixed_key = _get_prefixed_state_key(ctx, key)
    request_state = getattr(ctx, "_request_state", None)
    if prefixed_key is None or not isinstance(request_state, dict):
        return
    request_state[prefixed_key] = value


def _resolve_sync_awaitable(result, default=None):
    if not inspect.isawaitable(result):
        return result

    async def _await_value(awaitable: Awaitable[object]) -> object:
        return await awaitable

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(_await_value(result))

    if inspect.iscoroutine(result):
        result.close()
    return default


def _dispatch_awaitable(result) -> None:
    if not inspect.isawaitable(result):
        return

    try:
        asyncio.get_running_loop()
    except RuntimeError:

        async def _await_value(awaitable: Awaitable[object]) -> object:
            return await awaitable

        asyncio.run(_await_value(result))
        return

    asyncio.ensure_future(result)


async def get_session_value_async(ctx: Context, key: str, default=None):
    """Read a session-scoped value, awaiting async FastMCP Context state if needed."""

    request_value = _get_request_state_value(ctx, key, _MISSING)
    if request_value is not _MISSING:
        return request_value

    try:
        value = ctx.get_state(key)
    except Exception:
        return default

    if inspect.isawaitable(value):
        try:
            value = await value
        except Exception:
            return default
    return default if value is None else value


async def set_session_value_async(
    ctx: Context,
    key: str,
    value,
    *,
    serializable: bool = True,
) -> None:
    """Write a session-scoped value, awaiting async FastMCP Context state if needed."""

    _mirror_request_state_value(ctx, key, value)

    try:
        result = ctx.set_state(key, value, serializable=serializable)
    except Exception:
        return

    if inspect.isawaitable(result):
        try:
            await result
        except Exception:
            return

    _mirror_request_state_value(ctx, key, value)


def get_session_value(ctx: Context, key: str, default=None):
    """Read a session-scoped value with a default fallback."""

    request_value = _get_request_state_value(ctx, key, _MISSING)
    if request_value is not _MISSING:
        return request_value

    try:
        value = _resolve_sync_awaitable(ctx.get_state(key), default=default)
    except Exception:
        return default
    return default if value is None else value


def set_session_value(ctx: Context, key: str, value, *, serializable: bool = True) -> None:
    """Write a session-scoped value without failing the tool call."""

    _mirror_request_state_value(ctx, key, value)

    try:
        _dispatch_awaitable(ctx.set_state(key, value, serializable=serializable))
    except Exception:
        return

    _mirror_request_state_value(ctx, key, value)


def get_session_phase(ctx: Context) -> str:
    """Return the canonical session phase, defaulting to bootstrap."""

    return str(get_session_value(ctx, SESSION_PHASE_KEY, DEFAULT_SESSION_PHASE))


def set_session_phase(ctx: Context, phase: str) -> None:
    """Store the canonical session phase."""

    set_session_value(ctx, SESSION_PHASE_KEY, phase)
