# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Typed result envelopes for bounded MCP sampling assistants."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Literal, TypeVar, cast

from pydantic import Field

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
VisionCapabilitySource = Literal["fallback_registry", "openrouter_api", "env_override", "unknown", "unavailable"]


class AssistantBudgetContract(MCPContract):
    """Deterministic budget limits for one assistant invocation."""

    max_input_chars: int
    max_messages: int
    max_tokens: int
    tool_budget: int
    max_images: int | None = None
    configured_max_input_chars: int | None = None
    configured_max_tokens: int | None = None
    configured_max_images: int | None = None
    effective_max_input_chars: int | None = None
    effective_max_tokens: int | None = None
    effective_max_images: int | None = None
    fail_safe_max_input_chars: int | None = None
    fail_safe_max_tokens: int | None = None
    fail_safe_max_images: int | None = None
    budget_clipped: bool = False
    budget_clip_fields: list[str] = []


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

    category: str = Field(description="Short slug grouping the issue, e.g. 'front_profile' or 'proportion'.")
    summary: str = Field(description="One-sentence advisory description of the suspected visible issue.")
    severity: Literal["high", "medium", "low"] = Field(
        default="medium",
        description="Advisory severity hint only; it does not gate anything and is not authoritative.",
    )


class VisionRecommendedCheckContract(MCPContract):
    """One deterministic follow-up check recommended after visual interpretation."""

    tool_name: str = Field(
        description="Name of the deterministic inspection/measurement tool to run to confirm this visual reading."
    )
    reason: str = Field(description="Why this deterministic check is recommended after the visual interpretation.")
    priority: Literal["high", "normal"] = Field(
        default="normal", description="Advisory ordering hint for the recommended check."
    )


VisionFindingAxisLiteral = Literal["x", "y", "z", "none"]
VisionFindingDirectionLiteral = Literal["increase", "decrease", "none"]


class VisionFindingContract(MCPContract):
    """One structured per-finding compare observation (advisory).

    Binds a finding to the view that revealed it, the canonical scene part/role
    it concerns, an axis/direction, and a PROPORTIONAL magnitude ratio versus a
    reference anchor. The magnitude is never an absolute measurement; vision
    stays advisory and deterministic checks own correctness.
    """

    finding: str = Field(description="One-sentence reference-relative finding (what differs from the reference).")
    view_id: str | None = Field(
        default=None, description="Which view revealed it (e.g. front/side/top/oblique), or null if unattributable."
    )
    target_label: str | None = Field(
        default=None,
        description="Canonical part/object role this concerns (reuse the reference role vocabulary), or null.",
    )
    axis: VisionFindingAxisLiteral | None = Field(
        default=None, description="Dominant axis of the divergence (x/y/z) or 'none'/null when not axis-specific."
    )
    direction: VisionFindingDirectionLiteral | None = Field(
        default=None, description="Whether the target should increase or decrease along the axis, or 'none'/null."
    )
    magnitude_ratio: float | None = Field(
        default=None,
        description=(
            "Proportional ratio vs a reference anchor (e.g. 1.4 = ~40% too large, 0.7 = ~30% too small), "
            "NEVER an absolute measurement; null if not estimable. Advisory only."
        ),
    )
    reference_id: str | None = Field(
        default=None, description="Reference image/label this finding was compared against."
    )
    confidence: float | None = Field(
        default=None, description="Non-authoritative confidence in [0,1]; deterministic checks remain the authority."
    )
    defect_id: str | None = Field(
        default=None,
        description=(
            "Server-computed stable identifier for this defect (a deterministic hash of its target/axis/direction "
            "and normalized text). Lets a Critic finding be tracked and checked off by a later Verify pass."
        ),
    )


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


class VisionPacketStatusContract(MCPContract):
    """Explicit packet-local extraction/ranking guidance for staged compare packets."""

    packet_status: Literal["ready", "clean", "low_information", "blocked"] | None = Field(
        default=None,
        description=(
            "Packet readiness: 'ready' has actionable signal; 'clean' already matches; "
            "'low_information' is too weak to rank; 'blocked' cannot be evaluated."
        ),
    )
    status_reason: str | None = Field(default=None, description="Short reason explaining the packet_status value.")
    ranking_recommendation: Literal["rank", "skip_clean", "skip_low_information", "skip_blocked"] | None = Field(
        default=None,
        description="Advisory recommendation for whether to rank this packet or skip it (and why), not a gate.",
    )


