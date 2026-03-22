"""Tests for TASK-091 version-filtered surface composition."""

from __future__ import annotations

import asyncio

import pytest
from fastmcp import FastMCP
from server.adapters.mcp.factory import build_server, build_surface_providers
from server.adapters.mcp.surfaces import resolve_surface_contract_profile
from server.adapters.mcp.transforms import build_surface_transform_pipeline
from server.adapters.mcp.transforms.prompts_bridge import build_prompts_bridge_transform


def _tool_names(server) -> set[str]:
    async def run():
        return {tool.name for tool in await server.list_tools()}

    return asyncio.run(run())


def get_tool_version(server, tool_name: str) -> str | None:
    async def run():
        tool = await server.get_tool(tool_name)
        return None if tool is None else tool.version

    return asyncio.run(run())


def _build_preview_server(surface_profile: str, contract_line: str) -> FastMCP:
    surface = resolve_surface_contract_profile(surface_profile, contract_line=contract_line)
    providers = build_surface_providers(surface)
    transforms = [
        stage.transform
        for stage in build_surface_transform_pipeline(surface)
        if stage.transform is not None and stage.name != "visibility"
    ]
    server = FastMCP(
        surface.server_name,
        providers=providers,
        transforms=transforms,
        list_page_size=surface.list_page_size,
        tasks=surface.tasks_enabled,
        instructions=surface.instructions,
    )
    prompts_bridge = build_prompts_bridge_transform(surface, provider=server)
    if prompts_bridge is not None:
        server.add_transform(prompts_bridge)
    return server


def _build_no_discovery_server(surface_profile: str, contract_line: str) -> FastMCP:
    surface = resolve_surface_contract_profile(surface_profile, contract_line=contract_line)
    providers = build_surface_providers(surface)
    transforms = [
        stage.transform
        for stage in build_surface_transform_pipeline(surface)
        if stage.transform is not None and stage.name not in {"visibility", "discovery"}
    ]
    server = FastMCP(
        surface.server_name,
        providers=providers,
        transforms=transforms,
        list_page_size=surface.list_page_size,
        tasks=surface.tasks_enabled,
        instructions=surface.instructions,
    )
    prompts_bridge = build_prompts_bridge_transform(surface, provider=server)
    if prompts_bridge is not None:
        server.add_transform(prompts_bridge)
    return server


def test_llm_guided_defaults_to_v2_contract_line():
    server = build_server("llm-guided")

    names = _tool_names(server)

    assert server._bam_contract_line == "llm-guided-v2"
    assert "browse_workflows" in names
    assert "router_set_goal" in names
    assert "router_get_status" in names
    assert "check_scene" not in names
    assert "inspect_scene" not in names
    assert "workflow_catalog" not in names


def test_llm_guided_can_boot_older_contract_line_for_safe_coexistence():
    server = _build_no_discovery_server("llm-guided", contract_line="llm-guided-v1")

    names = _tool_names(server)

    assert "scene_context" in names
    assert "scene_inspect" in names
    assert "workflow_catalog" in names
    assert "check_scene" not in names
    assert "inspect_scene" not in names
    assert "browse_workflows" not in names


def test_version_filter_selects_expected_component_versions_without_hiding_unversioned_tools():
    guided_v1 = _build_no_discovery_server("llm-guided", contract_line="llm-guided-v1")
    guided_v2 = _build_no_discovery_server("llm-guided", contract_line="llm-guided-v2")

    assert get_tool_version(guided_v1, "scene_context") == "1"
    assert get_tool_version(guided_v2, "check_scene") == "2"
    assert get_tool_version(guided_v1, "scene_list_objects") is None
    assert get_tool_version(guided_v2, "scene_list_objects") is None


def test_invalid_contract_line_override_fails_loudly():
    with pytest.raises(ValueError, match="not allowed"):
        build_server("legacy-flat", contract_line="llm-guided-v2")
