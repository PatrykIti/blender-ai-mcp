# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Goal-scoped reference image intake and lifecycle tools."""

from __future__ import annotations

import base64
import mimetypes
import re
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal, cast
from uuid import uuid4

from fastmcp import Context

from server.adapters.mcp.context_utils import ctx_info
from server.adapters.mcp.contracts.reference import (
    ReferenceCompareCheckpointResponseContract,
    ReferenceCompareStageCheckpointResponseContract,
    ReferenceCorrectionCandidateContract,
    ReferenceCorrectionTruthEvidenceContract,
    ReferenceCorrectionVisionEvidenceContract,
    ReferenceHybridBudgetControlContract,
    ReferenceImageRecordContract,
    ReferenceImagesResponseContract,
    ReferenceIterateStageCheckpointResponseContract,
)
from server.adapters.mcp.contracts.scene import (
    SceneAssembledTargetScopeContract,
    SceneAssertionPayloadContract,
    SceneCorrectionTruthBundleContract,
    SceneCorrectionTruthPairContract,
    SceneCorrectionTruthSummaryContract,
    SceneRepairMacroCandidateContract,
    SceneTruthFollowupContract,
    SceneTruthFollowupItemContract,
)
from server.adapters.mcp.sampling.result_types import to_vision_assistant_contract
from server.adapters.mcp.session_capabilities import (
    get_session_capability_state_async,
    replace_session_pending_reference_images_async,
    replace_session_reference_images_async,
)
from server.adapters.mcp.session_state import get_session_value_async, set_session_value_async
from server.adapters.mcp.visibility.tags import get_capability_tags
from server.adapters.mcp.vision import (
    CapturePresetProfile,
    VisionImageInput,
    VisionRequest,
    build_reference_capture_images,
    build_vision_request_from_stage_captures,
    capture_stage_images,
    run_vision_assist,
    select_reference_records_for_target,
)
from server.adapters.mcp.vision.runner import VISION_ASSIST_POLICY
from server.infrastructure.di import get_collection_handler, get_scene_handler, get_vision_backend_resolver
from server.infrastructure.tmp_paths import get_reference_image_storage_path, get_viewport_output_paths

REFERENCE_PUBLIC_TOOL_NAMES = (
    "reference_images",
    "reference_compare_checkpoint",
    "reference_compare_current_view",
    "reference_compare_stage_checkpoint",
    "reference_iterate_stage_checkpoint",
)
_ALLOWED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
_REFERENCE_CORRECTION_LOOP_STATE_KEY = "reference_correction_loop"
_REFERENCE_CORRECTION_STAGNATION_THRESHOLD = 2
_ANCHOR_ROLE_HINTS: tuple[tuple[str, int], ...] = (
    ("body", 50),
    ("torso", 45),
    ("trunk", 45),
    ("head", 40),
    ("skull", 35),
    ("core", 30),
    ("root", 25),
    ("base", 20),
)
_ACCESSORY_ROLE_HINTS: tuple[str, ...] = (
    "ear",
    "eye",
    "nose",
    "snout",
    "paw",
    "foot",
    "tail",
    "horn",
    "antler",
    "whisker",
)


def _register_existing_tool(target, tool_name: str):
    tool = globals()[tool_name]
    fn = getattr(tool, "fn", tool)
    return target.tool(fn, name=tool_name, tags=set(get_capability_tags("reference")))


def register_reference_tools(target):
    return {tool_name: _register_existing_tool(target, tool_name) for tool_name in REFERENCE_PUBLIC_TOOL_NAMES}


def _sorted_references(references: list[dict]) -> list[dict]:
    return sorted(references, key=lambda item: str(item.get("added_at") or ""))


def _as_response(
    *,
    action: Literal["attach", "list", "remove", "clear"],
    goal: str | None,
    references: list[dict],
    removed_reference_id: str | None = None,
    message: str | None = None,
    error: str | None = None,
) -> ReferenceImagesResponseContract:
    return ReferenceImagesResponseContract(
        action=action,
        goal=goal,
        reference_count=len(references),
        references=[ReferenceImageRecordContract.model_validate(item) for item in references],
        removed_reference_id=removed_reference_id,
        message=message,
        error=error,
    )


def _validate_local_reference_path(source_path: str) -> Path:
    path = Path(source_path).expanduser().resolve()
    if not path.exists() or not path.is_file():
        raise ValueError(f"Reference image path does not exist: {source_path}")
    if path.suffix.lower() not in _ALLOWED_IMAGE_SUFFIXES:
        raise ValueError("Reference image must be one of: .png, .jpg, .jpeg, .webp")
    return path


def _copy_reference_image(source_path: Path) -> tuple[str, str]:
    filename = f"ref_{uuid4().hex[:10]}{source_path.suffix.lower()}"
    internal_path, host_visible_path = get_reference_image_storage_path(filename)
    shutil.copy2(source_path, internal_path)
    return str(internal_path), host_visible_path


def _safe_checkpoint_token(value: str | None) -> str:
    """Return a filesystem-safe token for checkpoint/bundle ids."""

    raw = str(value or "scene").strip()
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "_", raw).strip("._-")
    return normalized or "scene"


def _compare_response(
    *,
    action: Literal["compare_checkpoint", "compare_current_view"],
    checkpoint_path: str,
    checkpoint_label: str | None,
    goal: str | None,
    target_object: str | None,
    target_view: str | None,
    reference_ids: list[str],
    reference_labels: list[str],
    vision_assistant=None,
    message: str | None = None,
    error: str | None = None,
) -> ReferenceCompareCheckpointResponseContract:
    return ReferenceCompareCheckpointResponseContract(
        action=action,
        goal=goal,
        target_object=target_object,
        target_view=target_view,
        checkpoint_path=checkpoint_path,
        checkpoint_label=checkpoint_label,
        reference_count=len(reference_ids),
        reference_ids=reference_ids,
        reference_labels=reference_labels,
        vision_assistant=vision_assistant,
        message=message,
        error=error,
    )


def _stage_compare_response(
    *,
    checkpoint_id: str,
    checkpoint_label: str | None,
    goal: str | None,
    target_object: str | None,
    target_objects: list[str],
    collection_name: str | None,
    target_view: str | None,
    preset_profile: CapturePresetProfile,
    preset_names: list[str],
    captures: list | tuple = (),
    reference_ids: list[str],
    reference_labels: list[str],
    vision_assistant=None,
    truth_bundle: SceneCorrectionTruthBundleContract | None = None,
    truth_followup: SceneTruthFollowupContract | None = None,
    correction_candidates: list[ReferenceCorrectionCandidateContract] | None = None,
    budget_control: ReferenceHybridBudgetControlContract | None = None,
    message: str | None = None,
    error: str | None = None,
) -> ReferenceCompareStageCheckpointResponseContract:
    assembled_target_scope = _assembled_target_scope(
        target_object=target_object,
        target_objects=target_objects,
        collection_name=collection_name,
    )
    return ReferenceCompareStageCheckpointResponseContract(
        action="compare_stage_checkpoint",
        goal=goal,
        target_object=target_object,
        target_objects=target_objects,
        collection_name=collection_name,
        assembled_target_scope=assembled_target_scope,
        truth_bundle=truth_bundle,
        truth_followup=truth_followup,
        correction_candidates=list(correction_candidates or []),
        budget_control=budget_control,
        target_view=target_view,
        checkpoint_id=checkpoint_id,
        checkpoint_label=checkpoint_label,
        preset_profile=preset_profile,
        preset_names=preset_names,
        capture_count=len(captures),
        captures=list(captures),
        reference_count=len(reference_ids),
        reference_ids=reference_ids,
        reference_labels=reference_labels,
        vision_assistant=vision_assistant,
        message=message,
        error=error,
    )


