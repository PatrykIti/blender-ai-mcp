"""Tests for Streamable guided visibility transaction helpers."""

from __future__ import annotations

import asyncio
import logging
from types import SimpleNamespace

import pytest
import server.adapters.mcp.visibility_runtime as visibility_runtime_module
from fastmcp.tools.tool import Tool
from server.adapters.mcp.discovery.search_surface import BlenderDiscoverySearchTransform
from server.adapters.mcp.visibility_runtime import (
    SessionVisibilityAuditMiddleware,
    _expected_audit_tool_names,
    audit_list_tools_snapshot,
    run_visibility_transaction,
)


class _FakeContext:
    def __init__(self, session_id: str = "session-1"):
        self.session_id = session_id
        self.fastmcp = SimpleNamespace(
            _bam_surface_profile="llm-guided",
            _bam_contract_line="llm-guided-v2",
            _bam_prompts_as_tools_enabled=False,
        )


def _tool(name: str) -> Tool:
    return Tool.from_function(lambda: "ok", name=name)


def test_expected_audit_tool_names_matches_shaped_guided_surface():
    assert _expected_audit_tool_names(
        surface_profile="llm-guided",
        contract_line="llm-guided-v2",
        prompts_as_tools_enabled=False,
    ) == (
        "browse_workflows",
        "call_tool",
        "reference_images",
        "router_get_status",
        "router_set_goal",
        "scene_relation_graph",
        "scene_scope_graph",
        "scene_view_diagnostics",
        "search_tools",
    )


def test_list_tools_middleware_waits_for_inflight_visibility_transaction():
    middleware = SessionVisibilityAuditMiddleware()
    ctx = _FakeContext()
    observed_lock_state: dict[str, bool | None] = {"locked": None}

    async def run() -> None:
        gate = asyncio.Event()

        async def slow_refresh() -> str:
            await gate.wait()
            return "done"

        refresh_task = asyncio.create_task(
            run_visibility_transaction(
                ctx,
                phase="build",
                current_step="place_secondary_parts",
                spatial_refresh_required=True,
                expected_tool_names=("call_tool", "scene_relation_graph"),
                apply=slow_refresh,
            )
        )
        await asyncio.sleep(0)

        async def call_next(_context):
            observed_lock_state["locked"] = refresh_task.done()
            return [_tool("call_tool"), _tool("scene_relation_graph")]

        middleware_task = asyncio.create_task(
            middleware.on_list_tools(
                SimpleNamespace(fastmcp_context=ctx),
                call_next,
            )
        )
        await asyncio.sleep(0)
        assert middleware_task.done() is False

        gate.set()
        tools = await middleware_task
        assert [tool.name for tool in tools] == ["call_tool", "scene_relation_graph"]
        await refresh_task

    asyncio.run(run())
    assert observed_lock_state["locked"] is True


def test_discovery_proxy_waits_for_inflight_visibility_transaction():
    transform = BlenderDiscoverySearchTransform(entry_map={})
    ctx = _FakeContext()
    observed_lock_state: dict[str, bool | None] = {"locked": None}
    refresh_task: asyncio.Task[None] | None = None

    class _FakeFastMCP:
        async def get_tool(self, _tool_name: str) -> object:
            observed_lock_state["locked"] = refresh_task.done() if refresh_task is not None else None
            return object()

    ctx.fastmcp = _FakeFastMCP()

    async def run() -> None:
        nonlocal refresh_task
        gate = asyncio.Event()

        async def slow_refresh() -> None:
            await gate.wait()

        refresh_task = asyncio.create_task(
            run_visibility_transaction(
                ctx,
                phase="build",
                current_step="place_secondary_parts",
                spatial_refresh_required=True,
                expected_tool_names=("call_tool", "scene_relation_graph"),
                apply=slow_refresh,
            )
        )
        await asyncio.sleep(0)

        visible_task = asyncio.create_task(transform._is_tool_currently_visible_safe(ctx, "call_tool"))
        await asyncio.sleep(0)
        assert visible_task.done() is False

        gate.set()
        assert await visible_task is True
        await refresh_task

    asyncio.run(run())
    assert observed_lock_state["locked"] is True


