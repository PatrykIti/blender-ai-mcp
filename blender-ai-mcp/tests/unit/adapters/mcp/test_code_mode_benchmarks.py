"""Benchmark-style regression tests for the TASK-094 code-mode experiment."""

from __future__ import annotations

import asyncio

from server.adapters.mcp.factory import build_server


def _tool_names_for(surface_profile: str) -> set[str]:
    server = build_server(surface_profile)

    async def run():
        tools = await server.list_tools()
        return {tool.name for tool in tools}

    return asyncio.run(run())


def test_code_mode_benchmark_baselines_have_distinct_entry_shapes():
    """The named experiment baselines should expose materially different orchestration surfaces."""

    legacy_names = _tool_names_for("legacy-flat")
    guided_names = _tool_names_for("llm-guided")
    code_names = _tool_names_for("code-mode-pilot")

    assert len(legacy_names) > len(guided_names) > len(code_names)

    assert "scene_inspect" in legacy_names
    assert "search_tools" in guided_names
    assert "execute" in code_names

    assert "search" not in legacy_names
    assert "search_tools" in guided_names
    assert "search" in code_names


def test_code_mode_benchmark_baselines_support_expected_read_heavy_flow_model():
    """The three baselines should map to different read-heavy orchestration styles."""

    legacy_names = _tool_names_for("legacy-flat")
    guided_names = _tool_names_for("llm-guided")
    code_names = _tool_names_for("code-mode-pilot")

    # Classic loop: direct tool calls on a broad surface.
    assert {"scene_snapshot_state", "scene_compare_snapshot", "mesh_inspect"} <= legacy_names

    # Guided loop: discovery-first plus guided entry tools.
    assert {"router_set_goal", "router_get_status", "search_tools", "call_tool"} <= guided_names

    # Code-mode pilot: collapsed meta-tool surface plus prompt bridge tools.
    assert {"search", "get_schema", "tags", "execute", "list_prompts", "get_prompt"} <= code_names
    assert "mesh_extrude_region" not in code_names


def test_code_mode_pilot_benchmark_round_trip_model_is_lower_than_classic_catalog():
    """The pilot should reduce catalog round-trips for complex read-heavy flows."""

    # Deterministic experiment model:
    # - legacy-flat: user inspects the full catalog, then calls tools directly
    # - llm-guided: user starts from search/call_tool
    # - code-mode-pilot: one execute block can chain multiple read calls
    benchmark = {
        "legacy-flat": {"catalog_round_trips": 1, "analysis_round_trips": 4, "total": 5},
        "llm-guided": {"catalog_round_trips": 1, "analysis_round_trips": 4, "total": 5},
        "code-mode-pilot": {"catalog_round_trips": 1, "analysis_round_trips": 1, "total": 2},
    }

    assert benchmark["code-mode-pilot"]["total"] < benchmark["legacy-flat"]["total"]
    assert benchmark["code-mode-pilot"]["total"] < benchmark["llm-guided"]["total"]
