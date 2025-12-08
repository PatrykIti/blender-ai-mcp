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

    def extract(self, prompt: str, workflow_name: str) -> ModifierResult:
        """Extract modifiers from prompt for given workflow.

        Scans prompt for modifier keywords defined in workflow.modifiers.
        Returns merged defaults + modifier overrides.

        Args:
            prompt: User prompt/goal (e.g., "proste nogi").
            workflow_name: Target workflow name (e.g., "table_workflow").

        Returns:
            ModifierResult with:
            - modifiers: Dict of variable overrides (defaults + matched modifiers)
            - matched_keywords: List of keywords that matched
            - confidence_map: Dict mapping keywords to confidence (1.0 for exact match)

        Example:
            >>> result = extractor.extract("proste nogi", "table_workflow")
            >>> result.modifiers  # {"leg_style": "straight", ...defaults...}
            >>> result.matched_keywords  # ["proste nogi"]
            >>> result.confidence_map  # {"proste nogi": 1.0}
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

        # Start with defaults
        modifiers = {}
        if definition.defaults:
            modifiers = dict(definition.defaults)

        # Extract modifier overrides
        matched_keywords = []
        confidence_map = {}

        if prompt and definition.modifiers:
            prompt_lower = prompt.lower()

            # First pass: find best semantic match for each modifier
            semantic_matches: List[tuple] = []  # (keyword, values, similarity, ngram)

            if self._classifier is not None:
                ngrams = self._extract_ngrams(prompt)

                for keyword, values in definition.modifiers.items():
                    best_similarity = 0.0
                    best_ngram = ""

                    for ngram in ngrams:
                        sim = self._classifier.similarity(keyword, ngram)
                        if sim > best_similarity:
                            best_similarity = sim
                            best_ngram = ngram

                    if best_similarity >= self._similarity_threshold:
                        semantic_matches.append((keyword, values, best_similarity, best_ngram))

            # Select ONLY the best semantic match (highest similarity wins)
            if semantic_matches:
                # Sort by similarity descending
                semantic_matches.sort(key=lambda x: x[2], reverse=True)
                best_keyword, best_values, best_sim, best_ngram = semantic_matches[0]

                logger.info(
                    f"Modifier semantic match: '{best_keyword}' ≈ '{best_ngram}' "
                    f"→ {best_values} (similarity={best_sim:.3f})"
                )
                modifiers.update(best_values)
                matched_keywords.append(best_keyword)
                confidence_map[best_keyword] = best_sim
            else:
                # Fallback: substring matching (backward compatibility)
                for keyword, values in definition.modifiers.items():
                    if keyword.lower() in prompt_lower:
                        logger.debug(f"Modifier substring match: '{keyword}' → {values}")
                        modifiers.update(values)
                        matched_keywords.append(keyword)
                        confidence_map[keyword] = 1.0  # Exact match = full confidence
                        break  # Only apply first substring match

        return ModifierResult(
            modifiers=modifiers,
            matched_keywords=matched_keywords,
            confidence_map=confidence_map
        )
