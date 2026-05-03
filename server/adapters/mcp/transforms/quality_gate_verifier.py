# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Deterministic quality-gate verification from existing scene truth payloads."""

from __future__ import annotations

import re
from typing import Any, Mapping, cast

from server.adapters.mcp.contracts.quality_gates import (
    GateEvidenceRefContract,
    GatePlanContract,
    GateStatusReasonCodeLiteral,
    GateVerifierResultContract,
    NormalizedQualityGateContract,
    refresh_gate_plan_status,
)
from server.adapters.mcp.contracts.scene import SceneRelationGraphPairContract, SceneRelationGraphPayloadContract


def verify_gate_plan_with_relation_graph(
    plan: GatePlanContract | Mapping[str, Any],
    relation_graph: SceneRelationGraphPayloadContract | Mapping[str, Any],
    *,
    spatial_state_version: int | None = None,
    scope_fingerprint: str | None = None,
    guided_part_registry: list[Mapping[str, Any]] | None = None,
) -> GatePlanContract:
    """Update gate statuses using authoritative ``scene_relation_graph`` evidence."""

    contract = GatePlanContract.model_validate(plan)
    payload = SceneRelationGraphPayloadContract.model_validate(relation_graph)
    updated_gates: list[NormalizedQualityGateContract] = []

    for gate in contract.gates:
        result = _verify_gate_with_relation_graph(
            gate,
            payload=payload,
            spatial_state_version=spatial_state_version,
            scope_fingerprint=scope_fingerprint,
            guided_part_registry=guided_part_registry,
        )
        if result is None:
            updated_gates.append(gate)
            continue
        updated_gates.append(
            gate.model_copy(
                update={
                    "status": result.status,
                    "status_reason": result.reason_code,
                    "evidence_refs": result.evidence_refs,
                    "verified_at_spatial_version": spatial_state_version,
                    "stale_since_spatial_version": None,
                    "recommended_bounded_tools": result.recommended_bounded_tools or gate.recommended_bounded_tools,
                }
            )
        )

    updated_gates = _apply_final_completion_status(updated_gates, spatial_state_version=spatial_state_version)
    return refresh_gate_plan_status(
        contract.model_copy(update={"gates": updated_gates}),
        last_verification_source="scene_relation_graph",
    )


def _verify_gate_with_relation_graph(
    gate: NormalizedQualityGateContract,
    *,
    payload: SceneRelationGraphPayloadContract,
    spatial_state_version: int | None,
    scope_fingerprint: str | None,
    guided_part_registry: list[Mapping[str, Any]] | None,
) -> GateVerifierResultContract | None:
    if gate.status == "waived":
        return None
    if _skip_local_scope_verification(
        gate,
        payload=payload,
        guided_part_registry=guided_part_registry,
    ):
        return None
    if gate.gate_type == "required_part":
        return _verify_required_part_gate(
            gate,
            payload=payload,
            spatial_state_version=spatial_state_version,
            scope_fingerprint=scope_fingerprint,
            guided_part_registry=guided_part_registry,
        )
    if gate.gate_type == "attachment_seam":
        return _verify_attachment_gate(
            gate,
            payload=payload,
            spatial_state_version=spatial_state_version,
            scope_fingerprint=scope_fingerprint,
        )
    if gate.gate_type == "support_contact":
        return _verify_support_gate(
            gate,
            payload=payload,
            spatial_state_version=spatial_state_version,
            scope_fingerprint=scope_fingerprint,
        )
    if gate.gate_type == "symmetry_pair":
        return _verify_symmetry_gate(
            gate,
            payload=payload,
            spatial_state_version=spatial_state_version,
            scope_fingerprint=scope_fingerprint,
        )
    return None


