"""Docs coverage for TASK-094 code-mode pilot baseline."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]


def test_mcp_docs_describe_code_mode_pilot_baseline():
    text = (REPO_ROOT / "_docs" / "_MCP_SERVER" / "README.md").read_text(encoding="utf-8")

    for expected in (
        "Code Mode Pilot Baseline",
        "`code-mode-pilot`",
        "`search`",
        "`get_schema`",
        "`execute`",
        "`legacy-flat`",
        "`llm-guided`",
        "`code-mode-pilot`",
    ):
        assert expected in text


def test_task_board_marks_task_094_in_progress():
    text = (REPO_ROOT / "_docs" / "_TASKS" / "README.md").read_text(encoding="utf-8")

    assert "Code Mode Exploration for Large-Scale Orchestration" in text
    assert "Guardrails and read-only pilot are implemented" in text
