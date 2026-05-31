# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Structured contracts for goal-scoped reference image MCP tools."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from server.adapters.mcp.contracts.scene import (
    SceneAssembledTargetScopeContract,
    SceneCorrectionTruthBundleContract,
    SceneRelationKindLiteral,
    SceneRelationVerdictLiteral,
    SceneRepairMacroCandidateContract,
    SceneTruthFollowupContract,
    SceneTruthFollowupItemContract,
)
from server.adapters.mcp.contracts.vision import VisionCaptureImageContract, VisionOverlayMarkContract
from server.adapters.mcp.sampling.result_types import VisionAssistantContract

from .base import MCPContract
from .guided_flow import GuidedFlowFamilyLiteral, GuidedFlowStateContract
from .quality_gates import (
    GateCompletionBlockerContract,
    GatePlanContract,
    GateProposalGateContract,
    GateSourceProvenanceContract,
    NormalizedQualityGateContract,
)

ReferencePlannerFamilyLiteral = Literal["macro", "modeling_mesh", "sculpt_region", "inspect_only"]
ReferenceCompareComplexityTierLiteral = Literal["simple", "complex", "super_complex"]
ReferenceComparePacketKindLiteral = Literal["view", "scope", "view_scope", "synthesis"]
ReferenceComparePacketStatusLiteral = Literal["success", "blocked", "low_information", "skipped", "error"]
ReferenceCompareRankingStatusLiteral = Literal["success", "skipped", "not_needed", "error"]
ReferenceComparePacketGuidanceLiteral = Literal["ready", "clean", "low_information", "blocked"]
ReferenceCompareRankingRecommendationLiteral = Literal["rank", "skip_clean", "skip_low_information", "skip_blocked"]
ReferenceCompareScopeSourceLiteral = Literal["registered_graph", "focus_pairs", "target_scope", "fallback"]
ReferenceDefectSeverityLiteral = Literal["high", "medium", "low"]
ReferenceDefectVerifyStatusLiteral = Literal["resolved", "unresolved", "downgraded"]
ReferenceActionSourceLiteral = Literal["scene_truth", "spatial_relation", "mesh_metric", "planner", "policy", "vision"]
ReferenceLocalizedSupportReasonLiteral = Literal[
    "part_missing_ambiguity",
    "anchor_ambiguity",
    "attachment_gap",
    "seam_unclear",
    "mask_needed",
]
ReferenceRuntimeCapabilityNameLiteral = Literal["classifier", "vision", "localization", "segmentation"]
ReferenceRuntimeCapabilityStatusLiteral = Literal[
    "not_configured",
    "configured",
    "used",
    "skipped_by_policy",
    "unavailable",
    "error",
]
ReferenceShapeConvergenceDispositionLiteral = Literal[
    "shape_drift_build_hold",
    "build_path_exhausted",
    "hard_blocker_inspect",
    "stagnation_inspect",
    "not_evaluated",
]
ReferenceCompareSupportEvidenceKindLiteral = Literal[
    "silhouette_metric", "per_object_iou", "action_hint", "part_segmentation"
]
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
ReferenceUnderstandingStatusLiteral = Literal["available", "blocked", "unavailable"]
ReferenceUnderstandingSubjectCategoryLiteral = Literal[
    "creature",
    "hard_surface",
    "architectural_mass",
    "dental_surface",
    "organic_form",
    "unknown",
]
ReferenceUnderstandingStyleLiteral = Literal[
    "low_poly_faceted",
    "hard_surface",
    "smooth_organic",
    "architectural_mass",
    "dental_surface",
    "unknown",
]
ReferenceUnderstandingConstructionPathLiteral = Literal[
    "low_poly_facet",
    "hard_surface",
    "organic_sculpt",
    "creature_blockout",
    "dental_surface",
    "architectural_mass",
    "unknown",
]
ReferenceUnderstandingFinishPolicyLiteral = Literal[
    "preserve_facets",
    "inspect_first",
    "bounded_local_detail",
    "unknown",
]
ReferenceUnderstandingSculptPolicyLiteral = Literal["hidden", "local_detail_only", "allowed_or_primary"]
ReferenceUnderstandingViewLiteral = Literal["front", "side", "top", "back", "three_quarter", "detail", "unknown"]
ReferenceUnderstandingVisualMetricLiteral = Literal[
    "edge_density",
    "contour_count",
    "polygonal_contour_ratio",
    "dominant_color_count",
    "silhouette_aspect_ratio",
    "facet_likelihood",
]
ReferenceUnderstandingAttachmentRelationLiteral = Literal[
    "segment_attachment",
    "seated_attachment",
    "embedded_attachment",
    "support_contact",
    "symmetry_pair",
    "unknown",
]


