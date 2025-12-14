"""
Parameter Resolver Implementation.

Three-tier parameter resolution system:
1. YAML modifiers (highest priority) - from ModifierExtractor
2. Learned mappings - from ParameterStore via LaBSE
3. LLM interaction - mark as unresolved for LLM input

TASK-055-3
"""

import logging
import re
from typing import Any, Dict, List, Optional

from server.router.domain.entities.parameter import (
    ParameterResolutionResult,
    ParameterSchema,
    StoredMapping,
    UnresolvedParameter,
)
from server.router.domain.interfaces.i_parameter_resolver import (
    IParameterResolver,
    IParameterStore,
)
from server.router.domain.interfaces.i_workflow_intent_classifier import (
    IWorkflowIntentClassifier,
)

logger = logging.getLogger(__name__)


class ParameterResolver(IParameterResolver):
    """Resolves workflow parameters using three-tier system.

    Priority order:
    1. YAML modifiers (from ModifierExtractor / EnsembleResult)
    2. Learned mappings (from ParameterStore via LaBSE)
    3. Mark as unresolved (needs LLM input)

    When a parameter is mentioned in the prompt but has no known value,
    it's marked as unresolved for interactive LLM resolution.
    """

    def __init__(
        self,
        classifier: IWorkflowIntentClassifier,
        store: IParameterStore,
        relevance_threshold: float = 0.4,  # TASK-055: Lowered for cross-language LaBSE
        memory_threshold: float = 0.85,
    ):
        """Initialize parameter resolver.

        Args:
            classifier: LaBSE classifier for semantic matching.
            store: Parameter store for learned mappings.
            relevance_threshold: Minimum similarity for "prompt relates to param".
            memory_threshold: Minimum similarity to reuse stored mapping.
        """
        self._classifier = classifier
        self._store = store
        self._relevance_threshold = relevance_threshold
        self._memory_threshold = memory_threshold

        logger.info(
            f"ParameterResolver initialized: "
            f"relevance_threshold={relevance_threshold}, "
            f"memory_threshold={memory_threshold}"
        )

    def resolve(
        self,
        prompt: str,
        workflow_name: str,
        parameters: Dict[str, ParameterSchema],
        existing_modifiers: Optional[Dict[str, Any]] = None,
    ) -> ParameterResolutionResult:
        """Resolve parameters using three-tier system.

        Args:
            prompt: User prompt for semantic matching.
            workflow_name: Current workflow name.
            parameters: Parameter schemas from workflow definition.
            existing_modifiers: Already extracted modifiers from YAML
                (from ModifierExtractor/EnsembleMatcher). Can be None.

        Returns:
            ParameterResolutionResult with resolved and unresolved parameters.
        """
        resolved: Dict[str, Any] = {}
        unresolved: List[UnresolvedParameter] = []
        sources: Dict[str, str] = {}

        # Handle None modifiers
        modifiers = existing_modifiers or {}

        logger.debug(
            f"Resolving parameters for workflow '{workflow_name}': "
            f"{list(parameters.keys())}"
        )
        logger.debug(f"Existing modifiers: {modifiers}")

        for param_name, schema in parameters.items():
            # TIER 1: Check YAML modifiers first (highest priority)
            if param_name in modifiers:
                value = modifiers[param_name]
                resolved[param_name] = value
                sources[param_name] = "yaml_modifier"
                logger.debug(
                    f"TIER 1: {param_name}={value} (yaml_modifier)"
                )
                continue

            # TASK-056-5: Computed parameters are internal by default.
            #
            # - They should be computed during workflow expansion.
            # - They should NOT be resolved from learned mappings (stale) or defaults.
            # - They should never be requested as interactive input.
            #
            # Users can still override them explicitly via Tier 1 (modifiers/resolved_params),
            # but we avoid persisting/reusing them automatically.
            if schema.computed:
                logger.debug(f"TIER 3: {param_name} deferred (computed param)")
                continue

            # TIER 2: Check learned mappings (from previous LLM interactions)
            stored_mapping = self._store.find_mapping(
                prompt=prompt,
                parameter_name=param_name,
                workflow_name=workflow_name,
                similarity_threshold=self._memory_threshold,
            )

            if stored_mapping is not None:
                resolved[param_name] = stored_mapping.value
                sources[param_name] = "learned"
                # Increment usage count for analytics
                self._store.increment_usage(stored_mapping)
                logger.debug(
                    f"TIER 2: {param_name}={stored_mapping.value} "
                    f"(learned, similarity={stored_mapping.similarity:.3f})"
                )
                continue

            # TIER 3: Check if prompt relates to this parameter
            relevance = self.calculate_relevance(prompt, schema)

            if relevance > self._relevance_threshold:
                # Prompt mentions this parameter but we don't know value
                # → Mark for LLM resolution
                context = self.extract_context(prompt, schema)
                unresolved.append(
                    UnresolvedParameter(
                        name=param_name,
                        schema=schema,
                        context=context,
                        relevance=relevance,
                    )
                )
                logger.debug(
                    f"TIER 3: {param_name} UNRESOLVED "
                    f"(relevance={relevance:.3f}, context='{context}')"
                )
            else:
                # Prompt doesn't mention this parameter - use default
                resolved[param_name] = schema.default
                sources[param_name] = "default"
                logger.debug(
                    f"TIER 3: {param_name}={schema.default} "
                    f"(default, relevance={relevance:.3f} < threshold)"
                )

        result = ParameterResolutionResult(
            resolved=resolved,
            unresolved=unresolved,
            resolution_sources=sources,
        )

        logger.info(
            f"Resolution complete: {len(resolved)} resolved, "
            f"{len(unresolved)} unresolved"
        )

        return result

    def calculate_relevance(
        self,
        prompt: str,
        schema: ParameterSchema,
    ) -> float:
        """Calculate how relevant a prompt is to a parameter.

        Uses LaBSE similarity between prompt and:
        1. Parameter description
        2. Semantic hints
        3. Semantic word matching (cross-language support)

        Returns the maximum similarity found.

        TASK-055: Added semantic word matching for cross-language support.
        Instead of only literal matching (e.g., "kąt" in prompt), we now also
        check if ANY word in prompt is semantically similar to ANY hint.
        This allows German "Winkel" to match English "angle" without adding
        hints for every language.

        Args:
            prompt: User prompt.
            schema: Parameter schema with description and hints.

        Returns:
            Relevance score (0.0-1.0). Higher = more relevant.
        """
        max_relevance = 0.0

        # Check similarity with description
        if schema.description:
            desc_similarity = self._classifier.similarity(
                prompt, schema.description
            )
            max_relevance = max(max_relevance, desc_similarity)

        # Check similarity with semantic hints (full prompt vs hint)
        for hint in schema.semantic_hints:
            hint_similarity = self._classifier.similarity(prompt, hint)
            max_relevance = max(max_relevance, hint_similarity)

        # Literal matching (fast path) - if hint appears literally in prompt
        prompt_lower = prompt.lower()
        for hint in schema.semantic_hints:
            if hint.lower() in prompt_lower:
                # Boost relevance if hint literally appears
                max_relevance = max(max_relevance, 0.8)
                return max_relevance  # Early exit - strong signal

        # Semantic word matching (cross-language support)
        # Check if any word in prompt is semantically similar to any hint
        # This allows "Winkel" (DE) to match "angle" (EN) without explicit hints
        prompt_words = [w for w in prompt_lower.split() if len(w) > 2]
        for hint in schema.semantic_hints:
            for word in prompt_words:
                word_sim = self._classifier.similarity(word, hint)
                if word_sim > 0.65:  # Higher threshold for single words
                    max_relevance = max(max_relevance, 0.75)
                    logger.debug(
                        f"Semantic word match: '{word}' ↔ '{hint}' = {word_sim:.3f}"
                    )
                    break
            if max_relevance >= 0.75:
                break

        return max_relevance

    def _extract_sentence_context(
        self,
        prompt: str,
        hint_idx: int,
        hint: str,
        max_length: int,
    ) -> str:
        """Extract complete sentences around hint position.

        Includes:
        - 1 sentence before hint (if exists)
        - Sentence containing hint
        - 1 sentence after hint (if exists)

        TASK-055-FIX-3: Smart sentence extraction for better semantic context.

        Args:
            prompt: Full prompt text.
            hint_idx: Character index where hint starts.
            hint: Semantic hint string.
            max_length: Maximum total context length.

        Returns:
            Extracted sentence context or empty string if extraction fails.
        """
        # Sentence boundary characters
        SENTENCE_ENDINGS = {'.', '!', '?', '\n'}

        # Find sentence containing hint
        # Walk backwards to find sentence start
        sent_start = hint_idx
        for i in range(hint_idx - 1, -1, -1):
            if prompt[i] in SENTENCE_ENDINGS:
                sent_start = i + 1
                break
        else:
            sent_start = 0  # Beginning of prompt

        # Walk forwards to find sentence end
        sent_end = hint_idx + len(hint)
        for i in range(hint_idx + len(hint), len(prompt)):
            if prompt[i] in SENTENCE_ENDINGS:
                sent_end = i + 1
                break
        else:
            sent_end = len(prompt)  # End of prompt

        # Extract hint sentence
        hint_sentence = prompt[sent_start:sent_end].strip()

        # Try to include previous sentence
        prev_start = 0
        if sent_start > 0:
            for i in range(sent_start - 2, -1, -1):
                if prompt[i] in SENTENCE_ENDINGS:
                    prev_start = i + 1
                    break

        # Try to include next sentence
        next_end = len(prompt)
        if sent_end < len(prompt):
            for i in range(sent_end, len(prompt)):
                if prompt[i] in SENTENCE_ENDINGS:
                    next_end = i + 1
                    break

        # Build context: prev + hint + next
        context_parts = []

        if prev_start < sent_start:
            prev_sentence = prompt[prev_start:sent_start].strip()
            if prev_sentence:
                context_parts.append(prev_sentence)

        context_parts.append(hint_sentence)

        if sent_end < next_end:
            next_sentence = prompt[sent_end:next_end].strip()
            if next_sentence:
                context_parts.append(next_sentence)

        context = " ".join(context_parts)

        # Truncate if too long
        if len(context) > max_length:
            # Try to preserve hint by keeping middle portion
            hint_pos_in_context = context.lower().find(hint.lower())
            if hint_pos_in_context >= 0:
                # Center around hint
                half_length = max_length // 2
                context_start = max(0, hint_pos_in_context - half_length)
                context_end = min(
                    len(context), hint_pos_in_context + len(hint) + half_length
                )
                context = context[context_start:context_end].strip()
            else:
                # Simple truncation
                context = context[:max_length].strip()

        return context

    def extract_context(
        self,
        prompt: str,
        schema: ParameterSchema,
        max_context_length: int = 400,
    ) -> str:
        """Extract semantic context around hint using hybrid strategy.

        TIER 1: Smart sentence extraction (complete sentences with hint)
        TIER 2: Expanded window (200+ chars)
        TIER 3: Full prompt (if ≤500 chars)

        TASK-055-FIX-3: Fixes truncation bug that lost semantic info like "X-shaped".
        Old implementation: 60 chars → New: 100-400 chars with sentence awareness.

        Args:
            prompt: Full user prompt.
            schema: Parameter schema with semantic hints.
            max_context_length: Maximum context length (default 400).

        Returns:
            Extracted context string containing semantic information around hint.
        """
        if not prompt:
            return ""

        # TIER 3: If prompt is short enough, use entire prompt
        if len(prompt) <= 500:
            logger.debug(
                f"[TIER 3] Using full prompt as context (length={len(prompt)} ≤ 500)"
            )
            return prompt.strip()

        # Look for semantic hints in prompt
        prompt_lower = prompt.lower()
        for hint in schema.semantic_hints:
            hint_lower = hint.lower()
            idx = prompt_lower.find(hint_lower)

            if idx == -1:
                continue  # Try next hint

            # TIER 1: Smart sentence extraction
            context = self._extract_sentence_context(
                prompt, idx, hint, max_context_length
            )

            if context and len(context) >= 100:  # Minimum viable context length
                logger.debug(
                    f"[TIER 1] Extracted sentence context for hint='{hint}' "
                    f"(length={len(context)}): '{context[:50]}...{context[-50:]}'"
                )
                return context

            # TIER 2: Expanded window fallback
            logger.debug(
                f"[TIER 2] Sentence extraction insufficient (len={len(context) if context else 0}), "
                f"using expanded window for hint='{hint}'"
            )
            start = max(0, idx - 100)
            end = min(len(prompt), idx + len(hint) + 100)
            context = prompt[start:end].strip()

            # Remove leading/trailing punctuation
            context = re.sub(r"^[,.:;!?\s]+", "", context)
            context = re.sub(r"[,.:;!?\s]+$", "", context)

            if len(context) > max_context_length:
                # Truncate to max_context_length while preserving hint position
                context = context[:max_context_length].strip()

            logger.debug(
                f"[TIER 2] Expanded window context (length={len(context)}): "
                f"'{context[:50]}...{context[-50:]}'"
            )
            return context

        # No hint found in any semantic hints, try description keywords
        if schema.description:
            # Extract nouns from description (simple approach)
            desc_words = set(
                word.lower()
                for word in re.findall(r"\b\w+\b", schema.description)
                if len(word) > 3
            )

            # Find sentences in prompt containing these words
            sentences = re.split(r"[.!?]", prompt)
            for sentence in sentences:
                sentence_lower = sentence.lower()
                if any(word in sentence_lower for word in desc_words):
                    context = sentence.strip()
                    if len(context) <= max_context_length:
                        logger.debug(
                            f"[FALLBACK] Matched description keyword, "
                            f"context (length={len(context)}): '{context[:50]}...'"
                        )
                        return context

        # Final fallback: return truncated full prompt
        logger.debug(
            f"[FALLBACK] No hints/keywords found, using truncated prompt "
            f"(length={min(len(prompt), max_context_length)})"
        )
        return prompt[:max_context_length].strip()

    def store_resolved_value(
        self,
        context: str,
        parameter_name: str,
        value: Any,
        workflow_name: str,
        schema: Optional[ParameterSchema] = None,
    ) -> str:
        """Store LLM-provided parameter value for future reuse.

        Validates the value against schema if provided.

        Args:
            context: Original prompt fragment.
            parameter_name: Parameter name.
            value: The resolved value.
            workflow_name: Workflow name.
            schema: Optional schema for validation.

        Returns:
            Success message or error message.
        """
        # Validate value if schema provided
        if schema is not None:
            if not schema.validate_value(value):
                return (
                    f"Error: Value {value} is invalid for parameter "
                    f"'{parameter_name}' (type={schema.type}, "
                    f"range={schema.range})"
                )

        # Store the mapping
        self._store.store_mapping(
            context=context,
            parameter_name=parameter_name,
            value=value,
            workflow_name=workflow_name,
        )

        return (
            f"Stored: '{context}' → {parameter_name}={value} "
            f"(workflow: {workflow_name})"
        )
