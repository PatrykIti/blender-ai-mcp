"""Compatibility tests for legacy-flat list-tools pagination."""

from __future__ import annotations

import asyncio

from mcp.types import ListToolsRequest, PaginatedRequestParams
from server.adapters.mcp.factory import build_server


def test_legacy_flat_first_page_contains_full_catalog_without_next_cursor():
    """legacy-flat should fit the current catalog in one page for compatibility clients."""

    async def run():
        server = build_server("legacy-flat")
        result = await server._list_tools_mcp(
            ListToolsRequest(method="tools/list", params=PaginatedRequestParams())
        )
        return len(result.tools), result.nextCursor

    tool_count, next_cursor = asyncio.run(run())

    assert tool_count == 157
    assert next_cursor is None


def test_legacy_flat_camera_focus_description_clarifies_parameter_name():
    """The public tool description should steer clients toward object_name for camera focus."""

    async def run():
        server = build_server("legacy-flat")
        result = await server._list_tools_mcp(
            ListToolsRequest(method="tools/list", params=PaginatedRequestParams())
        )
        tool = next(tool for tool in result.tools if tool.name == "scene_camera_focus")
        return tool.description

    description = asyncio.run(run())

    assert "object_name" in description
    assert "target_object" in description
    assert "focus_target" in description


def test_legacy_manual_first_page_omits_router_and_workflow_tools():
    """legacy-manual should keep the first page router-free and workflow-free for manual clients."""

    async def run():
        server = build_server("legacy-manual")
        result = await server._list_tools_mcp(
            ListToolsRequest(method="tools/list", params=PaginatedRequestParams())
        )
        return {tool.name for tool in result.tools}, len(result.tools), result.nextCursor

    names, tool_count, next_cursor = asyncio.run(run())

    assert "router_set_goal" not in names
    assert "router_get_status" not in names
    assert "router_clear_goal" not in names
    assert "workflow_catalog" not in names
    assert "modeling_create_primitive" in names
    assert tool_count == 150
    assert next_cursor is None


def test_internal_debug_first_page_keeps_platform_pagination_active():
    """Non-compatibility surfaces should still expose cursor-based pagination on the first page."""

    async def run():
        server = build_server("internal-debug")
        result = await server._list_tools_mcp(
            ListToolsRequest(method="tools/list", params=PaginatedRequestParams())
        )
        return len(result.tools), result.nextCursor

    tool_count, next_cursor = asyncio.run(run())

    assert tool_count == 100
    assert next_cursor is not None
