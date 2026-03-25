"""Tests for TASK-084 search infrastructure on the shaped public surface."""

from __future__ import annotations

import asyncio
import json
from dataclasses import replace
from typing import Any, cast

import pytest
from fastmcp import FastMCP
from fastmcp.exceptions import NotFoundError, ToolError
from fastmcp.server.transforms.visibility import create_visibility_transforms
from server.adapters.mcp.factory import build_server, build_surface_providers
from server.adapters.mcp.session_phase import SessionPhase
from server.adapters.mcp.surfaces import get_surface_profile
from server.adapters.mcp.transforms import build_surface_transform_pipeline, materialize_transforms
from server.adapters.mcp.transforms.discovery import build_discovery_transform
from server.adapters.mcp.transforms.prompts_bridge import build_prompts_bridge_transform
from server.adapters.mcp.transforms.visibility_policy import build_visibility_rules


def _build_search_enabled_server() -> FastMCP:
    base_surface = get_surface_profile("llm-guided")
    search_surface = replace(base_surface, search_enabled=True, search_max_results=5)

    server: Any = FastMCP(
        search_surface.server_name,
        providers=build_surface_providers(search_surface),
        transforms=materialize_transforms(search_surface),
        list_page_size=search_surface.list_page_size,
        tasks=search_surface.tasks_enabled,
        instructions=search_surface.instructions,
    )
    prompts_bridge = build_prompts_bridge_transform(search_surface, provider=server)
    if prompts_bridge is not None:
        server.add_transform(prompts_bridge)
    server._bam_surface_profile = search_surface.name
    return cast(FastMCP, server)


def _build_phase_search_server(phase: SessionPhase) -> FastMCP:
    surface = replace(get_surface_profile("llm-guided"), search_enabled=True)
    base_pipeline = build_surface_transform_pipeline(surface)
    transforms = []
    for stage in base_pipeline:
        if stage.name == "visibility":
            transforms.extend(create_visibility_transforms(build_visibility_rules(surface.name, phase)))
            continue
        transform = stage.transform
        if transform is None:
            continue
        if isinstance(transform, (list, tuple)):
            transforms.extend(transform)
        else:
            transforms.append(transform)

    server: Any = FastMCP(
        surface.server_name,
        providers=build_surface_providers(surface),
        transforms=transforms,
        list_page_size=surface.list_page_size,
        tasks=surface.tasks_enabled,
        instructions=surface.instructions,
    )
    prompts_bridge = build_prompts_bridge_transform(surface, provider=server)
    if prompts_bridge is not None:
        server.add_transform(prompts_bridge)
    server._bam_surface_profile = surface.name
    return cast(FastMCP, server)


def _build_phase_visible_server(phase: SessionPhase) -> FastMCP:
    surface = replace(get_surface_profile("llm-guided"), search_enabled=False)
    base_pipeline = build_surface_transform_pipeline(surface)
    transforms = []
    for stage in base_pipeline:
        if stage.name == "visibility":
            transforms.extend(create_visibility_transforms(build_visibility_rules(surface.name, phase)))
            continue
        if stage.name == "discovery":
            continue
        transform = stage.transform
        if transform is None:
            continue
        if isinstance(transform, (list, tuple)):
            transforms.extend(transform)
        else:
            transforms.append(transform)

    server: Any = FastMCP(
        surface.server_name,
        providers=build_surface_providers(surface),
        transforms=transforms,
        list_page_size=surface.list_page_size,
        tasks=surface.tasks_enabled,
        instructions=surface.instructions,
    )
    server._bam_surface_profile = surface.name
    return cast(FastMCP, server)


def _decode_tool_result(result):
    structured = getattr(result, "structured_content", None)
    if structured is not None:
        if isinstance(structured, dict) and "result" in structured:
            return structured["result"]
        return structured

    blocks = getattr(result, "content", []) or []
    text = "".join(getattr(block, "text", "") for block in blocks).strip()
    return json.loads(text)


def test_discovery_transform_enabled_by_default_for_llm_guided():
    """llm-guided should now default to search-first discovery."""

    assert build_discovery_transform(get_surface_profile("llm-guided")) is not None


def test_default_llm_guided_surface_lists_only_pinned_and_synthetic_tools():
    """Default llm-guided surface should expose only pinned entry tools plus search proxies."""

    server = build_server("llm-guided")

    async def run():
        tools = await server.list_tools()
        return {tool.name for tool in tools}

    tool_names = asyncio.run(run())

    assert tool_names == {
        "router_set_goal",
        "router_get_status",
        "browse_workflows",
        "list_prompts",
        "get_prompt",
        "search_tools",
        "call_tool",
    }


def test_bootstrap_search_does_not_leak_hidden_build_tools():
    """Bootstrap-phase discovery should not surface hidden build tools."""

    server = build_server("llm-guided")

    async def run():
        return await server.call_tool("search_tools", {"query": "inspect topology object materials"})

    payload = _decode_tool_result(asyncio.run(run()))

    assert all(tool["name"] != "inspect_scene" for tool in payload)
    assert all(tool["name"] != "scene_inspect" for tool in payload)


