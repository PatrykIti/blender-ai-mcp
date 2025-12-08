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

        # Calculate maximum possible score based on which matchers contributed
        # This normalizes the score to account for single-matcher scenarios
        max_possible_score = self._calculate_max_possible_score(best_contributions)

        # Determine confidence level (normalized)
        confidence_level = self._determine_confidence_level(
            best_score, prompt, max_possible_score
        )

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

    def _calculate_max_possible_score(self, contributions: Dict[str, float]) -> float:
        """Calculate maximum possible score based on which matchers contributed.

        When only semantic matcher contributes, max is 0.40 (not 0.95).
        This allows proper normalization for single-matcher scenarios.

        TASK-055-FIX: Critical for multilingual prompts where keyword matcher
        may not fire due to language mismatch.

        Args:
            contributions: Dict of matcher_name -> weighted_score.

        Returns:
            Maximum possible score for the contributing matchers.

        Example:
            >>> # Only semantic matcher contributed
            >>> contributions = {"semantic": 0.336}
            >>> _calculate_max_possible_score(contributions)
            0.40  # semantic weight = 0.40
        """
        # Standard weights
        WEIGHTS = {
            "keyword": 0.40,
            "semantic": 0.40,
            "pattern": 0.15 * self.PATTERN_BOOST,  # Include boost potential
        }

        max_score = 0.0
        for matcher_name in contributions.keys():
            max_score += WEIGHTS.get(matcher_name, 0.40)

        return max_score if max_score > 0 else 0.95  # Fallback to full possible

    def _determine_confidence_level(
        self, score: float, prompt: str, max_possible_score: float = 0.95
    ) -> str:
        """Determine confidence level from score and prompt analysis.

        TASK-055-FIX: Now normalizes score relative to max_possible_score.
        This fixes the bug where Polish prompts only matched semantic matcher
        (max 0.40) but thresholds were calibrated for full score (0.95).

        Checks for "simple" keywords that force LOW confidence.
        Uses NORMALIZED score thresholds for HIGH/MEDIUM/LOW classification.

        Args:
            score: Aggregated final score.
            prompt: User prompt to check for "simple" keywords.
            max_possible_score: Maximum possible score from contributing matchers.

        Returns:
            Confidence level: HIGH, MEDIUM, LOW, or NONE.

        Example:
            >>> # Semantic-only: 0.336 / 0.40 = 84% → HIGH
            >>> aggregator._determine_confidence_level(0.336, "stół piknikowy", 0.40)
            "HIGH"
            >>> # With "simple" keyword → forced LOW
            >>> aggregator._determine_confidence_level(0.336, "prosty stół", 0.40)
            "LOW"
        """
        prompt_lower = prompt.lower()

        # Check for "simple" keywords that force LOW confidence
        wants_simple = any(kw in prompt_lower for kw in self.SIMPLE_KEYWORDS)

        if wants_simple:
            logger.debug("User wants simple version → forcing LOW confidence")
            return "LOW"

        # TASK-055-FIX: Normalize score relative to max possible
        # This fixes single-matcher scenarios (e.g., Polish prompt → semantic only)
        normalized_score = score / max_possible_score if max_possible_score > 0 else 0.0

        logger.debug(
            f"Confidence calculation: raw={score:.3f}, max={max_possible_score:.3f}, "
            f"normalized={normalized_score:.3f}"
        )

        # Use NORMALIZED thresholds
        # HIGH: normalized >= 0.70 (e.g., 0.28/0.40 = 70%)
        # MEDIUM: normalized >= 0.50 (e.g., 0.20/0.40 = 50%)
        # LOW: normalized < 0.50
        if normalized_score >= 0.70:
            return "HIGH"
        elif normalized_score >= 0.50:
            return "MEDIUM"
        else:
            return "LOW"
