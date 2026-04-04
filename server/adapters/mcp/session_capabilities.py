# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Session-scoped capability state for adaptive FastMCP surfaces."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Any, Literal

from fastmcp import Context

from server.adapters.mcp.session_phase import SessionPhase, coerce_session_phase
from server.adapters.mcp.session_state import (
    get_session_value,
    get_session_value_async,
    set_session_value,
    set_session_value_async,
)
from server.router.application.session_phase_hints import derive_phase_hint_from_router_result

if TYPE_CHECKING:
    from server.adapters.mcp.guided_mode import VisibilityDiagnostics

SESSION_GOAL_KEY = "goal"
SESSION_PENDING_CLARIFICATION_KEY = "pending_clarification"
SESSION_LAST_ROUTER_STATUS_KEY = "last_router_status"
SESSION_POLICY_CONTEXT_KEY = "policy_context"
SESSION_SURFACE_PROFILE_KEY = "surface_profile"
SESSION_CONTRACT_VERSION_KEY = "contract_version"
SESSION_PENDING_ELICITATION_ID_KEY = "pending_elicitation_id"
SESSION_PENDING_WORKFLOW_NAME_KEY = "pending_workflow_name"
SESSION_PARTIAL_ANSWERS_KEY = "partial_answers"
SESSION_PENDING_QUESTION_SET_ID_KEY = "pending_question_set_id"
SESSION_LAST_ELICITATION_ACTION_KEY = "last_elicitation_action"
SESSION_LAST_ROUTER_DISPOSITION_KEY = "last_router_disposition"
SESSION_LAST_ROUTER_ERROR_KEY = "last_router_error"
SESSION_REFERENCE_IMAGES_KEY = "reference_images"
SESSION_GUIDED_HANDOFF_KEY = "guided_handoff"
SESSION_PENDING_REFERENCE_IMAGES_KEY = "pending_reference_images"
_GENERIC_PENDING_GOAL = "__pending_goal__"


@dataclass(frozen=True)
class SessionCapabilityState:
    """Serializable session state used by phase-aware visibility decisions."""

    phase: SessionPhase
    goal: str | None = None
    pending_clarification: dict[str, Any] | None = None
    last_router_status: str | None = None
    policy_context: dict[str, Any] | None = None
    surface_profile: str | None = None
    contract_version: str | None = None
    pending_elicitation_id: str | None = None
    pending_workflow_name: str | None = None
    partial_answers: dict[str, Any] | None = None
    pending_question_set_id: str | None = None
    last_elicitation_action: str | None = None
    last_router_disposition: str | None = None
    last_router_error: str | None = None
    reference_images: list[dict[str, Any]] | None = None
    guided_handoff: dict[str, Any] | None = None
    pending_reference_images: list[dict[str, Any]] | None = None


GuidedReferenceBlockingReason = Literal[
    "active_goal_required",
    "goal_input_pending",
    "pending_references_detected",
    "reference_images_required",
    "reference_session_not_ready",
]
GuidedReferenceNextAction = Literal[
    "call_router_set_goal",
    "answer_pending_goal_questions",
    "attach_reference_images",
    "call_router_get_status",
]


@dataclass(frozen=True)
class GuidedReferenceReadinessState:
    """Serializable readiness state for guided reference compare/iterate flows."""

    status: Literal["ready", "blocked"] = "blocked"
    goal: str | None = None
    has_active_goal: bool = False
    goal_input_pending: bool = False
    attached_reference_count: int = 0
    pending_reference_count: int = 0
    compare_ready: bool = False
    iterate_ready: bool = False
    blocking_reason: GuidedReferenceBlockingReason | None = None
    next_action: GuidedReferenceNextAction | None = None


def infer_phase_from_router_status(
    status: str | None,
    *,
    current_phase: SessionPhase | None = None,
) -> SessionPhase:
    """Map coarse router statuses onto the first-pass phase set."""

    if current_phase == SessionPhase.INSPECT_VALIDATE:
        return current_phase

    mapping = {
        "ready": SessionPhase.BUILD,
        "needs_input": SessionPhase.PLANNING,
        "no_match": SessionPhase.PLANNING,
        "disabled": SessionPhase.PLANNING,
        "error": SessionPhase.PLANNING,
    }
    return mapping.get(status or "", current_phase or SessionPhase.BOOTSTRAP)


