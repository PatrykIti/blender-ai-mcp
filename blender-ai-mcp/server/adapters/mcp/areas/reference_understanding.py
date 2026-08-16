# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Advisory reference-understanding helpers for the reference MCP surface."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import replace
from typing import Any, Literal

from fastmcp import Context

from server.adapters.mcp.contracts.quality_gates import (
    GatePlanContract,
    GateProposalContract,
    refresh_gate_plan_status,
    without_proposal_source,
)
from server.adapters.mcp.contracts.reference import (
    ReferenceImageRecordContract,
    ReferenceUnderstandingSummaryContract,
)
from server.adapters.mcp.session_capabilities import SessionCapabilityState
from server.adapters.mcp.vision import VisionBackendUnavailableError, VisionImageInput, VisionRequest


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


def _active_reference_records(session: SessionCapabilityState) -> tuple[ReferenceImageRecordContract, ...]:
    return tuple(ReferenceImageRecordContract.model_validate(item) for item in list(session.reference_images or []))


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
) -> SessionCapabilityState:
    """Refresh session-scoped reference understanding from active references when possible."""

    current = session or await get_session_capability_state_async(ctx)
    existing_gate_plan = GatePlanContract.model_validate(current.gate_plan) if current.gate_plan is not None else None
    base_gate_plan = without_reference_understanding_gates(
        existing_gate_plan,
        tracked_gate_ids=current.reference_understanding_gate_ids,
    )
    if not current.goal:
        cleared = replace(
            current,
            gate_plan=None if base_gate_plan is None else base_gate_plan.model_dump(mode="json", exclude_none=True),
            reference_understanding_summary=None,
            reference_understanding_gate_ids=None,
        )
        return await _persist_reference_understanding_state_async(
            ctx,
            cleared,
            set_session_capability_state_async=set_session_capability_state_async,
            apply_visibility_for_session_state=apply_visibility_for_session_state,
        )

    reference_records = _active_reference_records(current)
    reference_ids = [record.reference_id for record in reference_records]
    if not reference_records:
        blocked = blocked_reference_understanding_summary(
            goal=current.goal,
            reason="reference_images_required",
            message="Attach at least one active reference image before reference understanding can run.",
        )
        updated = replace(
            current,
            gate_plan=None if base_gate_plan is None else base_gate_plan.model_dump(mode="json", exclude_none=True),
            reference_understanding_summary=blocked.model_dump(mode="json", exclude_none=True),
            reference_understanding_gate_ids=None,
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
        return current

    request = reference_understanding_request(
        goal=current.goal,
        reference_records=reference_records,
        build_reference_capture_images=build_reference_capture_images,
    )
    resolver = get_vision_backend_resolver()
    try:
        backend = resolver.resolve_default()
        payload = await backend.analyze(request)
        summary = ReferenceUnderstandingSummaryContract.model_validate(payload)
    except VisionBackendUnavailableError as exc:
        unavailable = blocked_reference_understanding_summary(
            goal=current.goal,
            reason="vision_backend_unavailable",
            message=str(exc),
            reference_ids=reference_ids,
        )
        updated = replace(
            current,
            gate_plan=None if base_gate_plan is None else base_gate_plan.model_dump(mode="json", exclude_none=True),
            reference_understanding_summary=unavailable.model_dump(mode="json", exclude_none=True),
            reference_understanding_gate_ids=None,
        )
        return await _persist_reference_understanding_state_async(
            ctx,
            updated,
            set_session_capability_state_async=set_session_capability_state_async,
            apply_visibility_for_session_state=apply_visibility_for_session_state,
        )
    except Exception as exc:
        unavailable = blocked_reference_understanding_summary(
            goal=current.goal,
            reason="vision_backend_unavailable",
            message=f"Reference understanding could not complete: {exc}",
            reference_ids=reference_ids,
        )
        updated = replace(
            current,
            gate_plan=None if base_gate_plan is None else base_gate_plan.model_dump(mode="json", exclude_none=True),
            reference_understanding_summary=unavailable.model_dump(mode="json", exclude_none=True),
            reference_understanding_gate_ids=None,
        )
        return await _persist_reference_understanding_state_async(
            ctx,
            updated,
            set_session_capability_state_async=set_session_capability_state_async,
            apply_visibility_for_session_state=apply_visibility_for_session_state,
        )

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

    final_state = replace(
        updated_session,
        reference_understanding_summary=summary.model_dump(mode="json", exclude_none=True),
        reference_understanding_gate_ids=accepted_gate_ids or None,
    )
    return await _persist_reference_understanding_state_async(
        ctx,
        final_state,
        set_session_capability_state_async=set_session_capability_state_async,
        apply_visibility_for_session_state=apply_visibility_for_session_state,
    )
