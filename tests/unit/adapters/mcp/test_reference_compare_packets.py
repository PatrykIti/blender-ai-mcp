"""Focused planner/synthesis coverage for staged reference compare packets."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any, Literal

from server.adapters.mcp.areas import reference_compare_packets as compare_packets_area
from server.adapters.mcp.areas.reference_compare_packets import (
    append_compare_synthesis_conflict_notes,
    merge_packet_phase_results,
)
from server.adapters.mcp.areas.reference_planner import build_compare_packets, synthesize_packet_vision_result
from server.adapters.mcp.areas.reference_silhouette import build_compare_support_evidence
from server.adapters.mcp.contracts.reference import (
    ReferenceCompareDiagnosticsContract,
    ReferenceComparePacketContract,
    ReferenceImageRecordContract,
)
from server.adapters.mcp.contracts.scene import SceneAssembledTargetScopeContract, SceneTruthFollowupContract
from server.adapters.mcp.contracts.vision import VisionCaptureImageContract
from server.adapters.mcp.sampling.result_types import (
    VisionAssistContract,
    VisionInputSummaryContract,
    VisionPacketStatusContract,
)


class _FakeSupportResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self._payload


class _FakeSupportAsyncClient:
    def __init__(self, *, responses: dict[str, Any], captured: list[dict[str, Any]]) -> None:
        self._responses = responses
        self._captured = captured

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, json=None, headers=None):
        self._captured.append({"url": url, "json": json, "headers": headers})
        payload = self._responses[url]
        if isinstance(payload, Exception):
            raise payload
        return _FakeSupportResponse(payload)


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


def test_build_compare_packets_prefers_generic_view_over_target_any_view_fallback():
    packets = build_compare_packets(
        target_view=None,
        captures=[
            _capture("target_front_after", preset_name="target_front"),
            _capture("target_side_after", preset_name="target_side"),
        ],
        reference_records=[
            _reference("creature_front", label="creature_front_ref", target_view="front"),
            _reference("generic_side", label="generic_side_ref", target_view="side").model_copy(
                update={"target_object": None}
            ),
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

    packet_by_view = {packet.target_view: packet for packet in packets.packets}
    assert packet_by_view["front"].reference_ids == ["creature_front"]
    assert packet_by_view["side"].reference_ids == ["generic_side"]


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


def test_build_compare_packets_can_prefer_primary_mass_scope_clusters_over_focus_pairs():
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
            focus_pairs=["Squirrel_Tail -> Squirrel_Body"],
        ),
        prefer_target_scope_clusters=True,
    )

    assert {packet.scope_label for packet in packets.packets} == {"Body + Head", "Tail"}
    assert {packet.target_view for packet in packets.packets} == {"front", "side"}


def test_build_compare_packets_clusters_architecture_facade_roof_and_support_scopes():
    scope = SceneAssembledTargetScopeContract(
        scope_kind="collection",
        primary_target="FacadeMainVolume",
        object_names=[
            "FacadeMainVolume",
            "WindowOpening_A",
            "DoorOpening_A",
            "FacadeRoofMass",
            "ColumnSupport_A",
        ],
        object_count=5,
        collection_name="Architecture",
    )
    packets = build_compare_packets(
        target_view=None,
        captures=[
            _capture("context_wide_after", preset_name="context_wide", view_kind="wide"),
            _capture("target_front_after", preset_name="target_front"),
            _capture("target_top_after", preset_name="target_top"),
        ],
        reference_records=[
            _reference("ref_front", label="front_elevation_ref", target_view="front").model_copy(
                update={"target_object": None}
            ),
            _reference("ref_plan", label="floor_plan_ref", target_view="plan").model_copy(
                update={"target_object": None}
            ),
        ],
        assembled_target_scope=scope,
        truth_followup=SceneTruthFollowupContract(
            scope=scope,
            continue_recommended=True,
            message="Facade openings, roofline, and supports need staged review.",
        ),
    )

    assert packets.complexity_tier == "complex"
    assert {packet.scope_label for packet in packets.packets} == {
        "Facade + Openings",
        "Roofline",
        "Supports",
    }
    assert {"front", "top"}.issubset({packet.target_view for packet in packets.packets})
    facade_packet = next(packet for packet in packets.packets if packet.scope_label == "Facade + Openings")
    roof_packet = next(packet for packet in packets.packets if packet.scope_label == "Roofline")
    assert "opening count" in facade_packet.compare_question
    assert "roof pitch" in roof_packet.compare_question
    assert "WindowOpening_A" in facade_packet.target_objects
    assert "FacadeRoofMass" in roof_packet.target_objects


def test_build_compare_packets_super_complex_slices_references_to_runtime_image_budget():
    packets = build_compare_packets(
        target_view="front",
        captures=[
            _capture("context_wide_after", preset_name="context_wide", view_kind="wide"),
            _capture("target_front_after", preset_name="target_front"),
        ],
        reference_records=[
            _reference(f"ref_front_{index}", label=f"front_ref_{index}", target_view="front") for index in range(1, 7)
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
        max_images_per_packet=4,
    )

    assert packets.complexity_tier == "super_complex"
    assert packets.packet_count == 3
    assert packets.synthesis_required is True
    assert [len(packet.reference_ids) for packet in packets.packets] == [2, 2, 2]
    assert all(packet.capture_labels == ["context_wide_after", "target_front_after"] for packet in packets.packets)
    assert [packet.packet_label for packet in packets.packets] == [
        "front packet reference slice 1",
        "front packet reference slice 2",
        "front packet reference slice 3",
    ]
    assert packets.budget_notes == [
        "Compare packet policy split reference evidence into bounded packet-local slices to stay within "
        "VISION_MAX_IMAGES=4."
    ]


def test_build_compare_packets_tight_image_budget_drops_context_before_reference_signal():
    packets = build_compare_packets(
        target_view="front",
        captures=[
            _capture("context_wide_after", preset_name="context_wide", view_kind="wide"),
            _capture("target_front_after", preset_name="target_front"),
        ],
        reference_records=[
            _reference("ref_front_1", label="front_ref_1", target_view="front"),
            _reference("ref_front_2", label="front_ref_2", target_view="front"),
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
        max_images_per_packet=2,
    )

    assert packets.packet_count == 2
    assert all(packet.capture_labels == ["target_front_after"] for packet in packets.packets)
    assert [packet.reference_ids for packet in packets.packets] == [["ref_front_1"], ["ref_front_2"]]
    assert packets.budget_notes == [
        "Compare packet policy omitted context captures from some packets to stay within VISION_MAX_IMAGES=2.",
        "Compare packet policy split reference evidence into bounded packet-local slices to stay within "
        "VISION_MAX_IMAGES=2.",
    ]


def test_build_compare_packets_reuses_stable_packet_ids_for_equivalent_retry_inputs():
    def _build() -> ReferenceCompareDiagnosticsContract:
        return build_compare_packets(
            target_view="front",
            captures=[
                _capture("context_wide_after", preset_name="context_wide", view_kind="wide"),
                _capture("target_front_after", preset_name="target_front"),
            ],
            reference_records=[
                _reference(f"ref_front_{index}", label=f"front_ref_{index}", target_view="front")
                for index in range(1, 7)
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
            max_images_per_packet=3,
        )

    first = _build()
    retry = _build()

    assert retry.packet_order == first.packet_order
    assert len(set(first.packet_order)) == first.packet_count
    assert [(packet.packet_id, packet.reference_ids, packet.capture_labels) for packet in retry.packets] == [
        (packet.packet_id, packet.reference_ids, packet.capture_labels) for packet in first.packets
    ]


def test_build_compare_packets_marks_one_image_budget_as_incomplete_reference_evidence():
    packets = build_compare_packets(
        target_view="front",
        captures=[
            _capture("context_wide_after", preset_name="context_wide", view_kind="wide"),
            _capture("target_front_after", preset_name="target_front"),
        ],
        reference_records=[
            _reference("ref_front_1", label="front_ref_1", target_view="front"),
            _reference("ref_front_2", label="front_ref_2", target_view="front"),
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
        max_images_per_packet=1,
    )

    assert packets.packet_count == 1
    assert packets.packets[0].capture_labels == ["target_front_after"]
    assert packets.packets[0].reference_ids == []
    assert packets.budget_notes == [
        "Compare packet policy omitted context captures from some packets to stay within VISION_MAX_IMAGES=1.",
        "Compare packet policy split reference evidence into bounded packet-local slices to stay within "
        "VISION_MAX_IMAGES=1.",
        "Runtime image budget is below the 2-image minimum for reference compare packets; "
        "raise VISION_MAX_IMAGES before treating packet conclusions as complete.",
    ]


def test_compare_synthesis_conflict_notes_call_out_mixed_packet_statuses():
    diagnostics = ReferenceCompareDiagnosticsContract(
        complexity_tier="complex",
        packet_count=2,
        packet_order=["packet:clean", "packet:ready"],
        synthesis_required=True,
        synthesis_status="success",
        packets=[
            ReferenceComparePacketContract(
                packet_id="packet:clean",
                packet_label="front packet",
                compare_question="Compare front.",
                extraction_status="success",
                packet_status="clean",
            ),
            ReferenceComparePacketContract(
                packet_id="packet:ready",
                packet_label="side packet",
                compare_question="Compare side.",
                extraction_status="success",
                packet_status="ready",
                correction_focus=["Tail arc"],
            ),
        ],
    )

    append_compare_synthesis_conflict_notes(diagnostics)

    assert diagnostics.conflict_notes == [
        "Compare packets returned mixed clean and corrective/uncertain statuses; "
        "treat synthesis as advisory until the bounded packet details are inspected."
    ]


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
    assert synthesized.packet_guidance is not None
    assert synthesized.packet_guidance.packet_status == "clean"
    assert synthesized.packet_guidance.ranking_recommendation == "skip_clean"


def test_merge_packet_phase_results_does_not_keep_extraction_focus_after_ranking_downgrade():
    extraction_result = VisionAssistContract(
        backend_kind="mlx_local",
        model_name="mlx-community/Qwen3-VL-4B-Instruct-4bit",
        goal_summary="Extraction found a possible head issue.",
        visible_changes=["Front silhouette is readable."],
        shape_mismatches=["Head looks too round."],
        correction_focus=["Head silhouette"],
        next_corrections=["Flatten the head silhouette."],
        packet_guidance=VisionPacketStatusContract(
            packet_status="ready",
            ranking_recommendation="rank",
        ),
    )
    ranking_result = VisionAssistContract(
        backend_kind="mlx_local",
        model_name="mlx-community/Qwen3-VL-4B-Instruct-4bit",
        goal_summary="Ranking pass could not confirm the packet.",
        visible_changes=["Front silhouette is readable."],
        shape_mismatches=["Contradictory low-information shape hint."],
        correction_focus=["Contradictory low-information focus."],
        next_corrections=["Contradictory low-information correction."],
        packet_guidance=VisionPacketStatusContract(
            packet_status="low_information",
            status_reason="Ranking pass found too little focused packet evidence.",
            ranking_recommendation="skip_low_information",
        ),
    )

    merged = merge_packet_phase_results(extraction_result, ranking_result)

    assert merged.packet_guidance is not None
    assert merged.packet_guidance.packet_status == "low_information"
    assert merged.correction_focus == []
    assert merged.shape_mismatches == []
    assert merged.next_corrections == []


def test_build_compare_packets_keeps_packet_reference_ids_local_to_scope_targets():
    scope = SceneAssembledTargetScopeContract(
        scope_kind="collection",
        primary_target="Squirrel_Body",
        object_names=["Squirrel_Head", "Squirrel_Body", "Squirrel_Tail"],
        object_count=3,
        collection_name="Squirrel",
    )
    packets = build_compare_packets(
        target_view="front",
        captures=[_capture("target_front_after", preset_name="target_front")],
        reference_records=[
            _reference("head_ref", label="head_front", target_view="front").model_copy(
                update={"target_object": "Squirrel_Head"}
            ),
            _reference("tail_ref", label="tail_front", target_view="front").model_copy(
                update={"target_object": "Squirrel_Tail"}
            ),
            _reference("generic_ref", label="generic_front", target_view="front"),
        ],
        assembled_target_scope=scope,
        truth_followup=SceneTruthFollowupContract(
            scope=scope,
            continue_recommended=True,
            message="Head and tail still need work.",
            focus_pairs=["Squirrel_Head -> Squirrel_Body", "Squirrel_Tail -> Squirrel_Body"],
        ),
    )

    assert packets.packet_count == 2
    packet_by_scope = {packet.scope_label: packet for packet in packets.packets}
    assert packet_by_scope["Body + Head"].reference_ids == ["head_ref"]
    assert packet_by_scope["Tail"].reference_ids == ["tail_ref"]


def test_collect_compare_time_segmentation_support_treats_empty_parts_as_unavailable(monkeypatch):
    sidecar = SimpleNamespace(
        enabled=True,
        provider_name="generic_sidecar",
        endpoint="http://localhost:9100/segment",
        model="sam-sidecar-v1",
        api_key=None,
        api_key_env=None,
        timeout_seconds=15.0,
        max_parts=4,
    )
    responses = {"http://localhost:9100/segment": {"parts": []}}
    captured: list[dict[str, Any]] = []
    monkeypatch.setattr(
        compare_packets_area.httpx,
        "AsyncClient",
        lambda timeout=None: _FakeSupportAsyncClient(responses=responses, captured=captured),
    )

    result = asyncio.run(
        compare_packets_area.collect_compare_time_segmentation_support(
            config=sidecar,
            goal="low poly creature",
            packet_id="packet:front:test",
            packet_label="front packet",
            target_view="front",
            scope_label=None,
            target_objects=["Creature"],
            reference_records=[_reference("ref_front", label="front_ref", target_view="front")],
            captures=[_capture("target_front_after", preset_name="target_front")],
        )
    )

    assert captured
    assert result is not None
    assert result.status == "unavailable"
    assert result.provider_name == "generic_sidecar"
    assert result.parts == []
    assert any("returned no bounded parts" in note for note in result.notes)
    assert build_compare_support_evidence(None, part_segmentation=result) == []
