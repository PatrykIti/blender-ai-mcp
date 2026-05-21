# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Advisory reference-understanding helpers for the reference MCP surface."""

from __future__ import annotations

import logging
import re
import time
from collections.abc import Awaitable, Callable
from dataclasses import replace
from typing import Any, Literal

from fastmcp import Context

from server.adapters.mcp.areas.reference_feedback import (
    augment_reference_understanding_summary,
    build_reference_strategy_state,
)
from server.adapters.mcp.contracts.quality_gates import (
    GatePlanContract,
    GateProposalContract,
    GateProposalGateContract,
    refresh_gate_plan_status,
    without_proposal_source,
)
from server.adapters.mcp.contracts.reference import (
    ReferenceImageRecordContract,
    ReferenceUnderstandingSummaryContract,
)
from server.adapters.mcp.session_capabilities import SessionCapabilityState
from server.adapters.mcp.vision import VisionBackendUnavailableError, VisionImageInput, VisionRequest
from server.adapters.mcp.vision.reference_gates import derive_tail_profile_gate_proposals
from server.adapters.mcp.vision.reference_support import augment_reference_understanding_optional_support
from server.infrastructure.debug_profiles import emit_debug_log

logger = logging.getLogger(__name__)


def _canonicalize_creature_reference_target_label(
    target_label: str,
    *,
    part_label: str,
) -> str:
    normalized = target_label.strip().lower().replace(" ", "_")
    if not normalized:
        return normalized
    target_tokens = {token for token in re.split(r"[^a-z0-9]+", normalized) if token}
    part_tokens = {token for token in re.split(r"[^a-z0-9]+", part_label.strip().lower()) if token}
    combined_tokens = target_tokens | part_tokens

    def _looks_generic(tokens: set[str], *, allowed: set[str]) -> bool:
        return bool(tokens) and tokens <= allowed

    if normalized in {"body", "body_core", "body_mass", "torso", "torso_mass"} or _looks_generic(
        combined_tokens,
        allowed={"body", "core", "mass", "torso", "main"},
    ):
        return "body_core"
    if normalized in {"head", "head_mass", "head_core"} or _looks_generic(
        combined_tokens,
        allowed={"head", "mass", "core"},
    ):
        return "head_mass"
    if normalized in {"tail", "tail_mass", "tail_core"} or _looks_generic(
        combined_tokens,
        allowed={"tail", "mass", "core", "silhouette", "profile"},
    ):
        return "tail_mass"
    if normalized in {"snout", "snout_mass", "muzzle", "nose"} or _looks_generic(
        combined_tokens,
        allowed={"snout", "mass", "muzzle", "nose", "core"},
    ):
        return "snout_mass"
    if normalized in {"ear", "ears", "ear_pair", "earpair"} or _looks_generic(
        combined_tokens,
        allowed={"ear", "ears", "pair", "silhouette"},
    ):
        return "ear_pair"
    if normalized in {"eye", "eyes", "eye_pair", "eyepair"} or _looks_generic(
        combined_tokens,
        allowed={"eye", "eyes", "pair", "visible", "readable"},
    ):
        return "eye_pair"
    if normalized in {
        "foreleg",
        "forelegs",
        "front_leg",
        "front_legs",
        "frontleg",
        "frontlegs",
        "forelimb",
        "forelimbs",
        "foreleg_pair",
        "forelegpair",
    } or _looks_generic(
        combined_tokens,
        allowed={
            "foreleg",
            "forelegs",
            "front",
            "frontleg",
            "frontlegs",
            "forelimb",
            "forelimbs",
            "legs",
            "leg",
            "pair",
        },
    ):
        return "foreleg_pair"
    if normalized in {
        "hindleg",
        "hindlegs",
        "back_leg",
        "back_legs",
        "backleg",
        "backlegs",
        "rear_leg",
        "rear_legs",
        "hindlimb",
        "hindlimbs",
        "hindleg_pair",
        "hindlegpair",
    } or _looks_generic(
        combined_tokens,
        allowed={
            "hindleg",
            "hindlegs",
            "back",
            "backleg",
            "backlegs",
            "rear",
            "rearleg",
            "rearlegs",
            "hindlimb",
            "hindlimbs",
            "legs",
            "leg",
            "pair",
        },
    ):
        return "hindleg_pair"
    return normalized