def test_cancelled_waiter_does_not_leak_session_lock():
    ctx = _FakeContext()

    async def run() -> None:
        gate = asyncio.Event()

        async def slow_refresh() -> None:
            await gate.wait()

        refresh_task = asyncio.create_task(
            run_visibility_transaction(
                ctx,
                phase="build",
                current_step="place_secondary_parts",
                spatial_refresh_required=True,
                expected_tool_names=("call_tool",),
                apply=slow_refresh,
            )
        )
        await asyncio.sleep(0)

        waiting_task = asyncio.create_task(
            run_visibility_transaction(
                ctx,
                phase="build",
                current_step="place_secondary_parts",
                spatial_refresh_required=True,
                expected_tool_names=("call_tool",),
                apply=lambda: asyncio.sleep(0, result=None),
            )
        )
        await asyncio.sleep(0.02)
        waiting_task.cancel()

        with pytest.raises(asyncio.CancelledError):
            await waiting_task

        gate.set()
        await refresh_task

        recovered = await asyncio.wait_for(
            run_visibility_transaction(
                ctx,
                phase="build",
                current_step="place_secondary_parts",
                spatial_refresh_required=False,
                expected_tool_names=("call_tool",),
                apply=lambda: asyncio.sleep(0, result="recovered"),
            ),
            timeout=0.2,
        )
        assert recovered == "recovered"

    asyncio.run(run())


def test_tracker_lookup_prunes_only_stale_idle_sessions(monkeypatch):
    visibility_runtime_module._SESSION_TRACKERS.clear()
    visibility_runtime_module._SESSION_TRACKERS.update(
        {
            "stale-session": visibility_runtime_module._SessionVisibilityTracker(last_touched_monotonic=0.0),
            "busy-session": visibility_runtime_module._SessionVisibilityTracker(
                busy=True,
                last_touched_monotonic=0.0,
            ),
            "recent-session": visibility_runtime_module._SessionVisibilityTracker(last_touched_monotonic=3500.0),
        }
    )
    monkeypatch.setattr(visibility_runtime_module.time, "monotonic", lambda: 4000.0)

    tracker = visibility_runtime_module._tracker_for_session("fresh-session")

    assert tracker is visibility_runtime_module._SESSION_TRACKERS["fresh-session"]
    assert "stale-session" not in visibility_runtime_module._SESSION_TRACKERS
    assert "busy-session" in visibility_runtime_module._SESSION_TRACKERS
    assert "recent-session" in visibility_runtime_module._SESSION_TRACKERS

    visibility_runtime_module._SESSION_TRACKERS.clear()


def test_audit_list_tools_snapshot_logs_visibility_mismatch(monkeypatch, caplog):
    ctx = _FakeContext()
    monkeypatch.setenv("BLENDER_AI_DEBUG", "visibility")

    async def fake_state(_ctx: _FakeContext) -> SimpleNamespace:
        return SimpleNamespace(
            surface_profile="llm-guided",
            contract_version="llm-guided-v2",
            phase="build",
            guided_handoff=None,
            guided_flow_state={"current_step": "place_secondary_parts"},
            gate_plan=None,
        )

    monkeypatch.setattr(visibility_runtime_module, "get_session_capability_state_async", fake_state)
    monkeypatch.setattr(
        visibility_runtime_module,
        "_expected_audit_tool_names",
        lambda **kwargs: ("call_tool", "scene_relation_graph"),
    )

    async def run() -> None:
        with caplog.at_level(logging.WARNING, logger="server.adapters.mcp.visibility_runtime"):
            await audit_list_tools_snapshot(
                ctx,
                tools=[_tool("call_tool"), _tool("unexpected_tool")],
                source="tools/list",
            )

    asyncio.run(run())
    assert "[VISIBILITY_AUDIT]" in caplog.text
    assert "missing=['scene_relation_graph']" in caplog.text
    assert "unexpected=['unexpected_tool']" in caplog.text


