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


@pytest.mark.slow
def test_guided_call_tool_hidden_tool_failure_points_back_to_search(tmp_path: Path):
    """Unknown guided call_tool targets should push the client back toward search_tools."""

    script_path = write_server_script(tmp_path, _PATCHED_GUIDED_SEARCH_SERVER)

    async def run() -> None:
        async with stdio_client(script_path) as client:
            with pytest.raises(ToolError, match="search_tools"):
                await client.call_tool(
                    "call_tool",
                    {"name": "inspect_scene", "arguments": {"action": "object", "target_object": "Cube"}},
                )

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
