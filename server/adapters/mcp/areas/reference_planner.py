# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Planner and budget helpers for staged reference compare responses."""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal, cast

from server.adapters.mcp.areas.reference_compare_packets import (
    build_compare_packets as _service_build_compare_packets,
)
from server.adapters.mcp.areas.reference_compare_packets import (
    resolve_compare_complexity_tier as _service_resolve_compare_complexity_tier,
)
from server.adapters.mcp.areas.reference_compare_packets import (
    synthesize_packet_vision_result as _service_synthesize_packet_vision_result,
)
from server.adapters.mcp.areas.reference_truth import dedupe_names, pair_label
from server.adapters.mcp.contracts.reference import (
    ReferenceCompareComplexityTierLiteral,
    ReferenceCompareDiagnosticsContract,
    ReferenceComparePacketContract,
    ReferenceCompareStageCheckpointResponseContract,
    ReferenceCorrectionCandidateContract,
    ReferenceCorrectionPacketEvidenceRefContract,
    ReferenceCorrectionTruthEvidenceContract,
    ReferenceCorrectionVisionEvidenceContract,
    ReferenceImageRecordContract,
    ReferencePlannerBlockerContract,
    ReferencePlannerEvidenceSourceContract,
    ReferencePlannerSourceLiteral,
    ReferencePlannerTargetScopeContract,
    ReferenceRefinementHandoffContract,
    ReferenceRefinementRouteContract,
    ReferenceRefinementToolCandidateContract,
    ReferenceRepairPlannerDetailContract,
    ReferenceRepairPlannerSummaryContract,
)
from server.adapters.mcp.contracts.scene import (
    SceneAssembledTargetScopeContract,
    SceneRepairMacroCandidateContract,
    SceneTruthFollowupContract,
    SceneTruthFollowupItemContract,
)
from server.adapters.mcp.contracts.vision import VisionCaptureImageContract
from server.adapters.mcp.sampling.result_types import (
    VisionAssistContract,
)
from server.adapters.mcp.vision.config import (
    VISION_FAIL_SAFE_MAX_IMAGES,
    VISION_FAIL_SAFE_MAX_INPUT_CHARS,
    VISION_FAIL_SAFE_MAX_TOKENS,
)
from server.adapters.mcp.vision.runner import VISION_ASSIST_POLICY

LOW_POLY_HINTS: tuple[str, ...] = ("low poly", "low-poly", "blockout")
HARD_SURFACE_HINTS: tuple[str, ...] = (
    "housing",
    "panel",
    "button",
    "electronics",
    "electronic",
    "device",
    "pcb",
    "circuit",
    "connector",
    "wall",
    "roof",
    "window",
    "door",
    "building",
    "architecture",
    "tower",
)
GARMENT_HINTS: tuple[str, ...] = (
    "shirt",
    "sleeve",
    "hood",
    "jacket",
    "coat",
    "dress",
    "skirt",
    "pants",
    "trousers",
    "fabric",
    "cloth",
    "cape",
)
ANATOMY_HINTS: tuple[str, ...] = (
    "organ",
    "heart",
    "lung",
    "liver",
    "kidney",
    "artery",
    "vein",
    "tumor",
    "anatomy",
    "biological",
)
ORGANIC_HINTS: tuple[str, ...] = (
    "animal",
    "beaver",
    "creature",
    "character",
    "canine",
    "cat",
    "squirrel",
    "rabbit",
    "owl",
    "dog",
    "feline",
    "fox",
    "bird",
    "face",
    "quadruped",
    "snout",
    "ear",
    "tail",
    "limb",
    "muscle",
    "organic",
)
SCULPT_RECOMMENDED_TOOLS: tuple[str, ...] = (
    "sculpt_deform_region",
    "sculpt_smooth_region",
    "sculpt_inflate_region",
    "sculpt_pinch_region",
    "sculpt_crease_region",
)

_STRUCTURAL_RELATION_BLOCKER_KINDS: frozenset[str] = frozenset(
    {"contact_failure", "gap", "overlap", "attachment", "support", "symmetry", "measurement_error"}
)
_PROPORTION_BLOCKING_HINT_TYPES: frozenset[str] = frozenset({"rebalance_proportion"})


@dataclass(frozen=True, slots=True)
class HybridBudgetRuntime:
    """Configured and effective vision budget values for staged compare."""

    max_tokens: int
    max_images: int
    max_input_chars: int
    model_name: str | None
    configured_max_tokens: int
    configured_max_images: int
    configured_max_input_chars: int
    fail_safe_max_tokens: int
    fail_safe_max_images: int
    fail_safe_max_input_chars: int
    budget_clip_fields: tuple[str, ...]

    @property
    def budget_clipped(self) -> bool:
        return bool(self.budget_clip_fields)


def resolve_compare_complexity_tier(
    *,
    assembled_target_scope: SceneAssembledTargetScopeContract | None,
    reference_count: int,
    capture_count: int,
    focus_pair_count: int,
) -> ReferenceCompareComplexityTierLiteral:
    return _service_resolve_compare_complexity_tier(
        assembled_target_scope=assembled_target_scope,
        reference_count=reference_count,
        capture_count=capture_count,
        focus_pair_count=focus_pair_count,
    )