def _canonicalize_reference_understanding_summary_targets(
    summary: ReferenceUnderstandingSummaryContract,
) -> ReferenceUnderstandingSummaryContract:
    if summary.status != "available" or summary.subject is None or summary.subject.category != "creature":
        return summary

    required_parts = [
        part.model_copy(
            update={
                "target_label": _canonicalize_creature_reference_target_label(
                    str(part.target_label or part.part_label),
                    part_label=part.part_label,
                )
            }
        )
        for part in list(summary.required_parts or [])
    ]
    gate_proposals = [
        gate.model_copy(
            update={
                "target_label": _canonicalize_creature_reference_target_label(
                    str(gate.target_label or gate.label),
                    part_label=str(gate.label or gate.target_label or ""),
                )
            }
        )
        for gate in list(summary.gate_proposals or [])
    ]
    mass_recipe = [
        item.model_copy(
            update={
                "target_label": _canonicalize_creature_reference_target_label(
                    item.target_label,
                    part_label=item.target_label,
                ),
                "anchor_role_candidates": [
                    _canonicalize_creature_reference_target_label(candidate, part_label=candidate)
                    for candidate in list(item.anchor_role_candidates or [])
                ],
            }
        )
        for item in list(summary.mass_recipe or [])
    ]
    attachment_plan = [
        item.model_copy(
            update={
                "target_label": _canonicalize_creature_reference_target_label(
                    item.target_label,
                    part_label=item.target_label,
                ),
                "anchor_role_candidates": [
                    _canonicalize_creature_reference_target_label(candidate, part_label=candidate)
                    for candidate in list(item.anchor_role_candidates or [])
                ],
            }
        )
        for item in list(summary.attachment_plan or [])
    ]
    contact_expectations = [
        item.model_copy(
            update={
                "target_label": _canonicalize_creature_reference_target_label(
                    item.target_label,
                    part_label=item.target_label,
                ),
            }
        )
        for item in list(summary.contact_expectations or [])
    ]
    shape_profile_hints = [
        item.model_copy(
            update={
                "target_label": _canonicalize_creature_reference_target_label(
                    item.target_label,
                    part_label=item.target_label,
                ),
            }
        )
        for item in list(summary.shape_profile_hints or [])
    ]
    silhouette_landmarks = [
        item.model_copy(
            update={
                "target_label": (
                    _canonicalize_creature_reference_target_label(item.target_label, part_label=item.target_label)
                    if item.target_label is not None
                    else None
                ),
            }
        )
        for item in list(summary.silhouette_landmarks or [])
    ]
    return summary.model_copy(
        update={
            "required_parts": required_parts,
            "mass_recipe": mass_recipe,
            "attachment_plan": attachment_plan,
            "contact_expectations": contact_expectations,
            "shape_profile_hints": shape_profile_hints,
            "silhouette_landmarks": silhouette_landmarks,
            "part_order": [
                _canonicalize_creature_reference_target_label(item, part_label=item)
                for item in list(summary.part_order or [])
            ],
            "must_seat_before_next_stage": [
                _canonicalize_creature_reference_target_label(item, part_label=item)
                for item in list(summary.must_seat_before_next_stage or [])
            ],
            "gate_proposals": gate_proposals,
        }
    )


def blocked_reference_understanding_summary(
    *,
    goal: str | None,
    reason: Literal["goal_required", "reference_images_required", "vision_backend_unavailable"],
    message: str,
    reference_ids: list[str] | None = None,
) -> ReferenceUnderstandingSummaryContract:
    status: Literal["blocked", "unavailable"] = "blocked"
    if reason == "vision_backend_unavailable":
        status = "unavailable"
    return ReferenceUnderstandingSummaryContract(
        status=status,
        goal=goal,
        reference_ids=list(reference_ids or []),
        reason=reason,
        message=message,
    )


