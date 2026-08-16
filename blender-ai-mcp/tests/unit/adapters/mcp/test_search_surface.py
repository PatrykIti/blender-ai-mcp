"""Tests for TASK-084 search infrastructure on the shaped public surface."""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import replace
from typing import Any, cast

import pytest
from fastmcp import FastMCP
from fastmcp.exceptions import NotFoundError, ToolError
from fastmcp.server.transforms.visibility import create_visibility_transforms
from server.adapters.mcp.factory import build_server, build_surface_providers
from server.adapters.mcp.guided_contract import canonicalize_guided_tool_arguments
from server.adapters.mcp.session_capabilities import SessionCapabilityState
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


def _build_handoff_search_server(phase: SessionPhase, guided_handoff: dict[str, object]) -> FastMCP:
    surface = replace(get_surface_profile("llm-guided"), search_enabled=True)
    base_pipeline = build_surface_transform_pipeline(surface)
    transforms = []
    for stage in base_pipeline:
        if stage.name == "visibility":
            transforms.extend(
                create_visibility_transforms(build_visibility_rules(surface.name, phase, guided_handoff=guided_handoff))
            )
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


def _build_flow_search_server(
    phase: SessionPhase,
    guided_flow_state: dict[str, object],
    *,
    guided_handoff: dict[str, object] | None = None,
    gate_plan: dict[str, object] | None = None,
) -> FastMCP:
    surface = replace(get_surface_profile("llm-guided"), search_enabled=True)
    base_pipeline = build_surface_transform_pipeline(surface)
    transforms = []
    for stage in base_pipeline:
        if stage.name == "visibility":
            transforms.extend(
                create_visibility_transforms(
                    build_visibility_rules(
                        surface.name,
                        phase,
                        guided_handoff=guided_handoff,
                        guided_flow_state=guided_flow_state,
                        gate_plan=gate_plan,
                    )
                )
            )
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