def build_compare_packets(
    *,
    target_view: str | None,
    captures: Sequence[VisionCaptureImageContract],
    reference_records: Sequence[ReferenceImageRecordContract],
    assembled_target_scope: SceneAssembledTargetScopeContract | None,
    truth_followup: SceneTruthFollowupContract | None,
    max_images_per_packet: int | None = None,
) -> ReferenceCompareDiagnosticsContract:
    return _service_build_compare_packets(
        target_view=target_view,
        captures=captures,
        reference_records=reference_records,
        assembled_target_scope=assembled_target_scope,
        truth_followup=truth_followup,
        max_images_per_packet=max_images_per_packet,
    )


def synthesize_packet_vision_result(
    packet_results: Sequence[tuple[ReferenceComparePacketContract, VisionAssistContract | None]],
) -> VisionAssistContract | None:
    return _service_synthesize_packet_vision_result(packet_results)


def _contains_any(text: str, hints: tuple[str, ...]) -> bool:
    normalized = text.lower()
    return any(hint in normalized for hint in hints)


def _refinement_context_text(compare_result: ReferenceCompareStageCheckpointResponseContract) -> str:
    parts = [
        str(compare_result.goal or ""),
        str(compare_result.target_object or ""),
        str(compare_result.collection_name or ""),
        *list(compare_result.target_objects or []),
    ]
    return " | ".join(part for part in parts if part)


def _classify_refinement_domain(
    compare_result: ReferenceCompareStageCheckpointResponseContract,
) -> Literal["assembly", "hard_surface", "soft_surface", "organic_form", "garment", "anatomy", "generic_form"]:
    context_text = _refinement_context_text(compare_result)
    truth_followup = compare_result.truth_followup
    if truth_followup is not None and (truth_followup.focus_pairs or truth_followup.macro_candidates):
        return "assembly"
    if _contains_any(context_text, GARMENT_HINTS):
        return "garment"
    if _contains_any(context_text, ANATOMY_HINTS):
        return "anatomy"
    if _contains_any(context_text, HARD_SURFACE_HINTS):
        return "hard_surface"
    if _contains_any(context_text, ORGANIC_HINTS):
        return "organic_form"
    return "generic_form"


def _planner_target_scope(
    compare_result: ReferenceCompareStageCheckpointResponseContract,
    *,
    local_region_hint: str | None = None,
) -> ReferencePlannerTargetScopeContract | None:
    assembled_scope = compare_result.assembled_target_scope
    if assembled_scope is not None:
        return ReferencePlannerTargetScopeContract(
            scope_kind=assembled_scope.scope_kind,
            target_object=compare_result.target_object or assembled_scope.primary_target,
            target_objects=list(assembled_scope.object_names or []),
            collection_name=assembled_scope.collection_name,
            local_region_hint=local_region_hint,
        )

    target_objects = dedupe_names(
        [
            *(compare_result.target_objects or []),
            *([compare_result.target_object] if compare_result.target_object else []),
        ]
    )
    if target_objects or compare_result.collection_name:
        scope_kind: Literal["single_object", "object_set", "collection", "scene", "unknown"]
        if compare_result.collection_name:
            scope_kind = "collection"
        elif len(target_objects) == 1:
            scope_kind = "single_object"
        else:
            scope_kind = "object_set"
        return ReferencePlannerTargetScopeContract(
            scope_kind=scope_kind,
            target_object=compare_result.target_object or (target_objects[0] if len(target_objects) == 1 else None),
            target_objects=target_objects,
            collection_name=compare_result.collection_name,
            local_region_hint=local_region_hint,
        )

    return None


def _candidate_ids_with_structural_relation_blockers(
    candidates: list[ReferenceCorrectionCandidateContract],
) -> list[str]:
    candidate_ids: list[str] = []
    for candidate in candidates:
        truth_evidence = candidate.truth_evidence
        if truth_evidence is None:
            continue
        if any(kind in _STRUCTURAL_RELATION_BLOCKER_KINDS for kind in truth_evidence.item_kinds):
            candidate_ids.append(candidate.candidate_id)
    return candidate_ids


def _relation_planner_blockers(
    candidates: list[ReferenceCorrectionCandidateContract],
) -> list[ReferencePlannerBlockerContract]:
    candidate_ids = _candidate_ids_with_structural_relation_blockers(candidates)
    if not candidate_ids:
        return []
    return [
        ReferencePlannerBlockerContract(
            blocker_id="relation_structural_failure",
            category="relation",
            severity="blocking",
            reason=(
                "Unresolved attachment/contact/support/symmetry/gap/overlap truth evidence still dominates, "
                "so sculpt-region handoff is blocked until the structural relation is repaired or re-inspected."
            ),
            candidate_ids=candidate_ids,
            recommended_tool="scene_relation_graph",
        )
    ]


