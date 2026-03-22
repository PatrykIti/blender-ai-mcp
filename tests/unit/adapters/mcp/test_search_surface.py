"""Tests for TASK-084 search infrastructure on the shaped public surface."""

from __future__ import annotations

import asyncio
import json
from dataclasses import replace

from fastmcp import FastMCP

from server.adapters.mcp.factory import build_surface_providers
from server.adapters.mcp.surfaces import get_surface_profile
from server.adapters.mcp.transforms import materialize_transforms
from server.adapters.mcp.transforms.discovery import build_discovery_transform


def _build_search_enabled_server() -> FastMCP:
    base_surface = get_surface_profile("llm-guided")
    search_surface = replace(base_surface, search_enabled=True, search_max_results=5)

    return FastMCP(
        search_surface.server_name,
        providers=build_surface_providers(search_surface),
        transforms=materialize_transforms(search_surface),
        list_page_size=search_surface.list_page_size,
        tasks=search_surface.tasks_enabled,
        instructions=search_surface.instructions,
    )


def _decode_tool_result(result):
    structured = getattr(result, "structured_content", None)
    if structured is not None:
        if isinstance(structured, dict) and "result" in structured:
            return structured["result"]
        return structured

    blocks = getattr(result, "content", []) or []
    text = "".join(getattr(block, "text", "") for block in blocks).strip()
    return json.loads(text)


def test_discovery_transform_stays_disabled_by_default_for_llm_guided():
    """Infrastructure may exist without forcing default public rollout yet."""

    assert build_discovery_transform(get_surface_profile("llm-guided")) is None


def test_search_enabled_surface_lists_only_pinned_and_synthetic_tools():
    """Search-enabled llm-guided surface should expose only pinned entry tools plus search proxies."""

    server = _build_search_enabled_server()

    async def run():
        tools = await server.list_tools()
        return {tool.name for tool in tools}

    tool_names = asyncio.run(run())

    assert tool_names == {
        "router_set_goal",
        "router_get_status",
        "browse_workflows",
        "search_tools",
        "call_tool",
    }


def test_search_tools_operate_on_public_alias_names(monkeypatch):
    """Search results should use public aliases for non-pinned discovered tools."""

    server = _build_search_enabled_server()

    async def run():
        return await server.call_tool("search_tools", {"query": "inspect topology object materials"})

    payload = _decode_tool_result(asyncio.run(run()))

    assert any(tool["name"] == "inspect_scene" for tool in payload)
    assert all(tool["name"] != "scene_inspect" for tool in payload)


def test_call_tool_proxy_matches_direct_public_alias_execution(monkeypatch):
    """call_tool should execute the same public alias path as a direct surface call."""

    class Handler:
        def list_workflows(self):
            return {"workflows_dir": "/tmp", "count": 1, "workflows": [{"name": "chair"}]}

    monkeypatch.setattr(
        "server.adapters.mcp.areas.workflow_catalog.get_workflow_catalog_handler",
        lambda: Handler(),
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.workflow_catalog.ctx_info",
        lambda ctx, message: None,
    )

    server = _build_search_enabled_server()

    async def run():
        direct = await server.call_tool("browse_workflows", {"action": "list"})
        discovered = await server.call_tool(
            "call_tool",
            {"name": "browse_workflows", "arguments": {"action": "list"}},
        )
        return direct, discovered

    direct, discovered = asyncio.run(run())

    assert _decode_tool_result(direct) == _decode_tool_result(discovered)
