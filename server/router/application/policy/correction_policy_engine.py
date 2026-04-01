"""Policy engine for auto-fix, ask, or block correction decisions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from server.router.domain.entities.confidence_policy import ConfidenceBand, NormalizedConfidence
from server.router.domain.entities.correction_policy import CorrectionRisk


class PolicyDecision(StrEnum):
    """Allowed policy outcomes for a correction path."""

    AUTO_FIX = "auto_fix"
    ASK = "ask"
    BLOCK = "block"


@dataclass(frozen=True)
class CorrectionPolicyDecision:
    """One explicit policy decision with rationale and provenance."""

    decision: PolicyDecision
    reason: str
    confidence: NormalizedConfidence

    def to_dict(self) -> dict:
        """Return a serializable operator-facing policy trace."""

        return {
            "decision": self.decision.value,
            "reason": self.reason,
            "source": self.confidence.source,
            "score": self.confidence.score,
            "band": self.confidence.band.value,
            "risk": self.confidence.risk.value,
            "metadata": self.confidence.metadata,
        }


class CorrectionPolicyEngine:
    """Maps normalized confidence + risk into auto-fix / ask / block."""

    def decide(self, confidence: NormalizedConfidence) -> CorrectionPolicyDecision:
        """Return the explicit policy decision for one normalized confidence signal."""

        risk = confidence.risk
        band = confidence.band

        if risk == CorrectionRisk.LOW and band == ConfidenceBand.HIGH:
            return CorrectionPolicyDecision(
                decision=PolicyDecision.AUTO_FIX,
                reason="High-confidence low-risk deterministic correction",
                confidence=confidence,
            )

        if risk == CorrectionRisk.CRITICAL:
            return CorrectionPolicyDecision(
                decision=PolicyDecision.BLOCK,
                reason="Critical-risk correction must not run automatically",
                confidence=confidence,
            )

        if band in {ConfidenceBand.MEDIUM, ConfidenceBand.LOW}:
            return CorrectionPolicyDecision(
                decision=PolicyDecision.ASK,
                reason="Ambiguous or bounded-risk correction should be clarified",
                confidence=confidence,
            )

        return CorrectionPolicyDecision(
            decision=PolicyDecision.BLOCK,
            reason="No-confidence or high-risk correction must not run automatically",
            confidence=confidence,
        )
