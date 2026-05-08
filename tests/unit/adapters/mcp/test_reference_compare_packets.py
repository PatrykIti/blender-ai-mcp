"""Focused planner/synthesis coverage for staged reference compare packets."""

from __future__ import annotations

from typing import Literal

from server.adapters.mcp.areas.reference_planner import build_compare_packets, synthesize_packet_vision_result
from server.adapters.mcp.contracts.reference import ReferenceImageRecordContract
from server.adapters.mcp.contracts.scene import SceneAssembledTargetScopeContract, SceneTruthFollowupContract
from server.adapters.mcp.contracts.vision import VisionCaptureImageContract
from server.adapters.mcp.sampling.result_types import VisionAssistContract, VisionInputSummaryContract


def _reference(reference_id: str, *, label: str, target_view: str | None = None) -> ReferenceImageRecordContract:
    return ReferenceImageRecordContract(
        reference_id=reference_id,
        goal="low poly creature",
        label=label,
        target_object="Creature",
        target_view=target_view,
        media_type="image/png",
        original_path=f"/tmp/{reference_id}.png",
        stored_path=f"/tmp/{reference_id}.png",
        added_at="2026-05-08T00:00:00Z",
    )


def _capture(
    label: str,
    *,
    preset_name: str,
    view_kind: Literal["wide", "focus", "overlay", "reference"] = "focus",
) -> VisionCaptureImageContract:
    return VisionCaptureImageContract(
        label=label,
        image_path=f"/tmp/{label}.png",
        host_visible_path=f"/tmp/{label}.png",
        preset_name=preset_name,
        media_type="image/png",
        view_kind=view_kind,
    )


def test_build_compare_packets_simple_front_and_side_use_explicit_view_packets():
    packets = build_compare_packets(
        target_view=None,
        captures=[
            _capture("target_front_after", preset_name="target_front"),
            _capture("target_side_after", preset_name="target_side"),
        ],
        reference_records=[
            _reference("ref_front", label="front_ref", target_view="front"),
            _reference("ref_side", label="side_ref", target_view="side"),
        ],
        assembled_target_scope=SceneAssembledTargetScopeContract(
            scope_kind="single_object",
            primary_target="Creature",
            object_names=["Creature"],
            object_count=1,
        ),
        truth_followup=SceneTruthFollowupContract(
            scope=SceneAssembledTargetScopeContract(
                scope_kind="single_object",
                primary_target="Creature",
                object_names=["Creature"],
                object_count=1,
            ),
            continue_recommended=False,
            message="No structural blocker.",
        ),
    )

    assert packets.complexity_tier == "simple"
    assert packets.packet_count == 2
    assert [packet.target_view for packet in packets.packets] == ["front", "side"]
    assert [packet.packet_kind for packet in packets.packets] == ["view", "view"]


def test_build_compare_packets_simple_drops_unmatched_reference_view_without_target_request():
    packets = build_compare_packets(
        target_view=None,
        captures=[_capture("target_front_after", preset_name="target_front")],
        reference_records=[
            _reference("ref_front", label="front_ref", target_view="front"),
            _reference("ref_side", label="side_ref", target_view="side"),
        ],
        assembled_target_scope=SceneAssembledTargetScopeContract(
            scope_kind="single_object",
            primary_target="Creature",
            object_names=["Creature"],
            object_count=1,
        ),
        truth_followup=SceneTruthFollowupContract(
            scope=SceneAssembledTargetScopeContract(
                scope_kind="single_object",
                primary_target="Creature",
                object_names=["Creature"],
                object_count=1,
            ),
            continue_recommended=False,
            message="No structural blocker.",
        ),
    )

    assert packets.packet_count == 1
    assert packets.packets[0].target_view == "front"
    assert packets.packets[0].capture_labels == ["target_front_after"]