def get_session_capability_state(ctx: Context) -> SessionCapabilityState:
    """Read the canonical session capability state from Context storage."""

    return SessionCapabilityState(
        phase=coerce_session_phase(get_session_value(ctx, "phase", SessionPhase.BOOTSTRAP)),
        goal=get_session_value(ctx, SESSION_GOAL_KEY),
        pending_clarification=get_session_value(ctx, SESSION_PENDING_CLARIFICATION_KEY),
        last_router_status=get_session_value(ctx, SESSION_LAST_ROUTER_STATUS_KEY),
        policy_context=get_session_value(ctx, SESSION_POLICY_CONTEXT_KEY),
        surface_profile=get_session_value(ctx, SESSION_SURFACE_PROFILE_KEY),
        contract_version=get_session_value(ctx, SESSION_CONTRACT_VERSION_KEY),
        pending_elicitation_id=get_session_value(ctx, SESSION_PENDING_ELICITATION_ID_KEY),
        pending_workflow_name=get_session_value(ctx, SESSION_PENDING_WORKFLOW_NAME_KEY),
        partial_answers=get_session_value(ctx, SESSION_PARTIAL_ANSWERS_KEY),
        pending_question_set_id=get_session_value(ctx, SESSION_PENDING_QUESTION_SET_ID_KEY),
        last_elicitation_action=get_session_value(ctx, SESSION_LAST_ELICITATION_ACTION_KEY),
        last_router_disposition=get_session_value(ctx, SESSION_LAST_ROUTER_DISPOSITION_KEY),
        last_router_error=get_session_value(ctx, SESSION_LAST_ROUTER_ERROR_KEY),
        reference_images=get_session_value(ctx, SESSION_REFERENCE_IMAGES_KEY),
        guided_handoff=get_session_value(ctx, SESSION_GUIDED_HANDOFF_KEY),
        pending_reference_images=get_session_value(ctx, SESSION_PENDING_REFERENCE_IMAGES_KEY),
    )


async def get_session_capability_state_async(ctx: Context) -> SessionCapabilityState:
    """Async variant of session capability state lookup for native FastMCP Context."""

    return SessionCapabilityState(
        phase=coerce_session_phase(await get_session_value_async(ctx, "phase", SessionPhase.BOOTSTRAP)),
        goal=await get_session_value_async(ctx, SESSION_GOAL_KEY),
        pending_clarification=await get_session_value_async(ctx, SESSION_PENDING_CLARIFICATION_KEY),
        last_router_status=await get_session_value_async(ctx, SESSION_LAST_ROUTER_STATUS_KEY),
        policy_context=await get_session_value_async(ctx, SESSION_POLICY_CONTEXT_KEY),
        surface_profile=await get_session_value_async(ctx, SESSION_SURFACE_PROFILE_KEY),
        contract_version=await get_session_value_async(ctx, SESSION_CONTRACT_VERSION_KEY),
        pending_elicitation_id=await get_session_value_async(ctx, SESSION_PENDING_ELICITATION_ID_KEY),
        pending_workflow_name=await get_session_value_async(ctx, SESSION_PENDING_WORKFLOW_NAME_KEY),
        partial_answers=await get_session_value_async(ctx, SESSION_PARTIAL_ANSWERS_KEY),
        pending_question_set_id=await get_session_value_async(ctx, SESSION_PENDING_QUESTION_SET_ID_KEY),
        last_elicitation_action=await get_session_value_async(ctx, SESSION_LAST_ELICITATION_ACTION_KEY),
        last_router_disposition=await get_session_value_async(ctx, SESSION_LAST_ROUTER_DISPOSITION_KEY),
        last_router_error=await get_session_value_async(ctx, SESSION_LAST_ROUTER_ERROR_KEY),
        reference_images=await get_session_value_async(ctx, SESSION_REFERENCE_IMAGES_KEY),
        guided_handoff=await get_session_value_async(ctx, SESSION_GUIDED_HANDOFF_KEY),
        pending_reference_images=await get_session_value_async(ctx, SESSION_PENDING_REFERENCE_IMAGES_KEY),
    )


