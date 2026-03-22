"""Tests for structured mesh contracts."""

from server.adapters.mcp.contracts.mesh import MeshInspectResponseContract
from server.adapters.mcp.sampling.result_types import (
    AssistantBudgetContract,
    InspectionSummaryAssistantContract,
    InspectionSummaryContract,
)


def test_mesh_contract_supports_summary_and_paged_items():
    """Mesh inspect contract should support summary and paged item envelopes."""

    summary = MeshInspectResponseContract(
        action="summary",
        object_name="Cube",
        summary={"vertex_count": 8},
    )
    vertices = MeshInspectResponseContract(
        action="vertices",
        object_name="Cube",
        total=8,
        returned=2,
        offset=0,
        limit=2,
        has_more=True,
        items=[{"index": 0}, {"index": 1}],
        metadata={"selected_count": 2},
        assistant=InspectionSummaryAssistantContract(
            status="success",
            assistant_name="inspection_summarizer",
            message="ok",
            budget=AssistantBudgetContract(
                max_input_chars=1000,
                max_messages=1,
                max_tokens=100,
                tool_budget=0,
            ),
            result=InspectionSummaryContract(
                inspection_action="vertices",
                object_name="Cube",
                overview="Vertex sample",
                key_findings=["2 returned items"],
            ),
        ),
    )

    assert summary.summary["vertex_count"] == 8
    assert vertices.returned == 2
    assert vertices.items[0]["index"] == 0
    assert vertices.assistant.result.overview == "Vertex sample"
