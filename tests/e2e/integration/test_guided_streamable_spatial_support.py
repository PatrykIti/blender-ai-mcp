"""Streamable HTTP guided-surface regressions for default spatial support."""

from __future__ import annotations

import asyncio
import textwrap
from pathlib import Path

import pytest

from ._guided_surface_harness import result_payload, run_streamable_server, streamable_client, write_server_script

_PATCHED_GUIDED_STREAMABLE_SERVER = textwrap.dedent(
    """
    from server.adapters.mcp.areas import router as router_area
    import server.adapters.mcp.areas.collection as collection_area
    import server.adapters.mcp.areas.modeling as modeling_area
    import server.adapters.mcp.areas.scene as scene_area
    import server.adapters.mcp.router_helper as router_helper


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
        def clean_scene(self, keep_lights_and_cameras):
            return "Scene cleaned."

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


    class CollectionHandler:
        def manage_collection(self, action, collection_name, new_name=None, parent_name=None, object_name=None):
            return f"Created collection '{collection_name}' under Scene Collection"


    class ModelingHandler:
        def create_primitive(self, primitive_type, radius=1.0, size=2.0, location=None, rotation=None, name=None):
            return f"Created {primitive_type} named '{name or primitive_type}'"

        def transform_object(self, name, location=None, rotation=None, scale=None):
            return f"Transformed object '{name}'"


    router_area.get_router_handler = lambda: RouterHandler()
    router_area._should_attach_repair_suggestion = lambda payload: False
    scene_area.get_scene_handler = lambda: SceneHandler()
    collection_area.get_collection_handler = lambda: CollectionHandler()
    modeling_area.get_modeling_handler = lambda: ModelingHandler()
    router_helper.is_router_enabled = lambda: False
    """
)


@pytest.mark.slow
def test_streamable_guided_session_expands_visible_tools_after_goal_handoff(tmp_path: Path):
    """The same streamable session should keep spatial support pinned while search can reach build tools after goal handoff."""

    script_path = write_server_script(tmp_path, _PATCHED_GUIDED_STREAMABLE_SERVER)

    async def run(url: str) -> None:
        async with streamable_client(url) as client:
            initial_tools = {tool.name for tool in await client.list_tools()}
            assert "scene_scope_graph" in initial_tools
            assert "scene_relation_graph" in initial_tools
            assert "scene_view_diagnostics" in initial_tools
            assert "modeling_create_primitive" not in initial_tools
            assert "collection_manage" not in initial_tools

            goal_result = result_payload(
                await client.call_tool(
                    "router_set_goal",
                    {"goal": "create a low-poly squirrel matching front and side reference images"},
                )
            )
            assert goal_result["guided_handoff"]["recipe_id"] == "low_poly_creature_blockout"
            assert goal_result["guided_flow_state"]["current_step"] == "establish_spatial_context"

            post_goal_tools = {tool.name for tool in await client.list_tools()}
            assert {"scene_scope_graph", "scene_relation_graph", "scene_view_diagnostics"}.issubset(post_goal_tools)
            assert "modeling_create_primitive" not in post_goal_tools
            assert "collection_manage" not in post_goal_tools

            spoof_attempt = result_payload(
                await client.call_tool(
                    "scene_view_diagnostics",
                    {"target_object": "Camera", "view_name": "TOP"},
                )
            )
            assert spoof_attempt["payload"]["scope"]["primary_target"] == "Camera"
            spoof_status = result_payload(await client.call_tool("router_get_status", {}))
            assert spoof_status["guided_flow_state"]["current_step"] == "establish_spatial_context"

            spatial_scope = {"target_object": "Squirrel_Body", "target_objects": ["Squirrel_Head", "Squirrel_Tail"]}
            await client.call_tool(
                "scene_scope_graph",
                spatial_scope,
            )
            await client.call_tool(
                "scene_relation_graph",
                {**spatial_scope, "goal_hint": "assembled creature"},
            )
            await client.call_tool(
                "scene_view_diagnostics",
                {**spatial_scope, "view_name": "TOP"},
            )

            status_result = result_payload(await client.call_tool("router_get_status", {}))
            assert status_result["guided_flow_state"]["current_step"] == "create_primary_masses"
            assert any(
                set(rule.get("names") or ()) >= {"guided_register_part", "modeling_create_primitive"}
                for rule in status_result["visibility_rules"]
                if rule.get("components") == ["tool"] or rule.get("components") == {"tool"}
            )

            blocked = result_payload(
                await client.call_tool(
                    "modeling_create_primitive",
                    {"primitive_type": "Cone", "name": "Squirrel_Ear_L", "radius": 0.1, "guided_role": "ear_pair"},
                )
            )
            assert "tool family 'secondary_parts'" in blocked

            await client.call_tool(
                "guided_register_part",
                {"object_name": "Squirrel_Body", "role": "body_core"},
            )
            await client.call_tool(
                "guided_register_part",
                {"object_name": "Squirrel_Head", "role": "head_mass"},
            )

            stale_status = result_payload(await client.call_tool("router_get_status", {}))
            assert stale_status["guided_flow_state"]["current_step"] == "place_secondary_parts"
            assert stale_status["guided_flow_state"]["spatial_refresh_required"] is True
            assert stale_status["guided_flow_state"]["next_actions"] == ["refresh_spatial_context"]
            assert stale_status["guided_flow_state"]["allowed_families"] == [
                "spatial_context",
                "reference_context",
            ]

            refresh_scope = {"target_object": "Squirrel_Body", "target_objects": ["Squirrel_Head"]}
            await client.call_tool("scene_scope_graph", refresh_scope)
            await client.call_tool(
                "scene_relation_graph",
                {**refresh_scope, "goal_hint": "assembled creature"},
            )
            await client.call_tool(
                "scene_view_diagnostics",
                {**refresh_scope, "view_name": "TOP"},
            )

            refreshed_status = result_payload(await client.call_tool("router_get_status", {}))
            assert refreshed_status["guided_flow_state"]["spatial_refresh_required"] is False
            assert refreshed_status["guided_flow_state"]["allowed_roles"] == [
                "snout_mass",
                "ear_pair",
                "foreleg_pair",
                "hindleg_pair",
            ]

            ear_result = result_payload(
                await client.call_tool(
                    "modeling_create_primitive",
                    {
                        "primitive_type": "Cone",
                        "name": "Squirrel_Ear_L",
                        "location": [0.22, -0.3, 1.82],
                        "radius": 0.1,
                        "guided_role": "ear_pair",
                    },
                )
            )
            assert ear_result == "Created Cone named 'Squirrel_Ear_L'"

            primitive_search = result_payload(
                await client.call_tool(
                    "search_tools",
                    {"query": "low poly creature head body primitive blockout"},
                )
            )
            primitive_names = {item["name"] for item in primitive_search}
            assert "modeling_create_primitive" in primitive_names

            collection_search = result_payload(
                await client.call_tool(
                    "search_tools",
                    {"query": "create squirrel blockout collection move object to collection"},
                )
            )
            collection_names = {item["name"] for item in collection_search}
            assert "collection_manage" in collection_names

    with run_streamable_server(script_path) as url:
        asyncio.run(run(url))


