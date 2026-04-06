# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Structured contracts for goal-scoped reference image MCP tools."""

from __future__ import annotations

from typing import Literal

from server.adapters.mcp.contracts.scene import (
    SceneAssembledTargetScopeContract,
    SceneCorrectionTruthBundleContract,
    SceneRepairMacroCandidateContract,
    SceneTruthFollowupContract,
    SceneTruthFollowupItemContract,
)
from server.adapters.mcp.contracts.vision import VisionCaptureImageContract
from server.adapters.mcp.sampling.result_types import VisionAssistantContract

from .base import MCPContract


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
    item_kinds: list[
        Literal["contact_failure", "gap", "overlap", "alignment", "measurement_error", "insufficient_scope"]
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
    selected_family: Literal["macro", "modeling_mesh", "sculpt_region", "inspect_only"] = "inspect_only"
    reason: str
    source_signals: list[Literal["vision", "truth", "macro", "scope", "naming"]] = []
    candidate_ids: list[str] = []


class ReferenceRefinementToolCandidateContract(MCPContract):
    """One bounded tool-level handoff candidate for the selected refinement family."""

    tool_name: str
    reason: str
    priority: Literal["high", "normal"] = "normal"
    arguments_hint: dict[str, object] | None = None


class ReferenceRefinementHandoffContract(MCPContract):
    """Explicit next-tool-family handoff payload for hybrid refinement routing."""

    selected_family: Literal["macro", "modeling_mesh", "sculpt_region", "inspect_only"]
    message: str
    recommended_tools: list[ReferenceRefinementToolCandidateContract] = []


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
    silhouette_analysis: ReferenceSilhouetteAnalysisContract | None = None
    action_hints: list[ReferenceActionHintContract] = []
    part_segmentation: ReferencePartSegmentationContract | None = None
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
    silhouette_analysis: ReferenceSilhouetteAnalysisContract | None = None
    action_hints: list[ReferenceActionHintContract] = []
    part_segmentation: ReferencePartSegmentationContract | None = None
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
    message: str | None = None
    error: str | None = None
