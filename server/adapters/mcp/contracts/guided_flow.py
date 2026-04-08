# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Structured contracts for server-driven guided flow state."""

from __future__ import annotations

from typing import Literal

from .base import MCPContract

GuidedFlowDomainProfileLiteral = Literal["generic", "creature", "building"]
GuidedFlowFamilyLiteral = Literal[
    "spatial_context",
    "reference_context",
    "primary_masses",
    "secondary_parts",
    "attachment_alignment",
    "checkpoint_iterate",
    "inspect_validate",
    "finish",
    "utility",
]
GuidedFlowStepLiteral = Literal[
    "understand_goal",
    "establish_spatial_context",
    "establish_reference_context",
    "create_primary_masses",
    "place_secondary_parts",
    "checkpoint_iterate",
    "inspect_validate",
    "finish_or_stop",
]
GuidedFlowStepStatusLiteral = Literal["ready", "blocked", "needs_checkpoint", "needs_validation"]


class GuidedFlowCheckContract(MCPContract):
    """One server-defined check required by the current guided flow step."""

    check_id: str
    tool_name: str
    reason: str
    status: Literal["pending", "completed"] = "pending"
    priority: Literal["high", "normal"] = "high"


class GuidedFlowStateContract(MCPContract):
    """Machine-readable guided flow state owned by the MCP server."""

    flow_id: str
    domain_profile: GuidedFlowDomainProfileLiteral
    current_step: GuidedFlowStepLiteral
    completed_steps: list[GuidedFlowStepLiteral] = []
    required_checks: list[GuidedFlowCheckContract] = []
    required_prompts: list[str] = []
    preferred_prompts: list[str] = []
    next_actions: list[str] = []
    blocked_families: list[str] = []
    allowed_families: list[GuidedFlowFamilyLiteral] = []
    allowed_roles: list[str] = []
    completed_roles: list[str] = []
    missing_roles: list[str] = []
    required_role_groups: list[str] = []
    step_status: GuidedFlowStepStatusLiteral = "ready"
