"""Tests for structured scene contracts."""

from server.adapters.mcp.contracts.scene import (
    SceneBoundingBoxContract,
    SceneContextResponseContract,
    SceneCustomPropertiesContract,
    SceneHierarchyContract,
    SceneInspectResponseContract,
    SceneModeContract,
    SceneOriginInfoContract,
    SceneSelectionContract,
    SceneSnapshotDiffContract,
    SceneSnapshotStateContract,
)


def test_scene_context_contract_supports_mode_and_selection_payloads():
    """Scene context contract should validate both mode and selection payloads."""

    mode = SceneContextResponseContract(
        action="mode",
        payload=SceneModeContract(
            mode="OBJECT",
            active_object="Cube",
            active_object_type="MESH",
            selected_object_names=["Cube"],
            selection_count=1,
        ),
    )
    selection = SceneContextResponseContract(
        action="selection",
        payload=SceneSelectionContract(
            mode="EDIT",
            selected_object_names=["Cube"],
            selection_count=1,
            edit_mode_vertex_count=8,
            edit_mode_edge_count=12,
            edit_mode_face_count=6,
        ),
    )

    assert mode.payload.mode == "OBJECT"
    assert selection.payload.mode == "EDIT"


def test_scene_inspect_contract_carries_structured_payload_or_error():
    """Scene inspect contract should remain machine-readable for payloads and errors."""

    payload = SceneInspectResponseContract(
        action="object",
        payload={"object_name": "Cube", "type": "MESH"},
    )
    error = SceneInspectResponseContract(
        action="object",
        error="object_name required",
    )

    assert payload.payload["object_name"] == "Cube"
    assert error.error == "object_name required"


def test_scene_snapshot_and_related_read_contracts_validate_structured_payloads():
    """Structured scene read contracts should validate the remaining read-heavy payloads."""

    snapshot = SceneSnapshotStateContract(
        snapshot={"object_count": 1, "mode": "OBJECT"},
        hash="abc123",
    )
    diff = SceneSnapshotDiffContract(
        objects_added=["Cube"],
        objects_removed=[],
        objects_modified=[],
        baseline_hash="base",
        target_hash="target",
        baseline_timestamp="t1",
        target_timestamp="t2",
        has_changes=True,
    )
    props = SceneCustomPropertiesContract(
        object_name="Cube",
        property_count=1,
        properties={"tag": "hero"},
    )
    hierarchy = SceneHierarchyContract(payload={"roots": [{"name": "Cube"}], "total_objects": 1})
    bbox = SceneBoundingBoxContract(payload={"min": [0, 0, 0], "max": [1, 1, 1]})
    origin = SceneOriginInfoContract(payload={"origin_world": [0, 0, 0], "suggestions": []})

    assert snapshot.hash == "abc123"
    assert diff.objects_added == ["Cube"]
    assert props.properties["tag"] == "hero"
    assert hierarchy.payload["total_objects"] == 1
    assert bbox.payload["max"] == [1, 1, 1]
    assert origin.payload["origin_world"] == [0, 0, 0]
