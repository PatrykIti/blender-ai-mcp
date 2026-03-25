"""Benchmark-style regression tests for the hardened llm-guided public surface."""

from __future__ import annotations

import asyncio
import json

from fastmcp import FastMCP
from fastmcp.server.transforms.visibility import create_visibility_transforms

from server.adapters.mcp.factory import build_server
from server.adapters.mcp.factory import build_surface_providers
from server.adapters.mcp.session_phase import SessionPhase
from server.adapters.mcp.surfaces import get_surface_profile
from server.adapters.mcp.transforms import build_surface_transform_pipeline
from server.adapters.mcp.transforms.visibility_policy import build_visibility_rules


def _build_phase_visible_server(phase: SessionPhase) -> FastMCP:
    surface = get_surface_profile("llm-guided")
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

    return FastMCP(
        surface.server_name,
        providers=build_surface_providers(surface),
        transforms=transforms,
        list_page_size=surface.list_page_size,
        tasks=surface.tasks_enabled,
        instructions=surface.instructions,
    )


def _tool_names_and_payload_size(phase: SessionPhase) -> tuple[set[str], int]:
    server = _build_phase_visible_server(phase)

    async def run():
        tools = await server.list_tools()
        payload = [tool.to_mcp_tool().model_dump(mode="json", exclude_none=True) for tool in tools]
        return {tool.name for tool in tools}, len(json.dumps(payload))

    return asyncio.run(run())


def _legacy_payload_size() -> int:
    server = build_server("legacy-flat")

    async def run():
        tools = await server.list_tools()
        payload = [tool.to_mcp_tool().model_dump(mode="json", exclude_none=True) for tool in tools]
        return len(json.dumps(payload))

    return asyncio.run(run())


def test_guided_surface_phase_baselines_stay_intentional():
    """The hardened guided surface should keep distinct, bounded phase footprints."""

    bootstrap_names, _ = _tool_names_and_payload_size(SessionPhase.BOOTSTRAP)
    build_names, _ = _tool_names_and_payload_size(SessionPhase.BUILD)
    inspect_names, _ = _tool_names_and_payload_size(SessionPhase.INSPECT_VALIDATE)

    assert len(bootstrap_names) == 3
    assert len(build_names) == 108
    assert len(inspect_names) == 37

    assert bootstrap_names == {"browse_workflows", "router_get_status", "router_set_goal"}

    assert "modeling_create_primitive" in build_names
    assert "mesh_extrude_region" in build_names
    assert "armature_create" not in build_names
    assert "sculpt_auto" not in build_names

    assert "extraction_render_angles" in inspect_names
    assert "modeling_create_primitive" not in inspect_names
    assert "router_clear_goal" not in inspect_names


def test_guided_surface_phase_payload_sizes_reflect_curated_growth():
    """Payload size should grow by phase, but remain materially below the broad catalog."""

    bootstrap_names, bootstrap_bytes = _tool_names_and_payload_size(SessionPhase.BOOTSTRAP)
    build_names, build_bytes = _tool_names_and_payload_size(SessionPhase.BUILD)
    inspect_names, inspect_bytes = _tool_names_and_payload_size(SessionPhase.INSPECT_VALIDATE)

    assert len(bootstrap_names) < len(inspect_names) < len(build_names)
    assert bootstrap_bytes < inspect_bytes < build_bytes
    legacy_bytes = _legacy_payload_size()

    assert inspect_bytes < legacy_bytes
    assert build_bytes < legacy_bytes