def _iterate_stage_response(
    *,
    goal: str | None,
    target_object: str | None,
    target_objects: list[str],
    collection_name: str | None,
    target_view: str | None,
    checkpoint_id: str,
    checkpoint_label: str | None,
    iteration_index: int,
    loop_disposition: Literal["continue_build", "inspect_validate", "stop"],
    continue_recommended: bool,
    prior_checkpoint_id: str | None,
    prior_correction_focus: list[str],
    correction_focus: list[str],
    repeated_correction_focus: list[str],
    stagnation_count: int,
    compare_result: ReferenceCompareStageCheckpointResponseContract,
    correction_candidates: list[ReferenceCorrectionCandidateContract] | None = None,
    budget_control: ReferenceHybridBudgetControlContract | None = None,
    stop_reason: str | None = None,
    message: str | None = None,
    error: str | None = None,
) -> ReferenceIterateStageCheckpointResponseContract:
    return ReferenceIterateStageCheckpointResponseContract(
        action="iterate_stage_checkpoint",
        goal=goal,
        target_object=target_object,
        target_objects=target_objects,
        collection_name=collection_name,
        assembled_target_scope=compare_result.assembled_target_scope,
        truth_bundle=compare_result.truth_bundle,
        truth_followup=compare_result.truth_followup,
        correction_candidates=list(correction_candidates or compare_result.correction_candidates or []),
        budget_control=budget_control or compare_result.budget_control,
        target_view=target_view,
        checkpoint_id=checkpoint_id,
        checkpoint_label=checkpoint_label,
        iteration_index=iteration_index,
        loop_disposition=loop_disposition,
        continue_recommended=continue_recommended,
        prior_checkpoint_id=prior_checkpoint_id,
        prior_correction_focus=prior_correction_focus,
        correction_focus=correction_focus,
        repeated_correction_focus=repeated_correction_focus,
        stagnation_count=stagnation_count,
        stop_reason=stop_reason,
        compare_result=compare_result,
        message=message,
        error=error,
    )


def _normalized_focus_key(value: str) -> str:
    return " ".join(value.strip().lower().split())


def _resolve_actionable_focus(compare_result: ReferenceCompareStageCheckpointResponseContract) -> list[str]:
    candidate_summaries = list(compare_result.correction_candidates or [])
    if candidate_summaries:
        deduped_candidates: list[str] = []
        seen_candidates: set[str] = set()
        for candidate in candidate_summaries:
            normalized = _normalized_focus_key(candidate.summary)
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
        normalized = _normalized_focus_key(item)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(item)
    return deduped[:3]


