"""
Semantic Matcher for Ensemble Matching System.

TASK-053-4: Wrapper around WorkflowIntentClassifier for IMatcher interface.

This is a refactor, NOT a replacement. Existing SemanticWorkflowMatcher
is kept for backward compatibility. This new SemanticMatcher is specifically
designed for ensemble matching.
"""

from typing import Dict, Any, Optional, TYPE_CHECKING
import logging

from server.router.domain.interfaces.matcher import IMatcher
from server.router.domain.entities.ensemble import MatcherResult
from server.router.infrastructure.config import RouterConfig

if TYPE_CHECKING:
    from server.router.application.classifier.workflow_intent_classifier import (
        WorkflowIntentClassifier,
    )
    from server.router.application.workflows.registry import WorkflowRegistry

logger = logging.getLogger(__name__)


class SemanticMatcher(IMatcher):
    """Matches workflows using LaBSE embeddings.

    Wrapper around WorkflowIntentClassifier for IMatcher interface.
    Does NOT include keyword matching (that's KeywordMatcher's job).

    This matcher provides flexible, context-aware matching using
    semantic similarity between prompts and workflow descriptions.

    Example:
        >>> matcher = SemanticMatcher(classifier, registry, weight=0.40)
        >>> result = matcher.match("make a mobile device")
        >>> print(result.workflow_name)  # "phone_workflow"
        >>> print(result.confidence)      # 0.84
    """

    def __init__(
        self,
        classifier: "WorkflowIntentClassifier",
        registry: "WorkflowRegistry",
        config: Optional[RouterConfig] = None,
        weight: float = 0.40,
    ):
        """Initialize semantic matcher.

        Args:
            classifier: WorkflowIntentClassifier for semantic matching.
            registry: Workflow registry for workflow info.
            config: Router configuration.
            weight: Weight for ensemble aggregation (default 0.40).
        """
        self._classifier = classifier
        self._registry = registry
        self._config = config or RouterConfig()
        self._weight = weight
        self._is_initialized = False

    @property
    def name(self) -> str:
        """Matcher name for logging and aggregation.

        Returns:
            "semantic"
        """
        return "semantic"

    @property
    def weight(self) -> float:
        """Weight for score aggregation.

        Standard weight: 0.40 (flexible, context-aware).

        Returns:
            Weight value between 0.0 and 1.0.
        """
        return self._weight

    def initialize(self, registry: "WorkflowRegistry") -> None:
        """Initialize embeddings for all workflows.

        Must be called before matching.

        Args:
            registry: Workflow registry containing workflows to index.
        """
        workflows = {}
        for name in registry.get_all_workflows():
            workflow = registry.get_workflow(name)
            if workflow:
                workflows[name] = workflow
            else:
                definition = registry.get_definition(name)
                if definition:
                    workflows[name] = definition

        self._classifier.load_workflow_embeddings(workflows)
        self._is_initialized = True
        logger.info(f"SemanticMatcher initialized with {len(workflows)} workflows")

    def is_initialized(self) -> bool:
        """Check if matcher is initialized.

        Returns:
            True if initialize() was called, False otherwise.
        """
        return self._is_initialized

    def match(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> MatcherResult:
        """Match prompt using semantic similarity.

        Uses LaBSE embeddings via WorkflowIntentClassifier.
        Does NOT check keywords (that's KeywordMatcher's responsibility).

        Args:
            prompt: User prompt/goal (e.g., "make a mobile device").
            context: Optional scene context (not used by semantic matcher).

        Returns:
            MatcherResult with workflow name and confidence if matched,
            or MatcherResult with workflow_name=None and confidence=0.0 if no match.

        Example:
            >>> result = matcher.match("create a mobile phone")
            >>> result.workflow_name  # "phone_workflow"
            >>> result.confidence     # 0.84
            >>> result.weighted_score # 0.336 (0.84 × 0.40)
        """
        if not self._is_initialized:
            logger.warning("SemanticMatcher not initialized, returning no match")
            return MatcherResult(
                matcher_name=self.name,
                workflow_name=None,
                confidence=0.0,
                weight=self.weight,
                metadata={"error": "Not initialized"}
            )

        # Use classifier's find_best_match_with_confidence
        result = self._classifier.find_best_match_with_confidence(prompt)

        workflow_id = result.get("workflow_id")
        score = result.get("score", 0.0)
        confidence_level = result.get("confidence_level", "NONE")

        # Only return match if above threshold and not NONE
        if workflow_id and confidence_level != "NONE":
            return MatcherResult(
                matcher_name=self.name,
                workflow_name=workflow_id,
                confidence=score,
                weight=self.weight,
                metadata={
                    "confidence_level": confidence_level,
                    "source_type": result.get("source_type"),
                    "matched_text": result.get("matched_text"),
                    "language_detected": result.get("language_detected"),
                }
            )

        # No match above threshold
        return MatcherResult(
            matcher_name=self.name,
            workflow_name=None,
            confidence=0.0,
            weight=self.weight,
            metadata={"confidence_level": confidence_level}
        )
