# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Structured contracts for router-facing MCP tools."""

from __future__ import annotations

from typing import Any, Literal

from server.adapters.mcp.contracts.base import MCPContract
from server.adapters.mcp.elicitation_contracts import ClarificationFallbackPayload


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


class RouterStatusContract(MCPContract):
    """Structured contract for router_get_status."""

    enabled: bool
    initialized: bool | None = None
    ready: bool | None = None
    component_status: dict[str, bool] | None = None
    stats: dict[str, Any] | None = None
    config: str | None = None
    message: str | None = None