def _verify_required_part_gate(
    gate: NormalizedQualityGateContract,
    *,
    payload: SceneRelationGraphPayloadContract,
    spatial_state_version: int | None,
    scope_fingerprint: str | None,
    guided_part_registry: list[Mapping[str, Any]] | None,
) -> GateVerifierResultContract:
    object_names = list(payload.scope.object_names)
    if not object_names:
        return _blocked_result(gate, "missing_scope", tool_name="scene_relation_graph")

    matched_objects = _matched_scope_objects(
        gate,
        object_names,
        guided_part_registry=guided_part_registry,
    )
    expected_count = 2 if _target_implies_pair(gate) else 1
    status = "passed" if len(matched_objects) >= expected_count else "failed"
    reason_code: GateStatusReasonCodeLiteral | None = None if status == "passed" else "missing_required_part"
    evidence = GateEvidenceRefContract(
        evidence_id=f"scene_relation_graph:{gate.gate_id}:scope",
        evidence_kind="scene_truth",
        source="scene_truth",
        authority="authoritative",
        status="available",
        tool_name="scene_relation_graph",
        scope_fingerprint=scope_fingerprint,
        reason_code=reason_code,
        summary=f"Matched required part scope objects: {', '.join(matched_objects) or 'none'}.",
        metadata={
            "object_names": object_names,
            "matched_objects": matched_objects,
            "expected_count": expected_count,
            "spatial_state_version": spatial_state_version,
        },
    )
    return GateVerifierResultContract(
        gate_id=gate.gate_id,
        status=cast(Any, status),
        reason_code=reason_code,
        evidence_refs=[evidence],
        recommended_bounded_tools=gate.recommended_bounded_tools,
    )


def _verify_attachment_gate(
    gate: NormalizedQualityGateContract,
    *,
    payload: SceneRelationGraphPayloadContract,
    spatial_state_version: int | None,
    scope_fingerprint: str | None,
) -> GateVerifierResultContract:
    pair = _find_relation_pair(gate, payload.pairs, relation_kind="attachment")
    if pair is None:
        return _blocked_result(gate, "missing_relation_pair", tool_name="scene_relation_graph")
    if pair.error:
        return _blocked_result(
            gate,
            "relation_error",
            tool_name="scene_relation_graph",
            pair=pair,
            summary=pair.error,
            scope_fingerprint=scope_fingerprint,
        )
    semantics = pair.attachment_semantics
    if semantics is None:
        return _blocked_result(
            gate,
            "missing_authoritative_evidence",
            tool_name="scene_relation_graph",
            pair=pair,
            scope_fingerprint=scope_fingerprint,
        )

    verdict = semantics.attachment_verdict
    reason_code: GateStatusReasonCodeLiteral | None = None
    status = "failed"
    if verdict == "seated_contact":
        status = "passed"
    elif verdict == "intersecting" and gate.allow_embedded_intersection:
        status = "passed"
    elif verdict == "intersecting":
        reason_code = "relation_intersecting_not_allowed"
    elif verdict == "floating_gap":
        reason_code = "relation_floating_gap"
    elif verdict == "misaligned_attachment" and gate.allow_alignment_drift:
        status = "passed"
        reason_code = "alignment_drift_allowed"
    elif verdict == "misaligned_attachment":
        reason_code = "relation_misaligned"
    else:
        status = "blocked"
        reason_code = "verifier_needs_followup"

    return GateVerifierResultContract(
        gate_id=gate.gate_id,
        status=cast(Any, status),
        reason_code=reason_code,
        evidence_refs=[
            _relation_evidence_ref(
                gate,
                pair,
                reason_code=reason_code,
                scope_fingerprint=scope_fingerprint,
                spatial_state_version=spatial_state_version,
                verdict=verdict,
            )
        ],
        recommended_bounded_tools=_repair_tools_for_pair(gate, pair),
    )


