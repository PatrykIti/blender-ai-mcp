"""Transport-backed guided-surface contract parity regressions for TASK-141."""

from __future__ import annotations

import asyncio
import textwrap
from pathlib import Path

import pytest
from fastmcp.exceptions import ToolError

from ._guided_surface_harness import result_payload, stdio_client, write_server_script

_PATCHED_GUIDED_CONTRACT_SERVER = textwrap.dedent(
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
                "scope_kind": "object_set",
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
                    "scope_kind": "object_set",
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


    router_area.get_router_handler = lambda: RouterHandler()
    router_area._should_attach_repair_suggestion = lambda payload: False
    scene_area.get_scene_handler = lambda: SceneHandler()
    collection_area.get_collection_handler = lambda: CollectionHandler()
    modeling_area.get_modeling_handler = lambda: ModelingHandler()
    router_helper.is_router_enabled = lambda: False
    """
)


@pytest.mark.slow
def test_guided_surface_contract_parity_over_stdio(tmp_path: Path):
    """The active stdio guided surface should keep the documented creature contract end to end."""

    image = tmp_path / "front_ref.png"
    image.write_bytes(b"fake-png")
    script_path = write_server_script(tmp_path, _PATCHED_GUIDED_CONTRACT_SERVER)

    async def run() -> None:
        async with stdio_client(script_path) as client:
            initial_tools = sorted(tool.name for tool in await client.list_tools())
            assert initial_tools == [
                "browse_workflows",
                "call_tool",
                "get_prompt",
                "list_prompts",
                "reference_images",
                "router_get_status",
                "router_set_goal",
                "scene_relation_graph",
                "scene_scope_graph",
                "scene_view_diagnostics",
                "search_tools",
            ]

            utility_search = result_payload(
                await client.call_tool("search_tools", {"query": "clean reset fresh scene"})
            )
            utility_names = {item["name"] for item in utility_search}
            assert "scene_clean_scene" in utility_names

            cleanup = result_payload(
                await client.call_tool(
                    "call_tool",
                    {"tool": "scene_clean_scene", "params": {"keep_lights": True, "keep_cameras": True}},
                )
            )
            assert cleanup == "Scene cleaned."

            batch_attach = result_payload(
                await client.call_tool(
                    "reference_images",
                    {"action": "attach", "images": [{"source_path": str(image)}]},
                )
            )
            assert "one reference per call" in str(batch_attach["error"])

            staged_attach = result_payload(
                await client.call_tool(
                    "reference_images",
                    {"action": "attach", "source_path": str(image), "label": "front_ref"},
                )
            )
            assert staged_attach["reference_count"] == 1
            assert "pending" in str(staged_attach["message"]).lower()

            goal_result = result_payload(
                await client.call_tool(
                    "router_set_goal",
                    {"goal": "create a low-poly squirrel matching front and side reference images"},
                )
            )
            assert goal_result["guided_handoff"]["recipe_id"] == "low_poly_creature_blockout"
            assert goal_result["guided_reference_readiness"]["attached_reference_count"] == 1
            assert goal_result["guided_reference_readiness"]["pending_reference_count"] == 0
            assert goal_result["guided_flow_state"]["current_step"] == "establish_spatial_context"

            post_goal_tools = {tool.name for tool in await client.list_tools()}
            assert {"scene_scope_graph", "scene_relation_graph", "scene_view_diagnostics"}.issubset(post_goal_tools)

            status_result = result_payload(await client.call_tool("router_get_status", {}))
            assert status_result["current_phase"] == "build"
            assert status_result["guided_flow_state"]["current_step"] == "establish_spatial_context"
            assert any(
                "scene_scope_graph" in set(rule.get("names") or ())
                for rule in status_result["visibility_rules"]
                if rule.get("components") == ["tool"] or rule.get("components") == {"tool"}
            )

            build_cleanup_search = result_payload(
                await client.call_tool(
                    "search_tools",
                    {"query": "clean reset stale scene during build recovery"},
                )
            )
            build_cleanup_names = {item["name"] for item in build_cleanup_search}
            assert "scene_clean_scene" in build_cleanup_names

            build_cleanup = result_payload(
                await client.call_tool(
                    "call_tool",
                    {"name": "scene_clean_scene", "arguments": {"keep_lights_and_cameras": True}},
                )
            )
            assert build_cleanup == "Scene cleaned."

            await client.call_tool(
                "scene_scope_graph",
                {"target_object": "Squirrel_Body", "target_objects": ["Squirrel_Head", "Squirrel_Tail"]},
            )
            await client.call_tool(
                "scene_relation_graph",
                {"target_objects": ["Squirrel_Head", "Squirrel_Body"], "goal_hint": "assembled creature"},
            )
            await client.call_tool(
                "scene_view_diagnostics",
                {"target_object": "Squirrel_Head", "target_objects": ["Squirrel_Body"], "view_name": "TOP"},
            )

            unlocked_status_result = result_payload(await client.call_tool("router_get_status", {}))
            assert unlocked_status_result["guided_flow_state"]["current_step"] == "create_primary_masses"
            assert any(
                set(rule.get("names") or ())
                >= {"collection_manage", "modeling_create_primitive", "guided_register_part"}
                for rule in unlocked_status_result["visibility_rules"]
                if rule.get("components") == ["tool"] or rule.get("components") == {"tool"}
            )

            blocked_body = result_payload(
                await client.call_tool(
                    "modeling_create_primitive",
                    {"primitive_type": "Sphere", "name": "Squirrel_Body", "radius": 0.5},
                )
            )
            assert "requires an explicit semantic role" in blocked_body

            register_body = result_payload(
                await client.call_tool(
                    "guided_register_part",
                    {"object_name": "Squirrel_Body", "role": "body_core"},
                )
            )
            assert register_body["guided_flow_state"]["completed_roles"] == ["body_core"]

            body_result = result_payload(
                await client.call_tool(
                    "modeling_create_primitive",
                    {"primitive_type": "Sphere", "name": "Squirrel_Body", "location": [0.0, 0.0, 0.6], "radius": 0.5},
                )
            )
            assert body_result == "Created Sphere named 'Squirrel_Body'"

            head_result = result_payload(
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
            )
            assert head_result == "Created Sphere named 'Squirrel_Head'"

            role_unlocked_status = result_payload(await client.call_tool("router_get_status", {}))
            assert role_unlocked_status["guided_flow_state"]["current_step"] == "place_secondary_parts"
            assert role_unlocked_status["guided_flow_state"]["allowed_roles"] == [
                "snout_mass",
                "ear_pair",
                "foreleg_pair",
                "hindleg_pair",
            ]

            blocked_ear = result_payload(
                await client.call_tool(
                    "modeling_create_primitive",
                    {"primitive_type": "Cone", "name": "Squirrel_Ear_L", "radius": 0.1},
                )
            )
            assert "requires an explicit semantic role" in blocked_ear

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

            collection_result = result_payload(
                await client.call_tool("collection_manage", {"action": "create", "name": "Squirrel"})
            )
            assert "tool family 'primary_masses'" in collection_result

            with pytest.raises(ToolError, match="modeling_transform_object\\(scale=\\.\\.\\.\\)"):
                await client.call_tool(
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
