"""
Modifier Extractor for Ensemble Matching System.

TASK-053-6: Consolidates modifier extraction logic from router.py and registry.py
into standalone component implementing IModifierExtractor interface.

Extracts parametric modifiers from user prompts based on workflow definitions.
"""

from typing import Dict, Any, List, Optional, TYPE_CHECKING
import logging

from server.router.domain.interfaces.matcher import IModifierExtractor
from server.router.domain.entities.ensemble import ModifierResult

if TYPE_CHECKING:
    from server.router.application.workflows.registry import WorkflowRegistry
    from server.router.application.classifier.workflow_intent_classifier import (
        WorkflowIntentClassifier,
    )

logger = logging.getLogger(__name__)


class ModifierExtractor(IModifierExtractor):
    """Extracts parametric modifiers from prompts.

    Consolidates logic from:
    - SupervisorRouter._build_variables() (router.py:601-630)
    - WorkflowRegistry._extract_modifiers() (registry.py:283-308)

    Scans prompt for modifier keywords and builds variable overrides.
    This ensures modifiers are ALWAYS extracted regardless of which
    matcher wins the ensemble vote.

    Example:
        >>> extractor = ModifierExtractor(registry)
        >>> result = extractor.extract("proste nogi", "table_workflow")
        >>> print(result.modifiers)  # {"leg_style": "straight"}
        >>> print(result.matched_keywords)  # ["proste nogi"]
    """

    def __init__(
        self,
        registry: "WorkflowRegistry",
        classifier: Optional["WorkflowIntentClassifier"] = None,
        similarity_threshold: float = 0.70,
    ):
        """Initialize modifier extractor.

        Args:
            registry: Workflow registry for accessing workflow definitions.
            classifier: Optional LaBSE classifier for semantic matching.
                If provided, uses semantic similarity instead of substring matching.
                This enables multilingual modifier detection (e.g., "prostymi nogami"
                matches "straight legs" via LaBSE embeddings).
            similarity_threshold: Minimum similarity score for semantic match (0.0-1.0).
                Default 0.70 provides good balance between precision and recall.
        """
        self._registry = registry
        self._classifier = classifier
        self._similarity_threshold = similarity_threshold

    def _extract_ngrams(self, text: str, min_n: int = 1, max_n: int = 3) -> List[str]:
        """Extract n-grams from text for semantic matching.

        Args:
            text: Input text to extract n-grams from.
            min_n: Minimum n-gram size (default 1 = single words).
            max_n: Maximum n-gram size (default 3 = up to 3-word phrases).

        Returns:
            List of n-grams extracted from text.

        Example:
            >>> _extract_ngrams("prosty stół z nogami", min_n=1, max_n=2)
            ["prosty", "stół", "z", "nogami", "prosty stół", "stół z", "z nogami"]
        """
        words = text.lower().split()
        ngrams = []
        for n in range(min_n, min(max_n + 1, len(words) + 1)):
            for i in range(len(words) - n + 1):
                ngrams.append(" ".join(words[i:i + n]))
        return ngrams

    def _has_negative_signals(self, prompt: str, negative_signals: list) -> bool:
        """Check if prompt contains negative signals.

        TASK-055-FIX-2: Negative signals detection for semantic matching.
        Rejects modifier match if prompt contains contradictory terms.

        Args:
            prompt: User prompt (e.g., "stół z nogami X")
            negative_signals: List of contradictory terms from YAML

        Returns:
            True if any negative signal found in prompt.

        Example:
            >>> _has_negative_signals("stół z nogami X", ["X", "crossed"])
            True  # "X" found in prompt
            >>> _has_negative_signals("prosty stół", ["X", "crossed"])
            False  # No negative signals
        """
        if not negative_signals:
            return False

        prompt_lower = prompt.lower()
        prompt_words = set(prompt_lower.split())

        for neg_word in negative_signals:
            neg_lower = neg_word.lower()
            # Check both substring and word boundary match
            if neg_lower in prompt_words or neg_lower in prompt_lower:
                logger.debug(f"Negative signal detected: '{neg_word}' in prompt")
                return True

        return False

    def extract(self, prompt: str, workflow_name: str) -> ModifierResult:
        """Extract modifiers from prompt for given workflow.

        Scans prompt for modifier keywords defined in workflow.modifiers.
        Returns ONLY matched modifiers (NOT defaults - those are handled by ParameterResolver).

        TASK-055-FIX: Defaults are no longer included here. They're applied by
        ParameterResolver in TIER 3 fallback, ensuring correct resolution_sources.

        Args:
            prompt: User prompt/goal (e.g., "proste nogi").
            workflow_name: Target workflow name (e.g., "table_workflow").

        Returns:
            ModifierResult with:
            - modifiers: Dict of MATCHED modifier overrides (no defaults)
            - matched_keywords: List of keywords that matched
            - confidence_map: Dict mapping keywords to confidence (1.0 for exact match)

        Example:
            >>> result = extractor.extract("straight legs", "table_workflow")
            >>> result.modifiers  # {"leg_angle_left": 0, "leg_angle_right": 0}
            >>> result.matched_keywords  # ["straight legs"]
            >>> result.confidence_map  # {"straight legs": 0.95}
        """
        # Get workflow definition
        definition = self._registry.get_definition(workflow_name)
        if not definition:
            logger.warning(f"No definition found for workflow: {workflow_name}")
            return ModifierResult(
                modifiers={},
                matched_keywords=[],
                confidence_map={}
            )

        # TASK-055-FIX: Start with empty dict - defaults should be handled by ParameterResolver TIER 3
        # Only include ACTUAL matched modifiers from YAML, not defaults
        modifiers = {}

        # Extract modifier overrides
        matched_keywords = []
        confidence_map = {}

        if prompt and definition.modifiers:
            prompt_lower = prompt.lower()

            # TASK-055-FIX-2: Multi-word semantic matching with negative signals
            semantic_matches: List[tuple] = []  # (keyword, param_values, avg_sim, matched_words)

            if self._classifier is not None:
                ngrams = self._extract_ngrams(prompt)

                for keyword, values in definition.modifiers.items():
                    keyword_words = keyword.lower().split()  # ["straight", "legs"]

                    # Multi-word matching: count how many keyword words match
                    matched_words = []  # [(kw_word, best_ngram, similarity), ...]

                    for kw_word in keyword_words:
                        best_sim = 0.0
                        best_ngram = ""

                        for ngram in ngrams:
                            sim = self._classifier.similarity(kw_word, ngram)
                            if sim > best_sim:
                                best_sim = sim
                                best_ngram = ngram

                        if best_sim >= 0.65:  # Per-word threshold (TASK-055-FIX-2)
                            matched_words.append((kw_word, best_ngram, best_sim))
                            logger.debug(
                                f"Word match: '{kw_word}' ↔ '{best_ngram}' (sim={best_sim:.3f})"
                            )

                    # Require min(N, 2) words to match
                    required_matches = min(len(keyword_words), 2)

                    if len(matched_words) >= required_matches:
                        # Calculate average similarity
                        avg_sim = sum(m[2] for m in matched_words) / len(matched_words)

                        # Check negative signals from YAML
                        negative_signals = values.get("negative_signals", [])
                        if self._has_negative_signals(prompt, negative_signals):
                            logger.debug(
                                f"Rejected '{keyword}': negative signals detected in prompt"
                            )
                            continue  # Skip this match

                        # Extract actual parameter values (filter out negative_signals key)
                        param_values = {k: v for k, v in values.items() if k != "negative_signals"}

                        logger.info(
                            f"Modifier match: '{keyword}' ({len(matched_words)}/{len(keyword_words)} words) "
                            f"→ {param_values} (avg_sim={avg_sim:.3f})"
                        )

                        semantic_matches.append((keyword, param_values, avg_sim, matched_words))
                    else:
                        logger.debug(
                            f"Insufficient word matches for '{keyword}': "
                            f"{len(matched_words)}/{len(keyword_words)} (need {required_matches})"
                        )

            # Select ONLY the best semantic match (highest similarity wins)
            if semantic_matches:
                # Sort by similarity descending
                semantic_matches.sort(key=lambda x: x[2], reverse=True)
                best_keyword, best_values, best_sim, best_matched_words = semantic_matches[0]

                modifiers.update(best_values)
                matched_keywords.append(best_keyword)
                confidence_map[best_keyword] = best_sim
            else:
                # Fallback: substring matching (backward compatibility)
                for keyword, values in definition.modifiers.items():
                    if keyword.lower() in prompt_lower:
                        # Filter out negative_signals for substring match too
                        param_values = {k: v for k, v in values.items() if k != "negative_signals"}
                        logger.debug(f"Modifier substring match: '{keyword}' → {param_values}")
                        modifiers.update(param_values)
                        matched_keywords.append(keyword)
                        confidence_map[keyword] = 1.0  # Exact match = full confidence
                        break  # Only apply first substring match

        return ModifierResult(
            modifiers=modifiers,
            matched_keywords=matched_keywords,
            confidence_map=confidence_map
        )