def _verify_support_gate(
    gate: NormalizedQualityGateContract,
    *,
    payload: SceneRelationGraphPayloadContract,
    spatial_state_version: int | None,
    scope_fingerprint: str | None,
) -> GateVerifierResultContract:
    pair = _find_relation_pair(gate, payload.pairs, relation_kind="support")
    if pair is None:
        return _blocked_result(gate, "missing_relation_pair", tool_name="scene_relation_graph")
    if pair.error:
        return _blocked_result(
            gate,
            "relation_error",
            tool_name="scene_relation_graph",
            pair=pair,
            summary=pair.error,
            scope_fingerprint=scope_fingerprint,
        )
    semantics = pair.support_semantics
    if semantics is None:
        return _blocked_result(
            gate,
            "missing_authoritative_evidence",
            tool_name="scene_relation_graph",
            pair=pair,
            scope_fingerprint=scope_fingerprint,
        )

    status = "passed" if semantics.verdict == "supported" else "failed"
    reason_code: GateStatusReasonCodeLiteral | None = None
    if semantics.verdict == "supported":
        reason_code = "relation_supported"
    elif "floating_gap" in pair.relation_verdicts:
        reason_code = "relation_floating_gap"
    else:
        reason_code = "relation_unsupported"

    return GateVerifierResultContract(
        gate_id=gate.gate_id,
        status=cast(Any, status),
        reason_code=None if status == "passed" else reason_code,
        evidence_refs=[
            _relation_evidence_ref(
                gate,
                pair,
                reason_code=reason_code,
                scope_fingerprint=scope_fingerprint,
                spatial_state_version=spatial_state_version,
                verdict=semantics.verdict,
            )
        ],
        recommended_bounded_tools=_repair_tools_for_pair(gate, pair),
    )


def _verify_symmetry_gate(
    gate: NormalizedQualityGateContract,
    *,
    payload: SceneRelationGraphPayloadContract,
    spatial_state_version: int | None,
    scope_fingerprint: str | None,
) -> GateVerifierResultContract:
    object_names = list(payload.scope.object_names)
    if not object_names:
        return _blocked_result(gate, "missing_scope", tool_name="scene_relation_graph")

    matched_objects = _matched_scope_objects(gate, object_names)
    if len(matched_objects) < 2:
        evidence = GateEvidenceRefContract(
            evidence_id=f"scene_relation_graph:{gate.gate_id}:symmetry_scope",
            evidence_kind="scene_truth",
            source="scene_truth",
            authority="authoritative",
            status="available",
            tool_name="scene_relation_graph",
            scope_fingerprint=scope_fingerprint,
            reason_code="missing_required_part",
            summary=f"Matched symmetry pair scope objects: {', '.join(matched_objects) or 'none'}.",
            metadata={
                "object_names": object_names,
                "matched_objects": matched_objects,
                "expected_count": 2,
                "spatial_state_version": spatial_state_version,
            },
        )
        return GateVerifierResultContract(
            gate_id=gate.gate_id,
            status="failed",
            reason_code="missing_required_part",
            evidence_refs=[evidence],
            recommended_bounded_tools=gate.recommended_bounded_tools,
        )

    pair = _find_relation_pair(gate, payload.pairs, relation_kind="symmetry")
    if pair is None:
        return _blocked_result(gate, "missing_relation_pair", tool_name="scene_relation_graph")
    if pair.error:
        return _blocked_result(
            gate,
            "relation_error",
            tool_name="scene_relation_graph",
            pair=pair,
            summary=pair.error,
            scope_fingerprint=scope_fingerprint,
        )
    semantics = pair.symmetry_semantics
    if semantics is None:
        return _blocked_result(
            gate,
            "missing_authoritative_evidence",
            tool_name="scene_relation_graph",
            pair=pair,
            scope_fingerprint=scope_fingerprint,
        )

    status = "passed" if semantics.verdict == "symmetric" else "failed"
    reason_code: GateStatusReasonCodeLiteral | None = None if status == "passed" else "relation_asymmetric"
    return GateVerifierResultContract(
        gate_id=gate.gate_id,
        status=cast(Any, status),
        reason_code=reason_code,
        evidence_refs=[
            _symmetry_evidence_ref(
                gate,
                pair,
                reason_code=reason_code,
                scope_fingerprint=scope_fingerprint,
                spatial_state_version=spatial_state_version,
                verdict=semantics.verdict,
            )
        ],
        recommended_bounded_tools=_repair_tools_for_pair(gate, pair),
    )


