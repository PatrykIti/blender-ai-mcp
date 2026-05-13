# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Session-scoped visibility transaction guards and audit helpers."""

from __future__ import annotations

import asyncio
import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Sequence, TypeVar

from fastmcp import Context
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.tools.tool import Tool

from server.adapters.mcp.session_capabilities import get_session_capability_state_async
from server.adapters.mcp.transforms.visibility_policy import GUIDED_DISCOVERY_TOOLS
from server.infrastructure.debug_profiles import emit_debug_log

logger = logging.getLogger(__name__)

_T = TypeVar("_T")
_TRACKERS_LOCK = threading.Lock()
_TRACKER_IDLE_TTL_SECONDS = 3600.0
_TRACKER_WAIT_POLL_SECONDS = 0.005


@dataclass
class _SessionVisibilityTracker:
    """In-memory audit/lock state for one FastMCP session."""

    busy: bool = False
    last_observed_tool_names: tuple[str, ...] = ()
    last_touched_monotonic: float = field(default_factory=time.monotonic)


_SESSION_TRACKERS: dict[str, _SessionVisibilityTracker] = {}


def _safe_session_id(ctx: Context | None) -> str | None:
    if ctx is None:
        return None
    try:
        session_id = getattr(ctx, "session_id", None)
    except Exception:
        return None
    if session_id is None:
        return None
    normalized = str(session_id).strip()
    return normalized or None


def _prune_stale_trackers(now: float) -> None:
    stale_session_ids = [
        session_id
        for session_id, tracker in _SESSION_TRACKERS.items()
        if not tracker.busy and now - tracker.last_touched_monotonic > _TRACKER_IDLE_TTL_SECONDS
    ]
    for session_id in stale_session_ids:
        _SESSION_TRACKERS.pop(session_id, None)


def _tracker_for_session(session_id: str) -> _SessionVisibilityTracker:
    now = time.monotonic()
    with _TRACKERS_LOCK:
        _prune_stale_trackers(now)
        tracker = _SESSION_TRACKERS.get(session_id)
        if tracker is None:
            tracker = _SessionVisibilityTracker()
            _SESSION_TRACKERS[session_id] = tracker
        tracker.last_touched_monotonic = now
        return tracker


def _limited_tool_list(names: Sequence[str], *, limit: int = 12) -> list[str]:
    normalized = sorted({str(name).strip() for name in names if str(name).strip()})
    if len(normalized) <= limit:
        return normalized
    return [*normalized[:limit], f"...(+{len(normalized) - limit} more)"]


async def _run_session_visibility_operation(
    ctx: Context | None,
    *,
    operation: str,
    action: Callable[[_SessionVisibilityTracker | None], Awaitable[_T]],
) -> _T:
    """Serialize one session-scoped visibility read/write operation."""

    session_id = _safe_session_id(ctx)
    if session_id is None:
        return await action(None)

    tracker = _tracker_for_session(session_id)
    wait_logged = False

    while True:
        with _TRACKERS_LOCK:
            if not tracker.busy:
                tracker.busy = True
                tracker.last_touched_monotonic = time.monotonic()
                break

        if not wait_logged:
            emit_debug_log(
                "visibility",
                logger,
                "[VISIBILITY_TXN] session=%s operation=%s wait_for_lock",
                session_id,
                operation,
                level=logging.DEBUG,
            )
            wait_logged = True
        await asyncio.sleep(_TRACKER_WAIT_POLL_SECONDS)

    try:
        return await action(tracker)
    finally:
        with _TRACKERS_LOCK:
            tracker.busy = False
            tracker.last_touched_monotonic = time.monotonic()


async def run_visibility_observation(
    ctx: Context | None,
    *,
    operation: str,
    read: Callable[[], Awaitable[_T]],
) -> _T:
    """Run one visibility-sensitive read under the same session barrier as refreshes."""

    async def _read(_tracker: _SessionVisibilityTracker | None) -> _T:
        return await read()

    return await _run_session_visibility_operation(
        ctx,
        operation=operation,
        action=_read,
    )


