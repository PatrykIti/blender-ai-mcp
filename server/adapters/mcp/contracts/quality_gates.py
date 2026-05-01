# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Structured contracts for goal-derived quality gates."""

from __future__ import annotations

import re
from typing import Any, Literal, Mapping, TypeAlias, cast, get_args

from .base import MCPContract
from .guided_flow import GuidedFlowDomainProfileLiteral, GuidedFlowFamilyLiteral

GateTypeLiteral: TypeAlias = Literal[
    "required_part",
    "attachment_seam",
    "support_contact",
    "symmetry_pair",
    "proportion_ratio",
    "shape_profile",
    "opening_or_cut",
    "refinement_stage",
    "final_completion",
]
GateProposalSourceLiteral: TypeAlias = Literal[
    "llm_goal",
    "reference_understanding",
    "domain_template",
    "silhouette_analysis",
    "part_segmentation",
    "classification_scores",
    "reference_checkpoint",
    "operator_override",
]
GatePriorityLiteral: TypeAlias = Literal["high", "normal", "low"]
GateDeclarationStatusLiteral: TypeAlias = Literal["proposed", "requested"]
GateStatusLiteral: TypeAlias = Literal["pending", "blocked", "passed", "failed", "waived", "stale"]
GateTargetKindLiteral: TypeAlias = Literal[
    "object",
    "object_role",
    "reference_part",
    "object_pair",
    "collection",
    "scene",
    "region",
    "unknown",
]
GateEvidenceKindLiteral: TypeAlias = Literal[
    "scene_truth",
    "spatial_relation",
    "mesh_metric",
    "silhouette_analysis",
    "part_segmentation",
    "classification_scores",
    "reference_understanding",
    "llm_rationale",
]
GateVerificationStrategyLiteral: TypeAlias = Literal[
    "object_existence",
    "spatial_contact",
    "spatial_support",
    "symmetry_pair",
    "mesh_metric",
    "shape_profile",
    "opening_or_cut",
    "stage_completion",
    "aggregate_required_gates",
]
GatePolicyWarningCodeLiteral: TypeAlias = Literal[
    "unsupported_gate_type",
    "unsupported_priority",
    "unsupported_proposal_status",
    "unsupported_completion_status",
    "hidden_tool_requirement",
    "unsupported_correction_family",
    "unsupported_evidence_kind",
    "raw_blender_instruction",
]

_GATE_TYPES = set(get_args(GateTypeLiteral))
_PROPOSAL_SOURCES = set(get_args(GateProposalSourceLiteral))
_PRIORITIES = set(get_args(GatePriorityLiteral))
_DECLARATION_STATUSES = set(get_args(GateDeclarationStatusLiteral))
_GATE_STATUSES = set(get_args(GateStatusLiteral))
_TARGET_KINDS = set(get_args(GateTargetKindLiteral))
_EVIDENCE_KINDS = set(get_args(GateEvidenceKindLiteral))
_CORRECTION_FAMILIES = set(get_args(GuidedFlowFamilyLiteral))
_TOOL_NAME_PREFIXES = (
    "baking_",
    "collection_",
    "curve_",
    "material_",
    "mesh_",
    "modeling_",
    "reference_",
    "router_",
    "scene_",
    "sculpt_",
    "system_",
    "text_",
    "uv_",
    "workflow_",
)
_RAW_BLENDER_PATTERNS = (
    "bpy.",
    "bmesh.",
    "import bpy",
    "python:",
    "exec(",
    "eval(",
)
_VERIFICATION_STRATEGY_BY_GATE_TYPE: dict[GateTypeLiteral, GateVerificationStrategyLiteral] = {
    "required_part": "object_existence",
    "attachment_seam": "spatial_contact",
    "support_contact": "spatial_support",
    "symmetry_pair": "symmetry_pair",
    "proportion_ratio": "mesh_metric",
    "shape_profile": "shape_profile",
    "opening_or_cut": "opening_or_cut",
    "refinement_stage": "stage_completion",
    "final_completion": "aggregate_required_gates",
}
_EVIDENCE_REQUIREMENTS_BY_GATE_TYPE: dict[GateTypeLiteral, tuple[GateEvidenceKindLiteral, ...]] = {
    "required_part": ("scene_truth",),
    "attachment_seam": ("spatial_relation",),
    "support_contact": ("spatial_relation",),
    "symmetry_pair": ("scene_truth", "spatial_relation"),
    "proportion_ratio": ("mesh_metric",),
    "shape_profile": ("mesh_metric",),
    "opening_or_cut": ("mesh_metric",),
    "refinement_stage": ("scene_truth",),
    "final_completion": ("scene_truth",),
}
_CORRECTION_FAMILIES_BY_GATE_TYPE: dict[GateTypeLiteral, tuple[GuidedFlowFamilyLiteral, ...]] = {
    "required_part": ("primary_masses", "secondary_parts", "inspect_validate"),
    "attachment_seam": ("spatial_context", "attachment_alignment", "inspect_validate"),
    "support_contact": ("spatial_context", "attachment_alignment", "inspect_validate"),
    "symmetry_pair": ("secondary_parts", "inspect_validate"),
    "proportion_ratio": ("secondary_parts", "inspect_validate"),
    "shape_profile": ("secondary_parts", "inspect_validate"),
    "opening_or_cut": ("secondary_parts", "inspect_validate"),
    "refinement_stage": ("secondary_parts", "inspect_validate"),
    "final_completion": ("inspect_validate", "finish"),
}


