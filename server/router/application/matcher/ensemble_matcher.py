"""
Ensemble Matcher for Ensemble Matching System.

TASK-053-8: Main orchestrator that runs all matchers and aggregates results.

Replaces the fallback-based SemanticWorkflowMatcher.match() flow with
parallel ensemble matching.
"""

from typing import List, Optional, Dict, Any, TYPE_CHECKING
import logging

from server.router.domain.interfaces.matcher import IMatcher
from server.router.domain.entities.ensemble import MatcherResult, EnsembleResult
from server.router.domain.entities.scene_context import SceneContext
from server.router.application.matcher.keyword_matcher import KeywordMatcher
from server.router.application.matcher.semantic_matcher import SemanticMatcher
from server.router.application.matcher.pattern_matcher import PatternMatcher
from server.router.application.matcher.ensemble_aggregator import EnsembleAggregator
from server.router.infrastructure.config import RouterConfig
from server.router.infrastructure.logger import RouterLogger

if TYPE_CHECKING:
    from server.router.application.workflows.registry import WorkflowRegistry

logger = logging.getLogger(__name__)


class EnsembleMatcher:
    """Orchestrates parallel matching using multiple matchers.

    Runs all matchers (keyword, semantic, pattern) and aggregates
    results using EnsembleAggregator for weighted consensus.

    This replaces the fallback-based SemanticWorkflowMatcher.match() flow.

    Example:
        >>> matcher = EnsembleMatcher(keyword_matcher, semantic_matcher, pattern_matcher, aggregator)
        >>> matcher.initialize(registry)
        >>> result = matcher.match("prosty stół z prostymi nogami")
        >>> print(result.workflow_name)  # "table_workflow"
        >>> print(result.modifiers)  # {"leg_style": "straight"}
    """

    def __init__(
        self,
        keyword_matcher: KeywordMatcher,
        semantic_matcher: SemanticMatcher,
        pattern_matcher: PatternMatcher,
        aggregator: EnsembleAggregator,
        config: Optional[RouterConfig] = None,
    ):
        """Initialize ensemble matcher.

        Args:
            keyword_matcher: Matcher for keyword-based matching.
            semantic_matcher: Matcher for LaBSE semantic matching.
            pattern_matcher: Matcher for geometry pattern matching.
            aggregator: Aggregator for combining results.
            config: Router configuration.
        """
        self._matchers: List[IMatcher] = [
            keyword_matcher,
            semantic_matcher,
            pattern_matcher
        ]
        self._aggregator = aggregator
        self._config = config or RouterConfig()
        self._router_logger = RouterLogger()
        self._is_initialized = False

    def initialize(self, registry: "WorkflowRegistry") -> None:
        """Initialize all matchers that need initialization.

        Currently only SemanticMatcher requires initialization.

        Args:
            registry: Workflow registry for initializing semantic matcher.
        """
        for matcher in self._matchers:
            # Check if matcher has initialize method and hasn't been initialized
            if hasattr(matcher, 'initialize') and callable(matcher.initialize):
                if hasattr(matcher, 'is_initialized') and not matcher.is_initialized():
                    matcher.initialize(registry)

        self._is_initialized = True
        logger.info("EnsembleMatcher initialized")

    def is_initialized(self) -> bool:
        """Check if ensemble matcher is initialized.

        Returns:
            True if initialize() was called, False otherwise.
        """
        return self._is_initialized

    def match(
        self,
        prompt: str,
        context: Optional[SceneContext] = None,
    ) -> EnsembleResult:
        """Run all matchers and aggregate results.

        Runs KeywordMatcher, SemanticMatcher, and PatternMatcher in sequence.
        Aggregates results using EnsembleAggregator with weighted consensus.

        Args:
            prompt: User prompt/goal (e.g., "prosty stół z prostymi nogami").
            context: Optional scene context (for pattern matching).

        Returns:
            EnsembleResult with workflow, confidence, and modifiers.

        Example:
            >>> result = matcher.match("create phone-like object")
            >>> result.workflow_name  # "phone_workflow"
            >>> result.final_score  # 0.74
            >>> result.confidence_level  # "HIGH"
            >>> result.modifiers  # {...}
        """
        # Convert context to dict for matchers
        context_dict: Optional[Dict[str, Any]] = None
        if context:
            context_dict = context.to_dict()
            # Context includes detected_pattern from GeometryPatternDetector
            # This is passed in from SupervisorRouter._detect_pattern()

        # Run all matchers
        results: List[MatcherResult] = []
        for matcher in self._matchers:
            try:
                result = matcher.match(prompt, context_dict)
                results.append(result)

                self._router_logger.log_info(
                    f"Matcher '{matcher.name}': "
                    f"{result.workflow_name or 'None'} "
                    f"(confidence: {result.confidence:.2f}, "
                    f"weighted: {result.confidence * result.weight:.3f})"
                )
            except Exception as e:
                logger.exception(f"Matcher '{matcher.name}' failed: {e}")
                self._router_logger.log_error(matcher.name, str(e))
                # Add failed result with zero confidence
                results.append(MatcherResult(
                    matcher_name=matcher.name,
                    workflow_name=None,
                    confidence=0.0,
                    weight=matcher.weight,
                    metadata={"error": str(e)}
                ))

        # Aggregate results
        ensemble_result = self._aggregator.aggregate(results, prompt)

        self._router_logger.log_info(
            f"Ensemble result: {ensemble_result.workflow_name} "
            f"(score: {ensemble_result.final_score:.3f}, "
            f"level: {ensemble_result.confidence_level}, "
            f"modifiers: {list(ensemble_result.modifiers.keys())})"
        )

        return ensemble_result

    def get_info(self) -> Dict[str, Any]:
        """Get ensemble matcher information.

        Returns:
            Dictionary with matcher status and configuration.

        Example:
            >>> info = matcher.get_info()
            >>> info["is_initialized"]  # True
            >>> info["matchers"]  # [{"name": "keyword", "weight": 0.40, ...}, ...]
        """
        return {
            "is_initialized": self._is_initialized,
            "matchers": [
                {
                    "name": m.name,
                    "weight": m.weight,
                    "initialized": getattr(m, 'is_initialized', lambda: True)()
                }
                for m in self._matchers
            ],
            "config": {
                "pattern_boost": EnsembleAggregator.PATTERN_BOOST,
                "composition_threshold": EnsembleAggregator.COMPOSITION_THRESHOLD,
            }
        }
