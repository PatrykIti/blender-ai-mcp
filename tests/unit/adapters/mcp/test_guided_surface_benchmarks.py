"""Benchmark-style regression tests for the hardened llm-guided public surface."""

from __future__ import annotations

import asyncio
import json

from fastmcp import FastMCP
from fastmcp.server.transforms.visibility import create_visibility_transforms
from server.adapters.mcp.factory import build_server, build_surface_providers
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


def _build_handoff_visible_server(phase: SessionPhase, guided_handoff: dict[str, object]) -> FastMCP:
    surface = get_surface_profile("llm-guided")
    base_pipeline = build_surface_transform_pipeline(surface)
    transforms = []

    for stage in base_pipeline:
        if stage.name == "visibility":
            transforms.extend(
                create_visibility_transforms(build_visibility_rules(surface.name, phase, guided_handoff=guided_handoff))
            )
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


def _surface_tool_names(surface_profile: str) -> set[str]:
    server = build_server(surface_profile)

    async def run():
        tools = await server.list_tools()
        return {tool.name for tool in tools}

    return asyncio.run(run())


def test_guided_surface_phase_baselines_stay_intentional():
    """The hardened guided surface should keep distinct, bounded phase footprints."""

    bootstrap_names, _ = _tool_names_and_payload_size(SessionPhase.BOOTSTRAP)
    build_names, _ = _tool_names_and_payload_size(SessionPhase.BUILD)
    inspect_names, _ = _tool_names_and_payload_size(SessionPhase.INSPECT_VALIDATE)

    assert len(bootstrap_names) == 6
    assert len(build_names) == 119
    assert len(inspect_names) == 44

    assert bootstrap_names == {
        "browse_workflows",
        "reference_images",
        "router_get_status",
        "router_set_goal",
        "scene_clean_scene",
        "scene_get_viewport",
    }

    assert "macro_relative_layout" in build_names
    assert "macro_attach_part_to_surface" in build_names
    assert "macro_align_part_with_contact" in build_names
    assert "macro_place_symmetry_pair" in build_names
    assert "macro_place_supported_pair" in build_names
    assert "macro_cleanup_part_intersections" in build_names
    assert "macro_adjust_relative_proportion" in build_names
    assert "macro_adjust_segment_chain_arc" in build_names
    assert "macro_finish_form" in build_names
    assert "macro_cutout_recess" in build_names
    assert "modeling_create_primitive" in build_names
    assert "scene_clean_scene" not in build_names
    assert "modeling_add_modifier" not in build_names
    assert "modeling_apply_modifier" not in build_names
    assert "modeling_list_modifiers" not in build_names
    assert "mesh_extrude_region" in build_names
    assert "armature_create" not in build_names
    assert "sculpt_auto" not in build_names

    assert "extraction_render_angles" in inspect_names
    assert "scene_scope_graph" in inspect_names
    assert "scene_relation_graph" in inspect_names
    assert "macro_relative_layout" not in inspect_names
    assert "macro_attach_part_to_surface" not in inspect_names
    assert "macro_align_part_with_contact" not in inspect_names
    assert "macro_place_symmetry_pair" not in inspect_names
    assert "macro_place_supported_pair" not in inspect_names
    assert "macro_cleanup_part_intersections" not in inspect_names
    assert "macro_adjust_relative_proportion" not in inspect_names
    assert "macro_adjust_segment_chain_arc" not in inspect_names
    assert "macro_finish_form" not in inspect_names
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


def test_macro_wave_benchmark_reduces_finishing_decision_points_vs_legacy_flat():
    """The guided macro layer should reduce the visible finishing-tool decision surface."""

    build_names, _ = _tool_names_and_payload_size(SessionPhase.BUILD)
    legacy_names = _surface_tool_names("legacy-flat")

    legacy_finishing_choices = {
        "macro_finish_form",
        "modeling_add_modifier",
        "modeling_apply_modifier",
        "modeling_list_modifiers",
        "mesh_bevel",
        "mesh_subdivide",
        "mesh_smooth",
    } & legacy_names
    guided_finishing_choices = {
        "macro_finish_form",
        "mesh_bevel",
        "mesh_subdivide",
        "mesh_smooth",
    } & build_names

    assert "macro_finish_form" in guided_finishing_choices
    assert {"modeling_add_modifier", "modeling_apply_modifier", "modeling_list_modifiers"}.isdisjoint(build_names)
    assert len(guided_finishing_choices) < len(legacy_finishing_choices)


def test_creature_handoff_surface_is_smaller_than_generic_build_surface():
    """Creature handoff should expose a materially smaller blockout-focused build surface."""

    generic_build_names, _ = _tool_names_and_payload_size(SessionPhase.BUILD)
    creature_server = _build_handoff_visible_server(
        SessionPhase.BUILD,
        {
            "kind": "guided_manual_build",
            "recipe_id": "low_poly_creature_blockout",
            "direct_tools": [
                "modeling_create_primitive",
                "modeling_transform_object",
                "mesh_select",
                "mesh_select_targeted",
                "mesh_extrude_region",
                "mesh_loop_cut",
                "mesh_bevel",
                "mesh_symmetrize",
                "mesh_merge_by_distance",
                "mesh_dissolve",
                "macro_adjust_relative_proportion",
                "macro_adjust_segment_chain_arc",
                "inspect_scene",
            ],
            "supporting_tools": [
                "reference_images",
                "reference_compare_stage_checkpoint",
                "reference_iterate_stage_checkpoint",
                "router_get_status",
            ],
        },
    )

    async def run():
        tools = await creature_server.list_tools()
        return {tool.name for tool in tools}

    creature_names = asyncio.run(run())

    assert len(creature_names) < len(generic_build_names)
    assert "mesh_randomize" not in creature_names
    assert "mesh_create_vertex_group" not in creature_names
    assert "macro_finish_form" not in creature_names
    assert "modeling_create_primitive" in creature_names
    assert "mesh_extrude_region" in creature_names