async def run_visibility_transaction(
    ctx: Context,
    *,
    phase: str,
    current_step: str | None,
    spatial_refresh_required: bool,
    expected_tool_names: Sequence[str],
    apply: Callable[[], Awaitable[_T]],
) -> _T:
    """Serialize one session-scoped visibility reapply and log the target surface."""

    async def _apply(_tracker: _SessionVisibilityTracker | None) -> _T:
        session_id = _safe_session_id(ctx)
        emit_debug_log(
            "visibility",
            logger,
            "[VISIBILITY_TXN] session=%s phase=%s step=%s spatial_refresh_required=%s expected_tool_count=%d expected_tools=%s",
            session_id or "-",
            phase,
            current_step or "-",
            spatial_refresh_required,
            len(set(expected_tool_names)),
            _limited_tool_list(expected_tool_names),
        )
        return await apply()

    return await _run_session_visibility_operation(
        ctx,
        operation=f"visibility_refresh:{phase}",
        action=_apply,
    )


async def audit_list_tools_snapshot(
    ctx: Context | None,
    *,
    tools: Sequence[Tool],
    source: str,
) -> None:
    """Compare observed `tools/list` output to the current guided visibility expectation."""

    if ctx is None:
        return

    session_id = _safe_session_id(ctx)
    if session_id is None:
        return

    tracker = _tracker_for_session(session_id)

    tool_names = tuple(sorted({tool.name for tool in tools}))
    previous_tool_names = tracker.last_observed_tool_names
    tracker.last_observed_tool_names = tool_names

    state = await get_session_capability_state_async(ctx)
    surface_profile = (
        getattr(state, "surface_profile", None) or getattr(ctx.fastmcp, "_bam_surface_profile", None) or "legacy-flat"
    )
    contract_line = getattr(state, "contract_version", None) or getattr(ctx.fastmcp, "_bam_contract_line", None)
    prompts_as_tools_enabled = bool(getattr(ctx.fastmcp, "_bam_prompts_as_tools_enabled", False))
    expected_tool_names = _expected_audit_tool_names(
        surface_profile=surface_profile,
        contract_line=contract_line,
        prompts_as_tools_enabled=prompts_as_tools_enabled,
    )
    if not expected_tool_names:
        return
    missing = sorted(set(expected_tool_names).difference(tool_names))
    unexpected = sorted(set(tool_names).difference(expected_tool_names))
    if missing or unexpected:
        emit_debug_log(
            "visibility",
            logger,
            "[VISIBILITY_AUDIT] session=%s source=%s phase=%s step=%s observed_tool_count=%d expected_tool_count=%d missing=%s unexpected=%s",
            session_id,
            source,
            getattr(state, "phase", None) or "-",
            str(state.guided_flow_state.get("current_step")) if isinstance(state.guided_flow_state, dict) else "-",
            len(tool_names),
            len(expected_tool_names),
            _limited_tool_list(missing),
            _limited_tool_list(unexpected),
            level=logging.WARNING,
        )
        return

    if previous_tool_names != tool_names:
        added = sorted(set(tool_names).difference(previous_tool_names))
        removed = sorted(set(previous_tool_names).difference(tool_names))
        emit_debug_log(
            "visibility",
            logger,
            "[VISIBILITY_AUDIT] session=%s source=%s tool_count=%d added=%s removed=%s",
            session_id,
            source,
            len(tool_names),
            _limited_tool_list(added),
            _limited_tool_list(removed),
        )


def _expected_audit_tool_names(
    *,
    surface_profile: str,
    contract_line: str | None,
    prompts_as_tools_enabled: bool,
) -> tuple[str, ...]:
    """Return the stable shaped public surface expected from `tools/list()`."""

    if surface_profile != "llm-guided":
        return ()

    from server.adapters.mcp.discovery.tool_inventory import get_pinned_public_tools

    public_visible_names = {
        *get_pinned_public_tools(contract_line=contract_line),
        *GUIDED_DISCOVERY_TOOLS,
    }
    if prompts_as_tools_enabled:
        public_visible_names.update({"list_prompts", "get_prompt"})
    return tuple(sorted(public_visible_names))


class SessionVisibilityAuditMiddleware(Middleware):
    """Serialize `tools/list` against in-flight visibility refreshes and audit results."""

    async def on_list_tools(
        self,
        context: MiddlewareContext[Any],
        call_next: Callable[[MiddlewareContext[Any]], Awaitable[Sequence[Tool]]],
    ) -> Sequence[Tool]:
        ctx = context.fastmcp_context

        async def _list_and_audit() -> Sequence[Tool]:
            tools = await call_next(context)
            try:
                await audit_list_tools_snapshot(ctx, tools=tools, source="tools/list")
            except Exception:
                logger.exception("[VISIBILITY_AUDIT] source=tools/list audit_failed")
            return tools

        return await run_visibility_observation(
            ctx,
            operation="tools/list",
            read=_list_and_audit,
        )
