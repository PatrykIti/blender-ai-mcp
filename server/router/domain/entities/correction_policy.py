"""Correction taxonomy and blast-radius classification for router safety policy."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class CorrectionCategory(StrEnum):
    """High-level category of a router correction."""

    PRECONDITION_MODE = "precondition_mode"
    PRECONDITION_ACTIVE_OBJECT = "precondition_active_object"
    PRECONDITION_SELECTION = "precondition_selection"
    PARAMETER_ALIAS = "parameter_alias"
    PARAMETER_CLAMP = "parameter_clamp"
    FIREWALL_MODIFICATION = "firewall_modification"
    TOOL_OVERRIDE = "tool_override"
    WORKFLOW_EXPANSION = "workflow_expansion"
    BLOCK = "block"
    UNKNOWN = "unknown"


class CorrectionRisk(StrEnum):
    """Blast-radius level for a correction category."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class CorrectionClassification:
    """Structured classification for one correction signal or rule."""

    category: CorrectionCategory
    risk: CorrectionRisk
    auto_safe: bool
    rationale: str


CORRECTION_MATRIX: dict[CorrectionCategory, CorrectionClassification] = {
    CorrectionCategory.PRECONDITION_MODE: CorrectionClassification(
        category=CorrectionCategory.PRECONDITION_MODE,
        risk=CorrectionRisk.LOW,
        auto_safe=True,
        rationale="Deterministic mode repair with narrow operational blast radius.",
    ),
    CorrectionCategory.PRECONDITION_SELECTION: CorrectionClassification(
        category=CorrectionCategory.PRECONDITION_SELECTION,
        risk=CorrectionRisk.MEDIUM,
        auto_safe=False,
        rationale="Selection injection changes execution target and may affect unintended geometry.",
    ),
    CorrectionCategory.PRECONDITION_ACTIVE_OBJECT: CorrectionClassification(
        category=CorrectionCategory.PRECONDITION_ACTIVE_OBJECT,
        risk=CorrectionRisk.HIGH,
        auto_safe=False,
        rationale="Active-object correction changes which object receives the operation.",
    ),
    CorrectionCategory.PARAMETER_ALIAS: CorrectionClassification(
        category=CorrectionCategory.PARAMETER_ALIAS,
        risk=CorrectionRisk.LOW,
        auto_safe=True,
        rationale="Alias normalization preserves intent while translating to canonical parameter names.",
    ),
    CorrectionCategory.PARAMETER_CLAMP: CorrectionClassification(
        category=CorrectionCategory.PARAMETER_CLAMP,
        risk=CorrectionRisk.MEDIUM,
        auto_safe=False,
        rationale="Clamping changes user-supplied magnitude and can materially alter the resulting shape.",
    ),
    CorrectionCategory.FIREWALL_MODIFICATION: CorrectionClassification(
        category=CorrectionCategory.FIREWALL_MODIFICATION,
        risk=CorrectionRisk.HIGH,
        auto_safe=False,
        rationale="Firewall-driven rewrites protect execution but materially change the requested operation.",
    ),
    CorrectionCategory.TOOL_OVERRIDE: CorrectionClassification(
        category=CorrectionCategory.TOOL_OVERRIDE,
        risk=CorrectionRisk.HIGH,
        auto_safe=False,
        rationale="Tool substitution replaces the requested action with a different execution path.",
    ),
    CorrectionCategory.WORKFLOW_EXPANSION: CorrectionClassification(
        category=CorrectionCategory.WORKFLOW_EXPANSION,
        risk=CorrectionRisk.HIGH,
        auto_safe=False,
        rationale="Workflow expansion fans a single intent into multiple steps with broad scene impact.",
    ),
    CorrectionCategory.BLOCK: CorrectionClassification(
        category=CorrectionCategory.BLOCK,
        risk=CorrectionRisk.CRITICAL,
        auto_safe=False,
        rationale="Blocking indicates unsafe or unacceptable execution conditions.",
    ),
    CorrectionCategory.UNKNOWN: CorrectionClassification(
        category=CorrectionCategory.UNKNOWN,
        risk=CorrectionRisk.HIGH,
        auto_safe=False,
        rationale="Unknown correction types should not be auto-applied without explicit review.",
    ),
}


def get_correction_classification(category: CorrectionCategory) -> CorrectionClassification:
    """Return the configured risk classification for a correction category."""

    return CORRECTION_MATRIX[category]


def classify_correction_token(token: str) -> CorrectionClassification:
    """Classify a correction token emitted by correction / firewall layers."""

    if token.startswith("mode_switch:") or token == "injected_mode_switch":
        return get_correction_classification(CorrectionCategory.PRECONDITION_MODE)
    if token.startswith("active_object_switch:") or token == "injected_active_object":
        return get_correction_classification(CorrectionCategory.PRECONDITION_ACTIVE_OBJECT)
    if token == "auto_select_all" or token == "injected_selection":
        return get_correction_classification(CorrectionCategory.PRECONDITION_SELECTION)
    if token.startswith("alias_"):
        return get_correction_classification(CorrectionCategory.PARAMETER_ALIAS)
    if token.startswith("clamp_"):
        return get_correction_classification(CorrectionCategory.PARAMETER_CLAMP)
    if token.startswith("override:"):
        return get_correction_classification(CorrectionCategory.TOOL_OVERRIDE)
    if token.startswith("workflow:"):
        return get_correction_classification(CorrectionCategory.WORKFLOW_EXPANSION)
    if token in {"firewall_auto_fix", "firewall_modified"}:
        return get_correction_classification(CorrectionCategory.FIREWALL_MODIFICATION)
    return get_correction_classification(CorrectionCategory.UNKNOWN)


def classify_firewall_action(action: str) -> CorrectionClassification:
    """Classify the blast radius of a firewall action."""

    if action == "block":
        return get_correction_classification(CorrectionCategory.BLOCK)
    if action in {"auto_fix", "modify"}:
        return get_correction_classification(CorrectionCategory.FIREWALL_MODIFICATION)
    return get_correction_classification(CorrectionCategory.UNKNOWN)


def classify_override_rule(rule_name: str) -> CorrectionClassification:
    """Classify override rules emitted by the override engine."""

    if rule_name:
        return get_correction_classification(CorrectionCategory.TOOL_OVERRIDE)
    return get_correction_classification(CorrectionCategory.UNKNOWN)
