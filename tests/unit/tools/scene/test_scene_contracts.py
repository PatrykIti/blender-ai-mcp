"""Tests for structured scene contracts."""

from server.adapters.mcp.contracts.scene import (
    SceneAssembledTargetScopeContract,
    SceneAssertContactContract,
    SceneAssertContainmentContract,
    SceneAssertDimensionsContract,
    SceneAssertionPayloadContract,
    SceneAssertProportionContract,
    SceneAssertSymmetryContract,
    SceneAttachmentSemanticsContract,
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
    SceneRelationGraphPairContract,
    SceneRelationGraphPayloadContract,
    SceneRelationGraphResponseContract,
    SceneRelationGraphSummaryContract,
    SceneRepairMacroCandidateContract,
    SceneScopeGraphPayloadContract,
    SceneScopeGraphResponseContract,
    SceneScopeObjectRoleContract,
    SceneSelectionContract,
    SceneSnapshotDiffContract,
    SceneSnapshotStateContract,
    SceneSupportSemanticsContract,
    SceneSymmetrySemanticsContract,
    SceneTruthFollowupContract,
    SceneTruthFollowupItemContract,
    SceneViewDiagnosticsPayloadContract,
    SceneViewDiagnosticsResponseContract,
    SceneViewDiagnosticsSummaryContract,
    SceneViewDiagnosticsTargetContract,
    SceneViewExtentContract,
    SceneViewPointContract,
    SceneViewProjectionEvidenceContract,
    SceneViewQueryContract,
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


def test_scene_scope_graph_contract_carries_object_roles_and_primary_anchor():
    payload = SceneScopeGraphPayloadContract(
        scope=SceneAssembledTargetScopeContract(
            scope_kind="object_set",
            primary_target="Squirrel_Body",
            object_names=["Squirrel_Head", "Squirrel_Body", "Squirrel_Tail"],
            object_count=3,
            object_roles=[
                SceneScopeObjectRoleContract(
                    object_name="Squirrel_Body",
                    role="anchor_core",
                    is_primary=True,
                    signals=["body_name_hint", "bbox_volume_anchor"],
                ),
                SceneScopeObjectRoleContract(
                    object_name="Squirrel_Head",
                    role="attached_mass",
                    signals=["head_name_hint"],
                ),
                SceneScopeObjectRoleContract(
                    object_name="Squirrel_Tail",
                    role="attached_appendage",
                    signals=["appendage_name_hint"],
                ),
            ],
        ),
        message="Scope graph derived from deterministic role heuristics.",
    )
    response = SceneScopeGraphResponseContract(payload=payload)

    assert response.payload is not None
    assert response.payload.scope.primary_target == "Squirrel_Body"
    assert response.payload.scope.object_roles[0].role == "anchor_core"
    assert response.payload.scope.object_roles[2].role == "attached_appendage"


def test_scene_relation_graph_contract_carries_compact_pair_semantics():
    response = SceneRelationGraphResponseContract(
        payload=SceneRelationGraphPayloadContract(
            scope=SceneAssembledTargetScopeContract(
                scope_kind="object_set",
                primary_target="Squirrel_Body",
                object_names=["Squirrel_Body", "Squirrel_Head", "Floor"],
                object_count=3,
            ),
            summary=SceneRelationGraphSummaryContract(
                pairing_strategy="guided_spatial_pairs",
                pair_count=2,
                evaluated_pairs=2,
                failing_pairs=1,
                attachment_pairs=1,
                support_pairs=1,
            ),
            pairs=[
                SceneRelationGraphPairContract(
                    pair_id="squirrel_body__squirrel_head",
                    from_object="Squirrel_Head",
                    to_object="Squirrel_Body",
                    pair_source="required_creature_seam",
                    relation_kinds=["contact", "gap", "alignment", "attachment"],
                    relation_verdicts=["separated", "misaligned", "misaligned_attachment", "floating_gap"],
                    gap_relation="separated",
                    gap_distance=0.1,
                    overlap_relation="disjoint",
                    contact_passed=False,
                    alignment_status="misaligned",
                    aligned_axes=["Y"],
                    measurement_basis="bounding_box",
                    attachment_semantics=SceneAttachmentSemanticsContract(
                        relation_kind="segment_attachment",
                        seam_kind="head_body",
                        part_object="Squirrel_Head",
                        anchor_object="Squirrel_Body",
                        required_seam=True,
                        preferred_macro="macro_align_part_with_contact",
                        attachment_verdict="floating_gap",
                    ),
                ),
                SceneRelationGraphPairContract(
                    pair_id="squirrel_body__floor",
                    from_object="Squirrel_Body",
                    to_object="Floor",
                    pair_source="support_candidate",
                    relation_kinds=["contact", "gap", "support"],
                    relation_verdicts=["contact", "supported"],
                    gap_relation="contact",
                    gap_distance=0.0,
                    contact_passed=True,
                    measurement_basis="bounding_box",
                    support_semantics=SceneSupportSemanticsContract(
                        supported_object="Squirrel_Body",
                        support_object="Floor",
                        axis="Z",
                        verdict="supported",
                    ),
                    symmetry_semantics=SceneSymmetrySemanticsContract(
                        left_object="Leg_L",
                        right_object="Leg_R",
                        axis="X",
                        mirror_coordinate=0.0,
                        verdict="symmetric",
                    ),
                ),
            ],
        )
    )

    assert response.payload is not None
    assert response.payload.summary.pairing_strategy == "guided_spatial_pairs"
    assert "misaligned_attachment" in response.payload.pairs[0].relation_verdicts
    assert response.payload.pairs[0].attachment_semantics is not None
    assert response.payload.pairs[1].support_semantics is not None


def test_scene_view_diagnostics_contract_carries_projection_and_visibility_evidence():
    response = SceneViewDiagnosticsResponseContract(
        payload=SceneViewDiagnosticsPayloadContract(
            view_query=SceneViewQueryContract(
                requested_view_source="user_perspective",
                resolved_view_source="user_perspective",
                analysis_backend="mirrored_user_perspective",
                available=True,
                state_restored=True,
            ),
            scope=SceneAssembledTargetScopeContract(
                scope_kind="object_set",
                primary_target="Squirrel_Head",
                object_names=["Squirrel_Head", "Squirrel_Body"],
                object_count=2,
            ),
            summary=SceneViewDiagnosticsSummaryContract(
                target_count=2,
                visible_count=1,
                partially_visible_count=1,
                centered_target_count=1,
                framing_issue_count=1,
            ),
            targets=[
                SceneViewDiagnosticsTargetContract(
                    object_name="Squirrel_Head",
                    visibility_verdict="visible",
                    projection_status="projected",
                    projection=SceneViewProjectionEvidenceContract(
                        projected_center=SceneViewPointContract(x=0.5, y=0.5),
                        projected_extent=SceneViewExtentContract(
                            min_x=0.4,
                            min_y=0.3,
                            max_x=0.6,
                            max_y=0.7,
                            width=0.2,
                            height=0.4,
                        ),
                        center_offset=SceneViewPointContract(x=0.0, y=0.0),
                        frame_coverage_ratio=1.0,
                        frame_occupancy_ratio=0.08,
                        centered=True,
                        sample_count=7,
                        in_front_sample_count=7,
                        in_frame_sample_count=7,
                        visible_sample_count=7,
                        occluded_sample_count=0,
                        occlusion_test_available=True,
                    ),
                ),
                SceneViewDiagnosticsTargetContract(
                    object_name="Squirrel_Body",
                    visibility_verdict="partially_visible",
                    projection_status="projected",
                    projection=SceneViewProjectionEvidenceContract(
                        projected_center=SceneViewPointContract(x=1.1, y=0.52),
                        projected_extent=SceneViewExtentContract(
                            min_x=0.8,
                            min_y=0.25,
                            max_x=1.3,
                            max_y=0.8,
                            width=0.5,
                            height=0.55,
                        ),
                        center_offset=SceneViewPointContract(x=0.6, y=0.02),
                        frame_coverage_ratio=0.4,
                        frame_occupancy_ratio=0.11,
                        centered=False,
                        sample_count=7,
                        in_front_sample_count=7,
                        in_frame_sample_count=3,
                        visible_sample_count=2,
                        occluded_sample_count=1,
                        occlusion_test_available=True,
                    ),
                ),
            ],
            message="View-space diagnostics only; use truth tools for contact/attachment verification.",
        )
    )

    assert response.payload is not None
    assert response.payload.view_query.analysis_backend == "mirrored_user_perspective"
    assert response.payload.summary.partially_visible_count == 1
    assert response.payload.targets[0].projection.projected_center.x == 0.5
    assert response.payload.targets[1].visibility_verdict == "partially_visible"


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
            pairing_strategy="required_creature_seams",
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
                relation_pair_id="squirrel_head__squirrel_body",
                relation_kinds=["contact", "gap", "alignment", "attachment"],
                relation_verdicts=["separated", "misaligned", "floating_gap"],
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
                attachment_semantics=SceneAttachmentSemanticsContract(
                    relation_kind="segment_attachment",
                    seam_kind="head_body",
                    part_object="Squirrel_Head",
                    anchor_object="Squirrel_Body",
                    required_seam=True,
                    preferred_macro="macro_align_part_with_contact",
                    attachment_verdict="floating_gap",
                ),
            )
        ],
    )

    assert bundle.summary.pairing_strategy == "required_creature_seams"
    assert bundle.checks[0].from_object == "Squirrel_Head"
    assert bundle.checks[0].contact_assertion.passed is False
    assert bundle.checks[0].attachment_semantics is not None
    assert bundle.checks[0].attachment_semantics.seam_kind == "head_body"
    assert bundle.checks[0].relation_kinds == ["contact", "gap", "alignment", "attachment"]


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
                kind="attachment",
                summary="Squirrel_Body -> Squirrel_Tail is still wrong for this organic attachment relation.",
                priority="high",
                from_object="Squirrel_Body",
                to_object="Squirrel_Tail",
                tool_name="scene_assert_contact",
                relation_pair_id="squirrel_body__squirrel_tail",
                relation_kinds=["contact", "gap", "attachment"],
                relation_verdicts=["floating_gap"],
            ),
            SceneTruthFollowupItemContract(
                kind="gap",
                summary="Squirrel_Head -> Squirrel_Tail still has measurable separation.",
                priority="normal",
                from_object="Squirrel_Head",
                to_object="Squirrel_Tail",
                tool_name="scene_measure_gap",
                relation_pair_id="squirrel_head__squirrel_tail",
                relation_kinds=["contact", "gap"],
                relation_verdicts=["separated"],
            ),
        ],
        macro_candidates=[
            SceneRepairMacroCandidateContract(
                macro_name="macro_align_part_with_contact",
                reason="Repair the pair with a bounded nudge.",
                priority="high",
                arguments_hint={"part_object": "Squirrel_Head", "reference_object": "Squirrel_Tail"},
            )
        ],
    )

    assert followup.continue_recommended is True
    assert followup.focus_pairs == ["Squirrel_Head -> Squirrel_Tail"]
    assert followup.items[0].kind == "attachment"
    assert followup.items[1].tool_name == "scene_measure_gap"
    assert followup.items[0].relation_kinds == ["contact", "gap", "attachment"]
    assert followup.macro_candidates[0].macro_name == "macro_align_part_with_contact"


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
