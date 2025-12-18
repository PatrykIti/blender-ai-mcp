"""
Pattern Matcher for Ensemble Matching System.

TASK-053-5: Extracts pattern matching logic from SemanticWorkflowMatcher
into standalone matcher implementing IMatcher interface.

Matches workflows by detected geometry patterns in the scene.
"""

from typing import Dict, Any, Optional, TYPE_CHECKING
import logging

from server.router.domain.interfaces.matcher import IMatcher
from server.router.domain.entities.ensemble import MatcherResult

if TYPE_CHECKING:
    from server.router.application.workflows.registry import WorkflowRegistry

logger = logging.getLogger(__name__)


class PatternMatcher(IMatcher):
    """Matches workflows by geometry patterns in scene.

    Extracts pattern matching from SemanticWorkflowMatcher._match_by_pattern().
    Checks context for detected_pattern and matches to workflow.

    This matcher is geometry-aware and provides very confident matches
    when triggered (confidence 0.95).

    Requires context with 'detected_pattern' key from GeometryPatternDetector.

    Example:
        >>> matcher = PatternMatcher(registry, weight=0.15)
        >>> context = {"detected_pattern": "phone_like"}
        >>> result = matcher.match("create object", context)
        >>> print(result.workflow_name)  # "phone_workflow"
        >>> print(result.confidence)      # 0.95
    """

    def __init__(self, registry: "WorkflowRegistry", weight: float = 0.15):
        """Initialize pattern matcher.

        Args:
            registry: Workflow registry for pattern lookup.
            weight: Weight for ensemble aggregation (default 0.15).
        """
        self._registry = registry
        self._weight = weight

    @property
    def name(self) -> str:
        """Matcher name for logging and aggregation.

        Returns:
            "pattern"
        """
        return "pattern"

    @property
    def weight(self) -> float:
        """Weight for score aggregation.

        Standard weight: 0.15 (geometry-aware, very confident when triggered).

        Returns:
            Weight value between 0.0 and 1.0.
        """
        return self._weight

    def match(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> MatcherResult:
        """Match by detected geometry pattern.

        Requires context with 'detected_pattern' key.
        Returns high confidence (0.95) for pattern matches.

        Args:
            prompt: User prompt (not used for pattern matching).
            context: Scene context dict with 'detected_pattern' key.
                    Example: {"detected_pattern": "phone_like"}

        Returns:
            MatcherResult with workflow name and confidence 0.95 if matched,
            or MatcherResult with workflow_name=None and confidence=0.0 if no match.

        Example:
            >>> context = {"detected_pattern": "tower_like"}
            >>> result = matcher.match("add details", context)
            >>> result.workflow_name  # "tower_workflow"
            >>> result.confidence     # 0.95
            >>> result.weighted_score # 0.1425 (0.95 × 0.15)
        """
        if not context:
            return MatcherResult(
                matcher_name=self.name,
                workflow_name=None,
                confidence=0.0,
                weight=self.weight
            )

        # Check if pattern was detected by GeometryPatternDetector
        detected_pattern = context.get("detected_pattern")
        if not detected_pattern:
            return MatcherResult(
                matcher_name=self.name,
                workflow_name=None,
                confidence=0.0,
                weight=self.weight
            )

        # Lookup workflow by pattern
        workflow_name = self._registry.find_by_pattern(detected_pattern)

        if workflow_name:
            logger.debug(f"Pattern match: {detected_pattern} → {workflow_name}")
            return MatcherResult(
                matcher_name=self.name,
                workflow_name=workflow_name,
                confidence=0.95,  # High confidence for pattern matches
                weight=self.weight,
                metadata={
                    "matched_by": "pattern",
                    "pattern": detected_pattern
                }
            )

        # Pattern detected but no matching workflow
        return MatcherResult(
            matcher_name=self.name,
            workflow_name=None,
            confidence=0.0,
            weight=self.weight,
            metadata={
                "pattern_detected": detected_pattern,
                "no_matching_workflow": True
            }
        )