class ReferenceUnderstandingSubjectContract(MCPContract):
    """Bounded subject classification derived from attached references."""

    label: str = Field(description="Short subject label inferred from the attached reference images.")
    category: ReferenceUnderstandingSubjectCategoryLiteral = Field(
        default="unknown", description="Controlled high-level subject family used for downstream build policy."
    )
    confidence: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Advisory classifier confidence in [0,1]; not a truth source."
    )
    uncertainty_notes: list[str] = Field(
        default_factory=list, description="Short caveats explaining ambiguity in the subject classification."
    )


class ReferenceUnderstandingStyleContract(MCPContract):
    """Controlled style classification for pre-build reference understanding."""

    style_label: ReferenceUnderstandingStyleLiteral = Field(
        default="unknown", description="Controlled visual style label used to choose build and finish policy."
    )
    confidence: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Advisory style confidence in [0,1]; deterministic checks still win."
    )
    notes: list[str] = Field(default_factory=list, description="Bounded style cues visible in the reference images.")


class ReferenceUnderstandingPartContract(MCPContract):
    """One candidate required part or detail derived from references."""

    part_label: str = Field(description="Human-readable part/detail name visible in the references.")
    target_label: str | None = Field(
        default=None,
        description="Canonical role label when known, e.g. body_core, head_mass, tail_mass, or ear_pair.",
    )
    construction_hint: str | None = Field(
        default=None, description="Advisory modeling hint for constructing this part; not executable code."
    )
    priority: Literal["high", "normal"] = Field(
        default="normal", description="Advisory ordering hint for build planning."
    )
    source_reference_ids: list[str] = Field(
        default_factory=list, description="Reference image ids that support this part cue."
    )


class ReferenceUnderstandingViewContract(MCPContract):
    """One normalized reference-view observation derived from active references."""

    view_id: ReferenceUnderstandingViewLiteral = Field(
        default="unknown", description="Normalized view direction represented by the reference image."
    )
    detected: bool = Field(default=False, description="True when this view was confidently detected.")
    confidence: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Advisory view-detection confidence in [0,1]."
    )
    reference_ids: list[str] = Field(default_factory=list, description="Reference ids that show this view.")
    key_features: list[str] = Field(default_factory=list, description="Short visible cues found in this view.")


class ReferenceUnderstandingAssemblyPartContract(MCPContract):
    """One advisory creature assembly part cue derived from references."""

    target_label: str
    geometry_family: str | None = None
    construction_hint: str | None = None
    anchor_role_candidates: list[str] = []
    support_surface_candidates: list[str] = []
    contact_expectations: list[str] = []
    source_reference_ids: list[str] = []


class ReferenceUnderstandingAttachmentPlanItemContract(MCPContract):
    """One advisory attachment-first step for creature assembly sequencing."""

    target_label: str
    anchor_role_candidates: list[str] = []
    required_relation: ReferenceUnderstandingAttachmentRelationLiteral = "unknown"
    support_surface_candidates: list[str] = []
    contact_expectations: list[str] = []
    notes: list[str] = []


class ReferenceUnderstandingContactExpectationContract(MCPContract):
    """One advisory contact or support expectation for a creature part."""

    target_label: str
    expected_contacts: list[str] = []
    avoid_contacts: list[str] = []
    notes: list[str] = []


class ReferenceUnderstandingShapeProfileHintContract(MCPContract):
    """One advisory shape-profile cue for a target part."""

    target_label: str
    summary: str
    reference_id: str | None = None


class ReferenceUnderstandingSilhouetteLandmarkContract(MCPContract):
    """One advisory silhouette landmark cue for a target part or whole form."""

    landmark_id: str
    target_label: str | None = None
    view_id: ReferenceUnderstandingViewLiteral = "unknown"
    summary: str


class ReferenceUnderstandingConstructionStrategyContract(MCPContract):
    """Controlled construction-path summary normalized for guided policy."""

    construction_path: ReferenceUnderstandingConstructionPathLiteral = "unknown"
    primary_family: ReferencePlannerFamilyLiteral = "inspect_only"
    allowed_families: list[ReferencePlannerFamilyLiteral] = []
    stage_sequence: list[str] = []
    finish_policy: ReferenceUnderstandingFinishPolicyLiteral = "unknown"


class ReferenceUnderstandingHandoffHintsContract(MCPContract):
    """Advisory family/visibility hints for guided policy normalization."""

    preferred_family: ReferencePlannerFamilyLiteral = "inspect_only"
    allowed_guided_families: list[GuidedFlowFamilyLiteral] = []
    sculpt_policy: ReferenceUnderstandingSculptPolicyLiteral = "hidden"