def test_build_phase_search_uses_public_alias_names_for_discovered_tools():
    """Build-phase discovery should expose public aliases on the shaped surface."""

    server = _build_phase_search_server(SessionPhase.BUILD)

    async def run():
        return await server.call_tool("search_tools", {"query": "inspect topology object materials"})

    payload = _decode_tool_result(asyncio.run(run()))

    assert any(tool["name"] == "inspect_scene" for tool in payload)
    assert all(tool["name"] != "scene_inspect" for tool in payload)


def test_phase_search_results_follow_visibility_profile_changes():
    """Search results should swap build-only and inspect-only capabilities by session phase."""

    build_server = _build_phase_search_server(SessionPhase.BUILD)
    inspect_server = _build_phase_search_server(SessionPhase.INSPECT_VALIDATE)

    async def run():
        build_result = await build_server.call_tool("search_tools", {"query": "create cube primitive light camera"})
        inspect_result = await inspect_server.call_tool("search_tools", {"query": "create cube primitive light camera"})
        return _decode_tool_result(build_result), _decode_tool_result(inspect_result)

    build_payload, inspect_payload = asyncio.run(run())
    build_names = {tool["name"] for tool in build_payload}
    inspect_names = {tool["name"] for tool in inspect_payload}

    assert "modeling_create_primitive" in build_names
    assert "bake_ao" not in build_names
    assert "bake_ao" in inspect_names
    assert "modeling_create_primitive" not in inspect_names


def test_phase_shaped_list_tools_follow_visibility_without_discovery():
    """Visibility policy should affect the actual listed tools even without discovery collapse."""

    build_server = _build_phase_visible_server(SessionPhase.BUILD)
    inspect_server = _build_phase_visible_server(SessionPhase.INSPECT_VALIDATE)

    async def run():
        build_names = {tool.name for tool in await build_server.list_tools()}
        inspect_names = {tool.name for tool in await inspect_server.list_tools()}
        return build_names, inspect_names

    build_names, inspect_names = asyncio.run(run())

    assert "modeling_create_primitive" in build_names
    assert "bake_ao" not in build_names
    assert "bake_ao" in inspect_names
    assert "modeling_create_primitive" not in inspect_names
    assert "inspect_scene" in build_names
    assert "inspect_scene" in inspect_names


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

    server = build_server("llm-guided")

    async def run():
        direct = await server.call_tool("browse_workflows", {"action": "list"})
        discovered = await server.call_tool(
            "call_tool",
            {"name": "browse_workflows", "arguments": {"action": "list"}},
        )
        return direct, discovered

    direct, discovered = asyncio.run(run())

    assert _decode_tool_result(direct) == _decode_tool_result(discovered)


def test_search_first_rollout_reduces_visible_tool_count_and_payload_size():
    """llm-guided search-first should materially reduce the initial tool payload."""

    legacy = build_server("legacy-flat")
    guided = build_server("llm-guided")

    async def run():
        legacy_tools = await legacy.list_tools()
        guided_tools = await guided.list_tools()
        legacy_payload = [tool.to_mcp_tool().model_dump(mode="json", exclude_none=True) for tool in legacy_tools]
        guided_payload = [tool.to_mcp_tool().model_dump(mode="json", exclude_none=True) for tool in guided_tools]
        return (
            len(legacy_tools),
            len(guided_tools),
            len(json.dumps(legacy_payload)),
            len(json.dumps(guided_payload)),
        )

    legacy_count, guided_count, legacy_bytes, guided_bytes = asyncio.run(run())

    assert legacy_count == 167
    assert guided_count == 7
    assert guided_bytes < legacy_bytes


def test_call_tool_cannot_invoke_hidden_tool_during_bootstrap():
    """Hidden tools should not become callable through call_tool during bootstrap."""

    server = build_server("llm-guided")

    async def run():
        return await server.call_tool(
            "call_tool",
            {"name": "inspect_scene", "arguments": {"action": "object", "target_object": "Cube"}},
        )

    with pytest.raises((NotFoundError, ToolError)):
        asyncio.run(run())


def test_guided_surface_fails_closed_for_direct_and_discovered_calls(monkeypatch):
    """Guided surfaces should not silently bypass router failures during discovery-first rollout."""

    class Handler:
        def list_objects(self):
            return ["Cube"]

    class FailingRouter:
        def process_llm_tool_call(self, tool_name, params, prompt=None):
            raise RuntimeError("router down")

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_scene_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.router_helper.get_router", lambda: FailingRouter())
    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: True)
    monkeypatch.setattr("server.adapters.mcp.areas.scene.ctx_info", lambda ctx, message: None)

    server = _build_phase_search_server(SessionPhase.BUILD)

    async def run():
        direct = await server.call_tool("scene_list_objects", {})
        discovered = await server.call_tool(
            "call_tool",
            {"name": "scene_list_objects", "arguments": {}},
        )
        return direct, discovered

    direct, discovered = asyncio.run(run())

    direct_text = "".join(getattr(block, "text", "") for block in direct.content)
    discovered_text = "".join(getattr(block, "text", "") for block in discovered.content)

    assert "Router processing failed" in direct_text
    assert discovered_text == direct_text