def set_session_capability_state(ctx: Context, state: SessionCapabilityState) -> None:
    """Persist the canonical session capability state to Context storage."""

    set_session_value(ctx, "phase", state.phase.value)
    set_session_value(ctx, SESSION_GOAL_KEY, state.goal)
    set_session_value(ctx, SESSION_PENDING_CLARIFICATION_KEY, state.pending_clarification)
    set_session_value(ctx, SESSION_LAST_ROUTER_STATUS_KEY, state.last_router_status)
    set_session_value(ctx, SESSION_POLICY_CONTEXT_KEY, state.policy_context)
    set_session_value(ctx, SESSION_SURFACE_PROFILE_KEY, state.surface_profile)
    set_session_value(ctx, SESSION_CONTRACT_VERSION_KEY, state.contract_version)
    set_session_value(ctx, SESSION_PENDING_ELICITATION_ID_KEY, state.pending_elicitation_id)
    set_session_value(ctx, SESSION_PENDING_WORKFLOW_NAME_KEY, state.pending_workflow_name)
    set_session_value(ctx, SESSION_PARTIAL_ANSWERS_KEY, state.partial_answers)
    set_session_value(ctx, SESSION_PENDING_QUESTION_SET_ID_KEY, state.pending_question_set_id)
    set_session_value(ctx, SESSION_LAST_ELICITATION_ACTION_KEY, state.last_elicitation_action)
    set_session_value(ctx, SESSION_LAST_ROUTER_DISPOSITION_KEY, state.last_router_disposition)
    set_session_value(ctx, SESSION_LAST_ROUTER_ERROR_KEY, state.last_router_error)
    set_session_value(ctx, SESSION_REFERENCE_IMAGES_KEY, state.reference_images)
    set_session_value(ctx, SESSION_GUIDED_HANDOFF_KEY, state.guided_handoff)
    set_session_value(ctx, SESSION_PENDING_REFERENCE_IMAGES_KEY, state.pending_reference_images)


async def set_session_capability_state_async(ctx: Context, state: SessionCapabilityState) -> None:
    """Async variant of session capability state persistence."""

    await set_session_value_async(ctx, "phase", state.phase.value)
    await set_session_value_async(ctx, SESSION_GOAL_KEY, state.goal)
    await set_session_value_async(ctx, SESSION_PENDING_CLARIFICATION_KEY, state.pending_clarification)
    await set_session_value_async(ctx, SESSION_LAST_ROUTER_STATUS_KEY, state.last_router_status)
    await set_session_value_async(ctx, SESSION_POLICY_CONTEXT_KEY, state.policy_context)
    await set_session_value_async(ctx, SESSION_SURFACE_PROFILE_KEY, state.surface_profile)
    await set_session_value_async(ctx, SESSION_CONTRACT_VERSION_KEY, state.contract_version)
    await set_session_value_async(ctx, SESSION_PENDING_ELICITATION_ID_KEY, state.pending_elicitation_id)
    await set_session_value_async(ctx, SESSION_PENDING_WORKFLOW_NAME_KEY, state.pending_workflow_name)
    await set_session_value_async(ctx, SESSION_PARTIAL_ANSWERS_KEY, state.partial_answers)
    await set_session_value_async(ctx, SESSION_PENDING_QUESTION_SET_ID_KEY, state.pending_question_set_id)
    await set_session_value_async(ctx, SESSION_LAST_ELICITATION_ACTION_KEY, state.last_elicitation_action)
    await set_session_value_async(ctx, SESSION_LAST_ROUTER_DISPOSITION_KEY, state.last_router_disposition)
    await set_session_value_async(ctx, SESSION_LAST_ROUTER_ERROR_KEY, state.last_router_error)
    await set_session_value_async(ctx, SESSION_REFERENCE_IMAGES_KEY, state.reference_images)
    await set_session_value_async(ctx, SESSION_GUIDED_HANDOFF_KEY, state.guided_handoff)
    await set_session_value_async(ctx, SESSION_PENDING_REFERENCE_IMAGES_KEY, state.pending_reference_images)


def _split_pending_reference_images_for_goal(
    pending_reference_images: list[dict[str, Any]] | None,
    *,
    goal: str,
) -> tuple[list[dict[str, Any]] | None, list[dict[str, Any]] | None]:
    """Split pending references into adopted items and goal-mismatched leftovers."""

    if not pending_reference_images:
        return None, None

    adopted: list[dict[str, Any]] = []
    remaining: list[dict[str, Any]] = []
    for item in pending_reference_images:
        recorded_goal = str(item.get("goal") or "").strip()
        if recorded_goal not in {"", _GENERIC_PENDING_GOAL, goal}:
            remaining.append(dict(item))
            continue
        adopted_item = dict(item)
        adopted_item["goal"] = goal
        adopted.append(adopted_item)
    return adopted or None, remaining or None


