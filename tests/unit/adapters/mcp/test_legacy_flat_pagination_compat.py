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

    assert tool_count == 161
    assert next_cursor is None
