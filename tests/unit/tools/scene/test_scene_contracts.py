"""Tests for structured scene contracts."""

from server.adapters.mcp.contracts.scene import (
    SceneAssembledTargetScopeContract,
    SceneAssertContactContract,
    SceneAssertContainmentContract,
    SceneAssertDimensionsContract,
    SceneAssertionPayloadContract,
    SceneAssertProportionContract,
    SceneAssertSymmetryContract,
    SceneBoundingBoxContract,
    SceneConfigureResponseContract,
    SceneContextResponseContract,
    SceneCorrectionTruthBundleContract,
    SceneCorrectionTruthPairContract,
    SceneCorrectionTruthSummaryContract,
    SceneCreateResponseContract,
    SceneCustomPropertiesContract,
    SceneHierarchyContract,
    SceneInspectResponseContract,
    SceneMeasureAlignmentContract,
    SceneMeasureDimensionsContract,
    SceneMeasureDistanceContract,
    SceneMeasureGapContract,
    SceneMeasureOverlapContract,
    SceneModeContract,
    SceneOriginInfoContract,
    ScenePartGroupContract,
    SceneSelectionContract,
    SceneSnapshotDiffContract,
    SceneSnapshotStateContract,
    SceneTruthFollowupContract,
    SceneTruthFollowupItemContract,
)
from server.adapters.mcp.sampling.result_types import (
    AssistantBudgetContract,
    InspectionSummaryAssistantContract,
    InspectionSummaryContract,
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


def test_scene_configure_contract_carries_structured_payload_or_error():
    """Scene configure contract should keep write-side results machine-readable."""

    payload = SceneConfigureResponseContract(
        action="render",
        payload={"render_engine": "CYCLES"},
    )
    error = SceneConfigureResponseContract(
        action="world",
        error="World 'Studio' not found",
    )

    assert payload.payload["render_engine"] == "CYCLES"
    assert "not found" in error.error


def test_scene_assembled_target_scope_contract_supports_scene_collection_and_part_groups():
    """Assembled target scope should support explicit scene/object grouping contracts."""

    single = SceneAssembledTargetScopeContract(
        scope_kind="single_object",
        primary_target="Squirrel_Head",
        object_names=["Squirrel_Head"],
        object_count=1,
    )
    collection = SceneAssembledTargetScopeContract(
        scope_kind="collection",
        primary_target="Squirrel_Head",
        object_names=["Squirrel_Head", "Squirrel_Body"],
        object_count=2,
        collection_name="Squirrel",
    )
    part_groups = SceneAssembledTargetScopeContract(
        scope_kind="part_groups",
        primary_target="Squirrel_Head",
        object_names=["Squirrel_Head", "Squirrel_Body"],
        object_count=2,
        part_groups=[
            ScenePartGroupContract(
                group_name="head_group",
                group_kind="role",
                role="head",
                object_names=["Squirrel_Head"],
            )
        ],
    )

    assert single.scope_kind == "single_object"
    assert collection.collection_name == "Squirrel"
    assert part_groups.part_groups[0].role == "head"


def test_scene_correction_truth_bundle_contract_carries_pair_checks_and_summary():
    """Correction truth bundle should keep pairwise measure/assert results machine-readable."""

    bundle = SceneCorrectionTruthBundleContract(
        scope=SceneAssembledTargetScopeContract(
            scope_kind="collection",
            primary_target="Squirrel_Head",
            object_names=["Squirrel_Head", "Squirrel_Body"],
            object_count=2,
            collection_name="Squirrel",
        ),
        summary=SceneCorrectionTruthSummaryContract(
            pairing_strategy="primary_to_others",
            pair_count=1,
            evaluated_pairs=1,
            contact_failures=1,
            separated_pairs=1,
            misaligned_pairs=1,
        ),
        checks=[
            SceneCorrectionTruthPairContract(
                from_object="Squirrel_Head",
                to_object="Squirrel_Body",
                gap={"relation": "separated", "gap": 0.1},
                alignment={"is_aligned": False, "axes": ["X", "Y", "Z"]},
                overlap={"overlaps": False, "relation": "disjoint"},
                contact_assertion=SceneAssertionPayloadContract(
                    assertion="scene_assert_contact",
                    passed=False,
                    subject="Squirrel_Head",
                    target="Squirrel_Body",
                    expected={"max_gap": 0.0001},
                    actual={"gap": 0.1, "relation": "separated"},
                ),
            )
        ],
    )

    assert bundle.summary.pairing_strategy == "primary_to_others"
    assert bundle.checks[0].from_object == "Squirrel_Head"
    assert bundle.checks[0].contact_assertion.passed is False


def test_scene_truth_followup_contract_carries_loop_ready_items():
    """Truth follow-up should summarize actionable pair findings for later loop handoff."""

    followup = SceneTruthFollowupContract(
        scope=SceneAssembledTargetScopeContract(
            scope_kind="object_set",
            primary_target="Squirrel_Head",
            object_names=["Squirrel_Head", "Squirrel_Tail"],
            object_count=2,
        ),
        continue_recommended=True,
        message="Truth follow-up identified 2 actionable finding(s) across 1 pair(s).",
        focus_pairs=["Squirrel_Head -> Squirrel_Tail"],
        items=[
            SceneTruthFollowupItemContract(
                kind="gap",
                summary="Squirrel_Head -> Squirrel_Tail still has measurable separation.",
                priority="normal",
                from_object="Squirrel_Head",
                to_object="Squirrel_Tail",
                tool_name="scene_measure_gap",
            )
        ],
    )

    assert followup.continue_recommended is True
    assert followup.focus_pairs == ["Squirrel_Head -> Squirrel_Tail"]
    assert followup.items[0].tool_name == "scene_measure_gap"


def test_scene_create_contract_carries_structured_payload_or_error():
    """Scene create contract should keep grouped helper-object creation machine-readable."""

    payload = SceneCreateResponseContract(
        action="light",
        payload={"object_name": "KeyLight", "object_type": "LIGHT"},
    )
    error = SceneCreateResponseContract(
        action="camera",
        error="Invalid location or rotation coordinate payload.",
    )

    assert payload.payload["object_name"] == "KeyLight"
    assert "Invalid location" in error.error


def test_scene_snapshot_and_related_read_contracts_validate_structured_payloads():
    """Structured scene read contracts should validate the remaining read-heavy payloads."""

    snapshot = SceneSnapshotStateContract(
        snapshot={"object_count": 1, "mode": "OBJECT"},
        hash="abc123",
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
                inspection_action="scene_snapshot_state",
                overview="Snapshot overview",
                key_findings=["1 object"],
                truth_source="inspection_contract",
            ),
        ),
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
    assert snapshot.assistant.result.overview == "Snapshot overview"
    assert diff.objects_added == ["Cube"]
    assert props.properties["tag"] == "hero"
    assert hierarchy.payload["total_objects"] == 1
    assert bbox.payload["max"] == [1, 1, 1]
    assert origin.payload["origin_world"] == [0, 0, 0]


