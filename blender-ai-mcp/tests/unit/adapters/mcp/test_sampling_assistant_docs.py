"""Docs coverage for TASK-092 server-side sampling assistants."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]


def test_readme_documents_sampling_assistant_baseline():
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    for expected in (
        "Server-Side Sampling Assistants Baseline",
        "assistant_summary",
        "repair_suggestion",
        "scene_snapshot_state",
        "workflow_catalog",
        "masked_error",
        "rejected_by_policy",
    ):
        assert expected in text


def test_mcp_docs_describe_current_assistant_enabled_paths():
    text = (REPO_ROOT / "_docs" / "_MCP_SERVER" / "README.md").read_text(encoding="utf-8")

    for expected in (
        "Server-Side Sampling Assistants Baseline",
        "scene_inspect(..., assistant_summary=True)",
        "mesh_inspect(..., assistant_summary=True)",
        "scene_snapshot_state(..., assistant_summary=True)",
        "scene_get_hierarchy(..., assistant_summary=True)",
        "router_set_goal()",
        "router_get_status()",
        "workflow_catalog()",
    ):
        assert expected in text


def test_responsibility_boundaries_define_sampling_guardrails():
    text = (REPO_ROOT / "_docs" / "_ROUTER" / "RESPONSIBILITY_BOUNDARIES.md").read_text(encoding="utf-8")

    for expected in (
        "Sampling Assistant Guardrails",
        "autonomous geometry-destructive planning",
        "scene-truth decisions without inspection contracts",
        "detached background reasoning outside an active MCP request",
    ):
        assert expected in text