def _build_flow_visible_server(
    phase: SessionPhase,
    guided_flow_state: dict[str, object],
    *,
    guided_handoff: dict[str, object] | None = None,
    gate_plan: dict[str, object] | None = None,
) -> FastMCP:
    surface = replace(get_surface_profile("llm-guided"), search_enabled=False)
    base_pipeline = build_surface_transform_pipeline(surface)
    transforms = []
    for stage in base_pipeline:
        if stage.name == "visibility":
            transforms.extend(
                create_visibility_transforms(
                    build_visibility_rules(
                        surface.name,
                        phase,
                        guided_handoff=guided_handoff,
                        guided_flow_state=guided_flow_state,
                        gate_plan=gate_plan,
                    )
                )
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


def test_default_llm_guided_surface_lists_pinned_search_and_spatial_support_tools():
    """Default llm-guided surface should expose pinned direct tools plus search proxies."""

    server = build_server("llm-guided")

    async def run():
        tools = await server.list_tools()
        return {tool.name for tool in tools}

    tool_names = asyncio.run(run())

    assert tool_names == {
        "reference_images",
        "router_set_goal",
        "router_get_status",
        "browse_workflows",
        "scene_scope_graph",
        "scene_relation_graph",
        "scene_view_diagnostics",
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


def test_bootstrap_search_surfaces_guided_utility_tools():
    """Bootstrap-phase discovery should surface the guided utility capture/prep path."""

    server = build_server("llm-guided")

    async def run():
        viewport = await server.call_tool("search_tools", {"query": "capture viewport screenshot save file"})
        cleanup = await server.call_tool("search_tools", {"query": "clean reset fresh scene"})
        return _decode_tool_result(viewport), _decode_tool_result(cleanup)

    viewport_payload, cleanup_payload = asyncio.run(run())
    viewport_names = {tool["name"] for tool in viewport_payload}
    cleanup_names = {tool["name"] for tool in cleanup_payload}

    assert "scene_get_viewport" in viewport_names
    assert "scene_clean_scene" in cleanup_names


def test_build_phase_search_uses_public_alias_names_for_discovered_tools():
    """Build-phase discovery should expose public aliases on the shaped surface."""

    server = _build_phase_search_server(SessionPhase.BUILD)

    async def run():
        return await server.call_tool("search_tools", {"query": "inspect topology object materials"})

    payload = _decode_tool_result(asyncio.run(run()))

    assert any(tool["name"] == "inspect_scene" for tool in payload)
    assert all(tool["name"] != "scene_inspect" for tool in payload)


def test_build_phase_search_can_surface_scene_cleanup_as_recovery_hatch():
    server = _build_phase_search_server(SessionPhase.BUILD)

    async def run():
        return await server.call_tool("search_tools", {"query": "clean reset stale default cube scene"})

    payload = _decode_tool_result(asyncio.run(run()))
    names = {tool["name"] for tool in payload}

    assert "scene_clean_scene" in names


def test_phase_search_results_follow_visibility_profile_changes():
    """Search results should swap build-only and inspect-only capabilities by session phase."""

    build_server = _build_phase_search_server(SessionPhase.BUILD)
    inspect_server = _build_phase_search_server(SessionPhase.INSPECT_VALIDATE)

    async def run():
        build_result = await build_server.call_tool("search_tools", {"query": "create cube primitive light camera"})
        inspect_result = await inspect_server.call_tool(
            "search_tools",
            {"query": "render angles capture inspection before after"},
        )
        return _decode_tool_result(build_result), _decode_tool_result(inspect_result)

    build_payload, inspect_payload = asyncio.run(run())
    build_names = {tool["name"] for tool in build_payload}
    inspect_names = {tool["name"] for tool in inspect_payload}

    assert "modeling_create_primitive" in build_names
    assert "armature_create" not in build_names
    assert "extraction_render_angles" not in build_names
    assert "extraction_render_angles" in inspect_names
    assert "modeling_create_primitive" not in inspect_names


def test_inspect_phase_list_tools_keeps_default_spatial_graph_support_visible():
    server = _build_phase_visible_server(SessionPhase.INSPECT_VALIDATE)

    async def run():
        tools = await server.list_tools()
        return {tool.name for tool in tools}

    names = asyncio.run(run())

    assert "scene_scope_graph" in names
    assert "scene_relation_graph" in names


def test_bootstrap_and_build_phase_both_surface_default_spatial_support_tools():
    build_phase_server = _build_phase_search_server(SessionPhase.BUILD)
    bootstrap_server = build_server("llm-guided")

    async def run():
        build_result = await build_phase_server.call_tool(
            "search_tools",
            {"query": "occluded off screen framing visibility diagnostics"},
        )
        bootstrap_tools = await bootstrap_server.list_tools()
        return _decode_tool_result(build_result), {tool.name for tool in bootstrap_tools}

    _build_payload, bootstrap_names = asyncio.run(run())
    assert "scene_scope_graph" in bootstrap_names
    assert "scene_relation_graph" in bootstrap_names
    assert "scene_view_diagnostics" in bootstrap_names


def test_async_scene_spatial_tools_preserve_public_descriptions():
    """Async registered scene helpers should expose the public product docstrings."""

    server = _build_phase_visible_server(SessionPhase.BUILD)

    async def run():
        return {tool.name: tool.description or "" for tool in await server.list_tools()}

    descriptions = asyncio.run(run())

    assert "compact structural scope graph" in descriptions["scene_scope_graph"]
    assert "which object is the structural anchor" in descriptions["scene_scope_graph"]
    assert "compact spatial relation graph" in descriptions["scene_relation_graph"]
    assert "truth primitives such as gap/alignment/overlap/contact checks" in descriptions["scene_relation_graph"]
    assert "compact view-space diagnostics" in descriptions["scene_view_diagnostics"]
    assert "USER_PERSPECTIVE" in descriptions["scene_view_diagnostics"]


def test_async_modeling_tools_preserve_public_descriptions():
    """Async registered modeling helpers should expose the public product docstrings."""

    server = _build_phase_visible_server(SessionPhase.BUILD)

    async def run():
        return {tool.name: tool.description or "" for tool in await server.list_tools()}

    descriptions = asyncio.run(run())

    assert "Creates a 3D primitive object" in descriptions["modeling_create_primitive"]
    assert "Workflow: START" in descriptions["modeling_create_primitive"]
    assert "modeling_transform_object(scale=...)" in descriptions["modeling_create_primitive"]
    assert "Transforms (move, rotate, scale)" in descriptions["modeling_transform_object"]
    assert "Workflow: AFTER" in descriptions["modeling_transform_object"]


def test_phase_shaped_list_tools_follow_visibility_without_discovery():
    """Visibility policy should affect the actual listed tools even without discovery collapse."""

    build_server = _build_phase_visible_server(SessionPhase.BUILD)
    inspect_server = _build_phase_visible_server(SessionPhase.INSPECT_VALIDATE)

    async def run():
        build_names = {tool.name for tool in await build_server.list_tools()}
        inspect_names = {tool.name for tool in await inspect_server.list_tools()}
        return build_names, inspect_names

    build_names, inspect_names = asyncio.run(run())

    assert "macro_cutout_recess" in build_names
    assert "macro_finish_form" in build_names
    assert "macro_relative_layout" in build_names
    assert "modeling_create_primitive" in build_names
    assert "scene_scope_graph" in build_names
    assert "scene_relation_graph" in build_names
    assert "scene_view_diagnostics" in build_names
    assert "modeling_add_modifier" not in build_names
    assert "modeling_apply_modifier" not in build_names
    assert "modeling_list_modifiers" not in build_names
    assert "armature_create" not in build_names
    assert "sculpt_auto" not in build_names
    assert "extraction_render_angles" not in build_names
    assert "extraction_render_angles" in inspect_names
    assert "scene_scope_graph" in inspect_names
    assert "scene_relation_graph" in inspect_names
    assert "scene_view_diagnostics" in inspect_names
    assert "modeling_create_primitive" not in inspect_names
    assert "armature_create" not in inspect_names
    assert "router_clear_goal" not in build_names
    assert "router_feedback" not in build_names
    assert "router_find_similar_workflows" not in build_names
    assert "router_get_inherited_proportions" not in build_names
    assert "router_clear_goal" not in inspect_names
    assert "inspect_scene" in build_names
    assert "inspect_scene" in inspect_names


def test_build_phase_search_prefers_macro_finish_tool_over_hidden_modifier_atomics():
    """Build-phase discovery should surface the finishing macro while hidden modifier atomics stay undiscoverable."""

    server = _build_phase_search_server(SessionPhase.BUILD)

    async def run():
        return await server.call_tool("search_tools", {"query": "finish housing bevel subdivision shell"})

    payload = _decode_tool_result(asyncio.run(run()))
    names = {tool["name"] for tool in payload}

    assert "macro_finish_form" in names
    assert "modeling_add_modifier" not in names
    assert "modeling_apply_modifier" not in names


def test_spatial_context_flow_search_hides_finish_family_until_checks_complete():
    """Flow-step gating should keep later build families out of search until required checks finish."""

    server = _build_flow_search_server(
        SessionPhase.BUILD,
        {
            "flow_id": "guided_building_flow",
            "domain_profile": "building",
            "current_step": "establish_spatial_context",
        },
    )

    async def run():
        finish = await server.call_tool("search_tools", {"query": "finish housing bevel subdivision shell"})
        return _decode_tool_result(finish)

    finish_payload = asyncio.run(run())
    finish_names = {tool["name"] for tool in finish_payload}

    assert "macro_finish_form" not in finish_names


def test_build_phase_search_can_discover_reference_compare_checkpoint():
    """Build-phase discovery should surface the bounded checkpoint-vs-reference compare path."""

    server = _build_phase_search_server(SessionPhase.BUILD)

    async def run():
        result = await server.call_tool("search_tools", {"query": "compare checkpoint against reference progress"})
        return _decode_tool_result(result)

    payload = asyncio.run(run())
    names = {tool["name"] for tool in payload}

    assert "reference_compare_checkpoint" in names
    assert "modeling_list_modifiers" not in names


def test_build_phase_search_can_discover_reference_compare_stage_checkpoint():
    """Build-phase discovery should surface the deterministic stage checkpoint compare path."""

    server = _build_phase_search_server(SessionPhase.BUILD)

    async def run():
        result = await server.call_tool(
            "search_tools", {"query": "compare current stage progress against reference set"}
        )
        return _decode_tool_result(result)

    payload = asyncio.run(run())
    names = {tool["name"] for tool in payload}

    assert "reference_compare_stage_checkpoint" in names
    assert "modeling_list_modifiers" not in names


def test_build_phase_search_can_discover_reference_iterate_stage_checkpoint():
    """Build-phase discovery should surface the session-aware iterative stage loop tool."""

    server = _build_phase_search_server(SessionPhase.BUILD)

    async def run():
        result = await server.call_tool(
            "search_tools", {"query": "iterate stage checkpoint continue building or validate"}
        )
        return _decode_tool_result(result)

    payload = asyncio.run(run())
    names = {tool["name"] for tool in payload}

    assert "reference_iterate_stage_checkpoint" in names
    assert "modeling_list_modifiers" not in names


def test_build_phase_search_prefers_creature_blockout_tools_for_creature_queries():
    """Generic build search should bias creature blockout queries toward real blockout tools."""

    server = _build_phase_search_server(SessionPhase.BUILD)

    async def run():
        result = await server.call_tool(
            "search_tools",
            {"query": "low poly creature ears snout tail arc paw placement organic blockout"},
        )
        return _decode_tool_result(result)

    payload = asyncio.run(run())
    names = [tool["name"] for tool in payload]

    assert any(
        name in names[:3]
        for name in {
            "modeling_create_primitive",
            "mesh_extrude_region",
            "mesh_loop_cut",
            "macro_adjust_relative_proportion",
            "macro_adjust_segment_chain_arc",
        }
    )
    assert "mesh_randomize" not in names[:3]
    assert "mesh_create_vertex_group" not in names[:3]
    assert "mesh_assign_to_group" not in names[:3]
    assert "mesh_remove_from_group" not in names[:3]


def test_creature_handoff_search_hides_noise_tools_and_keeps_blockout_surface_small():
    """Creature handoff search should stay within the bounded blockout recipe instead of broad build noise."""

    server = _build_handoff_search_server(
        SessionPhase.BUILD,
        guided_handoff={
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
                "macro_align_part_with_contact",
                "macro_cleanup_part_intersections",
                "inspect_scene",
                "scene_measure_dimensions",
                "scene_assert_proportion",
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
        result = await server.call_tool(
            "search_tools",
            {"query": "low poly creature ears snout tail arc paw placement organic blockout"},
        )
        return _decode_tool_result(result)

    payload = asyncio.run(run())
    names = {tool["name"] for tool in payload}

    assert "modeling_create_primitive" in names or "mesh_extrude_region" in names
    assert "macro_adjust_segment_chain_arc" in names
    assert "mesh_randomize" not in names
    assert "mesh_create_vertex_group" not in names
    assert "mesh_assign_to_group" not in names
    assert "mesh_remove_from_group" not in names


def test_spatial_context_flow_list_tools_stays_bounded_to_required_checks():
    """The directly visible tool list should match the same step-gated flow surface as discovery."""

    server = _build_flow_visible_server(
        SessionPhase.BUILD,
        {
            "flow_id": "guided_creature_flow",
            "domain_profile": "creature",
            "current_step": "establish_spatial_context",
        },
        guided_handoff={
            "kind": "guided_manual_build",
            "recipe_id": "low_poly_creature_blockout",
            "direct_tools": ["modeling_create_primitive", "mesh_extrude_region", "macro_finish_form"],
            "supporting_tools": ["reference_images", "reference_iterate_stage_checkpoint", "router_get_status"],
        },
    )

    async def run():
        return {tool.name for tool in await server.list_tools()}

    names = asyncio.run(run())

    assert "scene_scope_graph" in names
    assert "scene_relation_graph" in names
    assert "scene_view_diagnostics" in names
    assert "collection_manage" in names
    assert "modeling_create_primitive" not in names
    assert "macro_finish_form" not in names


def test_spatial_refresh_required_search_stays_bounded_to_spatial_context_tools():
    """Discovery should not reopen broad build families while spatial refresh is explicitly pending."""

    server = _build_flow_search_server(
        SessionPhase.BUILD,
        {
            "flow_id": "guided_creature_flow",
            "domain_profile": "creature",
            "current_step": "place_secondary_parts",
            "spatial_refresh_required": True,
        },
        guided_handoff={
            "kind": "guided_manual_build",
            "recipe_id": "low_poly_creature_blockout",
            "direct_tools": ["modeling_create_primitive", "mesh_extrude_region", "macro_finish_form"],
            "supporting_tools": ["reference_images", "reference_iterate_stage_checkpoint", "router_get_status"],
        },
    )

    async def run():
        result = await server.call_tool(
            "search_tools",
            {"query": "scene scope graph relation graph view diagnostics refresh spatial context"},
        )
        return _decode_tool_result(result)

    payload = asyncio.run(run())
    names = {tool["name"] for tool in payload}

    assert "modeling_create_primitive" not in names
    assert "macro_finish_form" not in names
    assert "guided_register_part" not in names


def test_failed_attachment_gate_search_surfaces_bounded_repair_tools():
    """Search should resolve active seam blockers through existing guided visibility."""

    server = _build_flow_search_server(
        SessionPhase.BUILD,
        {
            "flow_id": "guided_creature_flow",
            "domain_profile": "creature",
            "current_step": "place_secondary_parts",
        },
        guided_handoff={
            "kind": "guided_manual_build",
            "recipe_id": "low_poly_creature_blockout",
            "direct_tools": ["modeling_create_primitive"],
            "supporting_tools": ["reference_iterate_stage_checkpoint", "router_get_status"],
        },
        gate_plan={
            "plan_id": "creature_quality_gate_plan",
            "domain_profile": "creature",
            "completion_blockers": [
                {
                    "gate_id": "tail_body_seam",
                    "gate_type": "attachment_seam",
                    "label": "tail seated on body",
                    "status": "failed",
                    "reason_code": "relation_floating_gap",
                    "recommended_bounded_tools": [
                        "scene_relation_graph",
                        "scene_measure_gap",
                        "scene_assert_contact",
                        "macro_attach_part_to_surface",
                    ],
                    "message": "Tail seam is floating.",
                }
            ],
            "gates": [],
        },
    )

    async def run():
        result = await server.call_tool(
            "search_tools",
            {"query": "fix floating tail body gap attach contact seam"},
        )
        return _decode_tool_result(result)

    payload = asyncio.run(run())
    names = {tool["name"] for tool in payload}

    assert {"scene_measure_gap", "scene_assert_contact"}.intersection(names)
    assert "macro_attach_part_to_surface" in names or "macro_align_part_with_contact" in names
    assert "macro_finish_form" not in names


def test_active_gate_recovery_search_does_not_recommend_goal_reset(monkeypatch):
    """Reset-style recovery queries should prefer active gate repair tools."""

    gate_plan = {
        "plan_id": "creature_quality_gate_plan",
        "domain_profile": "creature",
        "completion_blockers": [
            {
                "gate_id": "tail_body_seam",
                "gate_type": "attachment_seam",
                "label": "tail seated on body",
                "status": "failed",
                "reason_code": "relation_floating_gap",
                "recommended_bounded_tools": [
                    "scene_relation_graph",
                    "scene_measure_gap",
                    "scene_assert_contact",
                    "macro_attach_part_to_surface",
                ],
                "message": "Tail seam is floating.",
            }
        ],
        "gates": [],
    }

    async def get_session_capability_state_async(ctx):
        return SessionCapabilityState(
            phase=SessionPhase.BUILD,
            surface_profile="llm-guided",
            guided_flow_state={
                "flow_id": "guided_creature_flow",
                "domain_profile": "creature",
                "current_step": "place_secondary_parts",
            },
            gate_plan=gate_plan,
        )

    monkeypatch.setattr(
        "server.adapters.mcp.discovery.search_surface.get_session_capability_state_async",
        get_session_capability_state_async,
    )
    server = _build_flow_search_server(
        SessionPhase.BUILD,
        {
            "flow_id": "guided_creature_flow",
            "domain_profile": "creature",
            "current_step": "place_secondary_parts",
        },
        gate_plan=gate_plan,
    )

    async def run():
        result = await server.call_tool("search_tools", {"query": "stuck reset goal because tail seam failed"})
        return _decode_tool_result(result)

    payload = asyncio.run(run())
    names = {tool["name"] for tool in payload}

    assert "router_set_goal" not in names
    assert {"scene_relation_graph", "scene_measure_gap", "scene_assert_contact"}.intersection(names)
    assert "macro_attach_part_to_surface" in names


@pytest.mark.parametrize(
    ("query", "expected_tool"),
    [
        ("ustaw nogę pod blatem z kontaktem na osi Z", "macro_relative_layout"),
        ("wyrównaj panel do obudowy i zostaw małą szczelinę", "macro_relative_layout"),
        ("zaokrąglij obudowę i dodaj lekki bevel oraz subdivision", "macro_finish_form"),
        ("pogrub tę skorupę jednym makrem wykończenia", "macro_finish_form"),
    ],
)
def test_build_phase_search_prefers_macro_tools_for_polish_macro_queries(query: str, expected_tool: str):
    """Polish macro-intent queries should surface the bounded macro layer before atomics."""

    server = _build_phase_search_server(SessionPhase.BUILD)

    async def run():
        return await server.call_tool("search_tools", {"query": query})

    payload = _decode_tool_result(asyncio.run(run()))

    assert payload
    assert payload[0]["name"] == expected_tool


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


def test_call_tool_accepts_legacy_tool_and_params_aliases(monkeypatch):
    """Legacy wrapper aliases should still resolve to the canonical call_tool path."""

    class Handler:
        def list_workflows(self, offset: int = 0, limit: int = 100):
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
        result = await server.call_tool(
            "call_tool",
            {"tool": "browse_workflows", "params": {"action": "list"}},
        )
        return _decode_tool_result(result)

    payload = asyncio.run(run())

    assert payload["count"] == 1
    assert payload["workflows"][0]["name"] == "chair"


def test_call_tool_proxy_preserves_proxied_valueerror_as_tool_error(monkeypatch):
    """call_tool should keep direct-tool failure semantics instead of turning validation errors into success text."""

    class FailingFastMCP:
        async def call_tool(self, name, arguments):
            raise ValueError("synthetic validation failure")

    class Ctx:
        fastmcp = FailingFastMCP()

    transform = build_discovery_transform(get_surface_profile("llm-guided"))
    assert transform is not None
    call_tool = transform._make_call_tool().fn  # type: ignore[attr-defined]

    async def run():
        await call_tool(name="scene_clean_scene", arguments={"keep_lights_and_cameras": True}, ctx=Ctx())

    with pytest.raises(ValueError, match="synthetic validation failure"):
        asyncio.run(run())


def test_search_tool_refreshes_visibility_from_session_state_before_query(monkeypatch):
    """search_tools should auto-sync visibility after guided-flow state mutations."""

    transform = build_discovery_transform(get_surface_profile("llm-guided"))
    assert transform is not None
    events: list[str] = []

    async def fake_get_session_capability_state_async(_ctx):
        events.append("get_session")
        return object()

    async def fake_apply_visibility_for_session_state(_ctx, _state):
        events.append("apply_visibility")

    async def fake_get_visible_tools(_ctx):
        events.append("get_visible_tools")
        return []

    async def fake_search(_tools, _query):
        events.append("search")
        return []

    async def fake_render_results(_results):
        events.append("render")
        return []

    monkeypatch.setattr(
        "server.adapters.mcp.discovery.search_surface.get_session_capability_state_async",
        fake_get_session_capability_state_async,
    )
    monkeypatch.setattr(
        "server.adapters.mcp.discovery.search_surface.apply_visibility_for_session_state",
        fake_apply_visibility_for_session_state,
    )
    monkeypatch.setattr(transform, "_get_visible_tools", fake_get_visible_tools)
    monkeypatch.setattr(transform, "_search", fake_search)
    monkeypatch.setattr(transform, "_render_results", fake_render_results)

    search_tool = transform._make_search_tool().fn  # type: ignore[attr-defined]

    asyncio.run(search_tool(query="squirrel blockout", ctx=object()))

    assert events == ["get_session", "apply_visibility", "get_visible_tools", "search", "render"]


def test_call_tool_refreshes_visibility_from_session_state_before_proxying(monkeypatch):
    """call_tool should auto-sync visibility before proxying newly unlocked guided tools."""

    class FakeFastMCP:
        async def call_tool(self, name, arguments):
            events.append(f"proxy:{name}")
            return {"result": "ok"}

    class Ctx:
        fastmcp = FakeFastMCP()

    transform = build_discovery_transform(get_surface_profile("llm-guided"))
    assert transform is not None
    events: list[str] = []

    async def fake_get_session_capability_state_async(_ctx):
        events.append("get_session")
        return object()

    async def fake_apply_visibility_for_session_state(_ctx, _state):
        events.append("apply_visibility")

    monkeypatch.setattr(
        "server.adapters.mcp.discovery.search_surface.get_session_capability_state_async",
        fake_get_session_capability_state_async,
    )
    monkeypatch.setattr(
        "server.adapters.mcp.discovery.search_surface.apply_visibility_for_session_state",
        fake_apply_visibility_for_session_state,
    )

    call_tool = transform._make_call_tool().fn  # type: ignore[attr-defined]

    asyncio.run(call_tool(name="modeling_create_primitive", arguments={"primitive_type": "CUBE"}, ctx=Ctx()))

    assert events == ["get_session", "apply_visibility", "proxy:modeling_create_primitive"]


def test_call_tool_logs_proxied_tool_name_and_canonical_argument_keys(monkeypatch, caplog):
    """Docker/server logs should show which real tool the synthetic call_tool proxy invoked."""

    class FakeFastMCP:
        async def call_tool(self, name, arguments):
            return {"result": "ok"}

    class Ctx:
        fastmcp = FakeFastMCP()

    transform = build_discovery_transform(get_surface_profile("llm-guided"))
    assert transform is not None

    async def fake_get_session_capability_state_async(_ctx):
        return object()

    async def fake_apply_visibility_for_session_state(_ctx, _state):
        return None

    monkeypatch.setattr(
        "server.adapters.mcp.discovery.search_surface.get_session_capability_state_async",
        fake_get_session_capability_state_async,
    )
    monkeypatch.setattr(
        "server.adapters.mcp.discovery.search_surface.apply_visibility_for_session_state",
        fake_apply_visibility_for_session_state,
    )

    call_tool = transform._make_call_tool().fn  # type: ignore[attr-defined]

    with caplog.at_level(logging.INFO, logger="server.adapters.mcp.discovery.search_surface"):
        asyncio.run(
            call_tool(
                name="modeling_transform_object",
                arguments={"object_name": "Body", "scale": [1.0, 0.8, 0.8]},
                ctx=Ctx(),
            )
        )

    log_text = "\n".join(caplog.messages)
    assert "[CALL_TOOL_PROXY] name=modeling_transform_object" in log_text
    assert "canonical_arg_keys=['name', 'scale']" in log_text


def test_call_tool_can_invoke_scene_clean_scene_during_bootstrap(monkeypatch):
    """Visible guided utility tools should stay callable through call_tool during bootstrap."""

    class Handler:
        def clean_scene(self, keep_lights_and_cameras: bool):
            assert keep_lights_and_cameras is True
            return "Scene cleaned."

    monkeypatch.setattr(
        "server.adapters.mcp.areas.scene.get_scene_handler",
        lambda: Handler(),
    )

    server = build_server("llm-guided")

    async def run():
        result = await server.call_tool(
            "call_tool",
            {"name": "scene_clean_scene", "arguments": {"keep_lights_and_cameras": True}},
        )
        return _decode_tool_result(result)

    payload = asyncio.run(run())

    assert payload == "Scene cleaned."


def test_call_tool_can_invoke_scene_clean_scene_during_build_phase(monkeypatch):
    """scene_clean_scene should stay callable as a bounded recovery hatch during build phase."""

    class Handler:
        def clean_scene(self, keep_lights_and_cameras: bool):
            assert keep_lights_and_cameras is True
            return "Scene cleaned."

    monkeypatch.setattr(
        "server.adapters.mcp.areas.scene.get_scene_handler",
        lambda: Handler(),
    )

    server = _build_phase_search_server(SessionPhase.BUILD)

    async def run():
        result = await server.call_tool(
            "call_tool",
            {"name": "scene_clean_scene", "arguments": {"keep_lights_and_cameras": True}},
        )
        return _decode_tool_result(result)

    payload = asyncio.run(run())

    assert payload == "Scene cleaned."


def test_call_tool_can_canonicalize_legacy_scene_clean_scene_split_flags(monkeypatch):
    """Guided utility proxy should tolerate the older split cleanup flags when they agree."""

    class Handler:
        def clean_scene(self, keep_lights_and_cameras: bool):
            assert keep_lights_and_cameras is True
            return "Scene cleaned."

    monkeypatch.setattr(
        "server.adapters.mcp.areas.scene.get_scene_handler",
        lambda: Handler(),
    )

    server = build_server("llm-guided")

    async def run():
        result = await server.call_tool(
            "call_tool",
            {"name": "scene_clean_scene", "arguments": {"keep_lights": True, "keep_cameras": True}},
        )
        return _decode_tool_result(result)

    payload = asyncio.run(run())

    assert payload == "Scene cleaned."


def test_direct_scene_clean_scene_can_canonicalize_legacy_split_flags(monkeypatch):
    """Direct guided utility execution should keep the same cleanup compatibility policy as call_tool."""

    class Handler:
        def clean_scene(self, keep_lights_and_cameras: bool):
            assert keep_lights_and_cameras is True
            return "Scene cleaned."

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_scene_handler", lambda: Handler())

    server = build_server("llm-guided")

    async def run():
        result = await server.call_tool(
            "scene_clean_scene",
            {"keep_lights": True, "keep_cameras": True},
        )
        return _decode_tool_result(result)

    payload = asyncio.run(run())

    assert payload == "Scene cleaned."


def test_call_tool_can_canonicalize_collection_manage_name_alias(monkeypatch):
    """Guided call_tool should tolerate legacy `name` for collection creation while keeping `collection_name` canonical."""

    class Handler:
        def manage_collection(self, action, collection_name, new_name=None, parent_name=None, object_name=None):
            assert action == "create"
            assert collection_name == "Squirrel"
            return "Created collection 'Squirrel' under Scene Collection"

    monkeypatch.setattr("server.adapters.mcp.areas.collection.get_collection_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)

    server = _build_phase_search_server(SessionPhase.BUILD)

    async def run():
        result = await server.call_tool(
            "call_tool",
            {"name": "collection_manage", "arguments": {"action": "create", "name": "Squirrel"}},
        )
        return _decode_tool_result(result)

    payload = asyncio.run(run())

    assert "Created collection 'Squirrel'" in payload


def test_direct_collection_manage_can_canonicalize_name_alias(monkeypatch):
    """Direct guided build execution should tolerate the narrow `name` compatibility alias."""

    class Handler:
        def manage_collection(self, action, collection_name, new_name=None, parent_name=None, object_name=None):
            assert action == "create"
            assert collection_name == "Squirrel"
            return "Created collection 'Squirrel' under Scene Collection"

    monkeypatch.setattr("server.adapters.mcp.areas.collection.get_collection_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)

    server = _build_phase_search_server(SessionPhase.BUILD)

    async def run():
        result = await server.call_tool(
            "collection_manage",
            {"action": "create", "name": "Squirrel"},
        )
        return _decode_tool_result(result)

    payload = asyncio.run(run())

    assert "Created collection 'Squirrel'" in payload


def test_call_tool_rejects_ambiguous_legacy_scene_clean_scene_split_flags(monkeypatch):
    """Split cleanup flags should fail clearly when they imply different cleanup behavior."""

    class Handler:
        def clean_scene(self, keep_lights_and_cameras: bool):
            raise AssertionError("Handler should not be reached for ambiguous legacy cleanup flags")

    monkeypatch.setattr(
        "server.adapters.mcp.areas.scene.get_scene_handler",
        lambda: Handler(),
    )

    server = build_server("llm-guided")

    async def run():
        with pytest.raises(ToolError, match="keep_lights_and_cameras"):
            await server.call_tool(
                "call_tool",
                {"name": "scene_clean_scene", "arguments": {"keep_lights": True, "keep_cameras": False}},
            )

    asyncio.run(run())


def test_guided_call_argument_canonicalization_accepts_common_macro_aliases():
    payload = canonicalize_guided_tool_arguments(
        "macro_attach_part_to_surface",
        {
            "part_object": "Head",
            "reference_object": "Body",
            "surface_axis": "+Z",
        },
    )

    assert payload == {
        "part_object": "Head",
        "surface_object": "Body",
        "surface_axis": "Z",
        "surface_side": "positive",
    }


def test_guided_call_argument_canonicalization_accepts_align_and_transform_aliases():
    align_payload = canonicalize_guided_tool_arguments(
        "macro_align_part_with_contact",
        {
            "part_object": "Head",
            "anchor_object": "Body",
            "contact_mode": "seat_on_surface",
        },
    )
    transform_payload = canonicalize_guided_tool_arguments(
        "modeling_transform_object",
        {
            "object_name": "Body",
            "scale": [1.15, 0.72, 0.82],
        },
    )

    assert align_payload == {
        "part_object": "Head",
        "reference_object": "Body",
        "target_relation": "contact",
    }
    assert transform_payload == {
        "name": "Body",
        "scale": [1.15, 0.72, 0.82],
    }


def test_call_tool_accepts_json_object_string_arguments(monkeypatch):
    class Handler:
        def clean_scene(self, keep_lights_and_cameras: bool):
            return f"cleaned={keep_lights_and_cameras}"

    monkeypatch.setattr(
        "server.adapters.mcp.areas.scene.get_scene_handler",
        lambda: Handler(),
    )

    server = build_server("llm-guided")

    async def run():
        result = await server.call_tool(
            "call_tool",
            {"name": "scene_clean_scene", "arguments": '{"keep_lights_and_cameras": true}'},
        )
        return _decode_tool_result(result)

    assert asyncio.run(run()) == "cleaned=True"


def test_guided_call_argument_canonicalization_accepts_proportion_axis_alias():
    payload = canonicalize_guided_tool_arguments(
        "scene_assert_proportion",
        {
            "object_name": "Head",
            "axis": "Z",
            "expected_ratio": 0.7,
            "reference_object": "Body",
        },
    )

    assert payload == {
        "object_name": "Head",
        "axis_a": "Z",
        "expected_ratio": 0.7,
        "reference_object": "Body",
    }


def test_direct_modeling_create_primitive_rejects_non_public_shape_with_actionable_guidance(monkeypatch):
    """Direct guided build execution should fail loudly for primitive drift instead of raw schema noise."""

    class Handler:
        def create_primitive(self, primitive_type, radius=1.0, size=2.0, location=None, rotation=None, name=None):
            raise AssertionError("Handler should not be reached for unsupported public primitive args")

    monkeypatch.setattr("server.adapters.mcp.areas.modeling.get_modeling_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)

    server = _build_phase_search_server(SessionPhase.BUILD)

    async def run():
        with pytest.raises(ToolError, match="modeling_transform_object\\(scale=\\.\\.\\.\\)"):
            await server.call_tool(
                "modeling_create_primitive",
                {
                    "primitive_type": "uv_sphere",
                    "name": "Head",
                    "location": [0.0, 0.0, 1.1],
                    "scale": [0.42, 0.38, 0.38],
                    "segments": 8,
                    "rings": 6,
                    "collection_name": "Squirrel",
                },
            )

    asyncio.run(run())


def test_call_tool_rejects_reference_images_batch_attach_shape():
    """Guided call_tool should explain that reference_images attach is one-reference-per-call."""

    server = build_server("llm-guided")

    async def run():
        with pytest.raises(ToolError, match="one reference per call"):
            await server.call_tool(
                "call_tool",
                {
                    "name": "reference_images",
                    "arguments": {
                        "action": "attach",
                        "images": [{"source_path": "/tmp/front.png"}, {"source_path": "/tmp/side.png"}],
                    },
                },
            )

    asyncio.run(run())


def test_call_tool_rejects_non_public_modeling_create_primitive_shape_with_actionable_guidance(monkeypatch):
    """Guided call_tool should fail with actionable guidance for primitive drift instead of opaque validation noise."""

    class Handler:
        def create_primitive(self, primitive_type, radius=1.0, size=2.0, location=None, rotation=None, name=None):
            raise AssertionError("Handler should not be reached for unsupported public primitive args")

    monkeypatch.setattr("server.adapters.mcp.areas.modeling.get_modeling_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)

    server = _build_phase_search_server(SessionPhase.BUILD)

    async def run():
        with pytest.raises(ToolError, match="modeling_transform_object\\(scale=\\.\\.\\.\\)"):
            await server.call_tool(
                "call_tool",
                {
                    "name": "modeling_create_primitive",
                    "arguments": {
                        "primitive_type": "uv_sphere",
                        "name": "Head",
                        "location": [0.0, 0.0, 1.1],
                        "scale": [0.42, 0.38, 0.38],
                        "segments": 8,
                        "rings": 6,
                        "collection_name": "Squirrel",
                    },
                },
            )

    asyncio.run(run())


def test_direct_modeling_create_primitive_can_register_guided_role_hint(monkeypatch):
    """Direct guided build execution may use guided_role as a convenience path on top of the canonical register tool."""

    recorded: list[tuple[str, str, str | None]] = []

    class Handler:
        def create_primitive(self, primitive_type, radius=1.0, size=2.0, location=None, rotation=None, name=None):
            return f"Created {primitive_type} named '{name or primitive_type}'"

    monkeypatch.setattr("server.adapters.mcp.areas.modeling.get_modeling_handler", lambda: Handler())
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.register_guided_part_role",
        lambda ctx, **kwargs: recorded.append((kwargs["object_name"], kwargs["role"], kwargs.get("role_group"))),
    )

    async def register_guided_part_role_async(ctx, **kwargs):
        recorded.append((kwargs["object_name"], kwargs["role"], kwargs.get("role_group")))
        return SessionCapabilityState(phase=SessionPhase.BUILD, guided_flow_state={"flow_id": "guided_creature_flow"})

    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.register_guided_part_role_async",
        register_guided_part_role_async,
    )

    async def get_session_capability_state_async(ctx):
        return SessionCapabilityState(phase=SessionPhase.BUILD, guided_flow_state={"flow_id": "guided_creature_flow"})

    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.get_session_capability_state",
        lambda ctx: SessionCapabilityState(
            phase=SessionPhase.BUILD,
            guided_flow_state={"flow_id": "guided_creature_flow"},
        ),
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.get_session_capability_state_async",
        get_session_capability_state_async,
    )
    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)

    server = _build_phase_search_server(SessionPhase.BUILD)

    async def run():
        result = await server.call_tool(
            "modeling_create_primitive",
            {
                "primitive_type": "Sphere",
                "name": "Squirrel_Body",
                "radius": 0.5,
                "guided_role": "body_core",
            },
        )
        return _decode_tool_result(result)

    payload = asyncio.run(run())

    assert "Created Sphere named 'Squirrel_Body'" == payload
    assert recorded == [("Squirrel_Body", "body_core", None)]


def test_direct_modeling_create_primitive_rejects_guided_role_without_explicit_name(monkeypatch):
    """Guided convenience create should require an explicit semantic name before mutation."""

    class Handler:
        def create_primitive(self, primitive_type, radius=1.0, size=2.0, location=None, rotation=None, name=None):
            raise AssertionError("Handler should not be reached when guided create has no semantic name")

    monkeypatch.setattr("server.adapters.mcp.areas.modeling.get_modeling_handler", lambda: Handler())
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.get_session_capability_state",
        lambda ctx: SessionCapabilityState(
            phase=SessionPhase.BUILD,
            guided_flow_state={
                "flow_id": "guided_creature_flow",
                "domain_profile": "creature",
                "current_step": "create_primary_masses",
            },
        ),
    )
    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)

    server = _build_phase_search_server(SessionPhase.BUILD)

    async def run():
        with pytest.raises(ToolError, match="explicit semantic `name`"):
            await server.call_tool(
                "modeling_create_primitive",
                {
                    "primitive_type": "Sphere",
                    "guided_role": "body_core",
                },
            )

    asyncio.run(run())


def test_call_tool_can_forward_guided_role_hint_for_modeling_create_primitive(monkeypatch):
    """Proxied guided build calls should preserve guided_role just like direct guided tool calls."""

    recorded: list[tuple[str, str, str | None]] = []

    class Handler:
        def create_primitive(self, primitive_type, radius=1.0, size=2.0, location=None, rotation=None, name=None):
            return f"Created {primitive_type} named '{name or primitive_type}'"

    monkeypatch.setattr("server.adapters.mcp.areas.modeling.get_modeling_handler", lambda: Handler())
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.register_guided_part_role",
        lambda ctx, **kwargs: recorded.append((kwargs["object_name"], kwargs["role"], kwargs.get("role_group"))),
    )

    async def register_guided_part_role_async(ctx, **kwargs):
        recorded.append((kwargs["object_name"], kwargs["role"], kwargs.get("role_group")))
        return SessionCapabilityState(phase=SessionPhase.BUILD, guided_flow_state={"flow_id": "guided_creature_flow"})

    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.register_guided_part_role_async",
        register_guided_part_role_async,
    )

    async def get_session_capability_state_async(ctx):
        return SessionCapabilityState(phase=SessionPhase.BUILD, guided_flow_state={"flow_id": "guided_creature_flow"})

    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.get_session_capability_state",
        lambda ctx: SessionCapabilityState(
            phase=SessionPhase.BUILD,
            guided_flow_state={"flow_id": "guided_creature_flow"},
        ),
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.get_session_capability_state_async",
        get_session_capability_state_async,
    )
    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)

    server = _build_phase_search_server(SessionPhase.BUILD)

    async def run():
        result = await server.call_tool(
            "call_tool",
            {
                "name": "modeling_create_primitive",
                "arguments": {
                    "primitive_type": "Sphere",
                    "name": "Squirrel_Head",
                    "radius": 0.35,
                    "guided_role": "head_mass",
                },
            },
        )
        return _decode_tool_result(result)

    payload = asyncio.run(run())

    assert "Created Sphere named 'Squirrel_Head'" == payload
    assert recorded == [("Squirrel_Head", "head_mass", None)]