def _view_planner_blockers(
    compare_result: ReferenceCompareStageCheckpointResponseContract,
    *,
    require_view_evidence: bool,
) -> list[ReferencePlannerBlockerContract]:
    hints = compare_result.view_diagnostics_hints
    if hints is None:
        if not require_view_evidence:
            return []
        target_scope = _planner_target_scope(compare_result)
        target_object = (
            target_scope.target_object
            if target_scope is not None and target_scope.target_object
            else compare_result.target_object
        )
        arguments_hint: dict[str, object] = {}
        if target_object:
            arguments_hint["target_object"] = target_object
        return [
            ReferencePlannerBlockerContract(
                blocker_id="view_diagnostics_required",
                category="view",
                severity="blocking",
                reason=(
                    "Staged compare did not carry typed view-diagnostics evidence. Run scene_view_diagnostics(...) "
                    "for the intended local target before treating sculpt-region handoff as ready."
                ),
                recommended_tool="scene_view_diagnostics",
                arguments_hint=arguments_hint or None,
            )
        ]

    blockers: list[ReferencePlannerBlockerContract] = []
    for index, hint in enumerate(hints, start=1):
        blockers.append(
            ReferencePlannerBlockerContract(
                blocker_id=f"view_{hint.trigger}_{index}",
                category="view",
                severity="blocking",
                reason=hint.reason,
                recommended_tool=hint.recommended_tool,
                arguments_hint=hint.arguments_hint,
            )
        )
    return blockers


def _proportion_planner_blockers(
    compare_result: ReferenceCompareStageCheckpointResponseContract,
    *,
    low_poly_intent: bool,
) -> list[ReferencePlannerBlockerContract]:
    blockers: list[ReferencePlannerBlockerContract] = []
    proportion_hint_ids = [
        hint.hint_id
        for hint in list(compare_result.action_hints or [])
        if hint.hint_type in _PROPORTION_BLOCKING_HINT_TYPES
    ]
    if proportion_hint_ids:
        blockers.append(
            ReferencePlannerBlockerContract(
                blocker_id="proportion_nonlocal_drift",
                category="proportion",
                severity="blocking",
                reason=(
                    "Deterministic silhouette/proportion metrics still indicate a non-local proportion issue, "
                    "so macro or mesh/modeling correction is safer than local sculpt."
                ),
                candidate_ids=proportion_hint_ids,
                recommended_tool="scene_assert_proportion",
            )
        )
    if low_poly_intent:
        blockers.append(
            ReferencePlannerBlockerContract(
                blocker_id="low_poly_blockout_not_local_sculpt",
                category="proportion",
                severity="warning",
                reason=(
                    "The active goal is a low-poly/blockout refinement. Preserve plane and silhouette control with "
                    "mesh/modeling edits before using local sculpt smoothing."
                ),
            )
        )
    return blockers


def _local_form_reason(compare_result: ReferenceCompareStageCheckpointResponseContract) -> str | None:
    for candidate in list(compare_result.correction_candidates or []):
        vision_evidence = candidate.vision_evidence
        if vision_evidence is None:
            continue
        for item in [
            *list(vision_evidence.correction_focus or []),
            *list(vision_evidence.shape_mismatches or []),
            *list(vision_evidence.next_corrections or []),
        ]:
            text = str(item or "").strip()
            if text:
                return text
    if compare_result.silhouette_analysis is not None and compare_result.silhouette_analysis.status == "available":
        return "Silhouette metrics point to bounded local-form refinement."
    return None


def _planner_source_signals(
    *,
    candidates: list[ReferenceCorrectionCandidateContract],
    compare_result: ReferenceCompareStageCheckpointResponseContract,
) -> list[ReferencePlannerSourceLiteral]:
    signals: list[ReferencePlannerSourceLiteral] = ["scope", "naming"]
    if any(candidate.truth_evidence is not None for candidate in candidates):
        signals.extend(["truth", "relation"])
    if any(
        candidate.truth_evidence is not None and bool(candidate.truth_evidence.macro_candidates)
        for candidate in candidates
    ):
        signals.append("macro")
    if any(candidate.vision_evidence is not None for candidate in candidates):
        signals.append("vision")
    if compare_result.view_diagnostics_hints is not None:
        signals.append("view")
    if compare_result.silhouette_analysis is not None:
        signals.append("silhouette")
    if compare_result.budget_control is not None:
        signals.append("budget")
    return list(dict.fromkeys(signals))


def _planner_provenance(
    compare_result: ReferenceCompareStageCheckpointResponseContract,
    *,
    candidates: list[ReferenceCorrectionCandidateContract],
    source_signals: list[ReferencePlannerSourceLiteral],
) -> list[ReferencePlannerEvidenceSourceContract]:
    candidate_ids = [candidate.candidate_id for candidate in candidates]
    provenance: list[ReferencePlannerEvidenceSourceContract] = []
    if "scope" in source_signals:
        target_scope = _planner_target_scope(compare_result)
        scope_summary = (
            f"{target_scope.scope_kind} scope with {len(target_scope.target_objects)} object(s)"
            if target_scope is not None
            else "No explicit target scope was available."
        )
        provenance.append(
            ReferencePlannerEvidenceSourceContract(
                source_id="scope",
                source_class="scope",
                summary=scope_summary,
                tool_name="scene_scope_graph",
            )
        )
    if "truth" in source_signals or "relation" in source_signals:
        provenance.append(
            ReferencePlannerEvidenceSourceContract(
                source_id="truth_followup",
                source_class="truth",
                summary="Truth follow-up and relation evidence were used before vision-only correction hints.",
                candidate_ids=[
                    candidate.candidate_id for candidate in candidates if candidate.truth_evidence is not None
                ],
                tool_name="scene_relation_graph",
            )
        )
    if "macro" in source_signals:
        provenance.append(
            ReferencePlannerEvidenceSourceContract(
                source_id="macro_candidates",
                source_class="macro",
                summary="Macro repair candidates are available for unresolved structural relations.",
                candidate_ids=[
                    candidate.candidate_id
                    for candidate in candidates
                    if candidate.truth_evidence is not None and candidate.truth_evidence.macro_candidates
                ],
            )
        )
    if "vision" in source_signals:
        provenance.append(
            ReferencePlannerEvidenceSourceContract(
                source_id="vision_candidates",
                source_class="vision",
                summary="Vision mismatch text is advisory and can prioritize local-form attention.",
                candidate_ids=[
                    candidate.candidate_id for candidate in candidates if candidate.vision_evidence is not None
                ],
            )
        )
    if "view" in source_signals:
        provenance.append(
            ReferencePlannerEvidenceSourceContract(
                source_id="view_diagnostics_hints",
                source_class="view",
                summary="View diagnostics hints constrain whether a local target is visible and framed enough.",
                tool_name="scene_view_diagnostics",
            )
        )
    if "silhouette" in source_signals:
        provenance.append(
            ReferencePlannerEvidenceSourceContract(
                source_id="silhouette_analysis",
                source_class="silhouette",
                summary="Deterministic silhouette metrics can recommend inspection, proportion, or local-form work.",
                candidate_ids=candidate_ids,
            )
        )
    if "budget" in source_signals:
        provenance.append(
            ReferencePlannerEvidenceSourceContract(
                source_id="budget_control",
                source_class="budget",
                summary="Model-aware budget control bounded the emitted evidence and planner detail.",
            )
        )
    return provenance