def test_scene_measure_contracts_validate_machine_readable_truth_payloads():
    """Measure/assert scene contracts should keep deterministic payloads structured."""

    distance = SceneMeasureDistanceContract(
        payload={
            "from_object": "Cube",
            "to_object": "Sphere",
            "distance": 2.5,
            "units": "blender_units",
        }
    )
    dimensions = SceneMeasureDimensionsContract(
        payload={
            "object_name": "Cube",
            "dimensions": [2.0, 1.0, 1.0],
            "volume": 2.0,
            "units": "blender_units",
        }
    )
    gap = SceneMeasureGapContract(
        payload={
            "from_object": "Cube",
            "to_object": "Sphere",
            "gap": 0.25,
            "relation": "separated",
            "units": "blender_units",
        }
    )
    alignment = SceneMeasureAlignmentContract(
        payload={
            "from_object": "Cube",
            "to_object": "Sphere",
            "is_aligned": True,
            "aligned_axes": ["Y", "Z"],
            "units": "blender_units",
        }
    )
    overlap = SceneMeasureOverlapContract(
        payload={
            "from_object": "Cube",
            "to_object": "Sphere",
            "overlaps": False,
            "relation": "disjoint",
            "units": "blender_units",
        }
    )

    assert distance.payload["distance"] == 2.5
    assert dimensions.payload["volume"] == 2.0
    assert gap.payload["relation"] == "separated"
    assert alignment.payload["is_aligned"] is True
    assert overlap.payload["overlaps"] is False


def test_scene_assert_contracts_validate_shared_assertion_payloads():
    """Scene assertion contracts should share one stable machine-readable result envelope."""

    contact = SceneAssertContactContract(
        payload=SceneAssertionPayloadContract(
            assertion="scene_assert_contact",
            passed=True,
            subject="Cube",
            target="Sphere",
            expected={"max_gap": 0.001},
            actual={"gap": 0.0, "relation": "contact"},
            delta={"gap_overage": 0.0},
            tolerance=0.001,
            units="blender_units",
        )
    )
    dimensions = SceneAssertDimensionsContract(
        payload=SceneAssertionPayloadContract(
            assertion="scene_assert_dimensions",
            passed=False,
            subject="Cube",
            expected={"dimensions": [2.0, 2.0, 2.0]},
            actual={"dimensions": [2.1, 2.0, 2.0]},
            delta={"x": 0.1, "y": 0.0, "z": 0.0},
            tolerance=0.01,
            units="blender_units",
        )
    )

    assert contact.payload.passed is True
    assert contact.payload.actual["relation"] == "contact"
    assert dimensions.payload.passed is False
    assert dimensions.payload.delta["x"] == 0.1

    containment = SceneAssertContainmentContract(
        payload=SceneAssertionPayloadContract(
            assertion="scene_assert_containment",
            passed=True,
            subject="Inner",
            target="Outer",
            actual={"min_clearance": 0.2},
            units="blender_units",
        )
    )
    symmetry = SceneAssertSymmetryContract(
        payload=SceneAssertionPayloadContract(
            assertion="scene_assert_symmetry",
            passed=False,
            subject="Left",
            target="Right",
            delta={"mirror_axis": 0.2},
            units="blender_units",
        )
    )
    proportion = SceneAssertProportionContract(
        payload=SceneAssertionPayloadContract(
            assertion="scene_assert_proportion",
            passed=True,
            subject="TableLeg",
            actual={"ratio": 0.25},
            units="ratio",
        )
    )

    assert containment.payload.actual["min_clearance"] == 0.2
    assert symmetry.payload.delta["mirror_axis"] == 0.2
    assert proportion.payload.actual["ratio"] == 0.25