def test_audit_list_tools_snapshot_accepts_shaped_public_names(monkeypatch, caplog):
    ctx = _FakeContext()
    monkeypatch.setenv("BLENDER_AI_DEBUG", "visibility")

    async def fake_state(_ctx: _FakeContext) -> SimpleNamespace:
        return SimpleNamespace(
            surface_profile="llm-guided",
            contract_version="llm-guided-v2",
            phase="build",
            guided_handoff=None,
            guided_flow_state={"current_step": "place_secondary_parts"},
            gate_plan=None,
        )

    monkeypatch.setattr(visibility_runtime_module, "get_session_capability_state_async", fake_state)
    ctx.fastmcp._bam_prompts_as_tools_enabled = True
    monkeypatch.setattr(
        visibility_runtime_module,
        "_expected_audit_tool_names",
        lambda **kwargs: (
            "scene_relation_graph",
            "search_tools",
            "call_tool",
            "list_prompts",
            "get_prompt",
        ),
    )

    async def run() -> None:
        with caplog.at_level(logging.WARNING, logger="server.adapters.mcp.visibility_runtime"):
            await audit_list_tools_snapshot(
                ctx,
                tools=[
                    _tool("scene_relation_graph"),
                    _tool("search_tools"),
                    _tool("call_tool"),
                    _tool("list_prompts"),
                    _tool("get_prompt"),
                ],
                source="tools/list",
            )

    asyncio.run(run())
    assert "[VISIBILITY_AUDIT]" not in caplog.text


def test_visibility_transactions_do_not_block_other_sessions_discovery():
    transform = BlenderDiscoverySearchTransform(entry_map={})
    blocked_ctx = _FakeContext("session-1")
    unblocked_ctx = _FakeContext("session-2")

    class _FakeFastMCP:
        async def get_tool(self, _tool_name: str) -> object:
            return object()

    blocked_ctx.fastmcp = _FakeFastMCP()
    unblocked_ctx.fastmcp = _FakeFastMCP()

    async def run() -> None:
        gate = asyncio.Event()

        async def slow_refresh() -> None:
            await gate.wait()

        refresh_task = asyncio.create_task(
            run_visibility_transaction(
                blocked_ctx,
                phase="build",
                current_step="place_secondary_parts",
                spatial_refresh_required=True,
                expected_tool_names=("call_tool", "scene_relation_graph"),
                apply=slow_refresh,
            )
        )
        await asyncio.sleep(0)

        other_session_task = asyncio.create_task(transform._is_tool_currently_visible_safe(unblocked_ctx, "call_tool"))
        assert await asyncio.wait_for(other_session_task, timeout=0.2) is True
        assert refresh_task.done() is False

        gate.set()
        await refresh_task

    asyncio.run(run())


def test_list_tools_middleware_swallows_audit_failures(monkeypatch, caplog):
    middleware = SessionVisibilityAuditMiddleware()
    ctx = _FakeContext()

    async def fake_audit(*args, **kwargs) -> None:
        raise RuntimeError("synthetic audit failure")

    monkeypatch.setattr(visibility_runtime_module, "audit_list_tools_snapshot", fake_audit)

    async def run() -> list[str]:
        async def call_next(_context):
            return [_tool("call_tool")]

        with caplog.at_level(logging.ERROR, logger="server.adapters.mcp.visibility_runtime"):
            tools = await middleware.on_list_tools(SimpleNamespace(fastmcp_context=ctx), call_next)
        return [tool.name for tool in tools]

    assert asyncio.run(run()) == ["call_tool"]
    assert "audit_failed" in caplog.text