def _merge_reference_images(
    current_reference_images: list[dict[str, Any]] | None,
    adopted_reference_images: list[dict[str, Any]] | None,
) -> list[dict[str, Any]] | None:
    """Merge active and newly adopted reference images without losing order."""

    merged = [*list(current_reference_images or []), *list(adopted_reference_images or [])]
    return merged or None


def router_result_has_ready_guided_reference_goal(router_result: dict[str, Any]) -> bool:
    """Return True when a router_set_goal result establishes a usable guided goal state."""

    status = str(router_result.get("status") or "")
    return status in {"ready", "no_match"}


def session_has_ready_guided_reference_goal(session: SessionCapabilityState) -> bool:
    """Return True when the session is coherent enough for staged reference work."""

    if not session.goal:
        return False

    if session.last_router_status in {"ready", "no_match"}:
        return True
    return False


def build_guided_reference_readiness(session: SessionCapabilityState) -> GuidedReferenceReadinessState:
    """Compute one explicit readiness contract for guided stage compare/iterate flows."""

    attached_reference_count = len(session.reference_images or [])
    pending_reference_count = len(session.pending_reference_images or [])
    has_active_goal = session.goal is not None
    goal_input_pending = bool(session.pending_clarification) or session.last_router_status == "needs_input"
    session_ready = session_has_ready_guided_reference_goal(session)

    if not has_active_goal:
        blocking_reason: GuidedReferenceBlockingReason | None = "active_goal_required"
        next_action: GuidedReferenceNextAction | None = "call_router_set_goal"
    elif goal_input_pending:
        blocking_reason = "goal_input_pending"
        next_action = "answer_pending_goal_questions"
    elif not session_ready:
        blocking_reason = "reference_session_not_ready"
        next_action = "call_router_get_status"
    elif pending_reference_count > 0:
        blocking_reason = "pending_references_detected"
        next_action = "call_router_get_status"
    elif attached_reference_count == 0:
        blocking_reason = "reference_images_required"
        next_action = "attach_reference_images"
    else:
        blocking_reason = None
        next_action = None

    compare_ready = blocking_reason is None
    return GuidedReferenceReadinessState(
        status="ready" if compare_ready else "blocked",
        goal=session.goal,
        has_active_goal=has_active_goal,
        goal_input_pending=goal_input_pending,
        attached_reference_count=attached_reference_count,
        pending_reference_count=pending_reference_count,
        compare_ready=compare_ready,
        iterate_ready=compare_ready,
        blocking_reason=blocking_reason,
        next_action=next_action,
    )


def build_guided_reference_readiness_payload(session: SessionCapabilityState) -> dict[str, Any]:
    """Return a serializable readiness payload for MCP contracts and tests."""

    return asdict(build_guided_reference_readiness(session))


def update_session_from_router_goal(
    ctx: Context,
    goal: str,
    router_result: dict[str, Any],
    *,
    provided_answers: dict[str, Any] | None = None,
    surface_profile: str | None = None,
    contract_version: str | None = None,
) -> SessionCapabilityState:
    """Update session capability state from a router_set_goal response."""

    current = get_session_capability_state(ctx)
    status = router_result.get("status")
    pending = router_result.get("unresolved") if status == "needs_input" else None
    hinted_phase = router_result.get("phase_hint") or derive_phase_hint_from_router_result(router_result)
    phase = coerce_session_phase(hinted_phase or infer_phase_from_router_status(status, current_phase=current.phase))
    clarification = router_result.get("clarification") or {}
    current_partial_answers = dict(current.partial_answers or {})
    current_partial_answers.update(provided_answers or {})
    same_goal = current.goal == goal

    if status == "needs_input":
        pending_elicitation_id = (
            f"elic_{clarification.get('question_set_id')}"
            if clarification.get("question_set_id")
            else current.pending_elicitation_id
        )
        pending_workflow_name = router_result.get("workflow") or current.pending_workflow_name
        pending_question_set_id = clarification.get("question_set_id") or current.pending_question_set_id
        last_elicitation_action = router_result.get("elicitation_action") or current.last_elicitation_action
        partial_answers = current_partial_answers or None
    else:
        pending_elicitation_id = None
        pending_workflow_name = None
        pending_question_set_id = None
        last_elicitation_action = None
        partial_answers = None

    goal_ready = router_result_has_ready_guided_reference_goal(router_result)
    adopted_reference_images, remaining_pending_reference_images = _split_pending_reference_images_for_goal(
        current.pending_reference_images,
        goal=goal,
    )
    reference_images = (
        _merge_reference_images(current.reference_images if same_goal else None, adopted_reference_images)
        if goal_ready
        else (current.reference_images if same_goal else None)
    )
    pending_reference_images = remaining_pending_reference_images if goal_ready else current.pending_reference_images

    state = SessionCapabilityState(
        phase=phase,
        goal=goal,
        pending_clarification=pending,
        last_router_status=status,
        policy_context=router_result.get("policy_context"),
        surface_profile=surface_profile or current.surface_profile,
        contract_version=contract_version or current.contract_version,
        pending_elicitation_id=pending_elicitation_id,
        pending_workflow_name=pending_workflow_name,
        partial_answers=partial_answers,
        pending_question_set_id=pending_question_set_id,
        last_elicitation_action=last_elicitation_action,
        last_router_disposition=current.last_router_disposition,
        last_router_error=current.last_router_error,
        reference_images=reference_images,
        guided_handoff=router_result.get("guided_handoff"),
        pending_reference_images=pending_reference_images,
    )
    set_session_capability_state(ctx, state)
    return state


