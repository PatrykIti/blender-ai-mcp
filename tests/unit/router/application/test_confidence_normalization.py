"""Tests for confidence scoring normalization across engines."""

from server.router.application.confidence_normalization import (
    normalize_ensemble_result,
    normalize_firewall_action,
    normalize_override_decision,
    normalize_semantic_match,
)
from server.router.application.matcher.semantic_workflow_matcher import MatchResult
from server.router.domain.entities.confidence_policy import ConfidenceBand
from server.router.domain.entities.correction_policy import CorrectionRisk
from server.router.domain.entities.ensemble import EnsembleResult


def test_semantic_and_ensemble_confidence_normalize_to_shared_bands():
    """Semantic and ensemble outputs should map into one normalized confidence model."""

    semantic = normalize_semantic_match(
        MatchResult(
            workflow_name="chair_workflow",
            confidence=0.82,
            match_type="semantic",
            confidence_level="MEDIUM",
            requires_adaptation=True,
        )
    )
    ensemble = normalize_ensemble_result(
        EnsembleResult(
            workflow_name="chair_workflow",
            final_score=0.82,
            confidence_level="MEDIUM",
            modifiers={},
            matcher_contributions={"semantic": 0.4},
            requires_adaptation=True,
        )
    )

    assert semantic.band == ConfidenceBand.MEDIUM
    assert ensemble.band == ConfidenceBand.MEDIUM


def test_override_and_firewall_normalize_to_policy_ready_envelopes():
    """Override and firewall actions should map into the same normalized envelope shape."""

    override = normalize_override_decision("extrude_for_screen", True)
    firewall = normalize_firewall_action("block", violation_count=1)

    assert override.risk == CorrectionRisk.HIGH
    assert override.band == ConfidenceBand.HIGH
    assert firewall.risk == CorrectionRisk.CRITICAL
    assert firewall.band == ConfidenceBand.NONE


def test_missing_or_negative_signals_fail_closed():
    """Unknown or empty signals should normalize deterministically to low/none confidence."""

    no_override = normalize_override_decision("", False)
    modified = normalize_firewall_action("modify", violation_count=2)

    assert no_override.band == ConfidenceBand.NONE
    assert modified.band == ConfidenceBand.LOW
