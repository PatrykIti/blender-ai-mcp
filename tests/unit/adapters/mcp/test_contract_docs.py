"""Docs coverage for TASK-089 structured contract baseline."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]


def test_readme_documents_structured_contract_baseline():
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    for expected in (
        "Structured Contract Baseline",
        "scene_create",
        "scene_configure",
        "mesh_select",
        "mesh_select_targeted",
        "scene_snapshot_state",
        "scene_compare_snapshot",
        "mesh_inspect",
        "workflow_catalog",
    ):
        assert expected in text


def test_mcp_docs_list_contract_enabled_surfaces():
    text = (REPO_ROOT / "_docs" / "_MCP_SERVER" / "README.md").read_text(encoding="utf-8")

    for expected in (
        "Structured Contract Baseline",
        "scene_create",
        "scene_configure",
        "mesh_select",
        "mesh_select_targeted",
        "scene_get_custom_properties",
        "scene_get_hierarchy",
        "scene_get_bounding_box",
        "scene_get_origin_info",
        "scene_measure_distance",
        "scene_measure_dimensions",
        "scene_assert_contact",
        "scene_assert_dimensions",
        "scene_assert_containment",
        "router_get_status",
    ):
        assert expected in text


def test_tools_summary_mentions_structured_contract_surfaces():
    text = (REPO_ROOT / "_docs" / "AVAILABLE_TOOLS_SUMMARY.md").read_text(encoding="utf-8")

    for expected in (
        "Structured Contract Surfaces",
        "scene_create",
        "scene_configure",
        "scene_context",
        "mesh_select",
        "mesh_select_targeted",
        "scene_measure_distance",
        "scene_measure_gap",
        "scene_assert_contact",
        "scene_assert_proportion",
        "mesh_inspect",
        "workflow_catalog",
    ):
        assert expected in text
