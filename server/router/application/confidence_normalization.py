"""Normalization helpers for matcher, override, and firewall confidence signals."""

from __future__ import annotations

from server.router.domain.entities.confidence_policy import (
    ConfidenceBand,
    NormalizedConfidence,
    confidence_band_from_score,
)
from server.router.domain.entities.correction_policy import (
    CorrectionRisk,
    classify_firewall_action,
    classify_override_rule,
)
from server.router.domain.entities.ensemble import EnsembleResult
from server.router.application.matcher.semantic_workflow_matcher import MatchResult


_WORKFLOW_CONFIDENCE_BANDS = {
    "HIGH": ConfidenceBand.HIGH,
    "MEDIUM": ConfidenceBand.MEDIUM,
    "LOW": ConfidenceBand.LOW,
    "NONE": ConfidenceBand.NONE,
}


def normalize_semantic_match(match: MatchResult) -> NormalizedConfidence:
    """Normalize semantic workflow match confidence into one shared envelope."""

    return NormalizedConfidence(
        source="semantic_matcher",
        score=match.confidence,
        band=_WORKFLOW_CONFIDENCE_BANDS.get(match.confidence_level, confidence_band_from_score(match.confidence)),
        risk=CorrectionRisk.HIGH if match.match_type in {"semantic", "generalized"} else CorrectionRisk.MEDIUM,
        rationale=f"Semantic workflow match ({match.match_type})",
        metadata={
            "workflow_name": match.workflow_name,
            "match_type": match.match_type,
            "requires_adaptation": match.requires_adaptation,
        },
    )


def normalize_ensemble_result(result: EnsembleResult) -> NormalizedConfidence:
    """Normalize ensemble aggregation confidence into one shared envelope."""

    return NormalizedConfidence(
        source="ensemble_aggregator",
        score=result.final_score,
        band=_WORKFLOW_CONFIDENCE_BANDS.get(result.confidence_level, confidence_band_from_score(result.final_score)),
        risk=CorrectionRisk.HIGH if result.composition_mode else CorrectionRisk.MEDIUM,
        rationale="Aggregated matcher consensus",
        metadata={
            "workflow_name": result.workflow_name,
            "confidence_level": result.confidence_level,
            "requires_adaptation": result.requires_adaptation,
            "composition_mode": result.composition_mode,
        },
    )


def normalize_workflow_match_confidence(
    *,
    workflow_name: str | None,
    confidence_level: str | None,
    requires_adaptation: bool,
) -> NormalizedConfidence:
    """Normalize coarse workflow match state when only a confidence band is available."""

    band = _WORKFLOW_CONFIDENCE_BANDS.get(confidence_level or "NONE", ConfidenceBand.NONE)
    score = {
        ConfidenceBand.HIGH: 0.9,
        ConfidenceBand.MEDIUM: 0.7,
        ConfidenceBand.LOW: 0.3,
        ConfidenceBand.NONE: 0.0,
    }[band]
    return NormalizedConfidence(
        source="workflow_match",
        score=score,
        band=band,
        risk=CorrectionRisk.HIGH if requires_adaptation else CorrectionRisk.MEDIUM,
        rationale="Workflow match confidence classification",
        metadata={
            "workflow_name": workflow_name,
            "confidence_level": confidence_level,
            "requires_adaptation": requires_adaptation,
        },
    )


def normalize_override_decision(rule_name: str, should_override: bool) -> NormalizedConfidence:
    """Normalize override engine confidence into one shared envelope."""

    classification = classify_override_rule(rule_name)
    score = 1.0 if should_override else 0.0
    return NormalizedConfidence(
        source="override_engine",
        score=score,
        band=confidence_band_from_score(score),
        risk=classification.risk,
        rationale=f"Override rule '{rule_name}'" if rule_name else "No override rule matched",
        metadata={"rule_name": rule_name, "should_override": should_override},
    )


def normalize_firewall_action(action: str, violation_count: int = 0) -> NormalizedConfidence:
    """Normalize firewall action severity into one shared envelope."""

    classification = classify_firewall_action(action)
    score = {
        "allow": 1.0,
        "auto_fix": 0.7,
        "modify": 0.5,
        "block": 0.0,
    }.get(action, 0.0)
    return NormalizedConfidence(
        source="error_firewall",
        score=score,
        band=confidence_band_from_score(score),
        risk=classification.risk,
        rationale=f"Firewall action '{action}' with {violation_count} violation(s)",
        metadata={"action": action, "violation_count": violation_count},
    )
