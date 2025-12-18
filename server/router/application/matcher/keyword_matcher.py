"""
Keyword Matcher for Ensemble Matching System.

TASK-053-3: Extracts keyword matching logic from SemanticWorkflowMatcher
into standalone matcher implementing IMatcher interface.

Uses WorkflowRegistry.find_by_keywords() for exact keyword matching.
"""

from typing import Dict, Any, Optional, TYPE_CHECKING

from server.router.domain.interfaces.matcher import IMatcher
from server.router.domain.entities.ensemble import MatcherResult

if TYPE_CHECKING:
    from server.router.application.workflows.registry import WorkflowRegistry


class KeywordMatcher(IMatcher):
    """Matches workflows by trigger keywords.

    Extracts keyword matching logic from SemanticWorkflowMatcher.
    Uses WorkflowRegistry.find_by_keywords() for matching.

    This is the most precise matcher with low false positive rate.
    When a keyword match occurs, confidence is always 1.0 (exact match).

    Example:
        >>> matcher = KeywordMatcher(registry, weight=0.40)
        >>> result = matcher.match("create a smartphone")
        >>> print(result.workflow_name)  # "phone_workflow"
        >>> print(result.confidence)      # 1.0
    """

    def __init__(self, registry: "WorkflowRegistry", weight: float = 0.40):
        """Initialize keyword matcher.

        Args:
            registry: Workflow registry for keyword lookup.
            weight: Weight for ensemble aggregation (default 0.40).
                   Higher weight = more influence on final decision.
        """
        self._registry = registry
        self._weight = weight

    @property
    def name(self) -> str:
        """Matcher name for logging and aggregation.

        Returns:
            "keyword"
        """
        return "keyword"

    @property
    def weight(self) -> float:
        """Weight for score aggregation.

        Standard weight: 0.40 (most precise matcher).

        Returns:
            Weight value between 0.0 and 1.0.
        """
        return self._weight

    def match(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> MatcherResult:
        """Match prompt by keywords.

        Delegates to WorkflowRegistry.find_by_keywords().
        Returns confidence 1.0 for exact keyword matches.

        Args:
            prompt: User prompt/goal (e.g., "create a smartphone").
            context: Optional scene context (not used by keyword matcher).

        Returns:
            MatcherResult with workflow name and confidence 1.0 if matched,
            or MatcherResult with workflow_name=None and confidence=0.0 if no match.

        Example:
            >>> result = matcher.match("create a smartphone")
            >>> result.workflow_name  # "phone_workflow"
            >>> result.confidence     # 1.0
            >>> result.weighted_score # 0.40 (1.0 × 0.40)
        """
        # Delegate to registry for keyword matching
        workflow_name = self._registry.find_by_keywords(prompt)

        if workflow_name:
            return MatcherResult(
                matcher_name=self.name,
                workflow_name=workflow_name,
                confidence=1.0,  # Exact keyword match = full confidence
                weight=self.weight,
                metadata={"matched_by": "keyword"}
            )

        # No keyword match found
        return MatcherResult(
            matcher_name=self.name,
            workflow_name=None,
            confidence=0.0,
            weight=self.weight
        )
