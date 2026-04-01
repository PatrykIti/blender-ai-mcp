"""Tests for task-mode registration semantics on FastMCP surfaces."""

from __future__ import annotations

import asyncio

import pytest
from fastmcp import FastMCP
from fastmcp.tools.tool import TaskConfig
from server.adapters.mcp.factory import build_server


def test_sync_function_with_task_mode_fails_registration():
    """FastMCP should reject sync functions when task execution is enabled."""

    server = FastMCP("demo", tasks=True)

    def sync_tool() -> str:
        return "ok"

    with pytest.raises(ValueError):
        server.tool(sync_tool, name="sync_tool", task=TaskConfig(mode="optional"))


def test_optional_required_and_forbidden_modes_are_preserved_on_registered_components():
    """Task-capable components should surface explicit mode semantics."""

    server = FastMCP("demo", tasks=True)

    @server.tool(task=TaskConfig(mode="optional"))
    async def optional_tool() -> str:
        return "ok"

    @server.tool(task=TaskConfig(mode="required"))
    async def required_tool() -> str:
        return "ok"

    @server.tool(task=TaskConfig(mode="forbidden"))
    async def forbidden_tool() -> str:
        return "ok"

    async def run():
        tasks = await server.get_tasks()
        listed = await server.list_tools()
        return tasks, {tool.name for tool in listed}

    tasks, listed_names = asyncio.run(run())
    by_name = {tool.name: tool.task_config.mode for tool in tasks}

    assert by_name["optional_tool"] == "optional"
    assert by_name["required_tool"] == "required"
    assert "forbidden_tool" not in by_name
    assert listed_names == {"optional_tool", "required_tool", "forbidden_tool"}


def test_guided_surface_exposes_adopted_task_capable_tools():
    """TASK-088 adopted endpoints should be visible to the FastMCP task registry."""

    server = build_server("internal-debug")

    async def run():
        return await server.get_tasks()

    tasks = asyncio.run(run())
    by_name = {tool.name: tool.task_config.mode for tool in tasks}

    assert by_name["scene_get_viewport"] == "optional"
    assert by_name["extraction_render_angles"] == "optional"
    assert by_name["workflow_catalog"] == "optional"
    assert by_name["export_glb"] == "optional"
    assert by_name["export_fbx"] == "optional"
    assert by_name["export_obj"] == "optional"
    assert by_name["import_obj"] == "optional"
    assert by_name["import_fbx"] == "optional"
    assert by_name["import_glb"] == "optional"
    assert by_name["import_image_as_plane"] == "optional"