def _with_reference_understanding_profile_gate_defaults(
    summary: ReferenceUnderstandingSummaryContract,
) -> ReferenceUnderstandingSummaryContract:
    """Derive generic profile gates from typed RU parts when no explicit gate slice exists."""

    if summary.gate_proposals:
        return summary

    derived = [
        GateProposalGateContract.model_validate(payload)
        for payload in derive_tail_profile_gate_proposals(
            [part.model_dump(mode="json", exclude_none=True) for part in summary.required_parts]
        )
    ]

    if not derived:
        return summary
    return summary.model_copy(update={"gate_proposals": [*summary.gate_proposals, *derived]})


def _redact_local_paths(text: str) -> str:
    return re.sub(
        r"(?<!\w)(?:[A-Za-z]:[\\/]|/|\.{1,2}[\\/]|~[\\/])[^\s,;:]+|[^\s,;:]*\\[^\s,;:]+",
        "[redacted-path]",
        text,
    )


def _sanitize_reference_understanding_error_message(message: str) -> str:
    return _redact_local_paths(message)


def _active_reference_records(session: SessionCapabilityState) -> tuple[ReferenceImageRecordContract, ...]:
    return tuple(ReferenceImageRecordContract.model_validate(item) for item in list(session.reference_images or []))


def _active_reference_ids(session: SessionCapabilityState) -> list[str]:
    return [record.reference_id for record in _active_reference_records(session)]


def _session_has_material_reference_state(session: SessionCapabilityState) -> bool:
    return any(
        (
            session.goal,
            session.reference_images,
            session.pending_reference_images,
            session.reference_understanding_summary,
            session.gate_plan,
            session.reference_strategy_state,
            session.guided_flow_state,
        )
    )


def reference_understanding_request(
    *,
    goal: str,
    reference_records: tuple[ReferenceImageRecordContract, ...],
    build_reference_capture_images: Callable[..., tuple[Any, ...]],
) -> VisionRequest:
    reference_images = build_reference_capture_images(reference_records)
    return VisionRequest(
        goal=goal,
        images=tuple(
            VisionImageInput(
                path=image.image_path,
                role="reference",
                label=image.label,
                media_type=image.media_type,
            )
            for image in reference_images
        ),
        prompt_hint="reference_understanding",
        metadata={
            "mode": "reference_understanding",
            "reference_ids": [record.reference_id for record in reference_records],
            "reference_labels": [record.label or record.reference_id for record in reference_records],
            "source": "reference_images",
        },
    )


def without_reference_understanding_gates(
    gate_plan: GatePlanContract | None,
    *,
    tracked_gate_ids: list[str] | None,
) -> GatePlanContract | None:
    if gate_plan is None:
        return None

    tracked_ids = {str(item).strip() for item in tracked_gate_ids or [] if str(item).strip()}
    retained_gates = []
    removed_gate_ids: set[str] = set()
    for gate in gate_plan.gates:
        if gate.gate_id not in tracked_ids and "reference_understanding" not in gate.proposal_sources:
            retained_gates.append(gate)
            continue
        retained_gate = without_proposal_source(gate, "reference_understanding")
        if retained_gate is None:
            removed_gate_ids.add(gate.gate_id)
            continue
        retained_gates.append(retained_gate)
    retained_warnings = [
        warning
        for warning in gate_plan.policy_warnings
        if warning.gate_id is None or warning.gate_id not in removed_gate_ids
    ]
    return refresh_gate_plan_status(
        gate_plan.model_copy(
            update={
                "gates": retained_gates,
                "policy_warnings": retained_warnings,
            }
        )
    )