class GateSourceProvenanceContract(MCPContract):
    """Bounded source metadata for a gate proposal or evidence ref."""

    source: GateProposalSourceLiteral
    source_id: str | None = None
    provider: str | None = None
    model_id: str | None = None
    vision_contract_profile: str | None = None
    reference_ids: list[str] = []
    capture_ids: list[str] = []
    evidence_ids: list[str] = []
    summary: str | None = None


class GateEvidenceRequirementContract(MCPContract):
    """One evidence class a verifier needs before a gate may pass."""

    evidence_kind: GateEvidenceKindLiteral
    required: bool = True
    reason: str | None = None


class GateEvidenceRefContract(MCPContract):
    """Stable reference to verifier or bounded perception evidence."""

    evidence_id: str
    evidence_kind: GateEvidenceKindLiteral
    source: GateProposalSourceLiteral
    status: Literal["available", "unavailable", "stale"] = "available"
    tool_name: str | None = None
    reference_id: str | None = None
    capture_id: str | None = None
    scope_fingerprint: str | None = None
    summary: str | None = None


class GatePolicyWarningContract(MCPContract):
    """Machine-readable warning emitted while normalizing proposed gates."""

    code: GatePolicyWarningCodeLiteral
    message: str
    action: Literal["dropped", "rewritten", "ignored"] = "ignored"
    gate_id: str | None = None
    gate_label: str | None = None
    field: str | None = None


class GateProposalGateContract(MCPContract):
    """One client/model-proposed quality gate before server normalization."""

    gate_id: str | None = None
    gate_type: str
    label: str | None = None
    target_kind: GateTargetKindLiteral = "unknown"
    target_label: str | None = None
    target_object: str | None = None
    target_objects: list[str] = []
    required: bool = True
    priority: str | None = None
    status: str | None = None
    rationale: str | None = None
    allowed_correction_families: list[str] = []
    evidence_requirements: list[Any] = []
    source_provenance: list[GateSourceProvenanceContract] = []


class GateProposalContract(MCPContract):
    """Client/model-supplied gate proposal envelope."""

    proposal_id: str | None = None
    source: GateProposalSourceLiteral = "llm_goal"
    goal: str | None = None
    gates: list[GateProposalGateContract] = []
    source_provenance: list[GateSourceProvenanceContract] = []


class NormalizedQualityGateContract(MCPContract):
    """Server-owned quality gate after policy normalization."""

    gate_id: str
    gate_type: GateTypeLiteral
    label: str
    target_kind: GateTargetKindLiteral = "unknown"
    target_label: str | None = None
    target_objects: list[str] = []
    required: bool = True
    priority: GatePriorityLiteral = "normal"
    status: GateStatusLiteral = "pending"
    verification_strategy: GateVerificationStrategyLiteral
    allowed_correction_families: list[GuidedFlowFamilyLiteral] = []
    proposal_sources: list[GateProposalSourceLiteral] = []
    source_provenance: list[GateSourceProvenanceContract] = []
    evidence_requirements: list[GateEvidenceRequirementContract] = []
    evidence_refs: list[GateEvidenceRefContract] = []
    rationale: str | None = None


