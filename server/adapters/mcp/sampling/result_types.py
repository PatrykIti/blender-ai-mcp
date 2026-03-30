# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Typed result envelopes for bounded MCP sampling assistants."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Literal, TypeVar, cast

from server.adapters.mcp.contracts.base import MCPContract

AssistantTerminalStatus = Literal[
    "success",
    "unavailable",
    "masked_error",
    "rejected_by_policy",
]
AssistantCapabilitySource = Literal[
    "client",
    "fallback_handler",
    "local_runtime",
    "external_runtime",
    "unavailable",
    "unknown",
]
AssistantResponsibility = Literal["inspection_summary", "repair_suggestion", "diagnostic_summary", "vision_assist"]


class AssistantBudgetContract(MCPContract):
    """Deterministic budget limits for one assistant invocation."""

    max_input_chars: int
    max_messages: int
    max_tokens: int
    tool_budget: int


class InspectionSummaryContract(MCPContract):
    """Structured summary produced from inspection contracts."""

    inspection_action: str
    object_name: str | None = None
    overview: str
    key_findings: list[str]
    risk_flags: list[str] = []
    suggested_followups: list[str] = []
    truth_source: Literal["inspection_contract"] = "inspection_contract"


class RepairSuggestionActionContract(MCPContract):
    """One bounded follow-up action suggested after a failure/diagnostic state."""

    kind: Literal[
        "inspect",
        "clarify",
        "retry",
        "adjust_parameters",
        "change_mode",
        "change_selection",
        "stop",
    ]
    reason: str


class RepairSuggestionContract(MCPContract):
    """Structured repair guidance derived from router/runtime diagnostics."""

    summary: str
    actions: list[RepairSuggestionActionContract]
    requires_user_input: bool = False
    requires_inspection: bool = False
    safety_notes: list[str] = []
    truth_source: Literal["router_diagnostics", "inspection_required"] = "router_diagnostics"


class VisionIssueContract(MCPContract):
    """One likely visible issue identified by the bounded vision layer."""

    category: str
    summary: str
    severity: Literal["high", "medium", "low"] = "medium"


class VisionRecommendedCheckContract(MCPContract):
    """One deterministic follow-up check recommended after visual interpretation."""

    tool_name: str
    reason: str
    priority: Literal["high", "normal"] = "normal"


class VisionInputSummaryContract(MCPContract):
    """Compact summary of the visual inputs used by the backend."""

    before_image_count: int = 0
    after_image_count: int = 0
    reference_image_count: int = 0
    target_object: str | None = None


class VisionBoundaryPolicyContract(MCPContract):
    """Explicit boundary contract for what the vision layer may and may not assert."""

    interpretation_only: bool = True
    not_truth_source: bool = True
    not_policy_source: bool = True
    requires_deterministic_checks_for_correctness: bool = True
    requires_bundle_or_reference_context: bool = True
    confidence_is_non_authoritative: bool = True


class VisionAssistContract(MCPContract):
    """Structured bounded vision result for macro/workflow reporting."""

    backend_kind: Literal["transformers_local", "mlx_local", "openai_compatible_external", "unknown"] = "unknown"
    backend_name: str | None = None
    model_name: str | None = None
    goal_summary: str
    reference_match_summary: str | None = None
    visible_changes: list[str]
    shape_mismatches: list[str] = []
    proportion_mismatches: list[str] = []
    correction_focus: list[str] = []
    likely_issues: list[VisionIssueContract] = []
    next_corrections: list[str] = []
    recommended_checks: list[VisionRecommendedCheckContract] = []
    confidence: float | None = None
    captures_used: list[str] = []
    input_summary: VisionInputSummaryContract | None = None
    boundary_policy: VisionBoundaryPolicyContract = VisionBoundaryPolicyContract()
    truth_source: Literal["vision_assist"] = "vision_assist"


class InspectionSummaryAssistantContract(MCPContract):
    """Structured envelope for inspection-summary assistant executions."""

    status: AssistantTerminalStatus
    assistant_name: str
    message: str
    request_id: str | None = None
    capability_source: AssistantCapabilitySource | None = None
    rejection_reason: str | None = None
    budget: AssistantBudgetContract
    result: InspectionSummaryContract | None = None


