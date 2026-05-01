# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Structured contracts for goal-scoped reference image MCP tools."""

from __future__ import annotations

from typing import Literal

from server.adapters.mcp.contracts.scene import (
    SceneAssembledTargetScopeContract,
    SceneCorrectionTruthBundleContract,
    SceneRelationKindLiteral,
    SceneRelationVerdictLiteral,
    SceneRepairMacroCandidateContract,
    SceneTruthFollowupContract,
    SceneTruthFollowupItemContract,
)
from server.adapters.mcp.contracts.vision import VisionCaptureImageContract
from server.adapters.mcp.sampling.result_types import VisionAssistantContract

from .base import MCPContract
from .guided_flow import GuidedFlowStateContract
from .quality_gates import GatePlanContract

ReferencePlannerFamilyLiteral = Literal["macro", "modeling_mesh", "sculpt_region", "inspect_only"]
ReferencePlannerSourceLiteral = Literal[
    "vision",
    "truth",
    "macro",
    "scope",
    "relation",
    "view",
    "silhouette",
    "budget",
    "naming",
]


class ReferenceImageRecordContract(MCPContract):
    """One normalized reference image stored in session scope."""

    reference_id: str
    goal: str
    label: str | None = None
    notes: str | None = None
    target_object: str | None = None
    target_view: str | None = None
    media_type: str
    source_kind: Literal["local_path"] = "local_path"
    original_path: str
    stored_path: str
    host_visible_path: str | None = None
    added_at: str


class GuidedReferenceReadinessContract(MCPContract):
    """Explicit readiness contract for guided goal/reference stage workflows."""

    status: Literal["ready", "blocked"] = "blocked"
    goal: str | None = None
    has_active_goal: bool = False
    goal_input_pending: bool = False
    attached_reference_count: int = 0
    pending_reference_count: int = 0
    compare_ready: bool = False
    iterate_ready: bool = False
    blocking_reason: (
        Literal[
            "active_goal_required",
            "goal_input_pending",
            "pending_references_detected",
            "reference_images_required",
            "reference_session_not_ready",
        ]
        | None
    ) = None
    next_action: (
        Literal[
            "call_router_set_goal",
            "answer_pending_goal_questions",
            "attach_reference_images",
            "call_router_get_status",
        ]
        | None
    ) = None


class ReferenceImagesResponseContract(MCPContract):
    """Structured response for the goal-scoped reference image surface."""

    action: Literal["attach", "list", "remove", "clear"]
    goal: str | None = None
    reference_count: int = 0
    references: list[ReferenceImageRecordContract] = []
    removed_reference_id: str | None = None
    message: str | None = None
    error: str | None = None


class ReferenceCompareCheckpointResponseContract(MCPContract):
    """Structured response for bounded checkpoint-vs-reference comparison."""

    action: Literal["compare_checkpoint", "compare_current_view"] = "compare_checkpoint"
    goal: str | None = None
    target_object: str | None = None
    target_view: str | None = None
    checkpoint_path: str
    checkpoint_label: str | None = None
    reference_count: int = 0
    reference_ids: list[str] = []
    reference_labels: list[str] = []
    view_diagnostics_hints: list["ReferenceViewDiagnosticsHintContract"] | None = None
    vision_assistant: VisionAssistantContract | None = None
    message: str | None = None
    error: str | None = None


class ReferenceCorrectionVisionEvidenceContract(MCPContract):
    """Vision-side evidence attached to one merged correction candidate."""

    correction_focus: list[str] = []
    shape_mismatches: list[str] = []
    proportion_mismatches: list[str] = []
    next_corrections: list[str] = []


class ReferenceCorrectionTruthEvidenceContract(MCPContract):
    """Truth-side evidence attached to one merged correction candidate."""

    focus_pairs: list[str] = []
    relation_kinds: list[SceneRelationKindLiteral] = []
    relation_verdicts: list[SceneRelationVerdictLiteral] = []
    item_kinds: list[
        Literal[
            "contact_failure", "gap", "overlap", "alignment", "attachment", "measurement_error", "insufficient_scope"
        ]
    ] = []
    items: list[SceneTruthFollowupItemContract] = []
    macro_candidates: list[SceneRepairMacroCandidateContract] = []


