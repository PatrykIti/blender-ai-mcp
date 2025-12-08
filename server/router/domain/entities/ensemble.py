"""
Ensemble Matcher Domain Entities.

TASK-053-1: Domain entities for ensemble matching system.

These entities support the new ensemble matcher that runs all matchers
(keyword, semantic, pattern) in parallel and aggregates results using
weighted consensus.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class MatcherResult:
    """Result from a single matcher (individual matcher output).

    NOTE: This is different from existing MatchResult in semantic_workflow_matcher.py.
    MatchResult = final result from SemanticWorkflowMatcher
    MatcherResult = intermediate result from individual IMatcher

    Attributes:
        matcher_name: Name of the matcher (e.g., "keyword", "semantic", "pattern").
        workflow_name: Name of matched workflow (or None if no match).
        confidence: Match confidence score (0.0 to 1.0).
        weight: Matcher's weight for aggregation.
        metadata: Additional metadata about the match.
    """

    matcher_name: str
    workflow_name: Optional[str]
    confidence: float
    weight: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate field values."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        if not 0.0 <= self.weight <= 1.0:
            raise ValueError(f"Weight must be between 0.0 and 1.0, got {self.weight}")

    @property
    def weighted_score(self) -> float:
        """Calculate weighted score (confidence × weight)."""
        return self.confidence * self.weight

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "matcher_name": self.matcher_name,
            "workflow_name": self.workflow_name,
            "confidence": self.confidence,
            "weight": self.weight,
            "weighted_score": self.weighted_score,
            "metadata": self.metadata,
        }


@dataclass
class ModifierResult:
    """Extracted modifiers from user prompt.

    Attributes:
        modifiers: Dictionary of variable overrides (e.g., {"leg_angle_left": 0}).
        matched_keywords: List of matched modifier keywords from prompt.
        confidence_map: Confidence score for each matched keyword.
    """

    modifiers: Dict[str, Any]
    matched_keywords: List[str]
    confidence_map: Dict[str, float]

    def has_modifiers(self) -> bool:
        """Check if any modifiers were extracted."""
        return len(self.modifiers) > 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "modifiers": self.modifiers,
            "matched_keywords": self.matched_keywords,
            "confidence_map": self.confidence_map,
            "has_modifiers": self.has_modifiers(),
        }


@dataclass
class EnsembleResult:
    """Aggregated result from all matchers.

    This is the NEW primary result type for workflow matching.
    Replaces MatchResult as the output of the matching pipeline.

    Attributes:
        workflow_name: Name of matched workflow (or None if no match).
        final_score: Aggregated score from all matchers.
        confidence_level: Confidence classification (HIGH, MEDIUM, LOW, NONE).
        modifiers: Extracted parametric modifiers (ALWAYS populated by ModifierExtractor).
        matcher_contributions: Weighted score contribution from each matcher.
        requires_adaptation: True if workflow needs adaptation based on confidence.
        composition_mode: True if multiple workflows should be combined.
        extra_workflows: Additional workflows for composition mode.
    """

    workflow_name: Optional[str]
    final_score: float
    confidence_level: str
    modifiers: Dict[str, Any]
    matcher_contributions: Dict[str, float]
    requires_adaptation: bool
    composition_mode: bool = False
    extra_workflows: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate field values."""
        if not 0.0 <= self.final_score:
            raise ValueError(f"Final score must be >= 0.0, got {self.final_score}")

        valid_levels = {"HIGH", "MEDIUM", "LOW", "NONE"}
        if self.confidence_level not in valid_levels:
            raise ValueError(
                f"Confidence level must be one of {valid_levels}, got {self.confidence_level}"
            )

    @property
    def confidence(self) -> float:
        """Alias for final_score (backward compatibility).

        This allows EnsembleResult to be used wherever MatchResult
        was previously used, since both have .confidence property.
        """
        return self.final_score

    def is_match(self) -> bool:
        """Check if a match was found."""
        return self.workflow_name is not None and self.final_score > 0

    def needs_adaptation(self) -> bool:
        """Check if workflow needs adaptation based on confidence.

        TASK-051: Only HIGH confidence matches get full workflow.
        MEDIUM/LOW confidence matches require adaptation.
        """
        return self.requires_adaptation and self.confidence_level != "HIGH"

    def has_modifiers(self) -> bool:
        """Check if any modifiers were extracted."""
        return len(self.modifiers) > 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "workflow_name": self.workflow_name,
            "final_score": self.final_score,
            "confidence_level": self.confidence_level,
            "modifiers": self.modifiers,
            "matcher_contributions": self.matcher_contributions,
            "requires_adaptation": self.requires_adaptation,
            "composition_mode": self.composition_mode,
            "extra_workflows": self.extra_workflows,
            "has_modifiers": self.has_modifiers(),
        }
