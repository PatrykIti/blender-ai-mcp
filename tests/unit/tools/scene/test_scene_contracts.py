"""Tests for structured scene contracts."""

from server.adapters.mcp.contracts.scene import (
    SceneContextResponseContract,
    SceneInspectResponseContract,
    SceneModeContract,
    SceneSelectionContract,
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
