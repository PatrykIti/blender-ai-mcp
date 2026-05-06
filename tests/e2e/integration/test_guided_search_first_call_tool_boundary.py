"""Transport-backed regressions for search-first guidance on the shaped guided surface."""

from __future__ import annotations

import asyncio
import textwrap
from pathlib import Path

import pytest
from fastmcp.exceptions import ToolError

from ._guided_surface_harness import result_payload, stdio_client, write_server_script

_PATCHED_GUIDED_SEARCH_SERVER = textwrap.dedent(
    """
    import server.adapters.mcp.areas.scene as scene_area
    import server.adapters.mcp.router_helper as router_helper


    class SceneHandler:
        def clean_scene(self, keep_lights_and_cameras):
            return "Scene cleaned."


    scene_area.get_scene_handler = lambda: SceneHandler()
    router_helper.is_router_enabled = lambda: False
    """
)

_PATCHED_GUIDED_SEARCH_REARM_SERVER = textwrap.dedent(
    """
    from server.adapters.mcp.areas import router as router_area
    import server.adapters.mcp.areas.modeling as modeling_area
    import server.adapters.mcp.areas.scene as scene_area
    import server.adapters.mcp.router_helper as router_helper
    import server.infrastructure.di as di


    class RouterHandler:
        def set_goal(self, goal, resolved_params=None):
            return {
                "status": "no_match",
                "continuation_mode": "guided_manual_build",
                "workflow": None,
                "resolved": {},
                "unresolved": [],
                "resolution_sources": {},
                "phase_hint": "build",
                "message": "Continue on the guided build surface.",
            }

        def clear_goal(self):
            return "cleared"


    class SceneHandler:
        def get_scope_graph(self, target_object=None, target_objects=None, collection_name=None):
            names = [name for name in [target_object, *(target_objects or [])] if name]
            primary = target_object or (names[0] if names else None)
            return {
                "scope_kind": "object_set" if len(names) > 1 else "single_object",
                "primary_target": primary,
                "object_names": names,
                "object_count": len(names),
                "object_roles": [],
            }

        def get_relation_graph(
            self,
            target_object=None,
            target_objects=None,
            collection_name=None,
            goal_hint=None,
            include_truth_payloads=False,
        ):
            names = [name for name in [target_object, *(target_objects or [])] if name]
            primary = target_object or (names[0] if names else None)
            return {
                "scope": {
                    "scope_kind": "object_set" if len(names) > 1 else "single_object",
                    "primary_target": primary,
                    "object_names": names,
                    "object_count": len(names),
                    "object_roles": [],
                },
                "pairs": [],
                "summary": {"pair_count": 0},
            }

        def get_view_diagnostics(
            self,
            target_object=None,
            target_objects=None,
            camera_name=None,
            focus_target=None,
            view_name=None,
            orbit_horizontal=0.0,
            orbit_vertical=0.0,
            zoom_factor=None,
            persist_view=False,
        ):
            names = [name for name in [target_object, *(target_objects or [])] if name]
            return {
                "view_query": {
                    "requested_view_source": "user_perspective",
                    "resolved_view_source": "user_perspective",
                    "analysis_backend": "mirrored_user_perspective",
                    "available": True,
                    "state_restored": True,
                },
                "summary": {
                    "target_count": len(names),
                    "visible_count": len(names),
                    "partially_visible_count": 0,
                    "fully_occluded_count": 0,
                    "outside_frame_count": 0,
                    "unavailable_count": 0,
                    "centered_target_count": len(names),
                    "framing_issue_count": 0,
                },
                "targets": [],
            }


    class ModelingHandler:
        def create_primitive(self, primitive_type, radius=1.0, size=2.0, location=None, rotation=None, name=None):
            return f"Created {primitive_type} named '{name or primitive_type}'"

        def transform_object(self, name, location=None, rotation=None, scale=None):
            return f"Transformed object '{name}'"


    router_area.get_router_handler = lambda: RouterHandler()
    router_area._should_attach_repair_suggestion = lambda payload: False
    router_area._scene_has_meaningful_guided_objects = lambda: False
    scene_area.get_scene_handler = lambda: SceneHandler()
    di.get_scene_handler = lambda: SceneHandler()
    modeling_area.get_modeling_handler = lambda: ModelingHandler()
    router_helper.is_router_enabled = lambda: False
    """
)


