"""Tests for structured mesh contracts."""

from server.adapters.mcp.contracts.mesh import MeshInspectResponseContract


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
    )

    assert summary.summary["vertex_count"] == 8
    assert vertices.returned == 2
    assert vertices.items[0]["index"] == 0