def _should_inspect_from_truth_signal(
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
        if any(kind in {"contact_failure", "overlap", "measurement_error"} for kind in truth_evidence.item_kinds):
            return True
    return False


def _model_budget_bias(model_name: str | None) -> int:
    normalized = str(model_name or "").lower()
    if any(token in normalized for token in ("2b", "3b", "4b", "flash", "mini")):
        return -1
    if any(token in normalized for token in ("27b", "70b", "72b", "grok")):
        return 1
    return 0


def _effective_pair_budget(*, max_tokens: int, model_name: str | None) -> int:
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
    return max(2, min(8, base + _model_budget_bias(model_name)))


def _effective_candidate_budget(*, pair_budget: int, max_tokens: int, model_name: str | None) -> int:
    base = pair_budget + 1
    if max_tokens <= 256:
        base = min(base, 3)
    elif max_tokens <= 400:
        base = min(base, 4)
    else:
        base = min(base, 6 + _model_budget_bias(model_name))
    return max(2, base)


def _resolve_hybrid_budget_runtime(resolver: Any) -> tuple[int, int, str | None]:
    runtime_config = getattr(resolver, "runtime_config", None)
    if runtime_config is None:
        return VISION_ASSIST_POLICY.max_tokens, 8, None
    return (
        int(getattr(runtime_config, "max_tokens", VISION_ASSIST_POLICY.max_tokens)),
        int(getattr(runtime_config, "max_images", 8)),
        cast(str | None, getattr(runtime_config, "active_model_name", None)),
    )


def _truth_summary_chars(bundle: SceneCorrectionTruthBundleContract) -> int:
    return len(bundle.model_dump_json())


def _check_priority_score(check: SceneCorrectionTruthPairContract) -> tuple[int, int, int, int, str]:
    overlap_score = 3 if check.overlap is not None and bool(check.overlap.get("overlaps")) else 0
    contact_score = 3 if check.contact_assertion is not None and not check.contact_assertion.passed else 0
    gap_score = 2 if check.gap is not None and str(check.gap.get("relation") or "").lower() == "separated" else 0
    alignment_score = 1 if check.alignment is not None and not bool(check.alignment.get("is_aligned")) else 0
    error_score = 4 if check.error else 0
    pair_label = _pair_label(check.from_object, check.to_object)
    return (
        error_score + overlap_score + contact_score + gap_score + alignment_score,
        overlap_score,
        contact_score,
        gap_score + alignment_score,
        pair_label,
    )


def _rebuild_truth_summary(
    *,
    pairing_strategy: Literal["none", "primary_to_others"],
    checks: list[SceneCorrectionTruthPairContract],
) -> SceneCorrectionTruthSummaryContract:
    return SceneCorrectionTruthSummaryContract(
        pairing_strategy=pairing_strategy,
        pair_count=len(checks),
        evaluated_pairs=sum(1 for item in checks if item.error is None),
        contact_failures=sum(
            1 for item in checks if item.contact_assertion is not None and not item.contact_assertion.passed
        ),
        overlap_pairs=sum(1 for item in checks if item.overlap is not None and bool(item.overlap.get("overlaps"))),
        separated_pairs=sum(
            1 for item in checks if item.gap is not None and str(item.gap.get("relation") or "").lower() == "separated"
        ),
        misaligned_pairs=sum(
            1 for item in checks if item.alignment is not None and not bool(item.alignment.get("is_aligned"))
        ),
    )


def _trim_truth_bundle_to_budget(
    *,
    truth_bundle: SceneCorrectionTruthBundleContract,
    pair_budget: int,
    max_truth_chars: int,
) -> tuple[SceneCorrectionTruthBundleContract, bool]:
    checks = list(truth_bundle.checks or [])
    if len(checks) <= pair_budget and _truth_summary_chars(truth_bundle) <= max_truth_chars:
        return truth_bundle, False

    ordered_checks = sorted(checks, key=_check_priority_score, reverse=True)
    trimmed = False
    selected_count = min(len(ordered_checks), pair_budget)

    while selected_count >= 1:
        selected_checks = ordered_checks[:selected_count]
        trimmed_bundle = SceneCorrectionTruthBundleContract(
            scope=truth_bundle.scope,
            summary=_rebuild_truth_summary(
                pairing_strategy=truth_bundle.summary.pairing_strategy,
                checks=selected_checks,
            ),
            checks=selected_checks,
            error=truth_bundle.error,
        )
        if _truth_summary_chars(trimmed_bundle) <= max_truth_chars or selected_count == 1:
            trimmed = selected_count < len(checks) or _truth_summary_chars(truth_bundle) > max_truth_chars
            return trimmed_bundle, trimmed
        selected_count -= 1

    return truth_bundle, False


def _trim_correction_candidates(
    candidates: list[ReferenceCorrectionCandidateContract],
    *,
    candidate_budget: int,
) -> tuple[list[ReferenceCorrectionCandidateContract], bool]:
    if len(candidates) <= candidate_budget:
        return candidates, False
    return list(candidates[:candidate_budget]), True


def _candidate_matches_pair_label(focus_item: str, pair_label: str) -> bool:
    normalized_focus = _normalized_focus_key(focus_item)
    normalized_pair = _normalized_focus_key(pair_label)
    if not normalized_focus or not normalized_pair:
        return False
    if normalized_pair in normalized_focus:
        return True
    from_object, to_object = pair_label.split(" -> ", 1)
    return (
        _normalized_focus_key(from_object) in normalized_focus and _normalized_focus_key(to_object) in normalized_focus
    )


def _macro_candidate_matches_pair(
    candidate: SceneRepairMacroCandidateContract,
    *,
    from_object: str,
    to_object: str,
) -> bool:
    arguments = candidate.arguments_hint or {}
    candidate_from = arguments.get("part_object") or arguments.get("left_object") or arguments.get("primary_object")
    candidate_to = arguments.get("reference_object") or arguments.get("right_object") or arguments.get("support_object")
    return candidate_from == from_object and candidate_to == to_object


def _build_vision_candidate_evidence(
    *,
    vision_result,
    focus_items: list[str],
) -> ReferenceCorrectionVisionEvidenceContract | None:
    if vision_result is None or not focus_items:
        return None
    return ReferenceCorrectionVisionEvidenceContract(
        correction_focus=focus_items,
        shape_mismatches=list(vision_result.shape_mismatches or []),
        proportion_mismatches=list(vision_result.proportion_mismatches or []),
        next_corrections=list(vision_result.next_corrections or []),
    )


def _build_correction_candidates(
    compare_result: ReferenceCompareStageCheckpointResponseContract,
) -> list[ReferenceCorrectionCandidateContract]:
    truth_followup = compare_result.truth_followup
    vision_result = compare_result.vision_assistant.result if compare_result.vision_assistant else None
    correction_focus = _resolve_actionable_focus(compare_result)
    candidates: list[ReferenceCorrectionCandidateContract] = []
    used_focus_items: set[str] = set()
    rank = 1
    focus_pairs = list(truth_followup.focus_pairs or []) if truth_followup is not None else []

    truth_items_by_pair: dict[str, list[SceneTruthFollowupItemContract]] = {}
    for item in list(truth_followup.items or []) if truth_followup is not None else []:
        if item.from_object is None or item.to_object is None:
            continue
        pair_label = _pair_label(item.from_object, item.to_object)
        truth_items_by_pair.setdefault(pair_label, []).append(item)

    truth_macros_by_pair: dict[str, list[SceneRepairMacroCandidateContract]] = {}
    for macro_candidate in list(truth_followup.macro_candidates or []) if truth_followup is not None else []:
        for pair_label in focus_pairs:
            from_object, to_object = pair_label.split(" -> ", 1)
            if _macro_candidate_matches_pair(macro_candidate, from_object=from_object, to_object=to_object):
                truth_macros_by_pair.setdefault(pair_label, []).append(macro_candidate)

    for pair_label in focus_pairs:
        pair_items = truth_items_by_pair.get(pair_label, [])
        pair_macros = truth_macros_by_pair.get(pair_label, [])
        matched_focus = [item for item in correction_focus if _candidate_matches_pair_label(item, pair_label)]
        used_focus_items.update(_normalized_focus_key(item) for item in matched_focus)
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
            else (matched_focus[0] if matched_focus else f"Review pair {pair_label}")
        )
        from_object, to_object = pair_label.split(" -> ", 1)
        candidates.append(
            ReferenceCorrectionCandidateContract(
                candidate_id=f"pair:{_normalized_focus_key(pair_label).replace(' ', '_')}",
                summary=summary,
                priority_rank=rank,
                priority=priority,
                candidate_kind="hybrid" if matched_focus else "truth_only",
                target_object=compare_result.target_object,
                target_objects=[from_object, to_object],
                focus_pairs=[pair_label],
                source_signals=signals,
                vision_evidence=_build_vision_candidate_evidence(
                    vision_result=vision_result,
                    focus_items=matched_focus,
                ),
                truth_evidence=ReferenceCorrectionTruthEvidenceContract(
                    focus_pairs=[pair_label],
                    item_kinds=[item.kind for item in pair_items],
                    items=pair_items,
                    macro_candidates=pair_macros,
                ),
            )
        )
        rank += 1

    for focus_item in correction_focus:
        normalized_focus = _normalized_focus_key(focus_item)
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
                ),
                truth_evidence=None,
            )
        )
        rank += 1

    return candidates


