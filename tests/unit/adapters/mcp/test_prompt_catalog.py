"""Tests for TASK-090 prompt catalog and recommendations."""

from server.adapters.mcp.prompts.prompt_catalog import (
    get_prompt_catalog,
    get_prompt_catalog_entry,
    get_recommended_prompt_entries,
)


def test_prompt_catalog_exposes_curated_prompt_assets():
    """Prompt catalog should expose the curated prompt products from _docs/_PROMPTS."""

    names = {entry.name for entry in get_prompt_catalog()}

    assert names == {
        "getting_started",
        "guided_session_start",
        "workflow_router_first",
        "manual_tools_no_router",
        "demo_low_poly_medieval_well",
        "demo_generic_modeling",
        "recommended_prompts",
    }

    entry = get_prompt_catalog_entry("workflow_router_first")
    assert entry.operating_mode == "router-first"
    assert entry.source_path is not None


def test_recommended_prompt_entries_change_by_profile_and_phase():
    """Recommendations should react to phase/profile instead of staying flat."""

    planning = {entry.name for entry in get_recommended_prompt_entries(surface_profile="llm-guided", phase="planning")}
    inspect_validate = {
        entry.name for entry in get_recommended_prompt_entries(surface_profile="llm-guided", phase="inspect_validate")
    }

    assert "workflow_router_first" in planning
    assert "guided_session_start" in planning
    assert "manual_tools_no_router" not in planning
    assert "manual_tools_no_router" in inspect_validate