def _support_tools_from_blockers(
    blockers: list[ReferencePlannerBlockerContract],
) -> list[ReferenceRefinementToolCandidateContract]:
    tools: list[ReferenceRefinementToolCandidateContract] = []
    seen: set[str] = set()
    for blocker in blockers:
        tool_name = blocker.recommended_tool
        if not tool_name or tool_name in seen:
            continue
        seen.add(tool_name)
        tools.append(
            ReferenceRefinementToolCandidateContract(
                tool_name=tool_name,
                reason=blocker.reason,
                priority="high" if blocker.severity == "blocking" else "normal",
                arguments_hint=blocker.arguments_hint,
            )
        )
    return tools


def select_refinement_route(
    compare_result: ReferenceCompareStageCheckpointResponseContract,
) -> ReferenceRefinementRouteContract:
    candidates = list(compare_result.correction_candidates or [])
    domain = _classify_refinement_domain(compare_result)
    target_scope = _planner_target_scope(compare_result)
    if not candidates:
        return ReferenceRefinementRouteContract(
            domain_classification=domain,
            selected_family="inspect_only",
            reason="No ranked correction candidates are available for deterministic refinement routing.",
            source_signals=[],
            candidate_ids=[],
            target_scope=target_scope,
            detail_available=False,
        )

    candidate_ids = [candidate.candidate_id for candidate in candidates]
    has_macro = any(
        candidate.truth_evidence is not None and bool(candidate.truth_evidence.macro_candidates)
        for candidate in candidates
    )
    has_vision_only = any(candidate.candidate_kind == "vision_only" for candidate in candidates)
    low_poly_intent = _contains_any(_refinement_context_text(compare_result), LOW_POLY_HINTS)
    source_signals = _planner_source_signals(candidates=candidates, compare_result=compare_result)
    relation_blockers = _relation_planner_blockers(candidates)
    proportion_blockers = _proportion_planner_blockers(compare_result, low_poly_intent=low_poly_intent)

    if relation_blockers or has_macro or domain == "assembly":
        return ReferenceRefinementRouteContract(
            domain_classification=domain,
            selected_family="macro",
            reason=(
                "Assembly-oriented truth/macro signals dominate, so bounded macro repair remains the primary "
                "refinement family."
            ),
            source_signals=source_signals,
            candidate_ids=candidate_ids,
            target_scope=target_scope,
            blockers=relation_blockers,
            detail_available=True,
        )

    view_hint_blockers = _view_planner_blockers(compare_result, require_view_evidence=False)
    if view_hint_blockers:
        return ReferenceRefinementRouteContract(
            domain_classification=domain,
            selected_family="inspect_only",
            reason=(
                "Typed view diagnostics reported visibility or framing blockers, so inspect/view correction must "
                "happen before local-form or sculpt-region refinement."
            ),
            source_signals=source_signals,
            candidate_ids=candidate_ids,
            target_scope=target_scope,
            blockers=view_hint_blockers,
            detail_available=True,
        )

    blocking_proportion = [blocker for blocker in proportion_blockers if blocker.severity == "blocking"]
    if blocking_proportion:
        return ReferenceRefinementRouteContract(
            domain_classification=domain,
            selected_family="modeling_mesh",
            reason=(
                "Non-local proportion drift remains, so bounded modeling/mesh or macro correction is safer than "
                "a local sculpt-region handoff."
            ),
            source_signals=source_signals,
            candidate_ids=candidate_ids,
            target_scope=target_scope,
            blockers=proportion_blockers,
            detail_available=True,
        )

    if domain in {"garment", "anatomy", "organic_form"} and has_vision_only and not low_poly_intent:
        view_evidence_blockers = _view_planner_blockers(compare_result, require_view_evidence=True)
        if view_evidence_blockers:
            return ReferenceRefinementRouteContract(
                domain_classification=domain,
                selected_family="inspect_only",
                reason=(
                    "Organic/local-form evidence is present, but staged view evidence is missing or blocking; "
                    "run view diagnostics before recommending sculpt-region tools."
                ),
                source_signals=source_signals,
                candidate_ids=candidate_ids,
                target_scope=target_scope,
                blockers=view_evidence_blockers,
                detail_available=True,
            )
        return ReferenceRefinementRouteContract(
            domain_classification=domain,
            selected_family="sculpt_region",
            reason=(
                "Local soft/organic-form refinement dominates without strong assembly signals, so deterministic "
                "sculpt-region tools are the preferred family."
            ),
            source_signals=source_signals,
            candidate_ids=candidate_ids,
            target_scope=_planner_target_scope(compare_result, local_region_hint=_local_form_reason(compare_result)),
            detail_available=True,
        )

    if domain in {"hard_surface", "generic_form", "soft_surface"} or low_poly_intent:
        return ReferenceRefinementRouteContract(
            domain_classification=domain,
            selected_family="modeling_mesh",
            reason=(
                "Current signals do not justify sculpt; bounded modeling/mesh refinement remains the safer default "
                "family."
            ),
            source_signals=source_signals,
            candidate_ids=candidate_ids,
            target_scope=target_scope,
            blockers=proportion_blockers,
            detail_available=True,
        )

    return ReferenceRefinementRouteContract(
        domain_classification=domain,
        selected_family="modeling_mesh",
        reason="Falling back to bounded modeling/mesh refinement because no stronger deterministic family gate was met.",
        source_signals=source_signals,
        candidate_ids=candidate_ids,
        target_scope=target_scope,
        detail_available=True,
    )