def reference_understanding_gate_slice(gate_plan: GatePlanContract | None) -> GatePlanContract | None:
    if gate_plan is None:
        return None

    slice_gates = [gate for gate in gate_plan.gates if "reference_understanding" in gate.proposal_sources]
    if not slice_gates:
        return None

    slice_gate_ids = {gate.gate_id for gate in slice_gates}
    slice_warnings = [
        warning for warning in gate_plan.policy_warnings if warning.gate_id is None or warning.gate_id in slice_gate_ids
    ]
    return refresh_gate_plan_status(
        gate_plan.model_copy(
            update={
                "gates": slice_gates,
                "policy_warnings": slice_warnings,
            }
        )
    )


def _rebuild_reference_understanding_gate_ids(gate_plan: Any) -> list[str] | None:
    if gate_plan is None:
        return None
    if isinstance(gate_plan, GatePlanContract):
        contract_gate_ids = [
            gate.gate_id for gate in gate_plan.gates if "reference_understanding" in gate.proposal_sources
        ]
        return contract_gate_ids or None
    if isinstance(gate_plan, dict):
        gate_ids: list[str] = []
        for raw_gate in list(gate_plan.get("gates") or []):
            if not isinstance(raw_gate, dict):
                continue
            gate_id = str(raw_gate.get("gate_id") or "").strip()
            proposal_sources = raw_gate.get("proposal_sources") or []
            if gate_id and isinstance(proposal_sources, list) and "reference_understanding" in proposal_sources:
                gate_ids.append(gate_id)
        return gate_ids or None
    return None


def _optional_support_needs_refresh(
    summary: ReferenceUnderstandingSummaryContract,
    *,
    runtime_config: Any,
) -> bool:
    if runtime_config is None:
        return False

    provenance_by_source: dict[str, list[Any]] = {}
    for item in list(summary.source_provenance or []):
        provenance_by_source.setdefault(item.source, []).append(item)

    classifier = getattr(runtime_config, "active_reference_classifier", None)
    if classifier is not None and getattr(classifier, "enabled", False):
        classifier_provenance = provenance_by_source.get("classification_scores", [])
        if not classifier_provenance:
            return True
        if any("unavailable" not in str(item.summary or "").lower() for item in classifier_provenance):
            pass
        if not summary.classification_scores and any(
            "unavailable" in str(item.summary or "").lower() for item in classifier_provenance
        ):
            if all("unavailable" in str(item.summary or "").lower() for item in classifier_provenance):
                return True

    segmentation = getattr(runtime_config, "active_segmentation_sidecar", None)
    if segmentation is not None and getattr(segmentation, "enabled", False):
        segmentation_provenance = provenance_by_source.get("part_segmentation", [])
        if not segmentation_provenance:
            return True
        if any("unavailable" not in str(item.summary or "").lower() for item in segmentation_provenance):
            pass
        if not summary.segmentation_artifacts and any(
            "unavailable" in str(item.summary or "").lower() for item in segmentation_provenance
        ):
            if all("unavailable" in str(item.summary or "").lower() for item in segmentation_provenance):
                return True

    return False


async def _persist_reference_understanding_state_async(
    ctx: Context,
    state: SessionCapabilityState,
    *,
    set_session_capability_state_async: Callable[[Context, SessionCapabilityState], Awaitable[None]],
    apply_visibility_for_session_state: Callable[[Context, SessionCapabilityState], Awaitable[Any]],
) -> SessionCapabilityState:
    """Persist one RU-driven session state update and immediately reapply visibility."""

    await set_session_capability_state_async(ctx, state)
    await apply_visibility_for_session_state(ctx, state)
    return state