class ReferenceUnderstandingVisualEvidenceRefContract(MCPContract):
    """One compact provenance/evidence item extracted from references."""

    evidence_id: str
    source_class: Literal["reference_image", "style_cue", "part_cue", "construction_hint", "gate_seed"]
    summary: str
    reference_id: str | None = None


class ReferenceUnderstandingVisualMetricContract(MCPContract):
    """One deterministic image-derived support metric for reference understanding."""

    metric_id: ReferenceUnderstandingVisualMetricLiteral
    reference_id: str | None = None
    observed_value: float
    computation_mode: Literal["heuristic_image_metrics"] = "heuristic_image_metrics"
    summary: str | None = None


class ReferenceUnderstandingVerificationRequirementContract(MCPContract):
    """One suggested deterministic follow-up check derived from references."""

    tool_name: str
    reason: str
    priority: Literal["high", "normal"] = "normal"


class ReferenceUnderstandingClassificationScoreContract(MCPContract):
    """Optional later classification score preserved as bounded support evidence."""

    label: str
    score: float = Field(ge=0.0, le=1.0)


class ReferenceUnderstandingSegmentationArtifactContract(MCPContract):
    """Optional later segmentation/localization artifact reference."""

    artifact_id: str
    artifact_kind: Literal["mask", "crop", "box"] = "mask"
    reference_id: str | None = None
    summary: str | None = None


class ReferenceUnderstandingBoundaryPolicyContract(MCPContract):
    """Explicit authority limits for reference-understanding output."""

    advisory_only: bool = True
    not_truth_source: bool = True
    may_unlock_tools: bool = False
    may_pass_gates: bool = False
    may_propose_gates: bool = True


class ReferenceUnderstandingSummaryContract(MCPContract):
    """Typed reference-understanding result surfaced through existing guided/reference seams."""

    status: ReferenceUnderstandingStatusLiteral
    understanding_id: str | None = None
    goal: str | None = None
    reference_ids: list[str] = []
    subject: ReferenceUnderstandingSubjectContract | None = None
    style: ReferenceUnderstandingStyleContract | None = None
    views: list[ReferenceUnderstandingViewContract] = []
    required_parts: list[ReferenceUnderstandingPartContract] = []
    mass_recipe: list[ReferenceUnderstandingAssemblyPartContract] = []
    attachment_plan: list[ReferenceUnderstandingAttachmentPlanItemContract] = []
    contact_expectations: list[ReferenceUnderstandingContactExpectationContract] = []
    shape_profile_hints: list[ReferenceUnderstandingShapeProfileHintContract] = []
    silhouette_landmarks: list[ReferenceUnderstandingSilhouetteLandmarkContract] = []
    part_order: list[str] = []
    must_seat_before_next_stage: list[str] = []
    non_goals: list[str] = []
    construction_strategy: ReferenceUnderstandingConstructionStrategyContract | None = None
    router_handoff_hints: ReferenceUnderstandingHandoffHintsContract | None = None
    gate_proposals: list[GateProposalGateContract] = []
    visual_evidence_refs: list[ReferenceUnderstandingVisualEvidenceRefContract] = []
    visual_metrics: list[ReferenceUnderstandingVisualMetricContract] = []
    classification_scores: list[ReferenceUnderstandingClassificationScoreContract] = Field(
        default_factory=list,
        max_length=5,
    )
    segmentation_artifacts: list[ReferenceUnderstandingSegmentationArtifactContract] = []
    verification_requirements: list[ReferenceUnderstandingVerificationRequirementContract] = []
    source_provenance: list[GateSourceProvenanceContract] = []
    boundary_policy: ReferenceUnderstandingBoundaryPolicyContract = ReferenceUnderstandingBoundaryPolicyContract()
    reason: Literal["goal_required", "reference_images_required", "vision_backend_unavailable"] | None = None
    message: str | None = None


class ReferenceStrategyStateContract(MCPContract):
    """Server-owned normalized strategy state derived from reference understanding."""

    status: ReferenceUnderstandingStatusLiteral = "blocked"
    understanding_id: str | None = None
    construction_path: ReferenceUnderstandingConstructionPathLiteral = "unknown"
    primary_family: ReferencePlannerFamilyLiteral = "inspect_only"
    allowed_families: list[ReferencePlannerFamilyLiteral] = []
    blocked_families: list[ReferencePlannerFamilyLiteral] = []
    sculpt_policy: ReferenceUnderstandingSculptPolicyLiteral = "hidden"
    finish_policy: ReferenceUnderstandingFinishPolicyLiteral = "unknown"
    recommended_next_checkpoint: (
        Literal[
            "reference_images",
            "router_get_status",
            "reference_compare_stage_checkpoint",
            "reference_iterate_stage_checkpoint",
        ]
        | None
    ) = None
    message: str | None = None