class DomainQualityGateTemplateContract(MCPContract):
    """Repo-owned required gate template for a guided domain profile."""

    domain_profile: GuidedFlowDomainProfileLiteral
    gate_id: str
    gate_type: GateTypeLiteral
    label: str
    target_kind: GateTargetKindLiteral = "unknown"
    target_label: str | None = None
    target_objects: list[str] = []
    required: bool = True
    priority: GatePriorityLiteral = "normal"
    verification_strategy: GateVerificationStrategyLiteral | None = None
    allowed_correction_families: list[GuidedFlowFamilyLiteral] = []
    evidence_requirements: list[GateEvidenceRequirementContract] = []


class GatePlanContract(MCPContract):
    """Normalized session-scoped gate plan."""

    plan_id: str
    domain_profile: GuidedFlowDomainProfileLiteral
    gates: list[NormalizedQualityGateContract] = []
    policy_warnings: list[GatePolicyWarningContract] = []
    proposal_id: str | None = None
    required_gate_count: int = 0
    optional_gate_count: int = 0


class GateIntakeResultContract(MCPContract):
    """Result of attempting to ingest a gate proposal into session state."""

    status: Literal["accepted", "ignored", "rejected"]
    reason: str | None = None
    gate_plan: GatePlanContract | None = None
    policy_warnings: list[GatePolicyWarningContract] = []


def templates_for_domain_profile(
    profile: GuidedFlowDomainProfileLiteral,
) -> list[DomainQualityGateTemplateContract]:
    """Return repo-owned required gate templates for a guided domain profile."""

    templates = [
        DomainQualityGateTemplateContract(
            domain_profile=profile,
            gate_id="final_completion",
            gate_type="final_completion",
            label="All required quality gates are complete",
            target_kind="scene",
            required=True,
            priority="high",
            allowed_correction_families=["inspect_validate", "finish"],
        )
    ]
    if profile == "creature":
        templates.extend(
            [
                DomainQualityGateTemplateContract(
                    domain_profile=profile,
                    gate_id="creature_body_core_required",
                    gate_type="required_part",
                    label="Body core is present",
                    target_kind="object_role",
                    target_label="body_core",
                    required=True,
                    priority="high",
                ),
                DomainQualityGateTemplateContract(
                    domain_profile=profile,
                    gate_id="creature_head_mass_required",
                    gate_type="required_part",
                    label="Head mass is present",
                    target_kind="object_role",
                    target_label="head_mass",
                    required=True,
                    priority="high",
                ),
            ]
        )
    elif profile == "building":
        templates.extend(
            [
                DomainQualityGateTemplateContract(
                    domain_profile=profile,
                    gate_id="building_wall_volume_required",
                    gate_type="required_part",
                    label="Wall or main volume is present",
                    target_kind="object_role",
                    target_label="main_volume",
                    required=True,
                    priority="high",
                ),
                DomainQualityGateTemplateContract(
                    domain_profile=profile,
                    gate_id="building_roof_mass_required",
                    gate_type="required_part",
                    label="Roof mass is present",
                    target_kind="object_role",
                    target_label="roof_mass",
                    required=True,
                    priority="high",
                ),
            ]
        )
    return templates


