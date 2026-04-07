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

            status_result = result_payload(await client.call_tool("router_get_status", {}))
            assert status_result["current_phase"] == "build"
            assert any(
                set(rule.get("names") or ()) >= {"collection_manage", "modeling_create_primitive"}
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
            assert collection_result == "Created collection 'Squirrel' under Scene Collection"

            primitive_result = result_payload(
                await client.call_tool(
                    "modeling_create_primitive",
                    {"primitive_type": "Sphere", "name": "Head", "location": [0.0, 0.0, 1.1]},
                )
            )
            assert primitive_result == "Created Sphere named 'Head'"

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