class ReferenceCompactRepairContract(MCPContract):
    """One bounded actionable repair hint projected on the compact orchestrator surface."""

    tool_name: str
    reason: str
    arguments_hint: dict[str, object] | None = None


class ReferenceAuthoritativeNextActionContract(MCPContract):
    """One provenance-tagged entry behind the consolidated next-action list."""

    action: str
    source: ReferenceActionSourceLiteral
    authority: Literal["authoritative", "deterministic", "advisory"] = "advisory"
    rank: int


class ReferenceRuntimeCapabilityUsageContract(MCPContract):
    """Bounded, redacted runtime participation summary for one optional/support capability."""

    capability: ReferenceRuntimeCapabilityNameLiteral
    status: ReferenceRuntimeCapabilityStatusLiteral = Field(
        description="Normalized capability outcome for this compare/status surface."
    )
    configured: bool = Field(description="True when the runtime/config made this capability available for use.")
    considered: bool = Field(description="True when the policy evaluated this capability for the current run.")
    invoked: bool = Field(description="True when the compare path actually called the capability/runtime.")
    provider_name: str | None = Field(default=None, description="Configured provider name, never a secret or key.")
    packet_ids: list[str] = Field(
        default_factory=list, description="Bounded packet ids where this capability was considered or invoked."
    )
    notes: list[str] = Field(default_factory=list, description="Short bounded policy/status notes.")


class ReferenceRuntimeEvidenceContract(MCPContract):
    """Machine-readable runtime evidence for guided/reference compare loops.

    This reports capability participation only. It is advisory diagnostics and
    never marks quality gates complete or overrides deterministic scene truth.
    """

    capabilities: list[ReferenceRuntimeCapabilityUsageContract] = Field(
        default_factory=list, description="Classifier, vision, localization, and segmentation participation summary."
    )
    checkpoint_id: str | None = Field(default=None, description="Checkpoint this evidence came from, when known.")
    packet_ids: list[str] = Field(default_factory=list, description="Packet ids represented by this evidence.")
    notes: list[str] = Field(default_factory=list, description="Bounded run-level runtime evidence notes.")


class ReferenceOrchestratorFeedbackContract(MCPContract):
    """Compact orchestrator-facing read model for guided reference sessions.

    This is the single normalized next-step contract the client should read
    FIRST on every guided/reference response, before the richer advisory vision
    payload. It summarizes deterministic guided/gate state (authoritative) plus a
    compact view of advisory evidence; it never overrides deterministic scene
    truth or marks gates complete by itself.
    """

    status: ReferenceUnderstandingStatusLiteral = Field(
        default="blocked", description="Current reference-understanding lifecycle status for the session."
    )
    goal: str | None = None
    understanding_id: str | None = None
    construction_path: ReferenceUnderstandingConstructionPathLiteral = Field(
        default="unknown", description="The construction path the references imply (e.g. faceted low-poly vs smooth)."
    )
    current_guided_step: str | None = None
    selected_family: ReferencePlannerFamilyLiteral = Field(
        default="inspect_only", description="The correction family currently selected by deterministic guided policy."
    )
    allowed_families: list[ReferencePlannerFamilyLiteral] = []
    blocked_families: list[ReferencePlannerFamilyLiteral] = []
    required_parts_pending: list[str] = []
    active_gate_ids: list[str] = []
    blocking_reasons: list[str] = []
    next_actions: list[str] = Field(
        default_factory=list,
        description="The normalized, authoritative ordered next steps to take; prefer these over raw vision prose.",
    )
    next_checkpoint_tool: (
        Literal[
            "reference_images",
            "router_get_status",
            "reference_compare_stage_checkpoint",
            "reference_iterate_stage_checkpoint",
        ]
        | None
    ) = None
    recommended_support_tools: list[str] = []
    recommended_repair: ReferenceCompactRepairContract | None = None
    evidence_summary: list[str] = Field(
        default_factory=list,
        description="Compact advisory summary of perceived/deterministic evidence behind the next steps.",
    )
    uncertainty_notes: list[str] = Field(
        default_factory=list, description="Advisory notes on what remains uncertain or under-grounded this cycle."
    )
    correction_focus: list[str] = Field(
        default_factory=list, description="The highest-priority mismatch targets to address next (advisory subset)."
    )
    loop_disposition: Literal["continue_build", "inspect_validate", "stop"] | None = Field(
        default=None,
        description="Recommended loop disposition; advisory input to deterministic guided policy, not a final gate.",
    )
    shape_convergence_disposition: ReferenceShapeConvergenceDispositionLiteral | None = Field(
        default=None,
        description=(
            "Compact distinction between shape-drift build hold, exhausted build path, hard blocker inspect, "
            "stagnation inspect, or not evaluated."
        ),
    )
    runtime_evidence: ReferenceRuntimeEvidenceContract | None = Field(
        default=None,
        description="Bounded machine-readable runtime participation summary for classifier/vision/sidecars.",
    )
    authoritative_next_actions: list[str] = Field(
        default_factory=list,
        description=(
            "Single consolidated, ranked next-step list merged from the overlapping advisory channels "
            "(deterministic next_actions first, then correction_focus, support tools, repair). Read THIS first; "
            "the other channels remain for detail. Deterministic guided policy still owns final gate decisions."
        ),
    )
    authoritative_next_action_provenance: list[ReferenceAuthoritativeNextActionContract] = Field(
        default_factory=list,
        description="Provenance and authority tags for each consolidated authoritative_next_actions entry.",
    )
    message: str | None = None


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
    guided_reference_readiness: GuidedReferenceReadinessContract | None = None
    reference_understanding_summary: ReferenceUnderstandingSummaryContract | None = None
    reference_understanding_gate_ids: list[str] = []
    reference_orchestrator_feedback: ReferenceOrchestratorFeedbackContract | None = None
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


