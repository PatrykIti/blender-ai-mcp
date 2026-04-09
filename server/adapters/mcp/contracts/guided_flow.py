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


class GuidedTargetScopeContract(MCPContract):
    """Compact guided target identity used for spatial-check binding."""

    scope_kind: Literal["single_object", "object_set", "collection", "part_groups", "scene"] = "scene"
    primary_target: str | None = None
    object_names: list[str] = []
    object_count: int = 0
    collection_name: str | None = None


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
    active_target_scope: GuidedTargetScopeContract | None = None
    spatial_scope_fingerprint: str | None = None
    spatial_state_version: int = 0
    spatial_state_stale: bool = False
    last_spatial_check_version: int | None = None
    spatial_refresh_required: bool = False
    last_spatial_mutation_reason: str | None = None
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