def normalize_gate_plan(
    proposal: GateProposalContract | Mapping[str, Any],
    *,
    domain_profile: GuidedFlowDomainProfileLiteral,
    templates: list[DomainQualityGateTemplateContract] | None = None,
) -> GatePlanContract:
    """Normalize proposed gates into the server-owned gate plan contract."""

    proposal_contract = GateProposalContract.model_validate(proposal)
    warnings: list[GatePolicyWarningContract] = []
    normalized_gates: list[NormalizedQualityGateContract] = []
    used_gate_ids: set[str] = set()

    for index, gate in enumerate(proposal_contract.gates, start=1):
        normalized = _normalize_one_gate(
            gate,
            proposal=proposal_contract,
            warnings=warnings,
            fallback_index=index,
        )
        if normalized is None:
            continue
        normalized = _with_unique_gate_id(normalized, used_gate_ids)
        used_gate_ids.add(normalized.gate_id)
        normalized_gates.append(normalized)

    selected_templates = templates if templates is not None else templates_for_domain_profile(domain_profile)
    for template in selected_templates:
        if _template_already_covered(template, normalized_gates):
            continue
        normalized = _normalized_gate_from_template(template)
        normalized = _with_unique_gate_id(normalized, used_gate_ids)
        used_gate_ids.add(normalized.gate_id)
        normalized_gates.append(normalized)

    normalized_gates = sorted(
        normalized_gates,
        key=lambda gate: (
            0 if gate.required else 1,
            {"high": 0, "normal": 1, "low": 2}.get(gate.priority, 1),
            gate.gate_id,
        ),
    )
    return GatePlanContract(
        plan_id=_plan_id(domain_profile=domain_profile, proposal_id=proposal_contract.proposal_id),
        domain_profile=domain_profile,
        gates=normalized_gates,
        policy_warnings=warnings,
        proposal_id=proposal_contract.proposal_id,
        required_gate_count=sum(1 for gate in normalized_gates if gate.required),
        optional_gate_count=sum(1 for gate in normalized_gates if not gate.required),
    )


def _normalize_one_gate(
    gate: GateProposalGateContract,
    *,
    proposal: GateProposalContract,
    warnings: list[GatePolicyWarningContract],
    fallback_index: int,
) -> NormalizedQualityGateContract | None:
    raw_gate_type = _normalize_token(gate.gate_type)
    gate_label = _clean_text(gate.label) or _clean_text(gate.target_label) or raw_gate_type or f"gate {fallback_index}"
    if _contains_raw_blender_instruction(gate_label, gate.rationale, gate.target_label, *gate.target_objects):
        warnings.append(
            _warning(
                "raw_blender_instruction",
                "Gate proposal contains raw Blender/Python instructions; dropping the gate declaration.",
                gate,
                field="label",
                action="dropped",
            )
        )
        return None

    if raw_gate_type not in _GATE_TYPES:
        warnings.append(
            _warning(
                "unsupported_gate_type",
                f"Gate type '{gate.gate_type}' is not supported by the quality-gate vocabulary.",
                gate,
                field="gate_type",
                action="dropped",
            )
        )
        return None
    gate_type = cast(GateTypeLiteral, raw_gate_type)

    priority = _normalize_token(gate.priority or "normal")
    if priority not in _PRIORITIES:
        warnings.append(
            _warning(
                "unsupported_priority",
                f"Gate priority '{gate.priority}' is not supported; using 'normal'.",
                gate,
                field="priority",
                action="rewritten",
            )
        )
        priority = "normal"

    raw_status = _normalize_token(gate.status or "proposed")
    if raw_status in _GATE_STATUSES:
        warnings.append(
            _warning(
                "unsupported_completion_status",
                f"Client-supplied completion status '{gate.status}' is advisory only; normalized gates start as pending.",
                gate,
                field="status",
                action="rewritten",
            )
        )
    elif raw_status not in _DECLARATION_STATUSES:
        warnings.append(
            _warning(
                "unsupported_proposal_status",
                f"Gate proposal status '{gate.status}' is not supported; normalized gates start as pending.",
                gate,
                field="status",
                action="rewritten",
            )
        )

    allowed_correction_families = _normalize_correction_families(gate, gate_type=gate_type, warnings=warnings)
    evidence_requirements = _normalize_evidence_requirements(gate, gate_type=gate_type, warnings=warnings)
    provenance = _normalize_source_provenance(
        source=proposal.source,
        proposal_provenance=proposal.source_provenance,
        gate_provenance=gate.source_provenance,
    )
    target_objects = _normalize_target_objects(gate)
    return NormalizedQualityGateContract(
        gate_id=_candidate_gate_id(gate, gate_type=gate_type, fallback_index=fallback_index),
        gate_type=gate_type,
        label=gate_label,
        target_kind=gate.target_kind if gate.target_kind in _TARGET_KINDS else "unknown",
        target_label=_clean_text(gate.target_label),
        target_objects=target_objects,
        required=gate.required,
        priority=cast(GatePriorityLiteral, priority),
        status="pending",
        verification_strategy=_VERIFICATION_STRATEGY_BY_GATE_TYPE[gate_type],
        allowed_correction_families=allowed_correction_families,
        proposal_sources=[proposal.source],
        source_provenance=provenance,
        evidence_requirements=evidence_requirements,
        evidence_refs=[],
        rationale=_clean_text(gate.rationale),
    )