class ReferenceCorrectionPacketEvidenceRefContract(MCPContract):
    """Bounded pointer from a correction candidate back to packet diagnostics."""

    packet_id: str
    packet_label: str
    target_view: str | None = None
    scope_label: str | None = None
    extraction_status: ReferenceComparePacketStatusLiteral = "skipped"
    ranking_status: ReferenceCompareRankingStatusLiteral = "not_needed"
    packet_status: ReferenceComparePacketGuidanceLiteral | None = None
    evidence_summary: str | None = None
    support_evidence_count: int = 0


class ReferenceCorrectionVisionEvidenceContract(MCPContract):
    """Vision-side evidence attached to one merged correction candidate."""

    correction_focus: list[str] = []
    shape_mismatches: list[str] = []
    proportion_mismatches: list[str] = []
    next_corrections: list[str] = []
    packet_evidence_refs: list[ReferenceCorrectionPacketEvidenceRefContract] = []


class ReferenceCorrectionTruthEvidenceContract(MCPContract):
    """Truth-side evidence attached to one merged correction candidate."""

    focus_pairs: list[str] = []
    relation_kinds: list[SceneRelationKindLiteral] = []
    relation_verdicts: list[SceneRelationVerdictLiteral] = []
    item_kinds: list[
        Literal[
            "contact_failure",
            "gap",
            "overlap",
            "alignment",
            "attachment",
            "support",
            "symmetry",
            "measurement_error",
            "insufficient_scope",
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


class ReferenceCompareSupportEvidenceContract(MCPContract):
    """One compact, machine-readable support-evidence item for packet compare."""

    evidence_kind: ReferenceCompareSupportEvidenceKindLiteral
    summary: str
    metric_id: str | None = None
    hint_type: str | None = None
    severity: Literal["high", "medium", "low"] | None = None
    observed_value: float | None = Field(
        default=None,
        description="Deterministic observed value for this evidence (e.g. a normalized silhouette overlap ratio).",
    )
    delta: float | None = Field(
        default=None,
        description="Reference-relative delta as a proportion/ratio against the reference anchor, not an absolute measurement.",
    )
    reference_label: str | None = None
    capture_label: str | None = None
    target_view: str | None = None
    part_label: str | None = None
    confidence: float | None = Field(
        default=None, description="Non-authoritative confidence in [0,1]; deterministic checks remain the authority."
    )


class ReferenceOpenDefectContract(MCPContract):
    """One stable Critic defect tracked across compare/verify cycles."""

    defect_id: str
    summary: str
    scope_label: str | None = None
    relation_ref: str | None = None
    severity: ReferenceDefectSeverityLiteral = "medium"


class ReferenceDefectVerifyStatusContract(MCPContract):
    """Verify status for one stable defect id after a same-view rerender."""

    defect_id: str
    status: ReferenceDefectVerifyStatusLiteral
    reason: str | None = None
    scope_label: str | None = None


class ReferenceComparePacketContract(MCPContract):
    """One packet-level compare unit surfaced additively on staged compare responses."""

    packet_id: str
    packet_kind: ReferenceComparePacketKindLiteral = "view"
    packet_label: str
    target_view: str | None = None
    scope_label: str | None = None
    scope_source: ReferenceCompareScopeSourceLiteral | None = Field(
        default=None,
        description="Planner source for this packet scope: guided registry graph, truth focus pairs, target scope, or fallback.",
    )
    target_objects: list[str] = []
    truth_pairs: list[str] = []
    reference_ids: list[str] = []
    capture_labels: list[str] = []
    mark_id_map: dict[str, int] = Field(
        default_factory=dict,
        description="Exact object_name -> stable mark id map used for any Set-of-Mark overlay in this packet.",
    )
    reference_marks: list[VisionOverlayMarkContract] = Field(
        default_factory=list,
        description="Optional reference-side marks produced by the default-off grounding sidecar.",
    )
    compare_question: str
    extraction_status: ReferenceComparePacketStatusLiteral = Field(
        default="skipped",
        description="Outcome of the per-packet evidence EXTRACTION pass (did the VLM read this packet).",
    )
    ranking_status: ReferenceCompareRankingStatusLiteral = Field(
        default="not_needed", description="Outcome of the cross-packet RANKING pass (was this packet ranked, and how)."
    )
    packet_status: ReferenceComparePacketGuidanceLiteral | None = Field(
        default=None,
        description="Packet-local delivery guidance (ready/clean/low_information/blocked) for downstream consumers.",
    )
    ranking_recommendation: ReferenceCompareRankingRecommendationLiteral | None = Field(
        default=None, description="Advisory recommendation to rank or skip this packet (and why); not a gate."
    )
    localized_support_reason: ReferenceLocalizedSupportReasonLiteral | None = Field(
        default=None, description="Why optional localized support was or was not attached to this packet."
    )
    status_reason: str | None = Field(
        default=None, description="Short reason explaining the packet's extraction/ranking/packet status."
    )
    support_evidence: list[ReferenceCompareSupportEvidenceContract] = []
    evidence_summary: str | None = None
    uncertainty_notes: list[str] = []
    correction_focus: list[str] = []
    open_defects: list[ReferenceOpenDefectContract] = []
    verify_status: list[ReferenceDefectVerifyStatusContract] = []


class ReferenceGraphNodeDeltaContract(MCPContract):
    """One per-node attribute mismatch in a graph-vs-graph compare diff."""

    target_label: str = Field(description="Canonical part/object role this node represents.")
    status: Literal["present", "missing", "unexpected"] = Field(
        description="present = in both graphs; missing = expected but absent; unexpected = built but not expected.",
    )
    attribute_mismatches: list[str] = Field(
        default_factory=list,
        description="Symbolic per-attribute divergences (e.g. 'profile too round'); proportional, never coordinates.",
    )


class ReferenceGraphEdgeDeltaContract(MCPContract):
    """One per-edge relation mismatch in a graph-vs-graph compare diff."""

    from_label: str = Field(description="Canonical role of the relation's subject node.")
    to_label: str = Field(description="Canonical role of the relation's object node.")
    relation_kind: SceneRelationKindLiteral = Field(description="The expected relation kind for this edge.")
    status: Literal["satisfied", "violated", "missing", "unknown"] = Field(
        description="satisfied = holds; violated = present but wrong; missing = expected edge absent; unknown.",
    )
    detail: str | None = Field(default=None, description="Short symbolic reason for a violated/missing edge.")


class ReferenceGraphDiffContract(MCPContract):
    """Graph-vs-graph compare diff: expected part graph vs the built scene graph.

    Advisory structural evidence parallel to the prose/finding channels: it reports
    per-node attribute mismatches and per-edge relation mismatches over the fixed
    relation vocabulary, so the orchestrator can see *which parts/relations* differ
    from the expected structure rather than inferring it from prose. Not a truth
    source; deterministic inspection/assertion still own correctness.
    """

    node_deltas: list[ReferenceGraphNodeDeltaContract] = Field(
        default_factory=list, description="Per-node attribute/presence mismatches against the expected part graph."
    )
    edge_deltas: list[ReferenceGraphEdgeDeltaContract] = Field(
        default_factory=list, description="Per-edge relation mismatches against the expected relations."
    )
    missing_parts: list[str] = Field(
        default_factory=list, description="Canonical roles expected by the reference but absent from the scene."
    )
    unexpected_parts: list[str] = Field(
        default_factory=list, description="Scene parts present but not in the expected part graph."
    )


class ReferenceCompareDiagnosticsContract(MCPContract):
    """Additive packet/synthesis diagnostics for staged compare and iterate flows."""

    complexity_tier: ReferenceCompareComplexityTierLiteral = "simple"
    packet_count: int = 0
    packet_order: list[str] = []
    synthesis_required: bool = False
    synthesis_status: Literal["success", "skipped", "not_needed", "error"] = "not_needed"
    packets: list[ReferenceComparePacketContract] = []
    conflict_notes: list[str] = []
    budget_notes: list[str] = []
    registered_compare_scope: SceneAssembledTargetScopeContract | None = Field(
        default=None,
        description=(
            "Guided registry-derived compare scope used when packets are planned from stable part roles "
            "instead of name heuristics."
        ),
    )
    runtime_evidence: ReferenceRuntimeEvidenceContract | None = Field(
        default=None,
        description="Bounded capability participation evidence for this packeted compare run.",
    )


class ReferenceHybridBudgetControlContract(MCPContract):
    """Budget/scope control metadata for hybrid-loop compare and iterate responses."""

    model_name: str | None = None
    max_input_chars: int
    max_output_tokens: int
    max_images: int
    configured_max_input_chars: int | None = None
    configured_max_output_tokens: int | None = None
    configured_max_images: int | None = None
    effective_max_input_chars: int | None = None
    effective_max_output_tokens: int | None = None
    effective_max_images: int | None = None
    fail_safe_max_input_chars: int | None = None
    fail_safe_max_output_tokens: int | None = None
    fail_safe_max_images: int | None = None
    budget_clipped: bool = False
    budget_clip_fields: list[str] = []
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


class ReferencePerObjectSilhouetteMetricContract(MCPContract):
    """One deterministic object-ID-mask IoU metric for a named scene object."""

    object_name: str = Field(description="Scene object decoded from the object-ID pass index map.")
    object_index: int | None = Field(default=None, description="Integer pass-index band used for this object.")
    status: Literal["available", "unavailable"] = Field(
        default="unavailable", description="Whether a stable object-ID mask could be decoded and compared."
    )
    mask_iou: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="BBox-normalized IoU between the reference mask and this object's decoded mask.",
    )
    severity: Literal["high", "medium", "low"] = Field(
        default="medium", description="Advisory severity derived from the per-object IoU value."
    )
    notes: list[str] = Field(default_factory=list, description="Decode or comparison caveats for this object.")


class ReferenceSilhouetteConvergenceContract(MCPContract):
    """Deterministic IoU convergence between two correction-loop checkpoints."""

    status: Literal["ok", "unavailable"] = Field(description="Whether previous/current IoU values were comparable.")
    previous_iou: float | None = Field(default=None, ge=0.0, le=1.0, description="Previous loop IoU when available.")
    current_iou: float | None = Field(default=None, ge=0.0, le=1.0, description="Current loop IoU when available.")
    delta: float | None = Field(default=None, description="Current minus previous IoU; positive means improvement.")
    verdict: Literal["improved", "regressed", "stalled", "unknown"] = Field(
        description="Bounded deterministic trend verdict for the correction loop."
    )


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

    status: Literal["available", "unavailable"] = Field(
        default="unavailable", description="Whether deterministic silhouette metrics were computed for this pair."
    )
    reference_label: str | None = Field(
        default=None, description="Reference image label used as the comparison anchor."
    )
    capture_label: str | None = Field(default=None, description="Capture label compared against the reference image.")
    target_view: str | None = Field(default=None, description="Normalized view token for this comparison when known.")
    mask_extraction_mode: Literal["alpha_or_otsu_largest_component", "unavailable"] = Field(
        default="unavailable", description="Deterministic mask extraction method used before metric computation."
    )
    alignment_mode: Literal["bbox_normalized", "unavailable"] = Field(
        default="unavailable", description="Deterministic alignment method used before comparing masks."
    )
    consistency_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Lightweight deterministic render-vs-reference consistency score; currently mask IoU.",
    )
    iou_convergence: ReferenceSilhouetteConvergenceContract | None = Field(
        default=None, description="Previous/current IoU trend for the active correction loop."
    )
    metrics: list[ReferenceSilhouetteMetricContract] = Field(
        default_factory=list, description="Bounded deterministic metrics such as IoU and contour drift."
    )
    per_object_metrics: list[ReferencePerObjectSilhouetteMetricContract] = Field(
        default_factory=list, description="Optional object-ID-mask IoU metrics keyed to named scene objects."
    )
    notes: list[str] = Field(default_factory=list, description="Short caveats or failure reasons for the analysis.")


