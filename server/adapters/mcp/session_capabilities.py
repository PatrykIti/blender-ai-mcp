# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Session-scoped capability state for adaptive FastMCP surfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from fastmcp import Context

from server.router.application.session_phase_hints import derive_phase_hint_from_router_result
from server.adapters.mcp.session_phase import SessionPhase, coerce_session_phase
from server.adapters.mcp.session_state import get_session_value, set_session_value

if TYPE_CHECKING:
    from server.adapters.mcp.guided_mode import VisibilityDiagnostics

SESSION_GOAL_KEY = "goal"
SESSION_PENDING_CLARIFICATION_KEY = "pending_clarification"
SESSION_LAST_ROUTER_STATUS_KEY = "last_router_status"
SESSION_POLICY_CONTEXT_KEY = "policy_context"
SESSION_SURFACE_PROFILE_KEY = "surface_profile"
SESSION_CONTRACT_VERSION_KEY = "contract_version"


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


def update_session_from_router_goal(
    ctx: Context,
    goal: str,
    router_result: dict[str, Any],
    *,
    surface_profile: str | None = None,
    contract_version: str | None = None,
) -> SessionCapabilityState:
    """Update session capability state from a router_set_goal response."""

    current = get_session_capability_state(ctx)
    status = router_result.get("status")
    pending = router_result.get("unresolved") if status == "needs_input" else None
    hinted_phase = router_result.get("phase_hint") or derive_phase_hint_from_router_result(router_result)
    phase = coerce_session_phase(hinted_phase or infer_phase_from_router_status(status, current_phase=current.phase))

    state = SessionCapabilityState(
        phase=phase,
        goal=goal,
        pending_clarification=pending,
        last_router_status=status,
        policy_context=router_result.get("policy_context"),
        surface_profile=surface_profile or current.surface_profile,
        contract_version=contract_version or current.contract_version,
    )
    set_session_capability_state(ctx, state)
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
    )
    set_session_capability_state(ctx, state)
    return state


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
