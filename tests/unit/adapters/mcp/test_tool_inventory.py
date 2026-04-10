"""Tests for TASK-084 discovery inventory normalization."""

from __future__ import annotations

from server.adapters.mcp.discovery import (
    build_discovery_entry_map,
    build_discovery_inventory,
    get_pinned_public_tools,
)


def test_discovery_inventory_represents_each_public_tool_once():
    """Each llm-guided public tool should appear exactly once in discovery inventory."""

    inventory = build_discovery_inventory()

    public_names = [entry.public_name for entry in inventory]
    assert len(public_names) == len(set(public_names))
    assert "check_scene" in public_names
    assert "inspect_scene" in public_names
    assert "configure_scene" in public_names
    assert "browse_workflows" in public_names
    assert "reference_images" in public_names
    assert "reference_compare_checkpoint" in public_names
    assert "reference_compare_current_view" in public_names
    assert "reference_compare_stage_checkpoint" in public_names
    assert "reference_iterate_stage_checkpoint" in public_names
    assert "scene_scope_graph" in public_names
    assert "scene_relation_graph" in public_names
    assert "scene_view_diagnostics" in public_names


def test_discovery_inventory_tracks_aliases_and_pinned_defaults():
    """Pinned defaults and canonical aliases should come from the platform-owned manifest."""

    entry_map = build_discovery_entry_map()

    assert entry_map["check_scene"].internal_name == "scene_context"
    assert "scene_context" in entry_map["check_scene"].aliases

    assert entry_map["inspect_scene"].internal_name == "scene_inspect"
    assert "scene_inspect" in entry_map["inspect_scene"].aliases

    assert entry_map["configure_scene"].internal_name == "scene_configure"
    assert "scene_configure" in entry_map["configure_scene"].aliases

    assert entry_map["browse_workflows"].pinned is True
    assert entry_map["reference_images"].pinned is True
    assert entry_map["router_set_goal"].pinned is True
    assert entry_map["router_get_status"].pinned is True
    assert "phase:planning" in entry_map["check_scene"].phase_hints
    assert "phase:build" in entry_map["check_scene"].phase_hints
    assert entry_map["browse_workflows"].phase_hints == ("phase:planning",)


def test_discovery_inventory_metadata_enrichment_covers_extended_router_areas():
    """Metadata loader enrichment should include areas added during TASK-084 normalization."""

    inventory = build_discovery_inventory()
    by_internal = {entry.internal_name: entry for entry in inventory}

    assert by_internal["armature_create"].metadata is not None
    assert by_internal["text_create"].metadata is not None
    assert by_internal["extraction_render_angles"].metadata is not None


def test_pinned_public_tools_are_resolved_on_public_surface_names():
    """Pinned discovery tools should use the current public names for the shaped surface."""

    pinned = get_pinned_public_tools()

    assert pinned == (
        "scene_scope_graph",
        "scene_relation_graph",
        "scene_view_diagnostics",
        "reference_images",
        "router_set_goal",
        "router_get_status",
        "browse_workflows",
    )
