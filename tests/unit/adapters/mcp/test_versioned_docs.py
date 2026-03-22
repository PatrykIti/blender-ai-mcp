"""Docs coverage for TASK-091 versioned client surface baseline."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]


def test_readme_documents_versioned_surface_baseline():
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    for expected in (
        "Versioned Surface Baseline",
        "legacy-v1",
        "llm-guided-v2",
        "llm-guided-v1",
        "workflow_catalog",
    ):
        assert expected in text


def test_mcp_docs_describe_surface_profile_to_contract_line_matrix():
    text = (REPO_ROOT / "_docs" / "_MCP_SERVER" / "README.md").read_text(encoding="utf-8")

    for expected in (
        "Versioned Client Surface Baseline",
        "Surface Profile",
        "Default Contract Line",
        "MCP_DEFAULT_CONTRACT_LINE",
        "llm-guided-v1",
        "llm-guided-v2",
    ):
        assert expected in text
