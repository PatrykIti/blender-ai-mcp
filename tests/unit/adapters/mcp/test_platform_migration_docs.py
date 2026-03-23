"""Docs coverage for the closed TASK-083 FastMCP platform baseline."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]


def test_clean_architecture_doc_describes_factory_provider_runtime():
    text = (REPO_ROOT / "_docs" / "_MCP_SERVER" / "clean_architecture.md").read_text(encoding="utf-8")

    for expected in (
        "`factory.py`",
        "`surfaces.py`",
        "`providers/`",
        "build_server(surface_profile=...)",
        "provider/transform based",
    ):
        assert expected in text

    assert "shared `FastMCP` application instance" not in text


def test_composition_and_migration_docs_describe_no_shim_baseline():
    composition = (REPO_ROOT / "_docs" / "_MCP_SERVER" / "fastmcp_3x_composition.md").read_text(
        encoding="utf-8"
    )
    matrix = (REPO_ROOT / "_docs" / "_MCP_SERVER" / "fastmcp_3x_migration_matrix.md").read_text(
        encoding="utf-8"
    )

    assert "decorator shim has been removed" in composition
    assert "Decorator shim removal | Completed" in matrix


def test_task_board_marks_task_083_done():
    text = (REPO_ROOT / "_docs" / "_TASKS" / "README.md").read_text(encoding="utf-8")

    assert "FastMCP 3.x Platform Migration" in text
    assert "| [TASK-083](./TASK-083_FastMCP_3x_Platform_Migration.md) | **FastMCP 3.x Platform Migration** | 🔴 High | 2026-03-23 |" in text
