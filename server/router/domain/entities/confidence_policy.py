"""Normalized confidence envelope for router policy decisions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from server.router.domain.entities.correction_policy import CorrectionRisk


class ConfidenceBand(StrEnum):
    """Normalized confidence classes consumed by policy logic."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


@dataclass(frozen=True)
class NormalizedConfidence:
    """One normalized confidence signal with provenance and risk context."""

    source: str
    score: float
    band: ConfidenceBand
    risk: CorrectionRisk
    rationale: str
    metadata: dict[str, Any]


def confidence_band_from_score(score: float) -> ConfidenceBand:
    """Map raw [0,1] score onto the normalized confidence bands."""

    if score >= 0.85:
        return ConfidenceBand.HIGH
    if score >= 0.6:
        return ConfidenceBand.MEDIUM
    if score > 0.0:
        return ConfidenceBand.LOW
    return ConfidenceBand.NONE