async def refresh_reference_understanding_summary(
    ctx: Context,
    *,
    session: SessionCapabilityState | None = None,
    get_session_capability_state_async: Callable[[Context], Awaitable[SessionCapabilityState]],
    set_session_capability_state_async: Callable[[Context, SessionCapabilityState], Awaitable[None]],
    apply_visibility_for_session_state: Callable[[Context, SessionCapabilityState], Awaitable[Any]],
    build_reference_capture_images: Callable[..., tuple[Any, ...]],
    get_vision_backend_resolver: Callable[[], Any],
    ingest_quality_gate_proposal_async: Callable[[Context, dict[str, Any]], Awaitable[Any]],
    retry_on_reference_drift: bool = True,
) -> SessionCapabilityState:
    """Refresh session-scoped reference understanding from active references when possible."""

    current = session or await get_session_capability_state_async(ctx)
    existing_gate_plan = GatePlanContract.model_validate(current.gate_plan) if current.gate_plan is not None else None
    base_gate_plan = without_reference_understanding_gates(
        existing_gate_plan,
        tracked_gate_ids=current.reference_understanding_gate_ids,
    )
    if not current.goal:
        emit_debug_log(
            "vision",
            logger,
            "ru_skip reason=goal_required active_reference_count=%d",
            len(current.reference_images or []),
        )
        cleared = replace(
            current,
            gate_plan=None if base_gate_plan is None else base_gate_plan.model_dump(mode="json", exclude_none=True),
            reference_understanding_summary=None,
            reference_understanding_gate_ids=None,
            reference_strategy_state=None,
        )
        return await _persist_reference_understanding_state_async(
            ctx,
            cleared,
            set_session_capability_state_async=set_session_capability_state_async,
            apply_visibility_for_session_state=apply_visibility_for_session_state,
        )

    reference_records = _active_reference_records(current)
    reference_ids = [record.reference_id for record in reference_records]

    async def _persist_refresh_state(
        state: SessionCapabilityState,
    ) -> SessionCapabilityState:
        latest = await get_session_capability_state_async(ctx)
        if session is not None and not _session_has_material_reference_state(latest):
            latest = current
        latest_reference_ids = _active_reference_ids(latest)
        if latest.goal != current.goal or latest_reference_ids != reference_ids:
            emit_debug_log(
                "vision",
                logger,
                "ru_retry_on_reference_drift goal_changed=%s reference_ids_before=%s reference_ids_after=%s retry=%s",
                latest.goal != current.goal,
                reference_ids,
                latest_reference_ids,
                retry_on_reference_drift,
                level=logging.WARNING,
            )
            if retry_on_reference_drift:
                return await refresh_reference_understanding_summary(
                    ctx,
                    session=latest,
                    get_session_capability_state_async=get_session_capability_state_async,
                    set_session_capability_state_async=set_session_capability_state_async,
                    apply_visibility_for_session_state=apply_visibility_for_session_state,
                    build_reference_capture_images=build_reference_capture_images,
                    get_vision_backend_resolver=get_vision_backend_resolver,
                    ingest_quality_gate_proposal_async=ingest_quality_gate_proposal_async,
                    retry_on_reference_drift=False,
                )
            return latest
        return await _persist_reference_understanding_state_async(
            ctx,
            state,
            set_session_capability_state_async=set_session_capability_state_async,
            apply_visibility_for_session_state=apply_visibility_for_session_state,
        )

    if not reference_records:
        emit_debug_log(
            "vision",
            logger,
            "ru_blocked reason=reference_images_required goal_present=%s",
            current.goal is not None,
            level=logging.WARNING,
        )
        blocked = blocked_reference_understanding_summary(
            goal=current.goal,
            reason="reference_images_required",
            message="Attach at least one active reference image before reference understanding can run.",
        )
        blocked_strategy = build_reference_strategy_state(blocked)
        updated = replace(
            current,
            gate_plan=None if base_gate_plan is None else base_gate_plan.model_dump(mode="json", exclude_none=True),
            reference_understanding_summary=blocked.model_dump(mode="json", exclude_none=True),
            reference_understanding_gate_ids=None,
            reference_strategy_state=(
                None if blocked_strategy is None else blocked_strategy.model_dump(mode="json", exclude_none=True)
            ),
        )
        return await _persist_reference_understanding_state_async(
            ctx,
            updated,
            set_session_capability_state_async=set_session_capability_state_async,
            apply_visibility_for_session_state=apply_visibility_for_session_state,
        )

    existing_summary = current.reference_understanding_summary or {}
    if (
        existing_summary.get("status") == "available"
        and existing_summary.get("goal") == current.goal
        and list(existing_summary.get("reference_ids") or []) == reference_ids
    ):
        summary = ReferenceUnderstandingSummaryContract.model_validate(existing_summary)
        resolver = get_vision_backend_resolver()
        runtime_config = getattr(resolver, "runtime_config", None)
        rebuilt_gate_ids = (
            _rebuild_reference_understanding_gate_ids(current.gate_plan)
            if current.reference_understanding_gate_ids is None
            else current.reference_understanding_gate_ids
        )
        if _optional_support_needs_refresh(summary, runtime_config=runtime_config):
            emit_debug_log(
                "vision",
                logger,
                "ru_cached_optional_support_refresh reference_count=%d model=%s",
                len(reference_records),
                getattr(runtime_config, "active_model_name", None) if runtime_config is not None else None,
            )
            refreshed_summary = await augment_reference_understanding_optional_support(
                summary,
                goal=current.goal,
                reference_records=reference_records,
                runtime_config=runtime_config,
            )
            if refreshed_summary.model_dump(mode="json", exclude_none=True) != existing_summary:
                rebuilt_strategy = (
                    build_reference_strategy_state(refreshed_summary)
                    if current.reference_strategy_state is None
                    else None
                )
                updated = replace(
                    current,
                    reference_understanding_summary=refreshed_summary.model_dump(mode="json", exclude_none=True),
                    reference_understanding_gate_ids=rebuilt_gate_ids,
                    reference_strategy_state=(
                        rebuilt_strategy.model_dump(mode="json", exclude_none=True)
                        if rebuilt_strategy is not None
                        else current.reference_strategy_state
                    ),
                )
                return await _persist_refresh_state(updated)

        emit_debug_log(
            "vision",
            logger,
            "ru_cached_reuse reference_count=%d model=%s",
            len(reference_records),
            getattr(runtime_config, "active_model_name", None) if runtime_config is not None else None,
        )
        if current.reference_strategy_state is None:
            rebuilt_strategy = build_reference_strategy_state(summary)
            if rebuilt_strategy is not None:
                repaired = replace(
                    current,
                    reference_understanding_gate_ids=rebuilt_gate_ids,
                    reference_strategy_state=rebuilt_strategy.model_dump(mode="json", exclude_none=True),
                )
                return await _persist_refresh_state(repaired)
        if current.reference_understanding_gate_ids is None and rebuilt_gate_ids is not None:
            repaired = replace(current, reference_understanding_gate_ids=rebuilt_gate_ids)
            return await _persist_refresh_state(repaired)
        return current

    request = reference_understanding_request(
        goal=current.goal,
        reference_records=reference_records,
        build_reference_capture_images=build_reference_capture_images,
    )
    resolver = get_vision_backend_resolver()
    runtime_config = getattr(resolver, "runtime_config", None)
    provider_name = getattr(runtime_config, "provider", None) if runtime_config is not None else None
    model_name = getattr(runtime_config, "active_model_name", None) if runtime_config is not None else None
    started = time.perf_counter()
    emit_debug_log(
        "vision",
        logger,
        "ru_start reference_count=%d provider=%s model=%s goal_present=%s",
        len(reference_records),
        provider_name,
        model_name,
        current.goal is not None,
    )
    try:
        backend = resolver.resolve_default()
        payload = await backend.analyze(request)
        summary = ReferenceUnderstandingSummaryContract.model_validate(payload)
        summary = _canonicalize_reference_understanding_summary_targets(summary)
        summary = augment_reference_understanding_summary(summary, reference_records=reference_records)
        summary = _with_reference_understanding_profile_gate_defaults(summary)
        summary = await augment_reference_understanding_optional_support(
            summary,
            goal=current.goal,
            reference_records=reference_records,
            runtime_config=runtime_config,
        )
        emit_debug_log(
            "vision",
            logger,
            "ru_finish reference_count=%d elapsed_ms=%.1f provider=%s model=%s status=%s",
            len(reference_records),
            (time.perf_counter() - started) * 1000.0,
            provider_name,
            model_name,
            summary.status,
        )
    except VisionBackendUnavailableError as exc:
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        sanitized_error = _sanitize_reference_understanding_error_message(str(exc))
        emit_debug_log(
            "vision",
            logger,
            "ru_unavailable reference_count=%d elapsed_ms=%.1f provider=%s model=%s reason=%s",
            len(reference_records),
            elapsed_ms,
            provider_name,
            model_name,
            sanitized_error,
            level=logging.WARNING,
        )
        unavailable = blocked_reference_understanding_summary(
            goal=current.goal,
            reason="vision_backend_unavailable",
            message=sanitized_error,
            reference_ids=reference_ids,
        )
        unavailable_strategy = build_reference_strategy_state(unavailable)
        updated = replace(
            current,
            gate_plan=None if base_gate_plan is None else base_gate_plan.model_dump(mode="json", exclude_none=True),
            reference_understanding_summary=unavailable.model_dump(mode="json", exclude_none=True),
            reference_understanding_gate_ids=None,
            reference_strategy_state=(
                None
                if unavailable_strategy is None
                else unavailable_strategy.model_dump(mode="json", exclude_none=True)
            ),
        )
        return await _persist_refresh_state(updated)
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        sanitized_error = _sanitize_reference_understanding_error_message(
            f"Reference understanding could not complete: {exc}"
        )
        emit_debug_log(
            "vision",
            logger,
            "ru_error reference_count=%d elapsed_ms=%.1f provider=%s model=%s reason=%s",
            len(reference_records),
            elapsed_ms,
            provider_name,
            model_name,
            sanitized_error,
            level=logging.WARNING,
        )
        unavailable = blocked_reference_understanding_summary(
            goal=current.goal,
            reason="vision_backend_unavailable",
            message=sanitized_error,
            reference_ids=reference_ids,
        )
        unavailable_strategy = build_reference_strategy_state(unavailable)
        updated = replace(
            current,
            gate_plan=None if base_gate_plan is None else base_gate_plan.model_dump(mode="json", exclude_none=True),
            reference_understanding_summary=unavailable.model_dump(mode="json", exclude_none=True),
            reference_understanding_gate_ids=None,
            reference_strategy_state=(
                None
                if unavailable_strategy is None
                else unavailable_strategy.model_dump(mode="json", exclude_none=True)
            ),
        )
        return await _persist_refresh_state(updated)

    accepted_gate_ids: list[str] | None = None
    updated_session = replace(
        current,
        gate_plan=None if base_gate_plan is None else base_gate_plan.model_dump(mode="json", exclude_none=True),
    )
    if summary.gate_proposals:
        gate_proposal = GateProposalContract(
            proposal_id=summary.understanding_id,
            source="reference_understanding",
            goal=current.goal,
            gates=summary.gate_proposals,
            source_provenance=summary.source_provenance,
        )
        intake_result = await ingest_quality_gate_proposal_async(
            ctx,
            gate_proposal.model_dump(mode="json", exclude_none=True),
        )
        if intake_result.status == "accepted" and intake_result.gate_plan is not None:
            replacement_slice = reference_understanding_gate_slice(intake_result.gate_plan)
            updated_session = replace(
                updated_session,
                gate_plan=intake_result.gate_plan.model_dump(mode="json", exclude_none=True),
            )
            accepted_gate_ids = (
                None if replacement_slice is None else [gate.gate_id for gate in replacement_slice.gates]
            )

    final_strategy = build_reference_strategy_state(summary)
    final_state = replace(
        updated_session,
        reference_understanding_summary=summary.model_dump(mode="json", exclude_none=True),
        reference_understanding_gate_ids=accepted_gate_ids or None,
        reference_strategy_state=None
        if final_strategy is None
        else final_strategy.model_dump(mode="json", exclude_none=True),
    )
    return await _persist_refresh_state(final_state)