def _apply_final_completion_status(
    gates: list[NormalizedQualityGateContract],
    *,
    spatial_state_version: int | None,
) -> list[NormalizedQualityGateContract]:
    non_final_blockers = [
        gate
        for gate in gates
        if gate.required
        and gate.gate_type != "final_completion"
        and gate.status in {"pending", "blocked", "failed", "stale"}
    ]
    updated: list[NormalizedQualityGateContract] = []
    for gate in gates:
        if gate.gate_type != "final_completion" or gate.status == "waived":
            updated.append(gate)
            continue
        if non_final_blockers:
            blocker_ids = [item.gate_id for item in non_final_blockers]
            updated.append(
                gate.model_copy(
                    update={
                        "status": "blocked",
                        "status_reason": "required_gate_unresolved",
                        "verified_at_spatial_version": spatial_state_version,
                        "recommended_bounded_tools": gate.recommended_bounded_tools,
                        "evidence_refs": [
                            GateEvidenceRefContract(
                                evidence_id=f"quality_gate_plan:{gate.gate_id}:aggregate",
                                evidence_kind="scene_truth",
                                source="scene_truth",
                                authority="authoritative",
                                status="available",
                                tool_name="scene_relation_graph",
                                reason_code="required_gate_unresolved",
                                summary="Required quality gates are unresolved.",
                                metadata={"blocking_gate_ids": blocker_ids},
                            )
                        ],
                    }
                )
            )
            continue
        updated.append(
            gate.model_copy(
                update={
                    "status": "passed",
                    "status_reason": None,
                    "verified_at_spatial_version": spatial_state_version,
                    "recommended_bounded_tools": gate.recommended_bounded_tools,
                    "evidence_refs": [
                        GateEvidenceRefContract(
                            evidence_id=f"quality_gate_plan:{gate.gate_id}:aggregate",
                            evidence_kind="scene_truth",
                            source="scene_truth",
                            authority="authoritative",
                            status="available",
                            tool_name="scene_relation_graph",
                            summary="All required non-final gates are passed or waived.",
                        )
                    ],
                }
            )
        )
    return updated


def _blocked_result(
    gate: NormalizedQualityGateContract,
    reason_code: GateStatusReasonCodeLiteral,
    *,
    tool_name: str,
    pair: SceneRelationGraphPairContract | None = None,
    summary: str | None = None,
    scope_fingerprint: str | None = None,
) -> GateVerifierResultContract:
    evidence_id = f"{tool_name}:{gate.gate_id}:blocked"
    if pair is not None:
        evidence_id = f"{tool_name}:{pair.pair_id}:{gate.gate_id}"
    evidence = GateEvidenceRefContract(
        evidence_id=evidence_id,
        evidence_kind="spatial_relation" if gate.gate_type in {"attachment_seam", "support_contact"} else "scene_truth",
        source="spatial_relation" if gate.gate_type in {"attachment_seam", "support_contact"} else "scene_truth",
        authority="authoritative",
        status="unavailable",
        tool_name=tool_name,
        scope_fingerprint=scope_fingerprint,
        relation_pair_id=None if pair is None else pair.pair_id,
        from_object=None if pair is None else pair.from_object,
        to_object=None if pair is None else pair.to_object,
        reason_code=reason_code,
        summary=summary or reason_code,
    )
    return GateVerifierResultContract(
        gate_id=gate.gate_id,
        status="blocked",
        reason_code=reason_code,
        evidence_refs=[evidence],
        recommended_bounded_tools=gate.recommended_bounded_tools,
    )


def _relation_evidence_ref(
    gate: NormalizedQualityGateContract,
    pair: SceneRelationGraphPairContract,
    *,
    reason_code: GateStatusReasonCodeLiteral | None,
    scope_fingerprint: str | None,
    spatial_state_version: int | None,
    verdict: str,
) -> GateEvidenceRefContract:
    return GateEvidenceRefContract(
        evidence_id=f"scene_relation_graph:{pair.pair_id}:{gate.gate_id}",
        evidence_kind="spatial_relation",
        source="spatial_relation",
        authority="authoritative",
        status="available",
        tool_name="scene_relation_graph",
        scope_fingerprint=scope_fingerprint,
        relation_pair_id=pair.pair_id,
        from_object=pair.from_object,
        to_object=pair.to_object,
        verdict=verdict,
        measured_value=pair.gap_distance,
        reason_code=reason_code,
        summary=f"{pair.from_object} -> {pair.to_object}: {verdict}.",
        metadata={
            "relation_kinds": pair.relation_kinds,
            "relation_verdicts": pair.relation_verdicts,
            "gap_relation": pair.gap_relation,
            "overlap_relation": pair.overlap_relation,
            "contact_passed": pair.contact_passed,
            "alignment_status": pair.alignment_status,
            "measurement_basis": pair.measurement_basis,
            "spatial_state_version": spatial_state_version,
        },
    )


