"""Docs coverage for the TASK-094 decision memo and recommendation."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]


def test_task_094_docs_record_named_benchmark_baselines():
    text = (REPO_ROOT / "_docs" / "_TASKS" / "TASK-094_Code_Mode_Exploration.md").read_text(encoding="utf-8")

    for expected in (
        "`legacy-flat`",
        "`llm-guided`",
        "`code-mode-pilot`",
    ):
        assert expected in text


def test_readme_and_mcp_docs_capture_go_decision_for_read_only_pilot():
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    mcp_docs = (REPO_ROOT / "_docs" / "_MCP_SERVER" / "README.md").read_text(encoding="utf-8")

    assert "Code Mode Decision" in readme
    assert "Go decision: keep `code-mode-pilot` as an experimental read-only surface" in readme
    assert "Code Mode Pilot Baseline" in mcp_docs
    assert "read-only allowlist" in mcp_docs
