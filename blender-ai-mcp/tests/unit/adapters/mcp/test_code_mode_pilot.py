"""Tests for the experimental read-only code-mode pilot surface."""

from __future__ import annotations

import asyncio
from dataclasses import replace

import pytest
from fastmcp.server.providers import LocalProvider
from server.adapters.mcp.factory import build_server
from server.adapters.mcp.settings import SurfaceProfileSettings
from server.adapters.mcp.surfaces import SURFACE_PROFILES, get_surface_profile


def _build_test_provider() -> LocalProvider:
    provider = LocalProvider()

    @provider.tool(name="scene_snapshot_state")
    def scene_snapshot_state(assistant_summary: bool = False):
        return {"snapshot": {"object_count": 1}, "hash": "abc123"}

    @provider.tool(name="mesh_extrude_region")
    def mesh_extrude_region(move=None):
        return "Extruded"

    return provider


def _unwrap_structured(result):
    structured = getattr(result, "structured_content", None)
    if structured is None:
        return None
    if isinstance(structured, dict) and "result" in structured:
        return structured["result"]
    return structured


def _code_mode_test_surface() -> SurfaceProfileSettings:
    surface = get_surface_profile("code-mode-pilot")
    return replace(
        surface,
        server_name="code-mode-test",
        provider_builders=(_build_test_provider,),
        tasks_enabled=False,
        code_mode_allowed_tools=("scene_snapshot_state",),
    )


def test_code_mode_pilot_lists_only_meta_tools(monkeypatch):
    """The pilot surface should collapse visible tools into discovery + execute meta-tools."""

    monkeypatch.setitem(SURFACE_PROFILES, "code-mode-pilot", _code_mode_test_surface())
    server = build_server("code-mode-pilot")

    async def run():
        tools = await server.list_tools()
        return {tool.name for tool in tools}

    names = asyncio.run(run())

    assert names == {"search", "get_schema", "tags", "execute", "list_prompts", "get_prompt"}


def test_code_mode_pilot_execute_can_call_allowed_read_only_tool(monkeypatch):
    """The pilot execute tool should be able to orchestrate visible read-only tools."""

    monkeypatch.setitem(SURFACE_PROFILES, "code-mode-pilot", _code_mode_test_surface())
    server = build_server("code-mode-pilot")

    async def run():
        return await server.call_tool(
            "execute",
            {"code": "return await call_tool('scene_snapshot_state', {})"},
        )

    result = asyncio.run(run())
    payload = _unwrap_structured(result)

    assert payload["snapshot"]["object_count"] == 1
    assert payload["hash"] == "abc123"


def test_code_mode_pilot_execute_blocks_non_visible_write_tools(monkeypatch):
    """The pilot execute tool should not reach tools outside the read-only allowlist."""

    monkeypatch.setitem(SURFACE_PROFILES, "code-mode-pilot", _code_mode_test_surface())
    server = build_server("code-mode-pilot")

    async def run():
        return await server.call_tool(
            "execute",
            {"code": "return await call_tool('mesh_extrude_region', {'move': [0, 0, 1]})"},
        )

    with pytest.raises(Exception, match="Unknown tool: mesh_extrude_region"):
        asyncio.run(run())


def test_code_mode_pilot_fails_fast_when_sandbox_dependency_is_missing(monkeypatch):
    """The pilot should fail clearly at build time if the sandbox dependency is unavailable."""

    monkeypatch.setitem(SURFACE_PROFILES, "code-mode-pilot", _code_mode_test_surface())

    def _fake_import(name: str):
        if name == "pydantic_monty":
            raise ModuleNotFoundError("missing")
        raise AssertionError(f"Unexpected import: {name}")

    monkeypatch.setattr("server.adapters.mcp.transforms.discovery.importlib.import_module", _fake_import)

    with pytest.raises(RuntimeError, match="requires pydantic-monty"):
        build_server("code-mode-pilot")