def _symmetry_evidence_ref(
    gate: NormalizedQualityGateContract,
    pair: SceneRelationGraphPairContract,
    *,
    reason_code: GateStatusReasonCodeLiteral | None,
    scope_fingerprint: str | None,
    spatial_state_version: int | None,
    verdict: str,
) -> GateEvidenceRefContract:
    return GateEvidenceRefContract(
        evidence_id=f"scene_relation_graph:{pair.pair_id}:{gate.gate_id}:symmetry",
        evidence_kind="scene_truth",
        source="assertion_tool",
        authority="authoritative",
        status="available",
        tool_name="scene_relation_graph",
        scope_fingerprint=scope_fingerprint,
        relation_pair_id=pair.pair_id,
        from_object=pair.from_object,
        to_object=pair.to_object,
        verdict=verdict,
        reason_code=reason_code,
        summary=f"{pair.from_object} <-> {pair.to_object}: {verdict}.",
        metadata={
            "relation_kinds": pair.relation_kinds,
            "relation_verdicts": pair.relation_verdicts,
            "symmetry_left_object": None if pair.symmetry_semantics is None else pair.symmetry_semantics.left_object,
            "symmetry_right_object": None if pair.symmetry_semantics is None else pair.symmetry_semantics.right_object,
            "mirror_axis": None if pair.symmetry_semantics is None else pair.symmetry_semantics.axis,
            "mirror_coordinate": None if pair.symmetry_semantics is None else pair.symmetry_semantics.mirror_coordinate,
            "spatial_state_version": spatial_state_version,
        },
    )


def _find_relation_pair(
    gate: NormalizedQualityGateContract,
    pairs: list[SceneRelationGraphPairContract],
    *,
    relation_kind: str,
) -> SceneRelationGraphPairContract | None:
    candidates = [
        pair
        for pair in pairs
        if (relation_kind == "attachment" and pair.attachment_semantics is not None)
        or (relation_kind == "support" and pair.support_semantics is not None)
        or (relation_kind == "symmetry" and pair.symmetry_semantics is not None)
    ]
    if not candidates:
        return None

    target_names = {_normalize_name(item) for item in gate.target_objects if item}
    if len(target_names) >= 2:
        for pair in candidates:
            pair_names = {_normalize_name(pair.from_object), _normalize_name(pair.to_object)}
            if target_names.issubset(pair_names):
                return pair
            semantics_names = _semantic_object_names(pair)
            if target_names.issubset(semantics_names):
                return pair

    label_tokens = _target_tokens(gate.target_label or gate.label)
    if label_tokens:
        for pair in candidates:
            pair_tokens = _target_tokens(" ".join([pair.from_object, pair.to_object]))
            semantics_tokens = _target_tokens(" ".join(_semantic_object_names(pair)))
            if label_tokens.issubset(pair_tokens | semantics_tokens):
                return pair
    meaningful_label_tokens = _meaningful_target_tokens(gate.target_label or gate.label)
    if len(candidates) == 1 and meaningful_label_tokens:
        pair = candidates[0]
        pair_tokens = _target_tokens(" ".join([pair.from_object, pair.to_object]))
        semantics_tokens = _target_tokens(" ".join(_semantic_object_names(pair)))
        if meaningful_label_tokens.issubset(pair_tokens | semantics_tokens):
            return pair
    return None


