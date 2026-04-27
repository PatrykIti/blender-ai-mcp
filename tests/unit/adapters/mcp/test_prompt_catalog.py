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
        "reference_guided_creature_build",
        "recommended_prompts",
    }

    entry = get_prompt_catalog_entry("workflow_router_first")
    assert entry.operating_mode == "router-first"
    assert entry.source_path is not None

    creature_entry = get_prompt_catalog_entry("reference_guided_creature_build")
    assert creature_entry.goal_tags == ("goal:creature",)
    assert creature_entry.profile_tags == ("profile:llm-guided",)


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


def test_recommended_prompt_entries_can_use_active_goal_context():
    """Creature-oriented goals should surface the creature prompt under the same phase/profile."""

    creature_planning = [
        entry.name
        for entry in get_recommended_prompt_entries(
            surface_profile="llm-guided",
            phase="planning",
            goal="create a low-poly creature matching front and side reference images",
        )
    ]
    generic_planning = [
        entry.name
        for entry in get_recommended_prompt_entries(
            surface_profile="llm-guided",
            phase="planning",
            goal="build a generic hard-surface housing",
        )
    ]

    assert creature_planning[0] == "reference_guided_creature_build"
    assert "reference_guided_creature_build" in creature_planning
    assert "reference_guided_creature_build" not in generic_planning
