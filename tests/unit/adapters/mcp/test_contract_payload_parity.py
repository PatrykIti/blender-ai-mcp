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
                "workflow": "chair_workflow",
                "resolved": {"height": 1.0},
                "unresolved": [],
                "resolution_sources": {"height": "default"},
                "message": "ok",
                "phase_hint": "build",
                "executed": 0,
            },
            "workflow",
            "chair_workflow",
        ),
        (
            RouterStatusContract,
            {
                "enabled": True,
                "initialized": True,
                "ready": True,
                "surface_profile": "legacy-flat",
                "visible_capabilities": ["router", "scene"],
                "visible_entry_capabilities": ["router"],
                "hidden_capability_count": 0,
                "router_failure_policy": "fail_open",
                "list_page_size": 250,
                "background_job_count": 0,
            },
            "surface_profile",
            "legacy-flat",
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