def _skip_local_scope_verification(
    gate: NormalizedQualityGateContract,
    *,
    payload: SceneRelationGraphPayloadContract,
    guided_part_registry: list[Mapping[str, Any]] | None,
) -> bool:
    if payload.scope.scope_kind == "scene":
        return False

    object_names = list(payload.scope.object_names)
    if gate.gate_type == "required_part":
        expected_count = 2 if _target_implies_pair(gate) else 1
        matched_objects = _matched_scope_objects(
            gate,
            object_names,
            guided_part_registry=guided_part_registry,
        )
        return len(matched_objects) < expected_count

    if gate.gate_type == "symmetry_pair":
        matched_objects = _matched_scope_objects(
            gate,
            object_names,
            guided_part_registry=guided_part_registry,
        )
        return len(matched_objects) < 2

    if gate.gate_type in {"attachment_seam", "support_contact"}:
        return not _scope_contains_all_target_objects(gate, object_names)

    return False


def _matched_scope_objects(
    gate: NormalizedQualityGateContract,
    object_names: list[str],
    *,
    guided_part_registry: list[Mapping[str, Any]] | None = None,
) -> list[str]:
    if gate.target_kind == "object_role" and gate.target_label:
        target_role = _normalize_name(gate.target_label)
        role_matches = [
            str(item.get("object_name") or "").strip()
            for item in list(guided_part_registry or [])
            if _normalize_name(str(item.get("role") or "")) == target_role
        ]
        if role_matches:
            normalized_scope = {_normalize_name(name) for name in object_names}
            return [name for name in role_matches if _normalize_name(name) in normalized_scope]

    target_names = {_normalize_name(item) for item in gate.target_objects if item}
    if gate.target_kind == "object" and gate.target_label:
        target_names.add(_normalize_name(gate.target_label))
    if target_names:
        return [name for name in object_names if _normalize_name(name) in target_names]

    target_tokens = _target_tokens(gate.target_label or gate.label)
    if not target_tokens:
        return []
    meaningful_tokens = _meaningful_target_tokens(gate.target_label or gate.label)
    return [name for name in object_names if meaningful_tokens and meaningful_tokens & _target_tokens(name)]


def _meaningful_target_tokens(value: str | None) -> set[str]:
    weak_tokens = {
        "aligned",
        "alignment",
        "attachment",
        "contact",
        "core",
        "main",
        "mass",
        "pair",
        "part",
        "required",
        "seam",
        "support",
        "supported",
        "symmetry",
        "symmetric",
        "visible",
    }
    return {token for token in _target_tokens(value or "") if token not in weak_tokens}


def _target_implies_pair(gate: NormalizedQualityGateContract) -> bool:
    target = _normalize_name(gate.target_label or gate.label)
    return gate.gate_type == "symmetry_pair" or target.endswith("_pair") or "_pair_" in target


def _scope_contains_all_target_objects(
    gate: NormalizedQualityGateContract,
    object_names: list[str],
) -> bool:
    target_names = {_normalize_name(item) for item in gate.target_objects if item}
    if not target_names:
        return True
    scope_names = {_normalize_name(item) for item in object_names if item}
    return target_names.issubset(scope_names)


def _repair_tools_for_pair(
    gate: NormalizedQualityGateContract,
    pair: SceneRelationGraphPairContract,
) -> list[str]:
    tools = list(gate.recommended_bounded_tools)
    preferred_macro = None
    if pair.attachment_semantics is not None:
        preferred_macro = pair.attachment_semantics.preferred_macro
    if preferred_macro and preferred_macro not in tools:
        tools.append(preferred_macro)
    return tools


def _semantic_object_names(pair: SceneRelationGraphPairContract) -> set[str]:
    names = {_normalize_name(pair.from_object), _normalize_name(pair.to_object)}
    if pair.attachment_semantics is not None:
        names.add(_normalize_name(pair.attachment_semantics.part_object))
        names.add(_normalize_name(pair.attachment_semantics.anchor_object))
    if pair.support_semantics is not None:
        names.add(_normalize_name(pair.support_semantics.supported_object))
        names.add(_normalize_name(pair.support_semantics.support_object))
    if pair.symmetry_semantics is not None:
        names.add(_normalize_name(pair.symmetry_semantics.left_object))
        names.add(_normalize_name(pair.symmetry_semantics.right_object))
    return names


def _target_tokens(value: str) -> set[str]:
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value.strip())
    return {token for token in re.split(r"[^a-zA-Z0-9]+", normalized.lower()) if token}


def _normalize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")