class ReferenceCorrectionCandidateContract(MCPContract):
    """One ranked correction candidate combining vision, truth, and macro evidence."""

    candidate_id: str
    summary: str
    priority_rank: int
    priority: Literal["high", "normal"] = "normal"
    candidate_kind: Literal["vision_only", "truth_only", "hybrid"] = "vision_only"
    target_object: str | None = None
    target_objects: list[str] = []
    focus_pairs: list[str] = []
    source_signals: list[Literal["vision", "truth", "macro"]] = []
    vision_evidence: ReferenceCorrectionVisionEvidenceContract | None = None
    truth_evidence: ReferenceCorrectionTruthEvidenceContract | None = None


class ReferenceHybridBudgetControlContract(MCPContract):
    """Budget/scope control metadata for hybrid-loop compare and iterate responses."""

    model_name: str | None = None
    max_input_chars: int
    max_output_tokens: int
    max_images: int
    original_pair_count: int = 0
    emitted_pair_count: int = 0
    original_candidate_count: int = 0
    emitted_candidate_count: int = 0
    trimming_applied: bool = False
    scope_trimmed: bool = False
    detail_trimmed: bool = False
    trim_reason: str | None = None
    selected_focus_pairs: list[str] = []


class ReferencePlannerTargetScopeContract(MCPContract):
    """Compact target scope selected by the repair planner."""

    scope_kind: Literal["single_object", "object_set", "collection", "part_groups", "scene", "unknown"] = "unknown"
    target_object: str | None = None
    target_objects: list[str] = []
    collection_name: str | None = None
    local_region_hint: str | None = None


class ReferencePlannerEvidenceSourceContract(MCPContract):
    """One bounded provenance item used by the repair planner."""

    source_id: str
    source_class: ReferencePlannerSourceLiteral
    summary: str
    candidate_ids: list[str] = []
    tool_name: str | None = None


class ReferencePlannerBlockerContract(MCPContract):
    """One typed blocker or precondition emitted by the repair planner."""

    blocker_id: str
    category: Literal["relation", "view", "proportion", "scope", "budget", "policy"]
    severity: Literal["blocking", "warning"] = "blocking"
    reason: str
    candidate_ids: list[str] = []
    recommended_tool: str | None = None
    arguments_hint: dict[str, object] | None = None


class ReferenceRefinementRouteContract(MCPContract):
    """Deterministic refinement-family routing result for hybrid loop responses."""

    domain_classification: Literal[
        "assembly",
        "hard_surface",
        "soft_surface",
        "organic_form",
        "garment",
        "anatomy",
        "generic_form",
    ] = "generic_form"
    selected_family: ReferencePlannerFamilyLiteral = "inspect_only"
    reason: str
    source_signals: list[ReferencePlannerSourceLiteral] = []
    candidate_ids: list[str] = []
    target_scope: ReferencePlannerTargetScopeContract | None = None
    blockers: list[ReferencePlannerBlockerContract] = []
    detail_available: bool = False


class ReferenceRefinementToolCandidateContract(MCPContract):
    """One bounded tool-level handoff candidate for the selected refinement family."""

    tool_name: str
    reason: str
    priority: Literal["high", "normal"] = "normal"
    arguments_hint: dict[str, object] | None = None


class ReferenceRefinementHandoffContract(MCPContract):
    """Explicit next-tool-family handoff payload for hybrid refinement routing."""

    selected_family: ReferencePlannerFamilyLiteral
    state: Literal["ready", "blocked", "suppressed"] = "suppressed"
    message: str
    target_object: str | None = None
    target_scope: ReferencePlannerTargetScopeContract | None = None
    local_reason: str | None = None
    blockers: list[ReferencePlannerBlockerContract] = []
    eligible_tool_names: list[str] = []
    visibility_unlock_recommended: bool = False
    recommended_tools: list[ReferenceRefinementToolCandidateContract] = []


