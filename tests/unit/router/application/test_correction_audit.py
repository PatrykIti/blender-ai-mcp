"""Tests for correction audit event model and execution report wiring."""

from server.adapters.mcp.contracts.correction_audit import CorrectionAuditEventContract
from server.adapters.mcp.execution_context import MCPExecutionContext
from server.adapters.mcp.execution_report import ExecutionStep, MCPExecutionReport
from server.adapters.mcp.router_helper import (
    _apply_postcondition_verification,
    _build_correction_audit_events,
)


def test_correction_audit_event_separates_intent_execution_and_verification():
    """Audit events should keep intent, execution, and verification as distinct fields."""

    events = _build_correction_audit_events(
        original_tool_name="mesh_extrude_region",
        original_params={"move": [0, 0, 1]},
        corrected_tools=[
            {"tool": "mesh_inset", "params": {"thickness": 0.03}},
            {"tool": "mesh_extrude_region", "params": {"move": [0, 0, -0.02]}},
        ],
        steps=[
            ExecutionStep(tool_name="mesh_inset", params={"thickness": 0.03}, result="Inset"),
            ExecutionStep(tool_name="mesh_extrude_region", params={"move": [0, 0, -0.02]}, result="Extruded"),
        ],
        policy_context={"decision": "ask", "reason": "medium confidence"},
    )

    assert len(events) == 2
    assert isinstance(events[0], CorrectionAuditEventContract)
    assert events[0].intent.original_tool_name == "mesh_extrude_region"
    assert events[0].execution.tool_name == "mesh_inset"
    assert events[0].verification.status == "not_run"


def test_execution_report_can_carry_audit_events():
    """Execution reports should carry structured audit events without losing legacy compatibility."""

    event = _build_correction_audit_events(
        original_tool_name="mesh_bevel",
        original_params={"offset": 100.0},
        corrected_tools=[{"tool": "mesh_bevel", "params": {"offset": 1.0}}],
        steps=[ExecutionStep(tool_name="mesh_bevel", params={"offset": 1.0}, result="Bevel")],
    )[0]

    report = MCPExecutionReport(
        context=MCPExecutionContext(tool_name="mesh_bevel", params={"offset": 100.0}),
        router_enabled=True,
        router_applied=True,
        router_disposition="corrected",
        steps=(ExecutionStep(tool_name="mesh_bevel", params={"offset": 1.0}, result="Bevel"),),
        audit_events=(event,),
    )

    assert report.audit_events[0].intent.category == "parameter_rewrite"
    assert report.to_legacy_text() == "Bevel"
    assert report.verification_status == "not_requested"


def test_postcondition_verification_passes_for_mode_correction(monkeypatch):
    """High-risk mode corrections should verify against scene truth."""

    events = _build_correction_audit_events(
        original_tool_name="mesh_extrude_region",
        original_params={"move": [0, 0, 1]},
        corrected_tools=[
            {"tool": "system_set_mode", "params": {"mode": "EDIT"}},
            {"tool": "mesh_extrude_region", "params": {"move": [0, 0, 1]}},
        ],
        steps=[
            ExecutionStep(tool_name="system_set_mode", params={"mode": "EDIT"}, result="OK"),
            ExecutionStep(tool_name="mesh_extrude_region", params={"move": [0, 0, 1]}, result="Extruded"),
        ],
    )

    monkeypatch.setattr(
        "server.adapters.mcp.router_helper.get_scene_handler",
        lambda: type("Handler", (), {"get_mode": lambda self: {"mode": "EDIT"}})(),
    )

    verified_events, status = _apply_postcondition_verification(events)

    assert status == "passed"
    assert verified_events[0].verification.status == "passed"


def test_postcondition_verification_fails_for_empty_selection(monkeypatch):
    """Selection injection should fail verification when no selection remains."""

    events = _build_correction_audit_events(
        original_tool_name="mesh_extrude_region",
        original_params={"move": [0, 0, 1]},
        corrected_tools=[
            {"tool": "mesh_select", "params": {"action": "all"}},
            {"tool": "mesh_extrude_region", "params": {"move": [0, 0, 1]}},
        ],
        steps=[
            ExecutionStep(tool_name="mesh_select", params={"action": "all"}, result="Selected"),
            ExecutionStep(tool_name="mesh_extrude_region", params={"move": [0, 0, 1]}, result="Extruded"),
        ],
    )

    monkeypatch.setattr(
        "server.adapters.mcp.router_helper.get_scene_handler",
        lambda: type("Handler", (), {"list_selection": lambda self: {"selection_count": 0}})(),
    )

    verified_events, status = _apply_postcondition_verification(events)

    assert status == "failed"
    assert verified_events[0].verification.status == "failed"