def _dedupe_names(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in values:
        normalized = item.strip()
        key = normalized.lower()
        if not normalized or key in seen:
            continue
        seen.add(key)
        result.append(normalized)
    return result


def _resolve_capture_scope(
    *,
    target_object: str | None,
    target_objects: list[str] | None,
    collection_name: str | None,
) -> tuple[str | None, list[str], str | None]:
    resolved_target_objects = _dedupe_names(list(target_objects or []))
    if target_object:
        resolved_target_objects = _dedupe_names([target_object, *resolved_target_objects])

    if collection_name:
        collection_payload = get_collection_handler().list_objects(
            collection_name=collection_name,
            recursive=True,
            include_hidden=False,
        )
        collection_objects = [
            str(item.get("name")).strip()
            for item in collection_payload.get("objects", [])
            if isinstance(item, dict) and str(item.get("name") or "").strip()
        ]
        resolved_target_objects = _dedupe_names([*resolved_target_objects, *collection_objects])

    normalized_primary = (
        target_object if target_object else (resolved_target_objects[0] if len(resolved_target_objects) == 1 else None)
    )
    return normalized_primary, resolved_target_objects, collection_name


def _name_anchor_weight(object_name: str) -> int:
    normalized = object_name.strip().lower()
    score = 0
    for token, weight in _ANCHOR_ROLE_HINTS:
        if token in normalized:
            score += weight
    for token in _ACCESSORY_ROLE_HINTS:
        if token in normalized:
            score -= 30
    return score


def _bbox_volume_or_zero(object_name: str) -> float:
    try:
        bbox = get_scene_handler().get_bounding_box(object_name, world_space=True)
    except Exception:
        return 0.0
    dimensions = bbox.get("dimensions") if isinstance(bbox, dict) else None
    if not isinstance(dimensions, list) or len(dimensions) != 3:
        return 0.0
    try:
        return float(dimensions[0]) * float(dimensions[1]) * float(dimensions[2])
    except Exception:
        return 0.0


def _looks_like_accessory_anchor(object_name: str) -> bool:
    normalized = object_name.strip().lower()
    return any(token in normalized for token in _ACCESSORY_ROLE_HINTS)


def _select_scope_primary_target(object_names: list[str]) -> str | None:
    if not object_names:
        return None
    first_name = object_names[0]
    if not _looks_like_accessory_anchor(first_name):
        return first_name

    candidates = [name for name in object_names if not _looks_like_accessory_anchor(name)]
    if not candidates:
        return first_name

    return max(
        candidates,
        key=lambda name: (_name_anchor_weight(name), _bbox_volume_or_zero(name), -object_names.index(name)),
    )


def _assembled_target_scope(
    *,
    target_object: str | None,
    target_objects: list[str] | None,
    collection_name: str | None,
) -> SceneAssembledTargetScopeContract:
    normalized_primary, resolved_target_objects, normalized_collection = _resolve_capture_scope(
        target_object=target_object,
        target_objects=target_objects,
        collection_name=collection_name,
    )

    if normalized_collection:
        scope_kind: Literal["single_object", "object_set", "collection", "scene"] = "collection"
    elif len(resolved_target_objects) > 1:
        scope_kind = "object_set"
    elif normalized_primary:
        scope_kind = "single_object"
    else:
        scope_kind = "scene"

    return SceneAssembledTargetScopeContract(
        scope_kind=scope_kind,
        primary_target=normalized_primary or _select_scope_primary_target(resolved_target_objects),
        object_names=resolved_target_objects,
        object_count=len(resolved_target_objects),
        collection_name=normalized_collection,
        part_groups=[],
    )


def _truth_bundle_pairs(
    scope: SceneAssembledTargetScopeContract,
) -> tuple[Literal["none", "primary_to_others"], list[tuple[str, str]]]:
    object_names = list(scope.object_names or [])
    if len(object_names) < 2 or scope.primary_target is None:
        return "none", []

    anchor = scope.primary_target
    pairs = [(anchor, name) for name in object_names if name != anchor]
    return ("primary_to_others", pairs) if pairs else ("none", [])


def _build_correction_truth_bundle(
    scene_handler,
    scope: SceneAssembledTargetScopeContract,
) -> SceneCorrectionTruthBundleContract:
    pairing_strategy, pairs = _truth_bundle_pairs(scope)
    checks: list[SceneCorrectionTruthPairContract] = []
    contact_failures = 0
    overlap_pairs = 0
    separated_pairs = 0
    misaligned_pairs = 0

    for from_object, to_object in pairs:
        error: str | None = None
        gap = None
        alignment = None
        overlap = None
        contact_assertion = None
        try:
            gap = scene_handler.measure_gap(from_object, to_object)
            alignment = scene_handler.measure_alignment(from_object, to_object, ["X", "Y", "Z"], "CENTER")
            overlap = scene_handler.measure_overlap(from_object, to_object)
            contact_assertion = SceneAssertionPayloadContract.model_validate(
                scene_handler.assert_contact(from_object, to_object)
            )
        except RuntimeError as exc:
            error = str(exc)

        if gap is not None and str(gap.get("relation") or "").lower() == "separated":
            separated_pairs += 1
        if overlap is not None and bool(overlap.get("overlaps")):
            overlap_pairs += 1
        if alignment is not None and not bool(alignment.get("is_aligned")):
            misaligned_pairs += 1
        if contact_assertion is not None and not contact_assertion.passed:
            contact_failures += 1

        checks.append(
            SceneCorrectionTruthPairContract(
                from_object=from_object,
                to_object=to_object,
                gap=gap,
                alignment=alignment,
                overlap=overlap,
                contact_assertion=contact_assertion,
                error=error,
            )
        )

    return SceneCorrectionTruthBundleContract(
        scope=scope,
        summary=SceneCorrectionTruthSummaryContract(
            pairing_strategy=pairing_strategy,
            pair_count=len(pairs),
            evaluated_pairs=sum(1 for item in checks if item.error is None),
            contact_failures=contact_failures,
            overlap_pairs=overlap_pairs,
            separated_pairs=separated_pairs,
            misaligned_pairs=misaligned_pairs,
        ),
        checks=checks,
    )


def _pair_label(from_object: str, to_object: str) -> str:
    return f"{from_object} -> {to_object}"


def _build_truth_followup(bundle: SceneCorrectionTruthBundleContract) -> SceneTruthFollowupContract:
    if bundle.summary.pair_count == 0:
        return SceneTruthFollowupContract(
            scope=bundle.scope,
            continue_recommended=False,
            message="No pairwise truth checks are available for this assembled target scope yet.",
            focus_pairs=[],
            items=[],
            macro_candidates=[],
        )

    items: list[SceneTruthFollowupItemContract] = []
    macro_candidates: list[SceneRepairMacroCandidateContract] = []
    focus_pairs: list[str] = []
    seen_pairs: set[str] = set()
    pair_issue_kinds: dict[str, set[str]] = {}

    for check in bundle.checks:
        pair_label = _pair_label(check.from_object, check.to_object)
        if check.error:
            items.append(
                SceneTruthFollowupItemContract(
                    kind="measurement_error",
                    summary=f"Truth checks failed for {pair_label}: {check.error}",
                    priority="high",
                    from_object=check.from_object,
                    to_object=check.to_object,
                )
            )
        else:
            if check.contact_assertion is not None and not check.contact_assertion.passed:
                items.append(
                    SceneTruthFollowupItemContract(
                        kind="contact_failure",
                        summary=f"{pair_label} failed the contact assertion.",
                        priority="high",
                        from_object=check.from_object,
                        to_object=check.to_object,
                        tool_name="scene_assert_contact",
                    )
                )
            if check.gap is not None and str(check.gap.get("relation") or "").lower() == "separated":
                items.append(
                    SceneTruthFollowupItemContract(
                        kind="gap",
                        summary=f"{pair_label} still has measurable separation.",
                        priority="normal",
                        from_object=check.from_object,
                        to_object=check.to_object,
                        tool_name="scene_measure_gap",
                    )
                )
            if check.overlap is not None and bool(check.overlap.get("overlaps")):
                items.append(
                    SceneTruthFollowupItemContract(
                        kind="overlap",
                        summary=f"{pair_label} still overlaps.",
                        priority="high",
                        from_object=check.from_object,
                        to_object=check.to_object,
                        tool_name="scene_measure_overlap",
                    )
                )
            if check.alignment is not None and not bool(check.alignment.get("is_aligned")):
                items.append(
                    SceneTruthFollowupItemContract(
                        kind="alignment",
                        summary=f"{pair_label} is still misaligned.",
                        priority="normal",
                        from_object=check.from_object,
                        to_object=check.to_object,
                        tool_name="scene_measure_alignment",
                    )
                )

        if any(item.from_object == check.from_object and item.to_object == check.to_object for item in items):
            if pair_label not in seen_pairs:
                seen_pairs.add(pair_label)
                focus_pairs.append(pair_label)
            pair_issue_kinds[pair_label] = {
                item.kind
                for item in items
                if item.from_object == check.from_object and item.to_object == check.to_object
            }

    for pair_label in focus_pairs:
        issue_kinds = pair_issue_kinds.get(pair_label, set())
        if not issue_kinds:
            continue
        if "measurement_error" in issue_kinds:
            continue
        from_object, to_object = pair_label.split(" -> ", 1)
        if "overlap" in issue_kinds:
            macro_candidates.append(
                SceneRepairMacroCandidateContract(
                    macro_name="macro_cleanup_part_intersections",
                    reason="Use a bounded cleanup push to separate the overlapping pair without broad manual re-placement.",
                    priority="high",
                    arguments_hint={
                        "part_object": from_object,
                        "reference_object": to_object,
                        "gap": 0.0,
                        "preserve_side": True,
                    },
                )
            )
            continue
        if not issue_kinds.intersection({"contact_failure", "gap", "alignment"}):
            continue
        macro_candidates.append(
            SceneRepairMacroCandidateContract(
                macro_name="macro_align_part_with_contact",
                reason="Use a bounded repair nudge to restore contact/alignment without re-placing the pair from scratch.",
                priority="high" if "contact_failure" in issue_kinds else "normal",
                arguments_hint={
                    "part_object": from_object,
                    "reference_object": to_object,
                    "target_relation": "contact",
                    "align_mode": "none",
                    "preserve_side": True,
                },
            )
        )

    return SceneTruthFollowupContract(
        scope=bundle.scope,
        continue_recommended=bool(items),
        message=(
            f"Truth follow-up identified {len(items)} actionable finding(s), plus {len(macro_candidates)} repair macro candidate(s), across {len(focus_pairs)} pair(s)."
            if items
            else "Truth follow-up found no actionable pairwise issues for the current assembled target scope."
        ),
        focus_pairs=focus_pairs,
        items=items,
        macro_candidates=macro_candidates,
    )


def _repeated_focus(current: list[str], prior: list[str]) -> list[str]:
    prior_keys = {_normalized_focus_key(item) for item in prior if _normalized_focus_key(item)}
    repeated: list[str] = []
    for item in current:
        normalized = _normalized_focus_key(item)
        if normalized and normalized in prior_keys:
            repeated.append(item)
    return repeated


async def _run_checkpoint_compare(
    ctx: Context,
    *,
    checkpoint: Path,
    checkpoint_label: str | None,
    target_object: str | None,
    target_view: str | None,
    goal_override: str | None,
    prompt_hint: str | None,
    response_action: Literal["compare_checkpoint", "compare_current_view"],
) -> ReferenceCompareCheckpointResponseContract:
    """Shared bounded checkpoint compare path."""

    session = await get_session_capability_state_async(ctx)
    goal = goal_override or session.goal
    if not goal:
        return _compare_response(
            action=response_action,
            checkpoint_path=str(checkpoint),
            checkpoint_label=checkpoint_label,
            goal=None,
            target_object=target_object,
            target_view=target_view,
            reference_ids=[],
            reference_labels=[],
            error="Set an active goal with router_set_goal(...) before comparing a checkpoint, or pass goal_override.",
        )

    references = list(session.reference_images or [])
    selected_reference_records = select_reference_records_for_target(
        references,
        target_object=target_object,
        target_view=target_view,
    )
    if not selected_reference_records:
        return _compare_response(
            action=response_action,
            checkpoint_path=str(checkpoint),
            checkpoint_label=checkpoint_label,
            goal=goal,
            target_object=target_object,
            target_view=target_view,
            reference_ids=[],
            reference_labels=[],
            error="No matching reference images are attached for the requested target_object/target_view.",
        )

    reference_images = build_reference_capture_images(selected_reference_records)
    vision_request = VisionRequest(
        goal=goal,
        images=(
            VisionImageInput(
                path=str(checkpoint),
                role="after",
                label=checkpoint_label or checkpoint.name,
                media_type=mimetypes.guess_type(str(checkpoint))[0] or "image/png",
            ),
            *tuple(
                VisionImageInput(
                    path=item.image_path,
                    role="reference",
                    label=item.label,
                    media_type=item.media_type,
                )
                for item in reference_images
            ),
        ),
        target_object=target_object,
        prompt_hint=" | ".join(
            part
            for part in (
                prompt_hint,
                "comparison_mode=checkpoint_vs_reference",
                f"checkpoint_label={checkpoint_label}" if checkpoint_label else None,
                f"target_view={target_view}" if target_view else None,
                *[
                    f"reference[{index}] label={record.label}"
                    for index, record in enumerate(selected_reference_records, start=1)
                    if record.label
                ],
            )
            if part
        )
        or None,
        metadata={
            "source": response_action,
            "checkpoint_path": str(checkpoint),
            "reference_count": len(selected_reference_records),
        },
    )
    outcome = await run_vision_assist(
        ctx,
        request=vision_request,
        resolver=get_vision_backend_resolver(),
    )
    vision_assistant = to_vision_assistant_contract(outcome)
    return _compare_response(
        action=response_action,
        checkpoint_path=str(checkpoint),
        checkpoint_label=checkpoint_label,
        goal=goal,
        target_object=target_object,
        target_view=target_view,
        reference_ids=[item.reference_id for item in selected_reference_records],
        reference_labels=[item.label or item.reference_id for item in selected_reference_records],
        vision_assistant=vision_assistant,
        message=(
            f"Compared checkpoint '{checkpoint_label or checkpoint.name}' against {len(selected_reference_records)} reference image(s)."
            if outcome.status == "success"
            else "Checkpoint comparison executed but vision assistance did not complete successfully."
        ),
        error=vision_assistant.rejection_reason if vision_assistant.status != "success" else None,
    )


async def _run_stage_checkpoint_compare(
    ctx: Context,
    *,
    checkpoint_id: str,
    checkpoint_label: str | None,
    target_object: str | None,
    target_objects: list[str] | None,
    collection_name: str | None,
    target_view: str | None,
    preset_profile: CapturePresetProfile,
    goal_override: str | None,
    prompt_hint: str | None,
) -> ReferenceCompareStageCheckpointResponseContract:
    """Capture one deterministic stage view-set, then compare it against references."""

    session = await get_session_capability_state_async(ctx)
    goal = goal_override or session.goal
    if not goal:
        return _stage_compare_response(
            checkpoint_id=checkpoint_id,
            checkpoint_label=checkpoint_label,
            goal=None,
            target_object=target_object,
            target_objects=list(target_objects or []),
            collection_name=collection_name,
            target_view=target_view,
            preset_profile=preset_profile,
            preset_names=[],
            reference_ids=[],
            reference_labels=[],
            error="Set an active goal with router_set_goal(...) before comparing a stage checkpoint, or pass goal_override.",
        )

    try:
        resolved_target_object, resolved_target_objects, resolved_collection_name = _resolve_capture_scope(
            target_object=target_object,
            target_objects=target_objects,
            collection_name=collection_name,
        )
    except RuntimeError as exc:
        return _stage_compare_response(
            checkpoint_id=checkpoint_id,
            checkpoint_label=checkpoint_label,
            goal=goal,
            target_object=target_object,
            target_objects=list(target_objects or []),
            collection_name=collection_name,
            target_view=target_view,
            preset_profile=preset_profile,
            preset_names=[],
            reference_ids=[],
            reference_labels=[],
            error=str(exc),
        )
    assembled_target_scope = _assembled_target_scope(
        target_object=resolved_target_object,
        target_objects=resolved_target_objects,
        collection_name=resolved_collection_name,
    )

    references = list(session.reference_images or [])
    selected_reference_records = select_reference_records_for_target(
        references,
        target_object=resolved_target_object,
        target_view=target_view,
    )
    if not selected_reference_records:
        return _stage_compare_response(
            checkpoint_id=checkpoint_id,
            checkpoint_label=checkpoint_label,
            goal=goal,
            target_object=resolved_target_object,
            target_objects=resolved_target_objects,
            collection_name=resolved_collection_name,
            target_view=target_view,
            preset_profile=preset_profile,
            preset_names=[],
            reference_ids=[],
            reference_labels=[],
            error="No matching reference images are attached for the requested target_object/target_view.",
        )

    try:
        captures = capture_stage_images(
            get_scene_handler(),
            bundle_id=checkpoint_id,
            stage="after",
            target_object=resolved_target_object,
            target_objects=resolved_target_objects,
            preset_profile=preset_profile,
        )
    except RuntimeError as exc:
        return _stage_compare_response(
            checkpoint_id=checkpoint_id,
            checkpoint_label=checkpoint_label,
            goal=goal,
            target_object=resolved_target_object,
            target_objects=resolved_target_objects,
            collection_name=resolved_collection_name,
            target_view=target_view,
            preset_profile=preset_profile,
            preset_names=[],
            reference_ids=[item.reference_id for item in selected_reference_records],
            reference_labels=[item.label or item.reference_id for item in selected_reference_records],
            error=str(exc),
        )

    resolver = get_vision_backend_resolver()
    runtime_max_tokens, runtime_max_images, runtime_model_name = _resolve_hybrid_budget_runtime(resolver)
    scene_handler = get_scene_handler()
    truth_bundle = _build_correction_truth_bundle(scene_handler, assembled_target_scope)
    pair_budget = _effective_pair_budget(
        max_tokens=runtime_max_tokens,
        model_name=runtime_model_name,
    )
    max_truth_chars = min(
        int(VISION_ASSIST_POLICY.max_input_chars * 0.5),
        max(1800, runtime_max_tokens * 12),
    )
    budgeted_truth_bundle, scope_trimmed = _trim_truth_bundle_to_budget(
        truth_bundle=truth_bundle,
        pair_budget=pair_budget,
        max_truth_chars=max_truth_chars,
    )
    truth_followup = _build_truth_followup(budgeted_truth_bundle)
    reference_images = build_reference_capture_images(selected_reference_records)
    vision_request = build_vision_request_from_stage_captures(
        captures,
        goal=goal,
        target_object=resolved_target_object,
        reference_images=reference_images,
        truth_summary=budgeted_truth_bundle.model_dump(mode="json"),
        prompt_hint=" | ".join(
            part
            for part in (
                prompt_hint,
                "comparison_mode=stage_checkpoint_vs_reference",
                f"checkpoint_label={checkpoint_label}" if checkpoint_label else None,
                f"preset_profile={preset_profile}",
                f"collection_name={resolved_collection_name}" if resolved_collection_name else None,
                f"target_objects={','.join(resolved_target_objects)}" if resolved_target_objects else None,
                f"target_view={target_view}" if target_view else None,
                *[f"capture[{index}] label={capture.label}" for index, capture in enumerate(captures, start=1)],
                *[
                    f"reference[{index}] label={record.label}"
                    for index, record in enumerate(selected_reference_records, start=1)
                    if record.label
                ],
            )
            if part
        )
        or None,
        metadata={
            "source": "compare_stage_checkpoint",
            "checkpoint_id": checkpoint_id,
            "preset_profile": preset_profile,
            "capture_count": len(captures),
            "collection_name": resolved_collection_name,
            "target_objects": list(resolved_target_objects),
            "assembled_target_scope": assembled_target_scope.model_dump(mode="json"),
        },
    )
    outcome = await run_vision_assist(
        ctx,
        request=vision_request,
        resolver=resolver,
    )
    vision_assistant = to_vision_assistant_contract(outcome)
    full_correction_candidates = _build_correction_candidates(
        ReferenceCompareStageCheckpointResponseContract(
            action="compare_stage_checkpoint",
            goal=goal,
            target_object=resolved_target_object,
            target_objects=resolved_target_objects,
            collection_name=resolved_collection_name,
            assembled_target_scope=assembled_target_scope,
            truth_bundle=budgeted_truth_bundle,
            truth_followup=truth_followup,
            target_view=target_view,
            checkpoint_id=checkpoint_id,
            checkpoint_label=checkpoint_label,
            preset_profile=preset_profile,
            preset_names=[capture.preset_name or capture.label for capture in captures],
            capture_count=len(captures),
            captures=list(captures),
            reference_count=len(selected_reference_records),
            reference_ids=[item.reference_id for item in selected_reference_records],
            reference_labels=[item.label or item.reference_id for item in selected_reference_records],
            vision_assistant=vision_assistant,
        )
    )
    candidate_budget = _effective_candidate_budget(
        pair_budget=pair_budget,
        max_tokens=runtime_max_tokens,
        model_name=runtime_model_name,
    )
    correction_candidates, detail_trimmed = _trim_correction_candidates(
        full_correction_candidates,
        candidate_budget=candidate_budget,
    )
    budget_control = ReferenceHybridBudgetControlContract(
        model_name=runtime_model_name,
        max_input_chars=VISION_ASSIST_POLICY.max_input_chars,
        max_output_tokens=runtime_max_tokens,
        max_images=runtime_max_images,
        original_pair_count=truth_bundle.summary.pair_count,
        emitted_pair_count=budgeted_truth_bundle.summary.pair_count,
        original_candidate_count=len(full_correction_candidates),
        emitted_candidate_count=len(correction_candidates),
        trimming_applied=scope_trimmed or detail_trimmed,
        scope_trimmed=scope_trimmed,
        detail_trimmed=detail_trimmed,
        trim_reason=("model_aware_budget_control" if scope_trimmed or detail_trimmed else None),
        selected_focus_pairs=list(truth_followup.focus_pairs or []),
    )
    return _stage_compare_response(
        checkpoint_id=checkpoint_id,
        checkpoint_label=checkpoint_label,
        goal=goal,
        target_object=resolved_target_object,
        target_objects=resolved_target_objects,
        collection_name=resolved_collection_name,
        target_view=target_view,
        preset_profile=preset_profile,
        preset_names=[capture.preset_name or capture.label for capture in captures],
        captures=captures,
        reference_ids=[item.reference_id for item in selected_reference_records],
        reference_labels=[item.label or item.reference_id for item in selected_reference_records],
        vision_assistant=vision_assistant,
        truth_bundle=budgeted_truth_bundle,
        truth_followup=truth_followup,
        correction_candidates=correction_candidates,
        budget_control=budget_control,
        message=(
            f"Captured and compared stage checkpoint '{checkpoint_label or checkpoint_id}' using {len(captures)} deterministic view(s)."
            if outcome.status == "success"
            else "Stage checkpoint capture executed but vision assistance did not complete successfully."
        ),
        error=vision_assistant.rejection_reason if vision_assistant.status != "success" else None,
    )


async def reference_images(
    ctx: Context,
    action: str,
    source_path: str | None = None,
    reference_id: str | None = None,
    label: str | None = None,
    notes: str | None = None,
    target_object: str | None = None,
    target_view: str | None = None,
) -> ReferenceImagesResponseContract:
    """Manage goal-scoped reference images for later vision/capture interpretation."""

    normalized_action = str(action).lower()
    if normalized_action not in {"attach", "list", "remove", "clear"}:
        return _as_response(
            action="list", goal=None, references=[], error="action must be attach, list, remove, or clear"
        )

    session = await get_session_capability_state_async(ctx)
    active_references = list(session.reference_images or [])
    pending_references = list(session.pending_reference_images or [])
    references = active_references if session.goal is not None else pending_references

    if normalized_action == "list":
        return _as_response(action="list", goal=session.goal, references=_sorted_references(references))

    if normalized_action == "clear":
        for item in references:
            stored_path = item.get("stored_path")
            if isinstance(stored_path, str):
                try:
                    Path(stored_path).unlink(missing_ok=True)
                except Exception:
                    pass
        if session.goal is None:
            await replace_session_pending_reference_images_async(ctx, [])
            ctx_info(ctx, "[REFERENCE] Cleared pending reference images")
            return _as_response(action="clear", goal=None, references=[], message="Cleared pending reference images.")

        await replace_session_reference_images_async(ctx, [])
        ctx_info(ctx, "[REFERENCE] Cleared session reference images")
        return _as_response(
            action="clear", goal=session.goal, references=[], message="Cleared session reference images."
        )

    if normalized_action == "remove":
        if not reference_id:
            return _as_response(
                action="remove",
                goal=session.goal,
                references=_sorted_references(references),
                error="reference_id is required for remove",
            )
        remaining: list[dict] = []
        removed: dict | None = None
        for item in references:
            if item.get("reference_id") == reference_id and removed is None:
                removed = item
                continue
            remaining.append(item)
        if removed is None:
            return _as_response(
                action="remove",
                goal=session.goal,
                references=_sorted_references(references),
                error=f"Reference image not found: {reference_id}",
            )
        stored_path = removed.get("stored_path")
        if isinstance(stored_path, str):
            try:
                Path(stored_path).unlink(missing_ok=True)
            except Exception:
                pass
        if session.goal is None:
            await replace_session_pending_reference_images_async(ctx, remaining)
        else:
            await replace_session_reference_images_async(ctx, remaining)
        ctx_info(ctx, f"[REFERENCE] Removed reference image {reference_id}")
        return _as_response(
            action="remove",
            goal=session.goal,
            references=_sorted_references(remaining),
            removed_reference_id=reference_id,
            message=f"Removed reference image '{reference_id}'.",
        )

    if not source_path:
        return _as_response(
            action="attach",
            goal=session.goal,
            references=_sorted_references(references),
            error="source_path is required for attach",
        )

    try:
        source = _validate_local_reference_path(source_path)
        stored_path, host_visible_path = _copy_reference_image(source)
    except ValueError as exc:
        return _as_response(
            action="attach",
            goal=session.goal,
            references=_sorted_references(references),
            error=str(exc),
        )

    reference = {
        "reference_id": f"ref_{uuid4().hex[:8]}",
        "goal": session.goal or "__pending_goal__",
        "label": label,
        "notes": notes,
        "target_object": target_object,
        "target_view": target_view,
        "media_type": mimetypes.guess_type(str(source))[0] or "image/png",
        "source_kind": "local_path",
        "original_path": str(source),
        "stored_path": stored_path,
        "host_visible_path": host_visible_path,
        "added_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }
    updated = [*references, reference]
    if session.goal is None:
        await replace_session_pending_reference_images_async(ctx, updated)
        ctx_info(ctx, f"[REFERENCE] Attached pending reference image {reference['reference_id']}")
        return _as_response(
            action="attach",
            goal=None,
            references=_sorted_references(updated),
            message=(
                f"Attached pending reference image '{reference['reference_id']}'. "
                "It will be adopted automatically when the next active goal is set."
            ),
        )

    await replace_session_reference_images_async(ctx, updated)
    ctx_info(ctx, f"[REFERENCE] Attached reference image {reference['reference_id']} for goal '{session.goal}'")
    return _as_response(
        action="attach",
        goal=session.goal,
        references=_sorted_references(updated),
        message=f"Attached reference image '{reference['reference_id']}'.",
    )


async def reference_compare_checkpoint(
    ctx: Context,
    checkpoint_path: str,
    checkpoint_label: str | None = None,
    target_object: str | None = None,
    target_view: str | None = None,
    goal_override: str | None = None,
    prompt_hint: str | None = None,
) -> ReferenceCompareCheckpointResponseContract:
    """Compare one current checkpoint image against the active goal and attached references."""

    try:
        checkpoint = _validate_local_reference_path(checkpoint_path)
    except ValueError as exc:
        return _compare_response(
            action="compare_checkpoint",
            checkpoint_path=checkpoint_path,
            checkpoint_label=checkpoint_label,
            goal=goal_override,
            target_object=target_object,
            target_view=target_view,
            reference_ids=[],
            reference_labels=[],
            error=str(exc),
        )

    return await _run_checkpoint_compare(
        ctx,
        checkpoint=checkpoint,
        checkpoint_label=checkpoint_label,
        target_object=target_object,
        target_view=target_view,
        goal_override=goal_override,
        prompt_hint=prompt_hint,
        response_action="compare_checkpoint",
    )


async def reference_compare_current_view(
    ctx: Context,
    checkpoint_label: str | None = None,
    target_object: str | None = None,
    target_view: str | None = None,
    goal_override: str | None = None,
    prompt_hint: str | None = None,
    width: int = 1280,
    height: int = 960,
    shading: str = "SOLID",
    camera_name: str | None = None,
    focus_target: str | None = None,
    view_name: str | None = None,
    orbit_horizontal: float = 0.0,
    orbit_vertical: float = 0.0,
    zoom_factor: float | None = None,
    persist_view: bool = False,
) -> ReferenceCompareCheckpointResponseContract:
    """Capture one current viewport/camera checkpoint and compare it against attached references."""

    session = await get_session_capability_state_async(ctx)
    effective_goal = goal_override or session.goal
    if not effective_goal:
        return _compare_response(
            action="compare_current_view",
            checkpoint_path="",
            checkpoint_label=checkpoint_label,
            goal=None,
            target_object=target_object,
            target_view=target_view,
            reference_ids=[],
            reference_labels=[],
            error="Set an active goal with router_set_goal(...) before comparing the current view, or pass goal_override.",
        )

    try:
        b64_data = get_scene_handler().get_viewport(
            width=width,
            height=height,
            shading=shading,
            camera_name=camera_name,
            focus_target=focus_target,
            view_name=view_name,
            orbit_horizontal=orbit_horizontal,
            orbit_vertical=orbit_vertical,
            zoom_factor=zoom_factor,
            persist_view=persist_view,
        )
    except RuntimeError as exc:
        return _compare_response(
            action="compare_current_view",
            checkpoint_path="",
            checkpoint_label=checkpoint_label,
            goal=goal_override,
            target_object=target_object,
            target_view=target_view,
            reference_ids=[],
            reference_labels=[],
            error=str(exc),
        )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"checkpoint_compare_{timestamp}_{uuid4().hex[:8]}.jpg"
    latest_name = "checkpoint_compare_latest.jpg"
    internal_file, internal_latest, _external_file, _external_latest = get_viewport_output_paths(
        filename,
        latest_name=latest_name,
    )
    image_bytes = base64.b64decode(b64_data)
    internal_file.write_bytes(image_bytes)
    internal_latest.write_bytes(image_bytes)

    return await _run_checkpoint_compare(
        ctx,
        checkpoint=internal_file,
        checkpoint_label=checkpoint_label,
        target_object=target_object or focus_target,
        target_view=target_view,
        goal_override=goal_override,
        prompt_hint=" | ".join(
            part
            for part in (
                prompt_hint,
                "comparison_mode=current_view_checkpoint",
                f"camera_name={camera_name}" if camera_name else None,
                f"view_name={view_name}" if view_name else None,
                f"shading={shading}",
            )
            if part
        )
        or None,
        response_action="compare_current_view",
    )


async def reference_compare_stage_checkpoint(
    ctx: Context,
    target_object: str | None = None,
    target_objects: list[str] | None = None,
    collection_name: str | None = None,
    checkpoint_label: str | None = None,
    target_view: str | None = None,
    goal_override: str | None = None,
    prompt_hint: str | None = None,
    preset_profile: CapturePresetProfile = "compact",
) -> ReferenceCompareStageCheckpointResponseContract:
    """Capture one deterministic stage view-set and compare it against attached references."""

    checkpoint_target = _safe_checkpoint_token(collection_name or target_object or "scene")
    checkpoint_id = f"stage_checkpoint_{checkpoint_target}_{uuid4().hex[:8]}"
    return await _run_stage_checkpoint_compare(
        ctx,
        checkpoint_id=checkpoint_id,
        checkpoint_label=checkpoint_label,
        target_object=target_object,
        target_objects=target_objects,
        collection_name=collection_name,
        target_view=target_view,
        preset_profile=preset_profile,
        goal_override=goal_override,
        prompt_hint=prompt_hint,
    )


async def reference_iterate_stage_checkpoint(
    ctx: Context,
    target_object: str | None = None,
    target_objects: list[str] | None = None,
    collection_name: str | None = None,
    checkpoint_label: str | None = None,
    target_view: str | None = None,
    goal_override: str | None = None,
    prompt_hint: str | None = None,
    preset_profile: CapturePresetProfile = "compact",
) -> ReferenceIterateStageCheckpointResponseContract:
    """Run one session-aware stage checkpoint iteration and return continuation guidance."""

    compare_result = await reference_compare_stage_checkpoint(
        ctx,
        target_object=target_object,
        target_objects=target_objects,
        collection_name=collection_name,
        checkpoint_label=checkpoint_label,
        target_view=target_view,
        goal_override=goal_override,
        prompt_hint=prompt_hint,
        preset_profile=preset_profile,
    )
    goal = compare_result.goal
    correction_focus = _resolve_actionable_focus(compare_result)
    continue_recommended = bool(correction_focus)
    inspect_from_truth_signal = _should_inspect_from_truth_signal(compare_result.correction_candidates)
    loop_disposition: Literal["continue_build", "inspect_validate", "stop"] = (
        "inspect_validate" if inspect_from_truth_signal else ("continue_build" if continue_recommended else "stop")
    )
    stop_reason = (
        None if continue_recommended else "No actionable correction guidance was returned for this checkpoint."
    )

    if compare_result.error or goal is None:
        return _iterate_stage_response(
            goal=goal,
            target_object=target_object,
            target_objects=list(target_objects or []),
            collection_name=collection_name,
            target_view=target_view,
            checkpoint_id=compare_result.checkpoint_id,
            checkpoint_label=checkpoint_label,
            iteration_index=1,
            loop_disposition="stop",
            continue_recommended=False,
            prior_checkpoint_id=None,
            prior_correction_focus=[],
            correction_focus=correction_focus,
            repeated_correction_focus=[],
            stagnation_count=0,
            compare_result=compare_result,
            correction_candidates=compare_result.correction_candidates,
            budget_control=compare_result.budget_control,
            stop_reason=compare_result.error or stop_reason,
            message="Stage iteration did not complete successfully.",
            error=compare_result.error,
        )

    prior_state = await get_session_value_async(ctx, _REFERENCE_CORRECTION_LOOP_STATE_KEY, None)
    if not isinstance(prior_state, dict):
        prior_state = None

    same_loop = (
        prior_state is not None
        and prior_state.get("goal") == goal
        and prior_state.get("target_object") == target_object
        and list(prior_state.get("target_objects") or []) == list(compare_result.target_objects or [])
        and prior_state.get("collection_name") == collection_name
        and prior_state.get("target_view") == target_view
        and prior_state.get("preset_profile") == preset_profile
    )
    prior_checkpoint_id = (
        str(prior_state.get("last_checkpoint_id")) if same_loop and prior_state.get("last_checkpoint_id") else None
    )
    prior_correction_focus = list(prior_state.get("last_correction_focus") or []) if same_loop else []
    iteration_index = int(prior_state.get("iteration_index") or 0) + 1 if same_loop else 1
    repeated_correction_focus = _repeated_focus(correction_focus, prior_correction_focus)
    prior_stagnation_count = int(prior_state.get("stagnation_count") or 0) if same_loop else 0
    stagnation_count = prior_stagnation_count + 1 if repeated_correction_focus and correction_focus else 0

    if continue_recommended and stagnation_count >= _REFERENCE_CORRECTION_STAGNATION_THRESHOLD:
        loop_disposition = "inspect_validate"

    await set_session_value_async(
        ctx,
        _REFERENCE_CORRECTION_LOOP_STATE_KEY,
        {
            "goal": goal,
            "target_object": target_object,
            "target_objects": list(compare_result.target_objects or []),
            "collection_name": collection_name,
            "target_view": target_view,
            "preset_profile": preset_profile,
            "last_checkpoint_id": compare_result.checkpoint_id,
            "last_checkpoint_label": checkpoint_label,
            "last_correction_focus": correction_focus,
            "iteration_index": iteration_index,
            "stagnation_count": stagnation_count,
        },
    )

    if loop_disposition == "inspect_validate":
        if inspect_from_truth_signal:
            message = (
                "Deterministic truth findings remain high-priority. "
                "Prefer inspect/measure/assert confirmation before another free-form build step."
            )
        else:
            message = (
                "Repeated correction focus persists across stage iterations. "
                "Prefer inspect/measure/assert confirmation before another free-form build step."
            )
    elif continue_recommended:
        message = "Continue the guided build loop using correction_focus first."
    else:
        message = "No further correction loop action is recommended for this checkpoint."

    return _iterate_stage_response(
        goal=goal,
        target_object=target_object,
        target_objects=list(compare_result.target_objects or []),
        collection_name=collection_name,
        target_view=target_view,
        checkpoint_id=compare_result.checkpoint_id,
        checkpoint_label=checkpoint_label,
        iteration_index=iteration_index,
        loop_disposition=loop_disposition,
        continue_recommended=continue_recommended,
        prior_checkpoint_id=prior_checkpoint_id,
        prior_correction_focus=prior_correction_focus,
        correction_focus=correction_focus,
        repeated_correction_focus=repeated_correction_focus,
        stagnation_count=stagnation_count,
        compare_result=compare_result,
        correction_candidates=compare_result.correction_candidates,
        budget_control=compare_result.budget_control,
        stop_reason=stop_reason,
        message=message,
    )
