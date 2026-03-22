# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Structured contracts for router-facing MCP tools."""

from __future__ import annotations

from typing import Any, Literal

from server.adapters.mcp.contracts.base import MCPContract
from server.adapters.mcp.elicitation_contracts import ClarificationFallbackPayload


class RouterPolicyContextContract(MCPContract):
    """Structured policy transparency context for router/operator surfaces."""

    decision: str
    reason: str
    source: str
    score: float
    band: str
    risk: str
    metadata: dict[str, Any] | None = None


class RouterGoalErrorContract(MCPContract):
    """Structured error details for router goal handling."""

    type: str
    details: str
    stage: str | None = None


class RouterGoalResponseContract(MCPContract):
    """Structured response contract for router_set_goal."""

    status: Literal["ready", "needs_input", "no_match", "disabled", "error"]
    workflow: str | None = None
    resolved: dict[str, Any]
    unresolved: list[dict[str, Any]]
    resolution_sources: dict[str, str]
    message: str
    phase_hint: str | None = None
    executed: int | None = None
    error: RouterGoalErrorContract | None = None
    clarification: ClarificationFallbackPayload | None = None
    elicitation_action: Literal["accept", "decline", "cancel", "unavailable"] | None = None
    elicitation_answers: dict[str, Any] | None = None
    policy_context: RouterPolicyContextContract | None = None


class RouterStatusContract(MCPContract):
    """Structured contract for router_get_status."""

    enabled: bool
    initialized: bool | None = None
    ready: bool | None = None
    component_status: dict[str, bool] | None = None
    stats: dict[str, Any] | None = None
    config: str | None = None
    message: str | None = None
    current_goal: str | None = None
    current_phase: str | None = None
    surface_profile: str | None = None
    contract_version: str | None = None
    pending_clarification: dict[str, Any] | list[dict[str, Any]] | None = None
    pending_question_set_id: str | None = None
    partial_answers: dict[str, Any] | None = None
    last_elicitation_action: str | None = None
    last_router_status: str | None = None
    policy_context: RouterPolicyContextContract | None = None
    visibility_rules: list[dict[str, Any]] | None = None
    visible_capabilities: list[str] | None = None
    visible_entry_capabilities: list[str] | None = None
    hidden_capability_count: int | None = None
    hidden_category_counts: dict[str, int] | None = None
    router_failure_policy: str | None = None
    last_router_disposition: str | None = None
    last_router_error: str | None = None
    timeout_policy: dict[str, Any] | None = None
    task_runtime: dict[str, Any] | None = None
    telemetry: dict[str, Any] | None = None
    list_page_size: int | None = None
    background_job_count: int | None = None
    background_job_counts_by_status: dict[str, int] | None = None
    background_jobs: list[dict[str, Any]] | None = None