def _normalize_correction_families(
    gate: GateProposalGateContract,
    *,
    gate_type: GateTypeLiteral,
    warnings: list[GatePolicyWarningContract],
) -> list[GuidedFlowFamilyLiteral]:
    families: list[GuidedFlowFamilyLiteral] = []
    seen: set[str] = set()
    for raw_family in gate.allowed_correction_families:
        family = _normalize_token(raw_family)
        if family in _CORRECTION_FAMILIES:
            if family not in seen:
                seen.add(family)
                families.append(cast(GuidedFlowFamilyLiteral, family))
            continue
        warning_code: GatePolicyWarningCodeLiteral = (
            "hidden_tool_requirement" if _looks_like_tool_name(family) else "unsupported_correction_family"
        )
        warnings.append(
            _warning(
                warning_code,
                f"Correction family '{raw_family}' is not a supported guided family and was dropped.",
                gate,
                field="allowed_correction_families",
                action="dropped",
            )
        )
    if families:
        return families
    return list(_CORRECTION_FAMILIES_BY_GATE_TYPE[gate_type])


def _normalize_evidence_requirements(
    gate: GateProposalGateContract,
    *,
    gate_type: GateTypeLiteral,
    warnings: list[GatePolicyWarningContract],
) -> list[GateEvidenceRequirementContract]:
    if not gate.evidence_requirements:
        return [
            GateEvidenceRequirementContract(evidence_kind=evidence_kind, required=True)
            for evidence_kind in _EVIDENCE_REQUIREMENTS_BY_GATE_TYPE[gate_type]
        ]

    requirements: list[GateEvidenceRequirementContract] = []
    for raw_requirement in gate.evidence_requirements:
        requirement_payload = (
            {"evidence_kind": raw_requirement}
            if isinstance(raw_requirement, str)
            else raw_requirement
            if isinstance(raw_requirement, Mapping)
            else None
        )
        if requirement_payload is None:
            warnings.append(
                _warning(
                    "unsupported_evidence_kind",
                    "Evidence requirement must be a string evidence kind or object payload; dropping it.",
                    gate,
                    field="evidence_requirements",
                    action="dropped",
                )
            )
            continue
        evidence_kind = _normalize_token(requirement_payload.get("evidence_kind"))
        if evidence_kind not in _EVIDENCE_KINDS:
            warnings.append(
                _warning(
                    "unsupported_evidence_kind",
                    f"Evidence kind '{requirement_payload.get('evidence_kind')}' is not supported and was dropped.",
                    gate,
                    field="evidence_requirements",
                    action="dropped",
                )
            )
            continue
        requirements.append(
            GateEvidenceRequirementContract(
                evidence_kind=cast(GateEvidenceKindLiteral, evidence_kind),
                required=bool(requirement_payload.get("required", True)),
                reason=_clean_text(requirement_payload.get("reason")),
            )
        )
    return requirements or [
        GateEvidenceRequirementContract(evidence_kind=evidence_kind, required=True)
        for evidence_kind in _EVIDENCE_REQUIREMENTS_BY_GATE_TYPE[gate_type]
    ]


def _normalized_gate_from_template(template: DomainQualityGateTemplateContract) -> NormalizedQualityGateContract:
    evidence_requirements = template.evidence_requirements or [
        GateEvidenceRequirementContract(evidence_kind=evidence_kind, required=True)
        for evidence_kind in _EVIDENCE_REQUIREMENTS_BY_GATE_TYPE[template.gate_type]
    ]
    allowed_correction_families = template.allowed_correction_families or list(
        _CORRECTION_FAMILIES_BY_GATE_TYPE[template.gate_type]
    )
    return NormalizedQualityGateContract(
        gate_id=template.gate_id,
        gate_type=template.gate_type,
        label=template.label,
        target_kind=template.target_kind,
        target_label=template.target_label,
        target_objects=template.target_objects,
        required=template.required,
        priority=template.priority,
        status="pending",
        verification_strategy=template.verification_strategy or _VERIFICATION_STRATEGY_BY_GATE_TYPE[template.gate_type],
        allowed_correction_families=allowed_correction_families,
        proposal_sources=["domain_template"],
        source_provenance=[
            GateSourceProvenanceContract(
                source="domain_template",
                source_id=f"{template.domain_profile}:{template.gate_id}",
                summary=template.label,
            )
        ],
        evidence_requirements=evidence_requirements,
        evidence_refs=[],
    )


