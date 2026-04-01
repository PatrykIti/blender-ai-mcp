"""Tests for auto-fix / ask / block policy decisions."""

from server.router.application.policy.correction_policy_engine import (
    CorrectionPolicyEngine,
    PolicyDecision,
)
from server.router.domain.entities.confidence_policy import ConfidenceBand, NormalizedConfidence
from server.router.domain.entities.correction_policy import CorrectionRisk


def make_confidence(
    *,
    score: float,
    band: ConfidenceBand,
    risk: CorrectionRisk,
) -> NormalizedConfidence:
    return NormalizedConfidence(
        source="test",
        score=score,
        band=band,
        risk=risk,
        rationale="test",
        metadata={},
    )


def test_policy_engine_auto_fixes_high_confidence_low_risk():
    """High-confidence low-risk deterministic corrections should auto-fix."""

    engine = CorrectionPolicyEngine()
    decision = engine.decide(
        make_confidence(
            score=0.95,
            band=ConfidenceBand.HIGH,
            risk=CorrectionRisk.LOW,
        )
    )

    assert decision.decision == PolicyDecision.AUTO_FIX


def test_policy_engine_asks_for_medium_or_low_confidence_noncritical_paths():
    """Medium/low confidence bounded-risk corrections should ask instead of mutating silently."""

    engine = CorrectionPolicyEngine()

    medium = engine.decide(
        make_confidence(
            score=0.7,
            band=ConfidenceBand.MEDIUM,
            risk=CorrectionRisk.MEDIUM,
        )
    )
    low = engine.decide(
        make_confidence(
            score=0.3,
            band=ConfidenceBand.LOW,
            risk=CorrectionRisk.HIGH,
        )
    )

    assert medium.decision == PolicyDecision.ASK
    assert low.decision == PolicyDecision.ASK


def test_policy_engine_blocks_critical_or_no_confidence_cases():
    """Critical-risk and no-confidence cases must fail closed."""

    engine = CorrectionPolicyEngine()

    critical = engine.decide(
        make_confidence(
            score=0.9,
            band=ConfidenceBand.HIGH,
            risk=CorrectionRisk.CRITICAL,
        )
    )
    none = engine.decide(
        make_confidence(
            score=0.0,
            band=ConfidenceBand.NONE,
            risk=CorrectionRisk.HIGH,
        )
    )

    assert critical.decision == PolicyDecision.BLOCK
    assert none.decision == PolicyDecision.BLOCK


def test_policy_decision_exposes_operator_trace_fields():
    """Policy decisions should expose stable operator-facing transparency fields."""

    engine = CorrectionPolicyEngine()
    decision = engine.decide(
        make_confidence(
            score=0.7,
            band=ConfidenceBand.MEDIUM,
            risk=CorrectionRisk.MEDIUM,
        )
    )

    trace = decision.to_dict()

    assert trace["decision"] == "ask"
    assert trace["source"] == "test"
    assert trace["band"] == "medium"
    assert trace["risk"] == "medium"
