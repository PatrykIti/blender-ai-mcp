"""Tests for the MCP context, session, and execution bridge."""

from __future__ import annotations

from dataclasses import dataclass, field

from server.adapters.mcp.context_utils import (
    ctx_error,
    ctx_info,
    ctx_progress,
    ctx_warning,
    get_session_phase,
    get_session_value,
    set_session_phase,
    set_session_value,
)
from server.adapters.mcp.execution_context import MCPExecutionContext
from server.adapters.mcp.execution_report import ExecutionStep, MCPExecutionReport
from server.adapters.mcp.router_helper import route_tool_call_report


@dataclass
class FakeContext:
    """Minimal sync Context stand-in for unit tests."""

    state: dict[str, object] = field(default_factory=dict)
    messages: list[tuple[str, str]] = field(default_factory=list)
    progress_events: list[tuple[float, float | None, str | None]] = field(default_factory=list)

    def get_state(self, key: str):
        return self.state.get(key)

    def set_state(self, key: str, value, *, serializable: bool = True) -> None:
        self.state[key] = value

    def info(self, message: str, logger_name=None, extra=None) -> None:
        self.messages.append(("info", message))

    def warning(self, message: str, logger_name=None, extra=None) -> None:
        self.messages.append(("warning", message))

    def error(self, message: str, logger_name=None, extra=None) -> None:
        self.messages.append(("error", message))

    def report_progress(self, progress: float, total: float | None = None, message: str | None = None) -> None:
        self.progress_events.append((progress, total, message))


def test_session_helpers_round_trip_phase_and_values():
    """Session helpers should read and write sync Context state consistently."""

    ctx = FakeContext()

    assert get_session_phase(ctx) == "bootstrap"
    assert get_session_value(ctx, "missing", "fallback") == "fallback"

    set_session_phase(ctx, "planning")
    set_session_value(ctx, "surface_profile", "llm-guided")

    assert get_session_phase(ctx) == "planning"
    assert get_session_value(ctx, "surface_profile") == "llm-guided"


def test_context_logging_and_progress_helpers_are_best_effort():
    """Context helpers should write sync notifications and progress without throwing."""

    ctx = FakeContext()

    ctx_info(ctx, "hello")
    ctx_warning(ctx, "warn")
    ctx_error(ctx, "oops")
    ctx_progress(ctx, 1, 4, "step")

    assert ctx.messages == [("info", "hello"), ("warning", "warn"), ("error", "oops")]
    assert ctx.progress_events == [(1, 4, "step")]


def test_execution_report_renders_legacy_text_for_multi_step_sequence():
    """Structured reports should still support the current string-based adapter contract."""

    report = MCPExecutionReport(
        context=MCPExecutionContext(tool_name="mesh_extrude_region", params={"move": [0, 0, 1]}),
        router_enabled=True,
        router_applied=True,
        router_disposition="corrected",
        steps=(
            ExecutionStep(tool_name="scene_set_mode", params={"mode": "EDIT"}, result="OK"),
            ExecutionStep(tool_name="mesh_extrude_region", params={"move": [0, 0, 1]}, result="Extruded"),
        ),
    )

    assert report.to_dict()["context"]["tool_name"] == "mesh_extrude_region"
    assert report.to_legacy_text() == "[Step 1: scene_set_mode] OK\n[Step 2: mesh_extrude_region] Extruded"


def test_route_tool_call_report_returns_direct_execution_when_router_disabled(monkeypatch):
    """route_tool_call_report should still build a structured report on direct execution."""

    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)

    report = route_tool_call_report(
        tool_name="scene_list_objects",
        params={},
        direct_executor=lambda: "['Cube']",
    )

    assert report.router_enabled is False
    assert report.router_applied is False
    assert report.router_disposition == "bypassed"
    assert report.steps[0].tool_name == "scene_list_objects"
    assert report.to_legacy_text() == "['Cube']"
