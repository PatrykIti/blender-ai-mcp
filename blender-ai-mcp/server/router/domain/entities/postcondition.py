"""Postcondition requirements for high-risk correction families."""

from __future__ import annotations

from dataclasses import dataclass

from server.router.domain.entities.correction_policy import CorrectionCategory


@dataclass(frozen=True)
class PostconditionRequirement:
    """Verification requirement for one correction family."""

    correction_category: CorrectionCategory
    verification_key: str
    reason: str
    required: bool = True