class RepairSuggestionAssistantContract(MCPContract):
    """Structured envelope for repair-suggestion assistant executions."""

    status: AssistantTerminalStatus
    assistant_name: str
    message: str
    request_id: str | None = None
    capability_source: AssistantCapabilitySource | None = None
    rejection_reason: str | None = None
    budget: AssistantBudgetContract
    result: RepairSuggestionContract | None = None


class VisionAssistantContract(MCPContract):
    """Structured envelope for bounded vision-assist executions."""

    status: AssistantTerminalStatus
    assistant_name: str
    message: str
    request_id: str | None = None
    capability_source: AssistantCapabilitySource | None = None
    rejection_reason: str | None = None
    budget: AssistantBudgetContract
    result: VisionAssistContract | None = None


@dataclass(frozen=True, slots=True)
class AssistantPolicy:
    """Policy/budget definition for one bounded assistant."""

    assistant_name: str
    responsibility: AssistantResponsibility
    max_input_chars: int
    max_messages: int
    max_tokens: int
    tool_budget: int = 0
    mask_error_details: bool = True
    temperature: float = 0.0
    allow_in_background: bool = False

    def to_budget_contract(self) -> AssistantBudgetContract:
        """Return the public budget contract for this policy."""

        return AssistantBudgetContract(
            max_input_chars=self.max_input_chars,
            max_messages=self.max_messages,
            max_tokens=self.max_tokens,
            tool_budget=self.tool_budget,
        )


AssistantResultT = TypeVar("AssistantResultT", bound=MCPContract)


@dataclass(slots=True)
class AssistantRunResult(Generic[AssistantResultT]):
    """Internal generic outcome from the assistant runner."""

    status: AssistantTerminalStatus
    assistant_name: str
    message: str
    budget: AssistantBudgetContract
    request_id: str | None = None
    capability_source: AssistantCapabilitySource | None = None
    rejection_reason: str | None = None
    result: AssistantResultT | None = None


def to_inspection_assistant_contract(
    outcome: AssistantRunResult[InspectionSummaryContract],
) -> InspectionSummaryAssistantContract:
    """Convert a generic runner outcome into the public inspection envelope."""

    return InspectionSummaryAssistantContract(
        status=outcome.status,
        assistant_name=outcome.assistant_name,
        message=outcome.message,
        request_id=outcome.request_id,
        capability_source=outcome.capability_source,
        rejection_reason=outcome.rejection_reason,
        budget=outcome.budget,
        result=cast(InspectionSummaryContract | None, outcome.result),
    )


def to_repair_assistant_contract(
    outcome: AssistantRunResult[RepairSuggestionContract],
) -> RepairSuggestionAssistantContract:
    """Convert a generic runner outcome into the public repair envelope."""

    return RepairSuggestionAssistantContract(
        status=outcome.status,
        assistant_name=outcome.assistant_name,
        message=outcome.message,
        request_id=outcome.request_id,
        capability_source=outcome.capability_source,
        rejection_reason=outcome.rejection_reason,
        budget=outcome.budget,
        result=cast(RepairSuggestionContract | None, outcome.result),
    )


def to_vision_assistant_contract(
    outcome: AssistantRunResult[VisionAssistContract],
) -> VisionAssistantContract:
    """Convert a generic runner/runtime outcome into the public vision envelope."""

    return VisionAssistantContract(
        status=outcome.status,
        assistant_name=outcome.assistant_name,
        message=outcome.message,
        request_id=outcome.request_id,
        capability_source=outcome.capability_source,
        rejection_reason=outcome.rejection_reason,
        budget=outcome.budget,
        result=cast(VisionAssistContract | None, outcome.result),
    )


__all__ = [
    "AssistantBudgetContract",
    "AssistantCapabilitySource",
    "AssistantPolicy",
    "AssistantResponsibility",
    "AssistantRunResult",
    "AssistantTerminalStatus",
    "InspectionSummaryAssistantContract",
    "InspectionSummaryContract",
    "RepairSuggestionActionContract",
    "RepairSuggestionAssistantContract",
    "RepairSuggestionContract",
    "VisionAssistantContract",
    "VisionAssistContract",
    "VisionInputSummaryContract",
    "VisionIssueContract",
    "VisionRecommendedCheckContract",
    "to_inspection_assistant_contract",
    "to_repair_assistant_contract",
    "to_vision_assistant_contract",
]