class ReferencePartSegmentationLandmarkContract(MCPContract):
    """One optional 2D landmark emitted by a future segmentation sidecar."""

    landmark_id: str
    x: float
    y: float


class ReferencePartSegmentationPartContract(MCPContract):
    """One optional part-aware segmentation artifact for a creature region."""

    part_label: str = Field(description="Canonical or provider-local part label for this segmented region.")
    mask_path: str | None = Field(default=None, description="Optional local mask artifact path for this part.")
    crop_path: str | None = Field(default=None, description="Optional local crop artifact path for this part.")
    confidence: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Advisory sidecar confidence in [0,1]; not deterministic truth."
    )
    landmarks: list[ReferencePartSegmentationLandmarkContract] = Field(
        default_factory=list, description="Optional bounded 2D landmarks emitted by the segmentation sidecar."
    )


class ReferencePartSegmentationContract(MCPContract):
    """Optional vendor-neutral sidecar payload for part-aware creature perception."""

    status: Literal["disabled", "available", "unavailable"] = Field(
        default="disabled", description="Sidecar availability status for this compare request."
    )
    provider_name: str | None = Field(default=None, description="Configured segmentation provider name when enabled.")
    advisory_only: bool = Field(default=True, description="Always true: segmentation helps targeting but is not truth.")
    parts: list[ReferencePartSegmentationPartContract] = Field(
        default_factory=list, description="Bounded part segmentation outputs accepted from the sidecar."
    )
    notes: list[str] = Field(default_factory=list, description="Short sidecar status notes or failure reasons.")


