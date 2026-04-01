"""Docs coverage for TASK-087 structured elicitation baseline."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]


def test_readme_documents_structured_clarification_flow():
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    for expected in (
        "Structured Clarification Flow",
        "Model-first clarification",
        "Typed fallback payloads",
        "partial answers",
        "workflow_catalog",
    ):
        assert expected in text


def test_mcp_docs_describe_native_and_fallback_elicitation_modes():
    text = (REPO_ROOT / "_docs" / "_MCP_SERVER" / "README.md").read_text(encoding="utf-8")

    for expected in (
        "Structured Elicitation Baseline",
        "router_set_goal",
        "typed `needs_input` fallback payload",
        "model-facing by default",
        "question_set_id",
        "workflow_catalog",
    ):
        assert expected in text


def test_prompt_docs_mention_structured_elicitation_behavior():
    prompt_readme = (REPO_ROOT / "_docs" / "_PROMPTS" / "README.md").read_text(encoding="utf-8")
    workflow_prompt = (REPO_ROOT / "_docs" / "_PROMPTS" / "WORKFLOW_ROUTER_FIRST.md").read_text(encoding="utf-8")

    assert "typed clarification payload as model-facing by default" in workflow_prompt
    assert "typed `needs_input` fallback payload" in prompt_readme