def build_refinement_handoff(
    compare_result: ReferenceCompareStageCheckpointResponseContract,
    route: ReferenceRefinementRouteContract,
) -> ReferenceRefinementHandoffContract:
    blockers = list(route.blockers or [])
    target_scope = route.target_scope or _planner_target_scope(compare_result)
    if route.selected_family != "sculpt_region":
        state: Literal["ready", "blocked", "suppressed"] = "blocked" if blockers else "suppressed"
        message = (
            "Sculpt-region handoff is blocked by the listed preconditions; follow the support tools before sculpting."
            if blockers
            else "Continue with the selected bounded refinement family; no sculpt handoff is recommended."
        )
        return ReferenceRefinementHandoffContract(
            selected_family=route.selected_family,
            state=state,
            message=message,
            target_object=target_scope.target_object if target_scope is not None else compare_result.target_object,
            target_scope=target_scope,
            local_reason=target_scope.local_region_hint if target_scope is not None else None,
            blockers=blockers,
            eligible_tool_names=list(SCULPT_RECOMMENDED_TOOLS),
            recommended_tools=[],
        )

    target_object = target_scope.target_object if target_scope is not None else compare_result.target_object
    arguments_hint = cast(dict[str, object] | None, {"object_name": target_object} if target_object else None)
    return ReferenceRefinementHandoffContract(
        selected_family="sculpt_region",
        state="ready",
        message=(
            "A deterministic sculpt-region path is recommended for the next refinement step. "
            "Keep the scope narrow and use only bounded sculpt-region tools."
        ),
        target_object=target_object,
        target_scope=target_scope,
        local_reason=target_scope.local_region_hint if target_scope is not None else _local_form_reason(compare_result),
        blockers=[],
        eligible_tool_names=list(SCULPT_RECOMMENDED_TOOLS),
        visibility_unlock_recommended=False,
        recommended_tools=[
            ReferenceRefinementToolCandidateContract(
                tool_name=tool_name,
                reason=(
                    "Deterministic local-form refinement is a better fit than more assembly-oriented "
                    "mesh/modeling edits."
                ),
                priority=(
                    "high"
                    if tool_name in {"sculpt_deform_region", "sculpt_smooth_region", "sculpt_crease_region"}
                    else "normal"
                ),
                arguments_hint=arguments_hint,
            )
            for tool_name in SCULPT_RECOMMENDED_TOOLS
        ],
    )


def build_repair_planner_summary(
    compare_result: ReferenceCompareStageCheckpointResponseContract,
    *,
    route: ReferenceRefinementRouteContract,
    handoff: ReferenceRefinementHandoffContract,
) -> ReferenceRepairPlannerSummaryContract:
    candidates = list(compare_result.correction_candidates or [])
    provenance = _planner_provenance(
        compare_result,
        candidates=candidates,
        source_signals=list(route.source_signals or []),
    )
    blockers = list(route.blockers or handoff.blockers or [])
    return ReferenceRepairPlannerSummaryContract(
        selected_family=route.selected_family,
        target_scope=route.target_scope or handoff.target_scope,
        rationale=route.reason,
        provenance=provenance,
        blockers=blockers,
        detail_available=route.detail_available,
        required_support_tools=_support_tools_from_blockers(blockers),
    )


def build_repair_planner_detail(
    compare_result: ReferenceCompareStageCheckpointResponseContract,
    *,
    summary: ReferenceRepairPlannerSummaryContract,
    route: ReferenceRefinementRouteContract,
    handoff: ReferenceRefinementHandoffContract,
    detail_trimmed: bool,
) -> ReferenceRepairPlannerDetailContract:
    notes: list[str] = []
    if detail_trimmed:
        notes.append("Planner detail reflects trimmed staged compare evidence after budget control was applied.")
    if handoff.selected_family == "sculpt_region" and handoff.visibility_unlock_recommended is False:
        notes.append("Sculpt handoff is recommendation-only and does not unlock guided sculpt visibility by itself.")
    return ReferenceRepairPlannerDetailContract(
        summary=summary,
        route=route,
        handoff=handoff,
        candidate_ids=list(route.candidate_ids or []),
        notes=notes,
        detail_trimmed=detail_trimmed,
    )


