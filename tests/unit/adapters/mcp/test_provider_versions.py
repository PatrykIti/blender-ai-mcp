"""Tests for versioned shared provider components."""

from __future__ import annotations

import asyncio

from server.adapters.mcp.providers import build_core_tools_provider, build_workflow_tools_provider


def test_core_provider_exposes_both_versions_for_versioned_scene_components():
    provider = build_core_tools_provider()

    async def run():
        tools = await provider.list_tools()
        return sorted((tool.name, tool.version) for tool in tools if tool.name in {"scene_context", "scene_inspect"})

    versions = asyncio.run(run())

    assert versions == [
        ("scene_context", "1"),
        ("scene_context", "2"),
        ("scene_inspect", "1"),
        ("scene_inspect", "2"),
    ]


def test_workflow_provider_exposes_both_versions_for_versioned_workflow_catalog():
    provider = build_workflow_tools_provider()

    async def run():
        tools = await provider.list_tools()
        return sorted((tool.name, tool.version) for tool in tools if tool.name == "workflow_catalog")

    versions = asyncio.run(run())

    assert versions == [
        ("workflow_catalog", "1"),
        ("workflow_catalog", "2"),
    ]
