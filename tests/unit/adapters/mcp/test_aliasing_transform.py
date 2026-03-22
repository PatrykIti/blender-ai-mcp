"""Tests for transform-based tool and parameter aliasing."""

from __future__ import annotations

import asyncio

from fastmcp.server.providers import LocalProvider

from server.adapters.mcp.areas.scene import register_scene_tools
from server.adapters.mcp.areas.workflow_catalog import register_workflow_tools
from server.adapters.mcp.surfaces import get_surface_profile
from server.adapters.mcp.transforms.naming import build_naming_transform


def test_llm_guided_naming_transform_renames_tools_and_arguments():
    """llm-guided naming transform should expose aliased tool and argument names."""

    provider = LocalProvider()
    register_scene_tools(provider)
    register_workflow_tools(provider)

    async def run():
        tools = await provider.list_tools()
        transform = build_naming_transform(get_surface_profile("llm-guided"))
        transformed = await transform.list_tools(tools)

        check_scene = next(tool for tool in transformed if tool.name == "check_scene")
        inspect_scene = next(tool for tool in transformed if tool.name == "inspect_scene")
        browse_workflows = next(tool for tool in transformed if tool.name == "browse_workflows")

        return check_scene, inspect_scene, browse_workflows

    check_scene, inspect_scene, browse_workflows = asyncio.run(run())

    assert "query" in check_scene.parameters["properties"]
    assert "action" not in check_scene.parameters["properties"]

    assert "target_object" in inspect_scene.parameters["properties"]
    assert "object_name" not in inspect_scene.parameters["properties"]

    assert "name" in browse_workflows.parameters["properties"]
    assert "search_query" in browse_workflows.parameters["properties"]