def _template_already_covered(
    template: DomainQualityGateTemplateContract,
    normalized_gates: list[NormalizedQualityGateContract],
) -> bool:
    template_key = _gate_match_key(
        gate_type=template.gate_type,
        target_label=template.target_label,
        target_objects=template.target_objects,
        target_kind=template.target_kind,
    )
    return any(
        _gate_match_key(
            gate_type=gate.gate_type,
            target_label=gate.target_label,
            target_objects=gate.target_objects,
            target_kind=gate.target_kind,
        )
        == template_key
        for gate in normalized_gates
    )


def _normalize_source_provenance(
    *,
    source: GateProposalSourceLiteral,
    proposal_provenance: list[GateSourceProvenanceContract],
    gate_provenance: list[GateSourceProvenanceContract],
) -> list[GateSourceProvenanceContract]:
    provenance = list(proposal_provenance)
    provenance.extend(gate_provenance)
    if provenance:
        return provenance
    return [GateSourceProvenanceContract(source=source)]


def _normalize_target_objects(gate: GateProposalGateContract) -> list[str]:
    names = [_clean_text(gate.target_object), *(_clean_text(item) for item in gate.target_objects)]
    cleaned = [name for name in names if name]
    seen: set[str] = set()
    result: list[str] = []
    for name in cleaned:
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(name)
    return result


def _candidate_gate_id(
    gate: GateProposalGateContract,
    *,
    gate_type: GateTypeLiteral,
    fallback_index: int,
) -> str:
    raw_id = _clean_text(gate.gate_id)
    if raw_id:
        return _slug(raw_id)
    base = _clean_text(gate.target_label) or _clean_text(gate.label) or f"gate_{fallback_index}"
    return _slug(f"{gate_type}_{base}")


def _with_unique_gate_id(
    gate: NormalizedQualityGateContract,
    used_gate_ids: set[str],
) -> NormalizedQualityGateContract:
    if gate.gate_id not in used_gate_ids:
        return gate
    index = 2
    candidate = f"{gate.gate_id}_{index}"
    while candidate in used_gate_ids:
        index += 1
        candidate = f"{gate.gate_id}_{index}"
    return gate.model_copy(update={"gate_id": candidate})


def _gate_match_key(
    *,
    gate_type: GateTypeLiteral,
    target_label: str | None,
    target_objects: list[str],
    target_kind: GateTargetKindLiteral,
) -> tuple[str, str, tuple[str, ...], str]:
    return (
        gate_type,
        _normalize_token(target_label or ""),
        tuple(sorted(_normalize_token(item) for item in target_objects if item)),
        target_kind,
    )


def _warning(
    code: GatePolicyWarningCodeLiteral,
    message: str,
    gate: GateProposalGateContract,
    *,
    field: str,
    action: Literal["dropped", "rewritten", "ignored"],
) -> GatePolicyWarningContract:
    return GatePolicyWarningContract(
        code=code,
        message=message,
        action=action,
        gate_id=_clean_text(gate.gate_id),
        gate_label=_clean_text(gate.label) or _clean_text(gate.target_label),
        field=field,
    )


def _plan_id(*, domain_profile: GuidedFlowDomainProfileLiteral, proposal_id: str | None) -> str:
    if proposal_id:
        return _slug(f"{domain_profile}_{proposal_id}")
    return f"{domain_profile}_quality_gate_plan"


def _contains_raw_blender_instruction(*values: object) -> bool:
    text = " ".join(str(value or "").lower() for value in values)
    return any(pattern in text for pattern in _RAW_BLENDER_PATTERNS)


def _looks_like_tool_name(value: str) -> bool:
    return value.startswith(_TOOL_NAME_PREFIXES) or value.startswith("macro_")


def _clean_text(value: object) -> str | None:
    text = str(value or "").strip()
    return text or None


def _normalize_token(value: object) -> str:
    return str(value or "").strip().lower().replace("-", "_").replace(" ", "_")


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_]+", "_", value.strip().lower())
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug or "quality_gate"