class ReferenceCompareStageCheckpointResponseContract(MCPContract):
    """Structured response for deterministic stage checkpoint capture + compare."""

    action: Literal["compare_stage_checkpoint"] = "compare_stage_checkpoint"
    session_id: str | None = None
    transport: str | None = None
    goal: str | None = None
    guided_flow_state: GuidedFlowStateContract | None = None
    active_gate_plan: GatePlanContract | None = None
    gate_statuses: list[NormalizedQualityGateContract] = []
    completion_blockers: list[GateCompletionBlockerContract] = []
    next_gate_actions: list[str] = []
    recommended_bounded_tools: list[str] = []
    guided_reference_readiness: GuidedReferenceReadinessContract | None = None
    reference_understanding_summary: ReferenceUnderstandingSummaryContract | None = None
    reference_understanding_gate_ids: list[str] = []
    reference_orchestrator_feedback: ReferenceOrchestratorFeedbackContract | None = None
    target_object: str | None = None
    target_objects: list[str] = []
    collection_name: str | None = None
    assembled_target_scope: SceneAssembledTargetScopeContract | None = None
    truth_bundle: SceneCorrectionTruthBundleContract | None = None
    truth_followup: SceneTruthFollowupContract | None = None
    compare_diagnostics: ReferenceCompareDiagnosticsContract | None = None
    correction_candidates: list[ReferenceCorrectionCandidateContract] = []
    budget_control: ReferenceHybridBudgetControlContract | None = None
    refinement_route: ReferenceRefinementRouteContract | None = None
    refinement_handoff: ReferenceRefinementHandoffContract | None = None
    planner_summary: ReferenceRepairPlannerSummaryContract | None = None
    planner_detail: ReferenceRepairPlannerDetailContract | None = None
    silhouette_analysis: ReferenceSilhouetteAnalysisContract | None = None
    action_hints: list[ReferenceActionHintContract] = []
    part_segmentation: ReferencePartSegmentationContract | None = None
    runtime_evidence: ReferenceRuntimeEvidenceContract | None = None
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
    gate_statuses: list[NormalizedQualityGateContract] = []
    completion_blockers: list[GateCompletionBlockerContract] = []
    next_gate_actions: list[str] = []
    recommended_bounded_tools: list[str] = []
    guided_reference_readiness: GuidedReferenceReadinessContract | None = None
    reference_understanding_summary: ReferenceUnderstandingSummaryContract | None = None
    reference_understanding_gate_ids: list[str] = []
    reference_orchestrator_feedback: ReferenceOrchestratorFeedbackContract | None = None
    target_object: str | None = None
    target_objects: list[str] = []
    collection_name: str | None = None
    assembled_target_scope: SceneAssembledTargetScopeContract | None = None
    truth_bundle: SceneCorrectionTruthBundleContract | None = None
    truth_followup: SceneTruthFollowupContract | None = None
    compare_diagnostics: ReferenceCompareDiagnosticsContract | None = None
    correction_candidates: list[ReferenceCorrectionCandidateContract] = []
    budget_control: ReferenceHybridBudgetControlContract | None = None
    refinement_route: ReferenceRefinementRouteContract | None = None
    refinement_handoff: ReferenceRefinementHandoffContract | None = None
    planner_summary: ReferenceRepairPlannerSummaryContract | None = None
    planner_detail: ReferenceRepairPlannerDetailContract | None = None
    silhouette_analysis: ReferenceSilhouetteAnalysisContract | None = None
    action_hints: list[ReferenceActionHintContract] = []
    part_segmentation: ReferencePartSegmentationContract | None = None
    runtime_evidence: ReferenceRuntimeEvidenceContract | None = None
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
    shape_convergence_disposition: ReferenceShapeConvergenceDispositionLiteral | None = None
    stop_reason: str | None = None
    compare_result: ReferenceCompareStageCheckpointResponseContract
    debug_payload_omitted: bool = False
    message: str | None = None
    error: str | None = None


ReferenceUnderstandingSummaryContract.model_rebuild()
ReferenceCompareStageCheckpointResponseContract.model_rebuild()
ReferenceIterateStageCheckpointResponseContract.model_rebuild()
