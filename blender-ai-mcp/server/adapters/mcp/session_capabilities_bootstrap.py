# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Goal bootstrap, prompt bundles, and reference-readiness helpers."""

from __future__ import annotations

from dataclasses import asdict, replace
from typing import Any

from fastmcp import Context

from server.adapters.mcp.contracts.guided_flow import (
    GuidedFlowCheckContract,
    GuidedFlowStateContract,
    GuidedFlowStepLiteral,
)
from server.adapters.mcp.session_capabilities_flow import (
    _GUIDED_FLOW_STOPPED_STEPS,
    _build_allowed_families,
    _build_required_checks,
    _build_required_prompt_bundle,
    _build_role_summary,
    _flow_state_for_current_step,
    _select_guided_flow_domain_profile,
)
from server.adapters.mcp.session_capabilities_state import (
    _GENERIC_PENDING_GOAL,
    GuidedReferenceBlockingReason,
    GuidedReferenceNextAction,
    GuidedReferenceReadinessState,
    SessionCapabilityState,
    _normalize_guided_flow_state,
    get_session_capability_state,
    get_session_capability_state_async,
    set_session_capability_state,
    set_session_capability_state_async,
)
from server.adapters.mcp.session_phase import SessionPhase, coerce_session_phase
from server.router.application.session_phase_hints import derive_phase_hint_from_router_result


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


def _build_initial_guided_flow_state(
    *,
    goal: str,
    router_result: dict[str, Any],
    previous_flow_state: dict[str, Any] | None = None,
    part_registry: list[dict[str, Any]] | None = None,
    preserve_existing: bool = False,
) -> dict[str, Any] | None:
    status = str(router_result.get("status") or "")
    if status == "disabled":
        return None

    guided_handoff = router_result.get("guided_handoff")
    domain_profile = _select_guided_flow_domain_profile(goal=goal, guided_handoff=guided_handoff)

    if preserve_existing and previous_flow_state is not None:
        previous_contract = GuidedFlowStateContract.model_validate(previous_flow_state)
        if (
            previous_contract.domain_profile == domain_profile
            and previous_contract.current_step not in _GUIDED_FLOW_STOPPED_STEPS
            and status != "needs_input"
            and previous_contract.current_step != "understand_goal"
        ):
            return previous_contract.model_dump(mode="json")

    if status == "needs_input":
        current_step: GuidedFlowStepLiteral = "understand_goal"
        next_actions = ["answer_router_questions"]
        blocked_families = ["build", "late_refinement", "finish"]
        step_status = "blocked"
        required_checks: list[dict[str, Any]] = []
    else:
        current_step = "establish_spatial_context"
        next_actions = ["run_required_checks"]
        blocked_families = ["build", "late_refinement", "finish"]
        required_checks = _build_required_checks(domain_profile=domain_profile, current_step=current_step)
        step_status = "blocked" if required_checks else "ready"

    completed_steps: list[GuidedFlowStepLiteral] = []
    if (
        previous_flow_state is not None
        and status != "needs_input"
        and previous_flow_state.get("current_step") == "understand_goal"
    ):
        completed_steps.append("understand_goal")

    required_prompts, preferred_prompts = _build_required_prompt_bundle(
        domain_profile=domain_profile,
        current_step=current_step,
    )
    flow_id = f"guided_{domain_profile}_flow"
    role_summary = _build_role_summary(
        domain_profile=domain_profile,
        current_step=current_step,
        part_registry=part_registry,
    )

    return GuidedFlowStateContract(
        flow_id=flow_id,
        domain_profile=domain_profile,
        current_step=current_step,  # type: ignore[arg-type]
        completed_steps=completed_steps,
        required_checks=[GuidedFlowCheckContract.model_validate(item) for item in required_checks],
        required_prompts=required_prompts,
        preferred_prompts=preferred_prompts,
        next_actions=next_actions,
        blocked_families=blocked_families,
        allowed_families=_build_allowed_families(domain_profile=domain_profile, current_step=current_step),
        allowed_roles=role_summary["allowed_roles"],
        completed_roles=role_summary["completed_roles"],
        missing_roles=role_summary["missing_roles"],
        required_role_groups=role_summary["required_role_groups"],
        step_status=step_status,  # type: ignore[arg-type]
    ).model_dump(mode="json")


