# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Session-capability state models and persistence helpers."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal

from fastmcp import Context

from server.adapters.mcp.contracts.guided_flow import GuidedFlowStateContract, GuidedFlowStepLiteral
from server.adapters.mcp.contracts.quality_gates import GatePlanContract
from server.adapters.mcp.contracts.reference import ReferenceUnderstandingSummaryContract
from server.adapters.mcp.session_phase import SessionPhase, coerce_session_phase
from server.adapters.mcp.session_state import (
    get_session_value,
    get_session_value_async,
    set_session_value,
    set_session_value_async,
)

SESSION_PHASE_KEY = "phase"
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
SESSION_GUIDED_FLOW_STATE_KEY = "guided_flow_state"
SESSION_GATE_PLAN_KEY = "gate_plan"
SESSION_REFERENCE_UNDERSTANDING_SUMMARY_KEY = "reference_understanding_summary"
SESSION_REFERENCE_UNDERSTANDING_GATE_IDS_KEY = "reference_understanding_gate_ids"
SESSION_PENDING_REFERENCE_IMAGES_KEY = "pending_reference_images"
SESSION_GUIDED_PART_REGISTRY_KEY = "guided_part_registry"

_GENERIC_PENDING_GOAL = "__pending_goal__"


@dataclass(frozen=True)
class GuidedPartRegistryItem:
    """Internal session-scoped record describing one guided part role."""

    object_name: str
    role: str
    role_group: str
    status: str = "registered"
    created_in_step: GuidedFlowStepLiteral | None = None


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
    guided_flow_state: dict[str, Any] | None = None
    gate_plan: dict[str, Any] | None = None
    reference_understanding_summary: dict[str, Any] | None = None
    reference_understanding_gate_ids: list[str] | None = None
    guided_part_registry: list[dict[str, Any]] | None = None
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