class ReferenceRepairPlannerSummaryContract(MCPContract):
    """Compact inline repair-planner summary for staged compare/iterate responses."""

    selected_family: ReferencePlannerFamilyLiteral
    target_scope: ReferencePlannerTargetScopeContract | None = None
    rationale: str
    provenance: list[ReferencePlannerEvidenceSourceContract] = []
    blockers: list[ReferencePlannerBlockerContract] = []
    detail_available: bool = False
    required_support_tools: list[ReferenceRefinementToolCandidateContract] = []


class ReferenceRepairPlannerDetailContract(MCPContract):
    """Opt-in rich repair-planner detail derived from the same stage state."""

    summary: ReferenceRepairPlannerSummaryContract
    route: ReferenceRefinementRouteContract
    handoff: ReferenceRefinementHandoffContract
    candidate_ids: list[str] = []
    notes: list[str] = []
    detail_trimmed: bool = False


class ReferenceSilhouetteMetricContract(MCPContract):
    """One deterministic silhouette metric comparing a capture against a reference."""

    metric_id: Literal[
        "mask_iou",
        "contour_drift",
        "aspect_ratio_delta",
        "upper_band_width_delta",
        "mid_band_width_delta",
        "lower_band_width_delta",
        "left_projection_delta",
        "right_projection_delta",
    ]
    reference_value: float
    observed_value: float
    delta: float
    severity: Literal["high", "medium", "low"] = "medium"


class ReferenceActionHintContract(MCPContract):
    """One typed corrective hint derived from deterministic perception metrics."""

    hint_id: str
    hint_type: Literal[
        "widen_upper_profile",
        "reduce_upper_profile",
        "extend_left_profile",
        "extend_right_profile",
        "rebalance_proportion",
        "inspect_before_edit",
    ]
    summary: str
    priority: Literal["high", "normal"] = "normal"
    target_object: str | None = None
    metric_ids: list[str] = []
    recommended_tools: list[ReferenceRefinementToolCandidateContract] = []


class ReferenceViewDiagnosticsHintContract(MCPContract):
    """Compact recommendation to call the separate view diagnostics surface."""

    hint_id: str
    trigger: Literal["framing_ambiguity", "visibility_ambiguity", "occlusion_detected", "target_off_frame"]
    reason: str
    recommended_tool: Literal["scene_view_diagnostics"] = "scene_view_diagnostics"
    priority: Literal["high", "normal"] = "normal"
    arguments_hint: dict[str, object] | None = None


class ReferenceSilhouetteAnalysisContract(MCPContract):
    """Deterministic silhouette-analysis payload attached to staged compare responses."""

    status: Literal["available", "unavailable"] = "unavailable"
    reference_label: str | None = None
    capture_label: str | None = None
    target_view: str | None = None
    mask_extraction_mode: Literal["alpha_or_otsu_largest_component", "unavailable"] = "unavailable"
    alignment_mode: Literal["bbox_normalized", "unavailable"] = "unavailable"
    metrics: list[ReferenceSilhouetteMetricContract] = []
    notes: list[str] = []


class ReferencePartSegmentationLandmarkContract(MCPContract):
    """One optional 2D landmark emitted by a future segmentation sidecar."""

    landmark_id: str
    x: float
    y: float


class ReferencePartSegmentationPartContract(MCPContract):
    """One optional part-aware segmentation artifact for a creature region."""

    part_label: str
    mask_path: str | None = None
    crop_path: str | None = None
    confidence: float | None = None
    landmarks: list[ReferencePartSegmentationLandmarkContract] = []


class ReferencePartSegmentationContract(MCPContract):
    """Optional vendor-neutral sidecar payload for part-aware creature perception."""

    status: Literal["disabled", "available", "unavailable"] = "disabled"
    provider_name: str | None = None
    advisory_only: bool = True
    parts: list[ReferencePartSegmentationPartContract] = []
    notes: list[str] = []