@pytest.mark.slow
def test_streamable_guided_reconnect_resets_build_only_visibility_but_keeps_spatial_support(tmp_path: Path):
    """A new streamable session should keep default spatial support while build tools remain search-discovered only."""

    script_path = write_server_script(tmp_path, _PATCHED_GUIDED_STREAMABLE_SERVER)

    async def first_session(url: str) -> tuple[str | None, set[str], set[str]]:
        async with streamable_client(url) as client:
            bootstrap_tools = {tool.name for tool in await client.list_tools()}
            status_payload = result_payload(await client.call_tool("router_get_status", {}))
            goal_result = result_payload(
                await client.call_tool(
                    "router_set_goal",
                    {"goal": "create a low-poly squirrel matching front and side reference images"},
                )
            )
            assert goal_result["guided_handoff"]["recipe_id"] == "low_poly_creature_blockout"
            build_tools = {tool.name for tool in await client.list_tools()}
            return status_payload.get("session_id"), bootstrap_tools, build_tools

    async def second_session(url: str) -> tuple[str | None, set[str]]:
        async with streamable_client(url) as client:
            status_payload = result_payload(await client.call_tool("router_get_status", {}))
            bootstrap_tools = {tool.name for tool in await client.list_tools()}
            return status_payload.get("session_id"), bootstrap_tools

    with run_streamable_server(script_path) as url:
        first_session_id, first_bootstrap_tools, first_build_tools = asyncio.run(first_session(url))
        second_session_id, second_bootstrap_tools = asyncio.run(second_session(url))

    assert first_session_id is not None
    assert second_session_id is not None
    assert first_session_id != second_session_id

    assert {"scene_scope_graph", "scene_relation_graph", "scene_view_diagnostics"}.issubset(first_bootstrap_tools)
    assert {"scene_scope_graph", "scene_relation_graph", "scene_view_diagnostics"}.issubset(first_build_tools)
    assert "modeling_create_primitive" not in first_build_tools
    assert "collection_manage" not in first_build_tools

    assert {"scene_scope_graph", "scene_relation_graph", "scene_view_diagnostics"}.issubset(second_bootstrap_tools)
    assert "modeling_create_primitive" not in second_bootstrap_tools
    assert "collection_manage" not in second_bootstrap_tools