def test_build_compare_packets_complex_focus_clusters_keep_view_and_scope_slices():
    scope = SceneAssembledTargetScopeContract(
        scope_kind="collection",
        primary_target="Squirrel_Body",
        object_names=["Squirrel_Head", "Squirrel_Body", "Squirrel_Tail"],
        object_count=3,
        collection_name="Squirrel",
    )
    packets = build_compare_packets(
        target_view=None,
        captures=[
            _capture("context_wide_after", preset_name="context_wide", view_kind="wide"),
            _capture("target_front_after", preset_name="target_front"),
            _capture("target_side_after", preset_name="target_side"),
        ],
        reference_records=[
            _reference("ref_front", label="front_ref", target_view="front"),
            _reference("ref_side", label="side_ref", target_view="side"),
        ],
        assembled_target_scope=scope,
        truth_followup=SceneTruthFollowupContract(
            scope=scope,
            continue_recommended=True,
            message="Tail and head seams still need work.",
            focus_pairs=["Squirrel_Head -> Squirrel_Body", "Squirrel_Tail -> Squirrel_Body"],
        ),
    )

    assert packets.complexity_tier == "complex"
    assert packets.packet_count == 4
    assert {packet.scope_label for packet in packets.packets} == {"Body + Head", "Tail"}
    assert {packet.target_view for packet in packets.packets} == {"front", "side"}
    assert all(packet.packet_kind == "view_scope" for packet in packets.packets)


def test_synthesize_packet_vision_result_dedupes_reused_capture_and_reference_counts():
    front_packet = build_compare_packets(
        target_view=None,
        captures=[
            _capture("context_wide_after", preset_name="context_wide", view_kind="wide"),
            _capture("target_front_after", preset_name="target_front"),
        ],
        reference_records=[_reference("ref_front", label="front_ref", target_view="front")],
        assembled_target_scope=SceneAssembledTargetScopeContract(
            scope_kind="single_object",
            primary_target="Creature",
            object_names=["Creature"],
            object_count=1,
        ),
        truth_followup=SceneTruthFollowupContract(
            scope=SceneAssembledTargetScopeContract(
                scope_kind="single_object",
                primary_target="Creature",
                object_names=["Creature"],
                object_count=1,
            ),
            continue_recommended=False,
            message="No structural blocker.",
        ),
    ).packets[0]
    side_packet = front_packet.model_copy(
        update={
            "packet_id": "packet:side:test",
            "packet_label": "side packet",
            "target_view": "side",
            "capture_labels": ["context_wide_after", "target_front_after"],
            "reference_ids": ["ref_front"],
        }
    )

    synthesized = synthesize_packet_vision_result(
        [
            (
                front_packet,
                VisionAssistContract(
                    backend_kind="mlx_local",
                    goal_summary="Front packet looks good.",
                    visible_changes=["Front silhouette is readable."],
                    shape_mismatches=[],
                    proportion_mismatches=[],
                    correction_focus=[],
                    likely_issues=[],
                    next_corrections=[],
                    recommended_checks=[],
                    input_summary=VisionInputSummaryContract(
                        before_image_count=0,
                        after_image_count=2,
                        reference_image_count=1,
                        target_object="Creature",
                    ),
                ),
            ),
            (
                side_packet,
                VisionAssistContract(
                    backend_kind="mlx_local",
                    goal_summary="Side packet looks good.",
                    visible_changes=["Side silhouette is readable."],
                    shape_mismatches=[],
                    proportion_mismatches=[],
                    correction_focus=[],
                    likely_issues=[],
                    next_corrections=[],
                    recommended_checks=[],
                    input_summary=VisionInputSummaryContract(
                        before_image_count=0,
                        after_image_count=2,
                        reference_image_count=1,
                        target_object="Creature",
                    ),
                ),
            ),
        ]
    )

    assert synthesized is not None
    assert synthesized.input_summary is not None
    assert synthesized.input_summary.after_image_count == 2
    assert synthesized.input_summary.reference_image_count == 1