class VisionCapabilitySummaryContract(MCPContract):
    """Bounded runtime/request capability summary for one vision execution."""

    model_id: str | None = None
    capability_source: VisionCapabilitySource | None = None
    context_length: int | None = None
    max_completion_tokens: int | None = None
    input_modalities: list[str] = []
    output_modalities: list[str] = []
    supported_parameters: list[str] = []
    requested_max_tokens: int | None = None
    request_mode: str | None = None
    response_healing_enabled: bool | None = None


class VisionAssistContract(MCPContract):
    """Structured bounded vision result for macro/workflow reporting."""

    backend_kind: Literal["transformers_local", "mlx_local", "openai_compatible_external", "unknown"] = "unknown"
    backend_name: str | None = None
    model_name: str | None = None
    vision_contract_profile: Literal["generic_full", "google_family_compare"] | None = None
    goal_summary: str = Field(
        description="Scalar narrative: one sentence on whether the after/render images move toward the goal/reference."
    )
    reference_match_summary: str | None = Field(
        default=None,
        description="Scalar narrative: how the current render compares to the reference overall; null when no reference.",
    )
    visible_changes: list[str] = Field(
        description=(
            "Descriptive observations of what visibly changed or is present, NOT a defect list. "
            "Use shape_mismatches/proportion_mismatches for reference-relative problems."
        )
    )
    shape_mismatches: list[str] = Field(
        default_factory=list,
        description="Reference-relative form/silhouette problems (wrong contour, missing/extra mass, wrong profile).",
    )
    proportion_mismatches: list[str] = Field(
        default_factory=list,
        description="Reference-relative size/ratio problems (a part too large/small relative to another or the whole).",
    )
    correction_focus: list[str] = Field(
        default_factory=list,
        description="The 1-3 highest-priority mismatch targets to fix next (a prioritized subset, not new findings).",
    )
    likely_issues: list[VisionIssueContract] = Field(
        default_factory=list, description="Lower-confidence suspected issues, each with a category and severity hint."
    )
    next_corrections: list[str] = Field(
        default_factory=list,
        description="Bounded, visually-justified next-step fixes to apply (concrete actions, not the targets themselves).",
    )
    recommended_checks: list[VisionRecommendedCheckContract] = Field(
        default_factory=list,
        description="Deterministic inspection/measurement tools to run to confirm visual readings before correcting.",
    )
    findings: list[VisionFindingContract] = Field(
        default_factory=list,
        description=(
            "Structured per-finding compare observations binding each finding to a view, scene part, axis, and "
            "proportional magnitude. Advisory and parallel to the string lists above; empty when unavailable."
        ),
    )
    packet_guidance: VisionPacketStatusContract | None = Field(
        default=None, description="Packet-local extraction/ranking guidance for staged compare packets; null otherwise."
    )
    capability_summary: VisionCapabilitySummaryContract | None = Field(
        default=None, description="Runtime/request capability metadata for this execution (model, modalities, caps)."
    )
    confidence: float | None = Field(
        default=None,
        description=(
            "Non-authoritative self-reported confidence in [0,1]. Advisory only: it is NOT proof of correctness; "
            "rely on deterministic inspection/assertion/silhouette for scene truth."
        ),
    )
    captures_used: list[str] = Field(
        default_factory=list, description="Labels of the capture/reference images the interpretation actually used."
    )
    evidence_truncated: bool = Field(
        default=False,
        description="True when one or more finding lists were capped; the orchestrator may request more if needed.",
    )
    omitted_count: int = Field(
        default=0, description="Total number of findings dropped by the per-list caps (0 when nothing was truncated)."
    )
    analysis_unusable: bool = Field(
        default=False,
        description=(
            "True when this result is a recovery placeholder (model echoed input, returned labels, or off-contract "
            "JSON), so empty finding lists mean 'analysis failed', NOT 'scene looks correct'. Distinct from confidence==0."
        ),
    )
    input_summary: VisionInputSummaryContract | None = Field(
        default=None, description="Compact summary of the visual inputs the backend received."
    )
    boundary_policy: VisionBoundaryPolicyContract = Field(
        default_factory=VisionBoundaryPolicyContract,
        description="Explicit advisory boundary: this result is interpretation only and not a truth or policy source.",
    )
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
    "VisionCapabilitySummaryContract",
    "VisionCapabilitySource",
    "VisionInputSummaryContract",
    "VisionIssueContract",
    "VisionRecommendedCheckContract",
    "to_inspection_assistant_contract",
    "to_repair_assistant_contract",
    "to_vision_assistant_contract",
]
