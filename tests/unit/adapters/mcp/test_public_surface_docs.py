"""Docs/tests coverage for the current llm-guided public surface baseline."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]


def test_readme_documents_llm_guided_public_aliases():
    """User-facing README should describe the current llm-guided public line."""

    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    for expected in (
        "LLM-Guided Public Surface",
        "check_scene",
        "inspect_scene",
        "browse_workflows",
        "target_object",
        "search_query",
    ):
        assert expected in text


def test_mcp_docs_describe_aliases_and_hidden_arguments():
    """MCP server docs should explain public aliases and current hidden args."""

    text = (REPO_ROOT / "_docs" / "_MCP_SERVER" / "README.md").read_text(encoding="utf-8")

    for expected in (
        "LLM-Guided Public Surface Baseline",
        "check_scene",
        "inspect_scene",
        "browse_workflows",
        "Current hidden/expert-only arguments on `llm-guided` include:",
        "`inspect_scene`",
        "`mesh_inspect`",
        "`browse_workflows`",
    ):
        assert expected in text


def test_tools_summary_describes_llm_guided_alias_layer():
    """Available tools summary should include the alias layer, not only canonical names."""

    text = (REPO_ROOT / "_docs" / "AVAILABLE_TOOLS_SUMMARY.md").read_text(encoding="utf-8")

    for expected in (
        "LLM-Guided Public Aliases",
        "check_scene",
        "inspect_scene",
        "browse_workflows",
    ):
        assert expected in text


def test_prompt_templates_use_llm_guided_aliases_for_public_surface_examples():
    """Prompt docs should prefer current llm-guided aliases for user-facing examples."""

    prompt_readme = (REPO_ROOT / "_docs" / "_PROMPTS" / "README.md").read_text(encoding="utf-8")
    workflow_prompt = (REPO_ROOT / "_docs" / "_PROMPTS" / "WORKFLOW_ROUTER_FIRST.md").read_text(
        encoding="utf-8"
    )
    manual_prompt = (REPO_ROOT / "_docs" / "_PROMPTS" / "MANUAL_TOOLS_NO_ROUTER.md").read_text(
        encoding="utf-8"
    )

    assert "check_scene" in prompt_readme
    assert "inspect_scene" in prompt_readme
    assert "browse_workflows" in prompt_readme

    assert 'browse_workflows(action="search", search_query="<user prompt>")' in workflow_prompt
    assert 'browse_workflows(action="get", name="<workflow_name>")' in workflow_prompt
    assert 'inspect_scene(action="object", target_object=...)' in workflow_prompt

    assert 'check_scene(query="mode")' in manual_prompt
    assert 'check_scene(query="selection")' in manual_prompt
    assert 'inspect_scene(action="object", target_object=...)' in manual_prompt