def model_budget_bias(model_name: str | None) -> int:
    normalized = str(model_name or "").lower()
    if re.search(r"(^|[-_./:])(2b|3b|4b|mini)($|[-_./:])", normalized):
        return -1
    if any(token in normalized for token in ("27b", "70b", "72b", "grok")):
        return 1
    return 0


def effective_pair_budget(*, max_tokens: int, model_name: str | None) -> int:
    if max_tokens <= 256:
        base = 2
    elif max_tokens <= 400:
        base = 3
    elif max_tokens <= 600:
        base = 4
    elif max_tokens <= 1000:
        base = 5
    else:
        base = 6
    return max(2, min(8, base + model_budget_bias(model_name)))


def effective_candidate_budget(*, pair_budget: int, max_tokens: int, model_name: str | None) -> int:
    base = pair_budget + 1
    if max_tokens <= 256:
        base = min(base, 3)
    elif max_tokens <= 400:
        base = min(base, 4)
    else:
        base = min(base, 6 + model_budget_bias(model_name))
    return max(2, base)


def trim_correction_candidates(
    candidates: list[ReferenceCorrectionCandidateContract],
    *,
    candidate_budget: int,
) -> tuple[list[ReferenceCorrectionCandidateContract], bool]:
    if len(candidates) <= candidate_budget:
        return candidates, False
    return list(candidates[:candidate_budget]), True


def _runtime_budget_clip_fields(
    *,
    configured_max_tokens: int,
    configured_max_images: int,
    configured_max_input_chars: int,
    effective_max_tokens: int,
    effective_max_images: int,
    effective_max_input_chars: int,
) -> tuple[str, ...]:
    clipped_fields: list[str] = []
    if effective_max_images < configured_max_images:
        clipped_fields.append("max_images")
    if effective_max_input_chars < configured_max_input_chars:
        clipped_fields.append("max_input_chars")
    if effective_max_tokens < configured_max_tokens:
        clipped_fields.append("max_output_tokens")
    return tuple(clipped_fields)


def resolve_hybrid_budget_runtime(resolver: Any) -> HybridBudgetRuntime:
    runtime_config = getattr(resolver, "runtime_config", None)
    if runtime_config is None:
        return HybridBudgetRuntime(
            max_tokens=VISION_ASSIST_POLICY.max_tokens,
            max_images=8,
            max_input_chars=VISION_ASSIST_POLICY.max_input_chars,
            model_name=None,
            configured_max_tokens=VISION_ASSIST_POLICY.max_tokens,
            configured_max_images=8,
            configured_max_input_chars=VISION_ASSIST_POLICY.max_input_chars,
            fail_safe_max_tokens=VISION_FAIL_SAFE_MAX_TOKENS,
            fail_safe_max_images=VISION_FAIL_SAFE_MAX_IMAGES,
            fail_safe_max_input_chars=VISION_FAIL_SAFE_MAX_INPUT_CHARS,
            budget_clip_fields=(),
        )

    configured_max_tokens = int(getattr(runtime_config, "max_tokens", VISION_ASSIST_POLICY.max_tokens))
    configured_max_images = int(getattr(runtime_config, "max_images", 8))
    configured_max_input_chars = int(getattr(runtime_config, "max_input_chars", VISION_ASSIST_POLICY.max_input_chars))
    effective_max_tokens = int(
        getattr(runtime_config, "effective_max_tokens", min(configured_max_tokens, VISION_FAIL_SAFE_MAX_TOKENS))
    )
    effective_max_images = int(
        getattr(runtime_config, "effective_max_images", min(configured_max_images, VISION_FAIL_SAFE_MAX_IMAGES))
    )
    effective_max_input_chars = int(
        getattr(
            runtime_config,
            "effective_max_input_chars",
            min(configured_max_input_chars, VISION_FAIL_SAFE_MAX_INPUT_CHARS),
        )
    )
    budget_clip_fields = tuple(
        getattr(
            runtime_config,
            "budget_clip_fields",
            _runtime_budget_clip_fields(
                configured_max_tokens=configured_max_tokens,
                configured_max_images=configured_max_images,
                configured_max_input_chars=configured_max_input_chars,
                effective_max_tokens=effective_max_tokens,
                effective_max_images=effective_max_images,
                effective_max_input_chars=effective_max_input_chars,
            ),
        )
    )
    return HybridBudgetRuntime(
        max_tokens=effective_max_tokens,
        max_images=effective_max_images,
        max_input_chars=effective_max_input_chars,
        model_name=cast(str | None, getattr(runtime_config, "active_model_name", None)),
        configured_max_tokens=configured_max_tokens,
        configured_max_images=configured_max_images,
        configured_max_input_chars=configured_max_input_chars,
        fail_safe_max_tokens=VISION_FAIL_SAFE_MAX_TOKENS,
        fail_safe_max_images=VISION_FAIL_SAFE_MAX_IMAGES,
        fail_safe_max_input_chars=VISION_FAIL_SAFE_MAX_INPUT_CHARS,
        budget_clip_fields=budget_clip_fields,
    )