def test_call_tool_can_block_placeholder_name_for_guided_role_hint(monkeypatch):
    """Proxied guided build calls should preserve naming-policy blocking for opaque placeholder names."""

    class Handler:
        def create_primitive(self, primitive_type, radius=1.0, size=2.0, location=None, rotation=None, name=None):
            raise AssertionError("Handler should not be reached when guided naming blocks the call")

    monkeypatch.setattr("server.adapters.mcp.areas.modeling.get_modeling_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)
    monkeypatch.setattr("server.adapters.mcp.router_helper._get_active_surface_profile", lambda: "llm-guided")
    monkeypatch.setattr(
        "server.adapters.mcp.router_helper._get_active_session_state",
        lambda: SessionCapabilityState(
            phase=SessionPhase.BUILD,
            guided_flow_state={
                "flow_id": "guided_creature_flow",
                "domain_profile": "creature",
                "current_step": "create_primary_masses",
                "completed_steps": ["understand_goal", "establish_spatial_context"],
                "required_checks": [],
                "required_prompts": ["guided_session_start", "reference_guided_creature_build"],
                "preferred_prompts": ["workflow_router_first"],
                "next_actions": ["begin_primary_masses"],
                "blocked_families": [],
                "allowed_families": ["primary_masses", "reference_context"],
                "allowed_roles": ["body_core", "head_mass", "tail_mass"],
                "completed_roles": [],
                "missing_roles": ["body_core", "head_mass", "tail_mass"],
                "required_role_groups": ["primary_masses"],
                "step_status": "ready",
            },
        ),
    )

    server = _build_phase_search_server(SessionPhase.BUILD)

    async def run():
        result = await server.call_tool(
            "call_tool",
            {
                "name": "modeling_create_primitive",
                "arguments": {
                    "primitive_type": "Sphere",
                    "name": "Sphere",
                    "radius": 0.5,
                    "guided_role": "body_core",
                },
            },
        )
        return _decode_tool_result(result)

    payload = asyncio.run(run())

    assert "Guided naming blocked object name 'Sphere'" in payload
    assert "Body" in payload


def test_search_tools_exact_match_returns_compact_result_for_visible_tool():
    """Exact tool-name queries should return a compact, tightly bounded result row."""

    server = _build_phase_search_server(SessionPhase.BUILD)

    async def run():
        result = await server.call_tool("search_tools", {"query": "collection_manage"})
        return _decode_tool_result(result)

    payload = asyncio.run(run())

    assert payload
    assert payload[0]["name"] == "collection_manage"
    assert set(payload[0]).issubset({"name", "description", "category", "capability_id", "aliases"})


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

    assert legacy_count == 187
    assert guided_count == 11
    assert guided_bytes < legacy_bytes


def test_call_tool_cannot_invoke_hidden_tool_during_bootstrap():
    """Hidden tools should not become callable through call_tool during bootstrap."""

    server = build_server("llm-guided")

    async def run():
        return await server.call_tool(
            "call_tool",
            {"name": "inspect_scene", "arguments": {"action": "object", "target_object": "Cube"}},
        )

    with pytest.raises((NotFoundError, ToolError), match="search_tools"):
        asyncio.run(run())


def test_guided_surface_fails_closed_for_non_bypassed_direct_and_discovered_calls(monkeypatch):
    """Guided surfaces should still fail closed for normal build tools when router processing breaks."""

    class Handler:
        def create_primitive(self, primitive_type, size=2.0, location=None, rotation=None, name=None):
            return "Created"

    class FailingRouter:
        def process_llm_tool_call(self, tool_name, params, prompt=None):
            raise RuntimeError("router down")

    monkeypatch.setattr("server.adapters.mcp.areas.modeling.get_modeling_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.router_helper.get_router", lambda: FailingRouter())
    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: True)

    server = _build_phase_search_server(SessionPhase.BUILD)

    async def run():
        direct = await server.call_tool("modeling_create_primitive", {"primitive_type": "CUBE"})
        discovered = await server.call_tool(
            "call_tool",
            {"name": "modeling_create_primitive", "arguments": {"primitive_type": "CUBE"}},
        )
        return direct, discovered

    direct, discovered = asyncio.run(run())

    direct_text = "".join(getattr(block, "text", "") for block in direct.content)
    discovered_text = "".join(getattr(block, "text", "") for block in discovered.content)

    assert "Router processing failed" in direct_text
    assert discovered_text == direct_text