@pytest.mark.slow
def test_guided_call_tool_hidden_tool_failure_points_back_to_search(tmp_path: Path):
    """Known-but-hidden guided call_tool targets should surface recovery guidance without killing the session."""

    script_path = write_server_script(tmp_path, _PATCHED_GUIDED_SEARCH_SERVER)

    async def run() -> None:
        async with stdio_client(script_path) as client:
            with pytest.raises(
                ToolError,
                match="Hidden tool on the current guided surface: 'inspect_scene'.*visibility_rules.*search_tools",
            ):
                await client.call_tool(
                    "call_tool",
                    {"name": "inspect_scene", "arguments": {"action": "object", "target_object": "Cube"}},
                )

            recovery = result_payload(await client.call_tool("search_tools", {"query": "clean reset fresh scene"}))
            assert "scene_clean_scene" in {item["name"] for item in recovery}

    asyncio.run(run())


@pytest.mark.slow
def test_guided_stdio_call_tool_hidden_after_spatial_rearm_points_to_required_checks(tmp_path: Path):
    """The stdio seam should also prove post-goal hidden-tool recovery after spatial rearm, not only bootstrap hidden tools."""

    script_path = write_server_script(tmp_path, _PATCHED_GUIDED_SEARCH_REARM_SERVER)

    async def run() -> None:
        async with stdio_client(script_path) as client:
            await client.call_tool(
                "router_set_goal",
                {"goal": "create a low-poly squirrel matching front and side reference images"},
            )
            await client.call_tool(
                "modeling_create_primitive",
                {
                    "primitive_type": "Sphere",
                    "name": "Squirrel_Body",
                    "location": [0.0, 0.0, 0.6],
                    "radius": 0.5,
                    "guided_role": "body_core",
                },
            )
            await client.call_tool(
                "modeling_create_primitive",
                {
                    "primitive_type": "Sphere",
                    "name": "Squirrel_Head",
                    "location": [0.0, -0.4, 1.45],
                    "radius": 0.35,
                    "guided_role": "head_mass",
                },
            )

            with pytest.raises(
                ToolError,
                match=(
                    "Hidden tool while spatial_refresh_required is active: 'modeling_transform_object'.*"
                    "scene_scope_graph\\(\\.\\.\\.\\).*scene_relation_graph\\(\\.\\.\\.\\).*scene_view_diagnostics\\(\\.\\.\\.\\)"
                ),
            ):
                await client.call_tool(
                    "call_tool",
                    {
                        "name": "modeling_transform_object",
                        "arguments": {"name": "Squirrel_Head", "scale": [1.0, 0.92, 0.95]},
                    },
                )

            status_result = result_payload(await client.call_tool("router_get_status", {}))
            assert status_result["guided_flow_state"]["current_step"] == "place_secondary_parts"
            assert status_result["guided_flow_state"]["spatial_refresh_required"] is True

            refresh_scope = {"target_object": "Squirrel_Body", "target_objects": ["Squirrel_Head"]}
            scope_result = result_payload(await client.call_tool("scene_scope_graph", refresh_scope))
            assert scope_result

    asyncio.run(run())


@pytest.mark.slow
def test_guided_search_then_call_tool_can_reach_visible_utility_path(tmp_path: Path):
    """A searched visible utility tool should still execute cleanly through call_tool."""

    script_path = write_server_script(tmp_path, _PATCHED_GUIDED_SEARCH_SERVER)

    async def run() -> None:
        async with stdio_client(script_path) as client:
            payload = result_payload(await client.call_tool("search_tools", {"query": "clean reset fresh scene"}))
            names = {item["name"] for item in payload}
            assert "scene_clean_scene" in names

            result = result_payload(
                await client.call_tool(
                    "call_tool",
                    {"name": "scene_clean_scene", "arguments": {"keep_lights_and_cameras": True}},
                )
            )
            assert result == "Scene cleaned."

    asyncio.run(run())