async def update_session_from_router_goal_async(
    ctx: Context,
    goal: str,
    router_result: dict[str, Any],
    *,
    provided_answers: dict[str, Any] | None = None,
    surface_profile: str | None = None,
    contract_version: str | None = None,
) -> SessionCapabilityState:
    """Async variant of router goal state persistence for native FastMCP Context."""

    current = await get_session_capability_state_async(ctx)
    status = router_result.get("status")
    pending = router_result.get("unresolved") if status == "needs_input" else None
    hinted_phase = router_result.get("phase_hint") or derive_phase_hint_from_router_result(router_result)
    phase = coerce_session_phase(hinted_phase or infer_phase_from_router_status(status, current_phase=current.phase))
    clarification = router_result.get("clarification") or {}
    current_partial_answers = dict(current.partial_answers or {})
    current_partial_answers.update(provided_answers or {})
    same_goal = current.goal == goal

    if status == "needs_input":
        pending_elicitation_id = (
            f"elic_{clarification.get('question_set_id')}"
            if clarification.get("question_set_id")
            else current.pending_elicitation_id
        )
        pending_workflow_name = router_result.get("workflow") or current.pending_workflow_name
        pending_question_set_id = clarification.get("question_set_id") or current.pending_question_set_id
        last_elicitation_action = router_result.get("elicitation_action") or current.last_elicitation_action
        partial_answers = current_partial_answers or None
    else:
        pending_elicitation_id = None
        pending_workflow_name = None
        pending_question_set_id = None
        last_elicitation_action = None
        partial_answers = None

    goal_ready = router_result_has_ready_guided_reference_goal(router_result)
    adopted_reference_images, remaining_pending_reference_images = _split_pending_reference_images_for_goal(
        current.pending_reference_images,
        goal=goal,
    )
    reference_images = (
        _merge_reference_images(current.reference_images if same_goal else None, adopted_reference_images)
        if goal_ready
        else (current.reference_images if same_goal else None)
    )
    pending_reference_images = remaining_pending_reference_images if goal_ready else current.pending_reference_images

    state = SessionCapabilityState(
        phase=phase,
        goal=goal,
        pending_clarification=pending,
        last_router_status=status,
        policy_context=router_result.get("policy_context"),
        surface_profile=surface_profile or current.surface_profile,
        contract_version=contract_version or current.contract_version,
        pending_elicitation_id=pending_elicitation_id,
        pending_workflow_name=pending_workflow_name,
        partial_answers=partial_answers,
        pending_question_set_id=pending_question_set_id,
        last_elicitation_action=last_elicitation_action,
        last_router_disposition=current.last_router_disposition,
        last_router_error=current.last_router_error,
        reference_images=reference_images,
        guided_handoff=router_result.get("guided_handoff"),
        pending_reference_images=pending_reference_images,
    )
    await set_session_capability_state_async(ctx, state)
    return state