class ReferenceCompareStageCheckpointResponseContract(MCPContract):
    """Structured response for deterministic stage checkpoint capture + compare."""

    action: Literal["compare_stage_checkpoint"] = "compare_stage_checkpoint"
    session_id: str | None = None
    transport: str | None = None
    goal: str | None = None
    guided_flow_state: GuidedFlowStateContract | None = None
    active_gate_plan: GatePlanContract | None = None
    guided_reference_readiness: GuidedReferenceReadinessContract | None = None
    target_object: str | None = None
    target_objects: list[str] = []
    collection_name: str | None = None
    assembled_target_scope: SceneAssembledTargetScopeContract | None = None
    truth_bundle: SceneCorrectionTruthBundleContract | None = None
    truth_followup: SceneTruthFollowupContract | None = None
    correction_candidates: list[ReferenceCorrectionCandidateContract] = []
    budget_control: ReferenceHybridBudgetControlContract | None = None
    refinement_route: ReferenceRefinementRouteContract | None = None
    refinement_handoff: ReferenceRefinementHandoffContract | None = None
    planner_summary: ReferenceRepairPlannerSummaryContract | None = None
    planner_detail: ReferenceRepairPlannerDetailContract | None = None
    silhouette_analysis: ReferenceSilhouetteAnalysisContract | None = None
    action_hints: list[ReferenceActionHintContract] = []
    part_segmentation: ReferencePartSegmentationContract | None = None
    view_diagnostics_hints: list[ReferenceViewDiagnosticsHintContract] | None = None
    target_view: str | None = None
    checkpoint_id: str
    checkpoint_label: str | None = None
    preset_profile: Literal["compact", "rich"] = "compact"
    preset_names: list[str] = []
    capture_count: int = 0
    captures: list[VisionCaptureImageContract] = []
    reference_count: int = 0
    reference_ids: list[str] = []
    reference_labels: list[str] = []
    vision_assistant: VisionAssistantContract | None = None
    message: str | None = None
    error: str | None = None


class ReferenceIterateStageCheckpointResponseContract(MCPContract):
    """Structured response for session-aware iterative stage checkpoint loops."""

    action: Literal["iterate_stage_checkpoint"] = "iterate_stage_checkpoint"
    session_id: str | None = None
    transport: str | None = None
    goal: str | None = None
    guided_flow_state: GuidedFlowStateContract | None = None
    active_gate_plan: GatePlanContract | None = None
    guided_reference_readiness: GuidedReferenceReadinessContract | None = None
    target_object: str | None = None
    target_objects: list[str] = []
    collection_name: str | None = None
    assembled_target_scope: SceneAssembledTargetScopeContract | None = None
    truth_bundle: SceneCorrectionTruthBundleContract | None = None
    truth_followup: SceneTruthFollowupContract | None = None
    correction_candidates: list[ReferenceCorrectionCandidateContract] = []
    budget_control: ReferenceHybridBudgetControlContract | None = None
    refinement_route: ReferenceRefinementRouteContract | None = None
    refinement_handoff: ReferenceRefinementHandoffContract | None = None
    planner_summary: ReferenceRepairPlannerSummaryContract | None = None
    planner_detail: ReferenceRepairPlannerDetailContract | None = None
    silhouette_analysis: ReferenceSilhouetteAnalysisContract | None = None
    action_hints: list[ReferenceActionHintContract] = []
    part_segmentation: ReferencePartSegmentationContract | None = None
    view_diagnostics_hints: list[ReferenceViewDiagnosticsHintContract] | None = None
    target_view: str | None = None
    checkpoint_id: str
    checkpoint_label: str | None = None
    iteration_index: int = 1
    loop_disposition: Literal["continue_build", "inspect_validate", "stop"] = "continue_build"
    continue_recommended: bool = True
    prior_checkpoint_id: str | None = None
    prior_correction_focus: list[str] = []
    correction_focus: list[str] = []
    repeated_correction_focus: list[str] = []
    stagnation_count: int = 0
    stop_reason: str | None = None
    compare_result: ReferenceCompareStageCheckpointResponseContract
    debug_payload_omitted: bool = False
    message: str | None = None
    error: str | None = None
