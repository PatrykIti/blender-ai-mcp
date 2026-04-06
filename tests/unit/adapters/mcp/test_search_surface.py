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
        "reference_images",
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
    assert "modeling_add_modifier" not in build_names
    assert "modeling_apply_modifier" not in build_names
    assert "modeling_list_modifiers" not in build_names
    assert "armature_create" not in build_names
    assert "sculpt_auto" not in build_names
    assert "extraction_render_angles" not in build_names
    assert "extraction_render_angles" in inspect_names
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

    assert legacy_count == 183
    assert guided_count == 8
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
