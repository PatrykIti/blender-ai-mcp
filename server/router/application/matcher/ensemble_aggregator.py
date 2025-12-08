"""
Ensemble Aggregator for Ensemble Matching System.

TASK-053-7: Aggregates results from multiple matchers using weighted consensus.

Combines MatcherResult from all matchers and produces a single EnsembleResult.
ALWAYS runs ModifierExtractor to ensure modifiers are applied (bug fix).
"""

from collections import defaultdict
from typing import Dict, List, Optional
import logging

from server.router.domain.entities.ensemble import MatcherResult, EnsembleResult
from server.router.application.matcher.modifier_extractor import ModifierExtractor
from server.router.infrastructure.config import RouterConfig

logger = logging.getLogger(__name__)


class EnsembleAggregator:
    """Aggregates results from multiple matchers using weighted consensus.

    Takes MatcherResult from each matcher and produces a single EnsembleResult.
    ALWAYS runs ModifierExtractor to ensure modifiers are applied.

    Example:
        >>> aggregator = EnsembleAggregator(modifier_extractor)
        >>> results = [keyword_result, semantic_result, pattern_result]
        >>> ensemble = aggregator.aggregate(results, "proste nogi")
        >>> print(ensemble.workflow_name)  # "table_workflow"
        >>> print(ensemble.modifiers)  # {"leg_style": "straight"}
    """

    # Score multiplier when pattern matcher fires
    PATTERN_BOOST = 1.3

    # Threshold for activating composition mode (two workflows with similar scores)
    COMPOSITION_THRESHOLD = 0.15

    # Keywords that force LOW confidence (simple workflow)
    SIMPLE_KEYWORDS = [
        "simple", "basic", "minimal", "just", "only", "plain",
        "prosty", "podstawowy", "tylko", "zwykły",  # Polish
        "einfach", "nur", "schlicht",  # German
    ]

    def __init__(
        self,
        modifier_extractor: ModifierExtractor,
        config: Optional[RouterConfig] = None,
    ):
        """Initialize aggregator.

        Args:
            modifier_extractor: Extractor for modifiers.
            config: Router configuration for thresholds.
        """
        self._modifier_extractor = modifier_extractor
        self._config = config or RouterConfig()

    def aggregate(
        self,
        results: List[MatcherResult],
        prompt: str,
    ) -> EnsembleResult:
        """Aggregate matcher results into final decision.

        Combines results from all matchers using weighted consensus.
        ALWAYS extracts modifiers (this is the bug fix!).

        Args:
            results: Results from all matchers (KeywordMatcher, SemanticMatcher, PatternMatcher).
            prompt: Original user prompt.

        Returns:
            EnsembleResult with final workflow, score, and modifiers.

        Example:
            >>> results = [
            ...     MatcherResult("keyword", None, 0.0, 0.40),
            ...     MatcherResult("semantic", "table_workflow", 0.84, 0.40),
            ...     MatcherResult("pattern", None, 0.0, 0.15)
            ... ]
            >>> ensemble = aggregator.aggregate(results, "proste nogi")
            >>> ensemble.workflow_name  # "table_workflow"
            >>> ensemble.final_score  # 0.336 (0.84 × 0.40)
        """
        # Group scores by workflow
        workflow_scores: Dict[str, Dict[str, float]] = defaultdict(dict)

        for result in results:
            if result.workflow_name:
                # Store weighted score per matcher
                weighted_score = result.confidence * result.weight
                workflow_scores[result.workflow_name][result.matcher_name] = weighted_score

        # No matches from any matcher
        if not workflow_scores:
            return EnsembleResult(
                workflow_name=None,
                final_score=0.0,
                confidence_level="NONE",
                modifiers={},
                matcher_contributions={},
                requires_adaptation=False
            )

        # Calculate final scores for each workflow
        final_scores: Dict[str, float] = {}
        for workflow, contributions in workflow_scores.items():
            score = sum(contributions.values())

            # Pattern boost: if pattern matcher contributed, multiply by boost factor
            if "pattern" in contributions and contributions["pattern"] > 0:
                score *= self.PATTERN_BOOST
                logger.debug(f"Applied pattern boost to {workflow}: {score:.3f}")

            final_scores[workflow] = score

        # Sort workflows by score (descending)
        sorted_workflows = sorted(
            final_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        best_workflow, best_score = sorted_workflows[0]
        best_contributions = workflow_scores[best_workflow]

        # Check for composition mode (two workflows with similar scores)
        composition_mode = False
        extra_workflows: List[str] = []
        if len(sorted_workflows) > 1:
            second_workflow, second_score = sorted_workflows[1]
            if abs(best_score - second_score) < self.COMPOSITION_THRESHOLD:
                composition_mode = True
                extra_workflows = [second_workflow]
                logger.info(
                    f"Composition mode activated: {best_workflow} ({best_score:.3f}) "
                    f"≈ {second_workflow} ({second_score:.3f})"
                )

        # CRITICAL: ALWAYS extract modifiers (this is the bug fix!)
        modifier_result = self._modifier_extractor.extract(prompt, best_workflow)

        # Determine confidence level
        confidence_level = self._determine_confidence_level(best_score, prompt)

        logger.info(
            f"Ensemble aggregation: {best_workflow} "
            f"(score: {best_score:.3f}, level: {confidence_level}, "
            f"modifiers: {list(modifier_result.modifiers.keys())})"
        )

        return EnsembleResult(
            workflow_name=best_workflow,
            final_score=best_score,
            confidence_level=confidence_level,
            modifiers=modifier_result.modifiers,
            matcher_contributions=best_contributions,
            requires_adaptation=confidence_level != "HIGH",
            composition_mode=composition_mode,
            extra_workflows=extra_workflows
        )

    def _determine_confidence_level(self, score: float, prompt: str) -> str:
        """Determine confidence level from score and prompt analysis.

        Checks for "simple" keywords that force LOW confidence.
        Uses score thresholds for HIGH/MEDIUM/LOW classification.

        Args:
            score: Aggregated final score.
            prompt: User prompt to check for "simple" keywords.

        Returns:
            Confidence level: HIGH, MEDIUM, LOW, or NONE.

        Example:
            >>> aggregator._determine_confidence_level(0.75, "create table")
            "HIGH"
            >>> aggregator._determine_confidence_level(0.75, "simple table")
            "LOW"  # "simple" keyword forces LOW
        """
        prompt_lower = prompt.lower()

        # Check for "simple" keywords that force LOW confidence
        wants_simple = any(kw in prompt_lower for kw in self.SIMPLE_KEYWORDS)

        if wants_simple:
            logger.debug("User wants simple version → forcing LOW confidence")
            return "LOW"

        # Use configured thresholds from RouterConfig
        # HIGH: score >= 0.7 (normalized), MEDIUM: >= 0.4, LOW: < 0.4
        if score >= 0.7:
            return "HIGH"
        elif score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"