def normalize_focus_key(value: str) -> str:
    return " ".join(value.strip().lower().split())


def resolve_actionable_focus(compare_result: ReferenceCompareStageCheckpointResponseContract) -> list[str]:
    candidate_summaries = list(compare_result.correction_candidates or [])
    if candidate_summaries:
        deduped_candidates: list[str] = []
        seen_candidates: set[str] = set()
        for candidate in candidate_summaries:
            normalized = normalize_focus_key(candidate.summary)
            if not normalized or normalized in seen_candidates:
                continue
            seen_candidates.add(normalized)
            deduped_candidates.append(candidate.summary)
        if deduped_candidates:
            return deduped_candidates[:3]

    vision_result = compare_result.vision_assistant.result if compare_result.vision_assistant else None
    if vision_result is None:
        return []

    ordered = list(vision_result.correction_focus or [])
    if not ordered:
        ordered.extend(vision_result.shape_mismatches or [])
        ordered.extend(vision_result.proportion_mismatches or [])
        ordered.extend(vision_result.next_corrections or [])

    deduped: list[str] = []
    seen: set[str] = set()
    for item in ordered:
        normalized = normalize_focus_key(item)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(item)
    return deduped[:3]


def resolve_gate_blocker_focus(compare_result: ReferenceCompareStageCheckpointResponseContract) -> list[str]:
    blockers = list(compare_result.completion_blockers or [])
    if not blockers:
        return []

    deduped: list[str] = []
    seen: set[str] = set()
    for blocker in blockers:
        item = (blocker.message or blocker.label or blocker.target_label or blocker.gate_id).strip()
        normalized = normalize_focus_key(item)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(item)
    return deduped[:3]


def should_inspect_from_truth_signal(
    correction_candidates: list[ReferenceCorrectionCandidateContract],
) -> bool:
    if not correction_candidates:
        return False

    for candidate in correction_candidates:
        if candidate.priority != "high":
            continue
        truth_evidence = candidate.truth_evidence
        if truth_evidence is None:
            continue
        if any(
            kind in {"contact_failure", "overlap", "attachment", "support", "symmetry", "measurement_error"}
            for kind in truth_evidence.item_kinds
        ):
            return True
    return False


def _candidate_matches_pair_label(focus_item: str, current_pair_label: str) -> bool:
    normalized_focus = normalize_focus_key(focus_item)
    normalized_pair = normalize_focus_key(current_pair_label)
    if not normalized_focus or not normalized_pair:
        return False
    if normalized_pair in normalized_focus:
        return True
    from_object, to_object = current_pair_label.split(" -> ", 1)
    return normalize_focus_key(from_object) in normalized_focus and normalize_focus_key(to_object) in normalized_focus


def _macro_candidate_matches_pair(
    candidate: SceneRepairMacroCandidateContract,
    *,
    from_object: str,
    to_object: str,
) -> bool:
    arguments = candidate.arguments_hint or {}
    candidate_from = (
        arguments.get("part_object")
        or arguments.get("left_object")
        or arguments.get("primary_object")
        or arguments.get("supported_object")
    )
    candidate_to = (
        arguments.get("reference_object")
        or arguments.get("surface_object")
        or arguments.get("right_object")
        or arguments.get("support_object")
    )
    return (candidate_from == from_object and candidate_to == to_object) or (
        candidate_from == to_object and candidate_to == from_object
    )


def _build_vision_candidate_evidence(
    *,
    vision_result,
    focus_items: list[str],
    compare_diagnostics: ReferenceCompareDiagnosticsContract | None,
) -> ReferenceCorrectionVisionEvidenceContract | None:
    if vision_result is None or not focus_items:
        return None
    return ReferenceCorrectionVisionEvidenceContract(
        correction_focus=focus_items,
        shape_mismatches=list(vision_result.shape_mismatches or []),
        proportion_mismatches=list(vision_result.proportion_mismatches or []),
        next_corrections=list(vision_result.next_corrections or []),
        packet_evidence_refs=_packet_evidence_refs_for_focus(compare_diagnostics, focus_items=focus_items),
    )


def _packet_evidence_refs_for_focus(
    compare_diagnostics: ReferenceCompareDiagnosticsContract | None,
    *,
    focus_items: Sequence[str],
) -> list[ReferenceCorrectionPacketEvidenceRefContract]:
    """Return bounded candidate-level refs; packet detail remains in compare_diagnostics."""

    if compare_diagnostics is None:
        return []

    normalized_focus = [normalize_focus_key(item) for item in focus_items if normalize_focus_key(item)]
    if not normalized_focus:
        return []

    refs: list[ReferenceCorrectionPacketEvidenceRefContract] = []
    seen_packet_ids: set[str] = set()
    for packet in compare_diagnostics.packets:
        packet_texts = [
            *list(packet.correction_focus or []),
            *([packet.evidence_summary] if packet.evidence_summary else []),
            *([packet.status_reason] if packet.status_reason else []),
        ]
        normalized_packet_texts = [normalize_focus_key(item) for item in packet_texts if normalize_focus_key(item)]
        if not any(
            focus == packet_text or focus in packet_text or packet_text in focus
            for focus in normalized_focus
            for packet_text in normalized_packet_texts
        ):
            continue
        if packet.packet_id in seen_packet_ids:
            continue
        seen_packet_ids.add(packet.packet_id)
        refs.append(
            ReferenceCorrectionPacketEvidenceRefContract(
                packet_id=packet.packet_id,
                packet_label=packet.packet_label,
                target_view=packet.target_view,
                scope_label=packet.scope_label,
                extraction_status=packet.extraction_status,
                ranking_status=packet.ranking_status,
                packet_status=packet.packet_status,
                evidence_summary=packet.evidence_summary,
                support_evidence_count=len(packet.support_evidence or []),
            )
        )
    return refs[:4]