async def bootstrap_guided_empty_scene_primary_workset_async(ctx: Context) -> SessionCapabilityState:
    """Move an empty guided scene from spatial bootstrap to first primary workset creation."""

    current = await get_session_capability_state_async(ctx)
    if current.guided_flow_state is None:
        return current

    contract = GuidedFlowStateContract.model_validate(current.guided_flow_state)
    if contract.current_step != "establish_spatial_context":
        return current

    contract.current_step = "bootstrap_primary_workset"
    contract.blocked_families = []
    contract.required_checks = []
    contract.active_target_scope = None
    contract.spatial_scope_fingerprint = None
    contract.spatial_refresh_required = False
    contract.spatial_state_stale = False
    contract.last_spatial_check_version = None
    _flow_state_for_current_step(contract, part_registry=current.guided_part_registry)

    state = replace(current, guided_flow_state=contract.model_dump(mode="json"))
    await set_session_capability_state_async(ctx, state)
    return state


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

    merged: list[dict[str, Any]] = []
    seen_reference_ids: set[str] = set()
    for item in [*list(current_reference_images or []), *list(adopted_reference_images or [])]:
        reference_id = item.get("reference_id")
        if isinstance(reference_id, str) and reference_id:
            if reference_id in seen_reference_ids:
                continue
            seen_reference_ids.add(reference_id)
        merged.append(item)
    return merged or None


def router_result_has_ready_guided_reference_goal(router_result: dict[str, Any]) -> bool:
    """Return True when a router_set_goal result establishes a usable guided goal state."""

    status = str(router_result.get("status") or "")
    return status in {"ready", "no_match"}


def session_has_ready_guided_reference_goal(session: SessionCapabilityState) -> bool:
    """Return True when the session is coherent enough for staged reference work."""

    if not session.goal:
        return False
    return session.last_router_status in {"ready", "no_match"}


def build_guided_reference_readiness(session: SessionCapabilityState) -> GuidedReferenceReadinessState:
    """Compute one explicit readiness contract for guided stage compare/iterate flows."""

    attached_reference_count = len(session.reference_images or [])
    has_active_goal = session.goal is not None
    goal_input_pending = bool(session.pending_clarification) or session.last_router_status == "needs_input"
    session_ready = session_has_ready_guided_reference_goal(session)
    relevant_pending_reference_count = 0
    blocking_reason: GuidedReferenceBlockingReason | None
    next_action: GuidedReferenceNextAction | None

    if session.goal:
        relevant_pending_references, _ = _split_pending_reference_images_for_goal(
            session.pending_reference_images,
            goal=session.goal,
        )
        relevant_pending_reference_count = len(relevant_pending_references or [])

    if not has_active_goal:
        blocking_reason = "active_goal_required"
        next_action = "call_router_set_goal"
    elif goal_input_pending:
        blocking_reason = "goal_input_pending"
        next_action = "answer_pending_goal_questions"
    elif not session_ready:
        blocking_reason = "reference_session_not_ready"
        next_action = "call_router_get_status"
    elif relevant_pending_reference_count > 0:
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
        pending_reference_count=relevant_pending_reference_count,
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
    gate_proposal: dict[str, Any] | None = None,
    surface_profile: str | None = None,
    contract_version: str | None = None,
) -> SessionCapabilityState:
    """Update session capability state from a router_set_goal response."""

    from server.adapters.mcp.session_capabilities_runtime_glue import ingest_quality_gate_proposal_for_state

    current = get_session_capability_state(ctx)
    status = router_result.get("status")
    pending = router_result.get("unresolved") if status == "needs_input" else None
    hinted_phase = router_result.get("phase_hint") or derive_phase_hint_from_router_result(router_result)
    phase = coerce_session_phase(hinted_phase or infer_phase_from_router_status(status, current_phase=current.phase))
    clarification = router_result.get("clarification") or {}
    current_partial_answers = dict(current.partial_answers or {})
    current_partial_answers.update(provided_answers or {})
    same_goal = current.goal == goal
    retained_guided_part_registry = current.guided_part_registry if same_goal else None
    previous_flow_state = _normalize_guided_flow_state(current.guided_flow_state)
    guided_flow_state = (
        _build_initial_guided_flow_state(
            goal=goal,
            router_result=router_result,
            previous_flow_state=previous_flow_state,
            part_registry=retained_guided_part_registry,
            preserve_existing=same_goal,
        )
        if (surface_profile or current.surface_profile or "legacy-flat") == "llm-guided"
        else None
    )

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

    state = replace(
        current,
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
        reference_images=reference_images,
        guided_handoff=router_result.get("guided_handoff"),
        guided_flow_state=guided_flow_state,
        gate_plan=current.gate_plan if same_goal else None,
        reference_understanding_summary=current.reference_understanding_summary if same_goal else None,
        reference_understanding_gate_ids=current.reference_understanding_gate_ids if same_goal else None,
        guided_part_registry=retained_guided_part_registry,
        pending_reference_images=pending_reference_images,
    )
    if gate_proposal is not None:
        state, _ = ingest_quality_gate_proposal_for_state(state, gate_proposal)
    set_session_capability_state(ctx, state)
    return state