def clear_session_goal_state(
    ctx: Context,
    *,
    surface_profile: str | None = None,
    contract_version: str | None = None,
) -> SessionCapabilityState:
    """Clear goal-specific session state and return the session to planning."""

    current = get_session_capability_state(ctx)
    state = SessionCapabilityState(
        phase=SessionPhase.PLANNING,
        goal=None,
        pending_clarification=None,
        last_router_status=None,
        policy_context=None,
        surface_profile=surface_profile or current.surface_profile,
        contract_version=contract_version or current.contract_version,
        pending_elicitation_id=None,
        pending_workflow_name=None,
        partial_answers=None,
        pending_question_set_id=None,
        last_elicitation_action=None,
        last_router_disposition=current.last_router_disposition,
        last_router_error=current.last_router_error,
        reference_images=None,
        guided_handoff=None,
        pending_reference_images=None,
    )
    set_session_capability_state(ctx, state)
    return state


async def clear_session_goal_state_async(
    ctx: Context,
    *,
    surface_profile: str | None = None,
    contract_version: str | None = None,
) -> SessionCapabilityState:
    """Async variant of goal reset for native FastMCP Context."""

    current = await get_session_capability_state_async(ctx)
    state = SessionCapabilityState(
        phase=SessionPhase.PLANNING,
        goal=None,
        pending_clarification=None,
        last_router_status=None,
        policy_context=None,
        surface_profile=surface_profile or current.surface_profile,
        contract_version=contract_version or current.contract_version,
        pending_elicitation_id=None,
        pending_workflow_name=None,
        partial_answers=None,
        pending_question_set_id=None,
        last_elicitation_action=None,
        last_router_disposition=current.last_router_disposition,
        last_router_error=current.last_router_error,
        reference_images=None,
        guided_handoff=None,
        pending_reference_images=None,
    )
    await set_session_capability_state_async(ctx, state)
    return state