def build_correction_candidates(
    compare_result: ReferenceCompareStageCheckpointResponseContract,
) -> list[ReferenceCorrectionCandidateContract]:
    truth_followup = compare_result.truth_followup
    vision_result = compare_result.vision_assistant.result if compare_result.vision_assistant else None
    correction_focus = resolve_actionable_focus(compare_result)
    candidates: list[ReferenceCorrectionCandidateContract] = []
    used_focus_items: set[str] = set()
    rank = 1
    focus_pairs = list(truth_followup.focus_pairs or []) if truth_followup is not None else []

    truth_items_by_pair: dict[str, list[SceneTruthFollowupItemContract]] = {}
    for item in list(truth_followup.items or []) if truth_followup is not None else []:
        if item.from_object is None or item.to_object is None:
            continue
        current_pair_label = pair_label(item.from_object, item.to_object)
        truth_items_by_pair.setdefault(current_pair_label, []).append(item)

    truth_macros_by_pair: dict[str, list[SceneRepairMacroCandidateContract]] = {}
    for macro_candidate in list(truth_followup.macro_candidates or []) if truth_followup is not None else []:
        for current_pair_label in focus_pairs:
            from_object, to_object = current_pair_label.split(" -> ", 1)
            if _macro_candidate_matches_pair(macro_candidate, from_object=from_object, to_object=to_object):
                truth_macros_by_pair.setdefault(current_pair_label, []).append(macro_candidate)

    for current_pair_label in focus_pairs:
        pair_items = truth_items_by_pair.get(current_pair_label, [])
        pair_macros = truth_macros_by_pair.get(current_pair_label, [])
        matched_focus = [item for item in correction_focus if _candidate_matches_pair_label(item, current_pair_label)]
        used_focus_items.update(normalize_focus_key(item) for item in matched_focus)
        item_priorities = {item.priority for item in pair_items}
        macro_priorities = {item.priority for item in pair_macros}
        priority: Literal["high", "normal"] = (
            "high" if "high" in item_priorities or "high" in macro_priorities else "normal"
        )
        signals: list[Literal["vision", "truth", "macro"]] = ["truth"]
        if pair_macros:
            signals.append("macro")
        if matched_focus:
            signals.append("vision")
        summary = (
            pair_items[0].summary
            if pair_items
            else (matched_focus[0] if matched_focus else f"Review pair {current_pair_label}")
        )
        from_object, to_object = current_pair_label.split(" -> ", 1)
        candidates.append(
            ReferenceCorrectionCandidateContract(
                candidate_id=f"pair:{normalize_focus_key(current_pair_label).replace(' ', '_')}",
                summary=summary,
                priority_rank=rank,
                priority=priority,
                candidate_kind="hybrid" if matched_focus else "truth_only",
                target_object=compare_result.target_object,
                target_objects=[from_object, to_object],
                focus_pairs=[current_pair_label],
                source_signals=signals,
                vision_evidence=_build_vision_candidate_evidence(
                    vision_result=vision_result,
                    focus_items=matched_focus,
                    compare_diagnostics=compare_result.compare_diagnostics,
                ),
                truth_evidence=ReferenceCorrectionTruthEvidenceContract(
                    focus_pairs=[current_pair_label],
                    relation_kinds=list(
                        dict.fromkeys(kind for item in pair_items for kind in list(item.relation_kinds or []))
                    ),
                    relation_verdicts=list(
                        dict.fromkeys(verdict for item in pair_items for verdict in list(item.relation_verdicts or []))
                    ),
                    item_kinds=[item.kind for item in pair_items],
                    items=pair_items,
                    macro_candidates=pair_macros,
                ),
            )
        )
        rank += 1

    for focus_item in correction_focus:
        normalized_focus = normalize_focus_key(focus_item)
        if not normalized_focus or normalized_focus in used_focus_items:
            continue
        target_objects = list(compare_result.target_objects or [])
        if compare_result.target_object and compare_result.target_object not in target_objects:
            target_objects = [compare_result.target_object, *target_objects]
        candidates.append(
            ReferenceCorrectionCandidateContract(
                candidate_id=f"vision:{normalized_focus.replace(' ', '_')}",
                summary=focus_item,
                priority_rank=rank,
                priority="normal",
                candidate_kind="vision_only",
                target_object=compare_result.target_object,
                target_objects=target_objects,
                focus_pairs=[],
                source_signals=["vision"],
                vision_evidence=_build_vision_candidate_evidence(
                    vision_result=vision_result,
                    focus_items=[focus_item],
                    compare_diagnostics=compare_result.compare_diagnostics,
                ),
                truth_evidence=None,
            )
        )
        rank += 1

    return candidates
