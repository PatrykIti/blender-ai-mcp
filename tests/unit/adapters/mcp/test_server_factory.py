"""Tests for the FastMCP server factory composition root."""

from __future__ import annotations

from pathlib import Path

from fastmcp import FastMCP
from server.adapters.mcp.factory import build_server
from server.adapters.mcp.platform.capability_manifest import get_capability_manifest
from server.adapters.mcp.surfaces import SURFACE_PROFILES, get_surface_profile


def test_get_surface_profile_returns_expected_profiles():
    """Surface lookup should expose the baseline profile matrix."""

    assert set(SURFACE_PROFILES) == {
        "legacy-flat",
        "llm-guided",
        "internal-debug",
        "code-mode-pilot",
    }


def test_build_server_builds_default_surface():
    """Factory should build the default legacy-flat server surface."""

    server = build_server()

    assert isinstance(server, FastMCP)
    assert server._bam_surface_profile == "legacy-flat"
    assert server._bam_capability_manifest == get_capability_manifest()
    assert len(server.providers) >= 4
    assert server._bam_task_runtime_report.tasks_required is False


def test_build_server_builds_alternate_surface_profile():
    """Factory should build multiple surface profiles from reusable provider groups."""

    guided = build_server("llm-guided")
    debug = build_server("internal-debug")
    code_mode = build_server("code-mode-pilot")

    assert guided._bam_surface_profile == "llm-guided"
    assert debug._bam_surface_profile == "internal-debug"
    assert code_mode._bam_surface_profile == "code-mode-pilot"
    assert guided.name == get_surface_profile("llm-guided").server_name
    assert debug.name == get_surface_profile("internal-debug").server_name
    assert code_mode.name == get_surface_profile("code-mode-pilot").server_name
    assert len(debug.providers) > len(guided.providers)
    assert guided._bam_task_runtime_report.tasks_required is True
    assert guided._bam_task_runtime_report.supported is True
    assert code_mode._bam_code_mode_enabled is True
    assert code_mode._bam_code_mode_benchmark_baselines == (
        "legacy-flat",
        "llm-guided",
        "code-mode-pilot",
    )


def test_factory_bootstrap_no_longer_imports_areas_side_effect_registry():
    """Server bootstrap should use the factory path instead of importing all areas for side effects."""

    server_source = Path("server/adapters/mcp/server.py").read_text(encoding="utf-8")

    assert "import server.adapters.mcp.areas" not in server_source
    assert "from server.adapters.mcp.instance import mcp" not in server_source


def test_build_server_can_use_explicit_contract_line_override():
    """Factory should surface the selected contract line explicitly for versioned surfaces."""

    server = build_server("llm-guided", contract_line="llm-guided-v1")

    assert server._bam_contract_line == "llm-guided-v1"


def test_build_server_fails_clearly_when_task_runtime_pair_is_unsupported(monkeypatch):
    """Task-capable surfaces should fail fast on an unsupported FastMCP+Docket pair."""

    monkeypatch.setattr(
        "server.adapters.mcp.factory.validate_task_runtime_or_raise",
        lambda tasks_required: (_ for _ in ()).throw(
            RuntimeError(
                "Unsupported task runtime for FastMCP task-capable surfaces. "
                "Resolved pair: fastmcp=3.1.1, pydocket=0.16.1. "
                "Supported pair: fastmcp>=3.1.1,<3.2.0 + pydocket>=0.18.2,<0.19.0. "
                "Reason: pydocket 0.16.1 is outside supported range >=0.18.2,<0.19.0"
            )
        ),
    )

    try:
        build_server("llm-guided")
    except RuntimeError as exc:
        assert "Unsupported task runtime" in str(exc)
        assert "pydocket=0.16.1" in str(exc)
    else:
        raise AssertionError("Expected unsupported task runtime to fail fast")
