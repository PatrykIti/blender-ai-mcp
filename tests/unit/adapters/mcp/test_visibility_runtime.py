"""Tests for Streamable guided visibility transaction helpers."""

from __future__ import annotations

import asyncio
import logging
from types import SimpleNamespace

import server.adapters.mcp.guided_mode as guided_mode_module
import server.adapters.mcp.visibility_runtime as visibility_runtime_module
from fastmcp.tools.tool import Tool
from server.adapters.mcp.discovery.search_surface import BlenderDiscoverySearchTransform
from server.adapters.mcp.visibility_runtime import (
    SessionVisibilityAuditMiddleware,
    audit_list_tools_snapshot,
    run_visibility_transaction,
)


class _FakeContext:
    def __init__(self, session_id: str = "session-1"):
        self.session_id = session_id


def _tool(name: str) -> Tool:
    return Tool.from_function(lambda: "ok", name=name)


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


def test_audit_list_tools_snapshot_logs_visibility_mismatch(monkeypatch, caplog):
    ctx = _FakeContext()

    async def fake_state(_ctx: _FakeContext) -> SimpleNamespace:
        return SimpleNamespace(
            surface_profile="llm-guided",
            phase="build",
            guided_handoff=None,
            guided_flow_state={"current_step": "place_secondary_parts"},
            gate_plan=None,
        )

    monkeypatch.setattr(visibility_runtime_module, "get_session_capability_state_async", fake_state)
    monkeypatch.setattr(
        guided_mode_module,
        "build_visibility_diagnostics",
        lambda *args, **kwargs: SimpleNamespace(
            visible_tool_names=("call_tool", "scene_relation_graph"),
            phase="build",
        ),
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