def _normalize_guided_flow_state(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    try:
        return GuidedFlowStateContract.model_validate(value).model_dump(mode="json", exclude_none=True)
    except Exception:
        return None


def _normalize_gate_plan(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    try:
        return GatePlanContract.model_validate(value).model_dump(mode="json", exclude_none=True)
    except Exception:
        return None


def _normalize_reference_understanding_summary(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    try:
        return ReferenceUnderstandingSummaryContract.model_validate(value).model_dump(mode="json", exclude_none=True)
    except Exception:
        return None


def _normalize_reference_understanding_gate_ids(value: Any) -> list[str] | None:
    if value is None:
        return None
    if not isinstance(value, list):
        return None
    normalized = [str(item).strip() for item in value if str(item).strip()]
    return normalized or None


def _normalize_guided_part_registry(value: Any) -> list[dict[str, Any]] | None:
    if value is None:
        return None
    if not isinstance(value, list):
        return None

    items: list[dict[str, Any]] = []
    for raw_item in value:
        try:
            if isinstance(raw_item, GuidedPartRegistryItem):
                items.append(asdict(raw_item))
                continue
            if not isinstance(raw_item, dict):
                return None
            items.append(asdict(GuidedPartRegistryItem(**raw_item)))
        except Exception:
            return None
    return items or None


def get_session_capability_state(ctx: Context) -> SessionCapabilityState:
    """Read the canonical session capability state from Context storage."""

    return SessionCapabilityState(
        phase=coerce_session_phase(get_session_value(ctx, SESSION_PHASE_KEY, SessionPhase.BOOTSTRAP)),
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
        guided_flow_state=_normalize_guided_flow_state(get_session_value(ctx, SESSION_GUIDED_FLOW_STATE_KEY)),
        gate_plan=_normalize_gate_plan(get_session_value(ctx, SESSION_GATE_PLAN_KEY)),
        reference_understanding_summary=_normalize_reference_understanding_summary(
            get_session_value(ctx, SESSION_REFERENCE_UNDERSTANDING_SUMMARY_KEY)
        ),
        reference_understanding_gate_ids=_normalize_reference_understanding_gate_ids(
            get_session_value(ctx, SESSION_REFERENCE_UNDERSTANDING_GATE_IDS_KEY)
        ),
        guided_part_registry=_normalize_guided_part_registry(get_session_value(ctx, SESSION_GUIDED_PART_REGISTRY_KEY)),
        pending_reference_images=get_session_value(ctx, SESSION_PENDING_REFERENCE_IMAGES_KEY),
    )


async def get_session_capability_state_async(ctx: Context) -> SessionCapabilityState:
    """Async variant of session capability state lookup for native FastMCP Context."""

    return SessionCapabilityState(
        phase=coerce_session_phase(await get_session_value_async(ctx, SESSION_PHASE_KEY, SessionPhase.BOOTSTRAP)),
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
        guided_flow_state=_normalize_guided_flow_state(
            await get_session_value_async(ctx, SESSION_GUIDED_FLOW_STATE_KEY)
        ),
        gate_plan=_normalize_gate_plan(await get_session_value_async(ctx, SESSION_GATE_PLAN_KEY)),
        reference_understanding_summary=_normalize_reference_understanding_summary(
            await get_session_value_async(ctx, SESSION_REFERENCE_UNDERSTANDING_SUMMARY_KEY)
        ),
        reference_understanding_gate_ids=_normalize_reference_understanding_gate_ids(
            await get_session_value_async(ctx, SESSION_REFERENCE_UNDERSTANDING_GATE_IDS_KEY)
        ),
        guided_part_registry=_normalize_guided_part_registry(
            await get_session_value_async(ctx, SESSION_GUIDED_PART_REGISTRY_KEY)
        ),
        pending_reference_images=await get_session_value_async(ctx, SESSION_PENDING_REFERENCE_IMAGES_KEY),
    )


def set_session_capability_state(ctx: Context, state: SessionCapabilityState) -> None:
    """Persist the canonical session capability state to Context storage."""

    set_session_value(ctx, SESSION_PHASE_KEY, state.phase.value)
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
    set_session_value(ctx, SESSION_GUIDED_FLOW_STATE_KEY, state.guided_flow_state)
    set_session_value(ctx, SESSION_GATE_PLAN_KEY, state.gate_plan)
    set_session_value(ctx, SESSION_REFERENCE_UNDERSTANDING_SUMMARY_KEY, state.reference_understanding_summary)
    set_session_value(ctx, SESSION_REFERENCE_UNDERSTANDING_GATE_IDS_KEY, state.reference_understanding_gate_ids)
    set_session_value(ctx, SESSION_GUIDED_PART_REGISTRY_KEY, state.guided_part_registry)
    set_session_value(ctx, SESSION_PENDING_REFERENCE_IMAGES_KEY, state.pending_reference_images)


async def set_session_capability_state_async(ctx: Context, state: SessionCapabilityState) -> None:
    """Async variant of session capability state persistence."""

    await set_session_value_async(ctx, SESSION_PHASE_KEY, state.phase.value)
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
    await set_session_value_async(ctx, SESSION_GUIDED_FLOW_STATE_KEY, state.guided_flow_state)
    await set_session_value_async(ctx, SESSION_GATE_PLAN_KEY, state.gate_plan)
    await set_session_value_async(
        ctx, SESSION_REFERENCE_UNDERSTANDING_SUMMARY_KEY, state.reference_understanding_summary
    )
    await set_session_value_async(
        ctx, SESSION_REFERENCE_UNDERSTANDING_GATE_IDS_KEY, state.reference_understanding_gate_ids
    )
    await set_session_value_async(ctx, SESSION_GUIDED_PART_REGISTRY_KEY, state.guided_part_registry)
    await set_session_value_async(ctx, SESSION_PENDING_REFERENCE_IMAGES_KEY, state.pending_reference_images)
