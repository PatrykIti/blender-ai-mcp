"""Tests for explicit FastMCP+Docket runtime policy."""

from __future__ import annotations

from server.adapters.mcp.tasks.runtime_policy import (
    SUPPORTED_FASTMCP_SPEC,
    SUPPORTED_PYDOCKET_SPEC,
    TaskRuntimeReport,
    get_task_runtime_report,
    validate_task_runtime_or_raise,
)


def test_supported_runtime_specs_are_explicit():
    """Task runtime support should be defined by one explicit FastMCP+Docket pair."""

    assert str(SUPPORTED_FASTMCP_SPEC) == "<3.2.0,>=3.1.1"
    assert str(SUPPORTED_PYDOCKET_SPEC) == "<0.19.0,>=0.18.2"


def test_current_environment_matches_supported_task_runtime_pair():
    """Current environment should satisfy the supported task-runtime pair."""

    report = get_task_runtime_report(tasks_required=True)

    assert report.supported is True
    assert report.reason is None
    assert report.supported_pair_label == "fastmcp<3.2.0,>=3.1.1 + pydocket<0.19.0,>=0.18.2"


def test_validate_task_runtime_or_raise_reports_clear_error_for_unsupported_pair(monkeypatch):
    """Unsupported pairs should fail with a clear pair-specific error."""

    monkeypatch.setattr(
        "server.adapters.mcp.tasks.runtime_policy.get_task_runtime_report",
        lambda tasks_required: TaskRuntimeReport(
            fastmcp_version="3.1.1",
            pydocket_version="0.16.1",
            tasks_required=tasks_required,
            supported=False,
            reason="pydocket 0.16.1 is outside supported range <0.19.0,>=0.18.2",
        ),
    )

    try:
        validate_task_runtime_or_raise(tasks_required=True)
    except RuntimeError as exc:
        text = str(exc)
        assert "Unsupported task runtime" in text
        assert "fastmcp=3.1.1" in text
        assert "pydocket=0.16.1" in text
    else:
        raise AssertionError("Expected unsupported task runtime to fail")