async def update_session_from_router_goal_async(
    ctx: Context,
    goal: str,
    router_result: dict[str, Any],
    *,
    provided_answers: dict[str, Any] | None = None,
    gate_proposal: dict[str, Any] | None = None,
    surface_profile: str | None = None,
    contract_version: str | None = None,
) -> SessionCapabilityState:
    """Async variant of router goal state persistence for native FastMCP Context."""

    from server.adapters.mcp.session_capabilities_runtime_glue import ingest_quality_gate_proposal_for_state

    current = await get_session_capability_state_async(ctx)
    status = router_result.get("status")
    pending = router_result.get("unresolved") if status == "needs_input" else None
    hinted_phase = router_result.get("phase_hint") or derive_phase_hint_from_router_result(router_result)
    phase = coerce_session_phase(hinted_phase or infer_phase_from_router_status(status, current_phase=current.phase))
    clarification = router_result.get("clarification") or {}
    current_partial_answers = dict(current.partial_answers or {})
    current_partial_answers.update(provided_answers or {})
    same_goal = current.goal == goal
    retained_guided_part_registry = current.guided_part_registry if same_goal else None
    previous_flow_state = _normalize_guided_flow_state(current.guided_flow_state)
    guided_flow_state = (
        _build_initial_guided_flow_state(
            goal=goal,
            router_result=router_result,
            previous_flow_state=previous_flow_state,
            part_registry=retained_guided_part_registry,
            preserve_existing=same_goal,
        )
        if (surface_profile or current.surface_profile or "legacy-flat") == "llm-guided"
        else None
    )

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

    state = replace(
        current,
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
        reference_images=reference_images,
        guided_handoff=router_result.get("guided_handoff"),
        guided_flow_state=guided_flow_state,
        gate_plan=current.gate_plan if same_goal else None,
        reference_understanding_summary=current.reference_understanding_summary if same_goal else None,
        reference_understanding_gate_ids=current.reference_understanding_gate_ids if same_goal else None,
        guided_part_registry=retained_guided_part_registry,
        pending_reference_images=pending_reference_images,
    )
    if gate_proposal is not None:
        state, _ = ingest_quality_gate_proposal_for_state(state, gate_proposal)
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
    state = replace(
        current,
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
        reference_images=None,
        guided_handoff=None,
        guided_flow_state=None,
        gate_plan=None,
        reference_understanding_summary=None,
        reference_understanding_gate_ids=None,
        guided_part_registry=None,
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
    state = replace(
        current,
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
        reference_images=None,
        guided_handoff=None,
        guided_flow_state=None,
        gate_plan=None,
        reference_understanding_summary=None,
        reference_understanding_gate_ids=None,
        guided_part_registry=None,
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


def replace_session_reference_images(
    ctx: Context,
    reference_images: list[dict[str, Any]] | None,
) -> SessionCapabilityState:
    """Replace the goal-scoped reference images kept in session state."""

    current = get_session_capability_state(ctx)
    state = replace(current, reference_images=reference_images or None)
    set_session_capability_state(ctx, state)
    return state


async def replace_session_reference_images_async(
    ctx: Context,
    reference_images: list[dict[str, Any]] | None,
) -> SessionCapabilityState:
    """Async variant of goal-scoped reference-image replacement."""

    current = await get_session_capability_state_async(ctx)
    state = replace(current, reference_images=reference_images or None)
    await set_session_capability_state_async(ctx, state)
    return state


def replace_session_pending_reference_images(
    ctx: Context,
    pending_reference_images: list[dict[str, Any]] | None,
) -> SessionCapabilityState:
    """Replace the pending reference images kept before a goal is active."""

    current = get_session_capability_state(ctx)
    state = replace(current, pending_reference_images=pending_reference_images or None)
    set_session_capability_state(ctx, state)
    return state


async def replace_session_pending_reference_images_async(
    ctx: Context,
    pending_reference_images: list[dict[str, Any]] | None,
) -> SessionCapabilityState:
    """Async variant of pending reference-image replacement."""

    current = await get_session_capability_state_async(ctx)
    state = replace(current, pending_reference_images=pending_reference_images or None)
    await set_session_capability_state_async(ctx, state)
    return state