def merge_resolved_params_with_session_answers(
    ctx: Context,
    resolved_params: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Merge explicit resolved params with any persisted partial answers."""

    current = get_session_capability_state(ctx)
    merged = dict(current.partial_answers or {})
    merged.update(resolved_params or {})
    return merged or None


async def merge_resolved_params_with_session_answers_async(
    ctx: Context,
    resolved_params: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Async variant of partial-answer merge for native FastMCP Context."""

    current = await get_session_capability_state_async(ctx)
    merged = dict(current.partial_answers or {})
    merged.update(resolved_params or {})
    return merged or None


async def apply_visibility_for_session_state(
    ctx: Context,
    state: SessionCapabilityState,
) -> VisibilityDiagnostics:
    """Apply native session visibility rules for the current capability state."""

    from server.adapters.mcp.guided_mode import apply_session_visibility

    surface_profile = state.surface_profile or "legacy-flat"
    return await apply_session_visibility(
        ctx,
        surface_profile=surface_profile,
        phase=state.phase,
    )


def replace_session_reference_images(
    ctx: Context,
    reference_images: list[dict[str, Any]] | None,
) -> SessionCapabilityState:
    """Replace the goal-scoped reference images kept in session state."""

    current = get_session_capability_state(ctx)
    state = SessionCapabilityState(
        phase=current.phase,
        goal=current.goal,
        pending_clarification=current.pending_clarification,
        last_router_status=current.last_router_status,
        policy_context=current.policy_context,
        surface_profile=current.surface_profile,
        contract_version=current.contract_version,
        pending_elicitation_id=current.pending_elicitation_id,
        pending_workflow_name=current.pending_workflow_name,
        partial_answers=current.partial_answers,
        pending_question_set_id=current.pending_question_set_id,
        last_elicitation_action=current.last_elicitation_action,
        last_router_disposition=current.last_router_disposition,
        last_router_error=current.last_router_error,
        reference_images=reference_images or None,
        guided_handoff=current.guided_handoff,
        pending_reference_images=current.pending_reference_images,
    )
    set_session_capability_state(ctx, state)
    return state


async def replace_session_reference_images_async(
    ctx: Context,
    reference_images: list[dict[str, Any]] | None,
) -> SessionCapabilityState:
    """Async variant of goal-scoped reference-image replacement."""

    current = await get_session_capability_state_async(ctx)
    state = SessionCapabilityState(
        phase=current.phase,
        goal=current.goal,
        pending_clarification=current.pending_clarification,
        last_router_status=current.last_router_status,
        policy_context=current.policy_context,
        surface_profile=current.surface_profile,
        contract_version=current.contract_version,
        pending_elicitation_id=current.pending_elicitation_id,
        pending_workflow_name=current.pending_workflow_name,
        partial_answers=current.partial_answers,
        pending_question_set_id=current.pending_question_set_id,
        last_elicitation_action=current.last_elicitation_action,
        last_router_disposition=current.last_router_disposition,
        last_router_error=current.last_router_error,
        reference_images=reference_images or None,
        guided_handoff=current.guided_handoff,
        pending_reference_images=current.pending_reference_images,
    )
    await set_session_capability_state_async(ctx, state)
    return state


def record_router_execution_outcome(
    ctx: Context,
    *,
    router_disposition: str,
    error: str | None = None,
) -> SessionCapabilityState:
    """Persist the last router execution outcome for diagnostics surfaces.

    Keep this write path narrowly scoped. Routed sync tools run through
    threadpool-backed FastMCP execution, so rewriting the full session snapshot
    here would risk clobbering unrelated goal/reference state if a sync-state
    read falls back or races. Diagnostics only need these two keys.
    """

    set_session_value(ctx, SESSION_LAST_ROUTER_DISPOSITION_KEY, router_disposition)
    set_session_value(ctx, SESSION_LAST_ROUTER_ERROR_KEY, error)

    current = get_session_capability_state(ctx)
    if current.last_router_disposition == router_disposition and current.last_router_error == error:
        return current

    return SessionCapabilityState(
        phase=current.phase,
        goal=current.goal,
        pending_clarification=current.pending_clarification,
        last_router_status=current.last_router_status,
        policy_context=current.policy_context,
        surface_profile=current.surface_profile,
        contract_version=current.contract_version,
        pending_elicitation_id=current.pending_elicitation_id,
        pending_workflow_name=current.pending_workflow_name,
        partial_answers=current.partial_answers,
        pending_question_set_id=current.pending_question_set_id,
        last_elicitation_action=current.last_elicitation_action,
        last_router_disposition=router_disposition,
        last_router_error=error,
        reference_images=current.reference_images,
        guided_handoff=current.guided_handoff,
        pending_reference_images=current.pending_reference_images,
    )


def replace_session_pending_reference_images(
    ctx: Context,
    pending_reference_images: list[dict[str, Any]] | None,
) -> SessionCapabilityState:
    """Replace the pending reference images kept before a goal is active."""

    current = get_session_capability_state(ctx)
    state = SessionCapabilityState(
        phase=current.phase,
        goal=current.goal,
        pending_clarification=current.pending_clarification,
        last_router_status=current.last_router_status,
        policy_context=current.policy_context,
        surface_profile=current.surface_profile,
        contract_version=current.contract_version,
        pending_elicitation_id=current.pending_elicitation_id,
        pending_workflow_name=current.pending_workflow_name,
        partial_answers=current.partial_answers,
        pending_question_set_id=current.pending_question_set_id,
        last_elicitation_action=current.last_elicitation_action,
        last_router_disposition=current.last_router_disposition,
        last_router_error=current.last_router_error,
        reference_images=current.reference_images,
        guided_handoff=current.guided_handoff,
        pending_reference_images=pending_reference_images or None,
    )
    set_session_capability_state(ctx, state)
    return state


async def replace_session_pending_reference_images_async(
    ctx: Context,
    pending_reference_images: list[dict[str, Any]] | None,
) -> SessionCapabilityState:
    """Async variant of pending reference-image replacement."""

    current = await get_session_capability_state_async(ctx)
    state = SessionCapabilityState(
        phase=current.phase,
        goal=current.goal,
        pending_clarification=current.pending_clarification,
        last_router_status=current.last_router_status,
        policy_context=current.policy_context,
        surface_profile=current.surface_profile,
        contract_version=current.contract_version,
        pending_elicitation_id=current.pending_elicitation_id,
        pending_workflow_name=current.pending_workflow_name,
        partial_answers=current.partial_answers,
        pending_question_set_id=current.pending_question_set_id,
        last_elicitation_action=current.last_elicitation_action,
        last_router_disposition=current.last_router_disposition,
        last_router_error=current.last_router_error,
        reference_images=current.reference_images,
        guided_handoff=current.guided_handoff,
        pending_reference_images=pending_reference_images or None,
    )
    await set_session_capability_state_async(ctx, state)
    return state
