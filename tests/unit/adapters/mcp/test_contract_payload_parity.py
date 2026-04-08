"""Representative parity checks for structured MCP contract payloads."""

from __future__ import annotations

import pytest
from server.adapters.mcp.contracts.correction_audit import CorrectionAuditEventContract
from server.adapters.mcp.contracts.mesh import MeshInspectResponseContract
from server.adapters.mcp.contracts.router import RouterGoalResponseContract, RouterStatusContract
from server.adapters.mcp.contracts.scene import SceneContextResponseContract, SceneInspectResponseContract
from server.adapters.mcp.contracts.workflow_catalog import WorkflowCatalogResponseContract


@pytest.mark.parametrize(
    ("contract_cls", "payload", "field_name", "expected"),
    [
        (
            SceneContextResponseContract,
            {
                "action": "mode",
                "payload": {
                    "mode": "OBJECT",
                    "active_object": "Cube",
                    "active_object_type": "MESH",
                    "selected_object_names": ["Cube"],
                    "selection_count": 1,
                },
            },
            "payload.active_object",
            "Cube",
        ),
        (
            SceneInspectResponseContract,
            {
                "action": "object",
                "payload": {
                    "object_name": "Cube",
                    "type": "MESH",
                    "location": [0.0, 0.0, 0.0],
                },
            },
            "payload.object_name",
            "Cube",
        ),
        (
            MeshInspectResponseContract,
            {
                "action": "vertices",
                "object_name": "Cube",
                "total": 8,
                "returned": 2,
                "offset": 0,
                "limit": 2,
                "has_more": True,
                "items": [{"index": 0}, {"index": 1}],
                "metadata": {"selected_count": 2},
            },
            "metadata.selected_count",
            2,
        ),
        (
            RouterGoalResponseContract,
            {
                "status": "ready",
                "session_id": "sess-1",
                "transport": "stdio",
                "continuation_mode": "workflow",
                "workflow": "chair_workflow",
                "resolved": {"height": 1.0},
                "unresolved": [],
                "resolution_sources": {"height": "default"},
                "message": "ok",
                "phase_hint": "build",
                "executed": 0,
                "guided_reference_readiness": {
                    "status": "blocked",
                    "goal": "chair",
                    "has_active_goal": True,
                    "goal_input_pending": False,
                    "attached_reference_count": 0,
                    "pending_reference_count": 0,
                    "compare_ready": False,
                    "iterate_ready": False,
                    "blocking_reason": "reference_images_required",
                    "next_action": "attach_reference_images",
                },
                "guided_flow_state": {
                    "flow_id": "guided_creature_flow",
                    "domain_profile": "creature",
                    "current_step": "establish_spatial_context",
                    "completed_steps": [],
                    "required_checks": [
                        {
                            "check_id": "scope_graph",
                            "tool_name": "scene_scope_graph",
                            "reason": "Establish the structural anchor and active object scope before broad edits.",
                            "status": "pending",
                            "priority": "high",
                        }
                    ],
                    "required_prompts": ["guided_session_start", "reference_guided_creature_build"],
                    "preferred_prompts": ["workflow_router_first"],
                    "next_actions": ["run_required_checks"],
                    "blocked_families": ["build", "late_refinement", "finish"],
                    "allowed_families": ["spatial_context", "reference_context"],
                    "allowed_roles": [],
                    "completed_roles": [],
                    "missing_roles": [],
                    "required_role_groups": ["spatial_context"],
                    "step_status": "blocked",
                },
            },
            "guided_flow_state.domain_profile",
            "creature",
        ),
        (
            RouterStatusContract,
            {
                "enabled": True,
                "session_id": "sess-1",
                "transport": "streamable-http",
                "initialized": True,
                "ready": True,
                "surface_profile": "legacy-flat",
                "visible_capabilities": ["router", "scene"],
                "visible_entry_capabilities": ["router"],
                "hidden_capability_count": 0,
                "router_failure_policy": "fail_open",
                "guided_reference_readiness": {
                    "status": "blocked",
                    "goal": "chair",
                    "has_active_goal": True,
                    "goal_input_pending": False,
                    "attached_reference_count": 0,
                    "pending_reference_count": 1,
                    "compare_ready": False,
                    "iterate_ready": False,
                    "blocking_reason": "pending_references_detected",
                    "next_action": "call_router_get_status",
                },
                "guided_flow_state": {
                    "flow_id": "guided_building_flow",
                    "domain_profile": "building",
                    "current_step": "create_primary_masses",
                    "completed_steps": ["understand_goal", "establish_spatial_context"],
                    "required_checks": [],
                    "required_prompts": ["guided_session_start"],
                    "preferred_prompts": ["workflow_router_first"],
                    "next_actions": ["begin_primary_masses"],
                    "blocked_families": [],
                    "allowed_families": ["primary_masses"],
                    "allowed_roles": ["footprint_mass", "main_volume", "roof_mass"],
                    "completed_roles": ["footprint_mass"],
                    "missing_roles": ["main_volume", "roof_mass"],
                    "required_role_groups": ["primary_masses"],
                    "step_status": "ready",
                },
                "list_page_size": 250,
                "background_job_count": 0,
            },
            "guided_flow_state.current_step",
            "create_primary_masses",
        ),
        (
            WorkflowCatalogResponseContract,
            {
                "action": "import_append",
                "status": "receiving",
                "session_id": "sess-1",
                "received_chunks": 1,
                "total_chunks": 3,
                "bytes_received": 128,
            },
            "session_id",
            "sess-1",
        ),
        (
            CorrectionAuditEventContract,
            {
                "event_id": "audit_1",
                "decision": "ask",
                "reason": "mode correction required",
                "intent": {
                    "original_tool_name": "mesh_extrude_region",
                    "original_params": {"move": [0, 0, 1]},
                    "corrected_tool_name": "system_set_mode",
                    "corrected_params": {"mode": "EDIT"},
                    "category": "precondition_mode",
                },
                "execution": {
                    "tool_name": "system_set_mode",
                    "params": {"mode": "EDIT"},
                    "result": {"mode": "EDIT"},
                    "error": None,
                },
                "verification": {
                    "status": "passed",
                    "details": {"mode": "EDIT"},
                },
            },
            "verification.status",
            "passed",
        ),
    ],
)
def test_contracts_accept_representative_handler_shaped_payloads(contract_cls, payload, field_name, expected):
    contract = contract_cls(**payload)

    current = contract
    for part in field_name.split("."):
        current = getattr(current, part) if hasattr(current, part) else current[part]

    assert current == expected


def test_router_goal_contract_omits_optional_guided_flow_state_cleanly():
    contract = RouterGoalResponseContract(
        status="ready",
        session_id="sess-1",
        transport="stdio",
        continuation_mode="workflow",
        workflow="chair_workflow",
        resolved={},
        unresolved=[],
        resolution_sources={},
        message="ok",
        phase_hint="build",
        executed=0,
    )

    assert contract.guided_flow_state is None
