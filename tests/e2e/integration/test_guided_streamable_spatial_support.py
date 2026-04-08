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

            post_goal_tools = {tool.name for tool in await client.list_tools()}
            assert {"scene_scope_graph", "scene_relation_graph", "scene_view_diagnostics"}.issubset(post_goal_tools)
            assert "modeling_create_primitive" not in post_goal_tools
            assert "collection_manage" not in post_goal_tools

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
