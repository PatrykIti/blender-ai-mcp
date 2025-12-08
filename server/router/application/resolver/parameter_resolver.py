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
        relevance_threshold: float = 0.5,
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

        Returns the maximum similarity found.

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

        # Check similarity with semantic hints
        for hint in schema.semantic_hints:
            hint_similarity = self._classifier.similarity(prompt, hint)
            max_relevance = max(max_relevance, hint_similarity)

        # Also check if any hint appears literally in prompt
        prompt_lower = prompt.lower()
        for hint in schema.semantic_hints:
            if hint.lower() in prompt_lower:
                # Boost relevance if hint literally appears
                max_relevance = max(max_relevance, 0.8)
                break

        return max_relevance

    def extract_context(
        self,
        prompt: str,
        schema: ParameterSchema,
    ) -> str:
        """Extract relevant context from prompt for this parameter.

        Finds the most relevant phrase in the prompt that relates
        to this parameter, using semantic hints.

        Args:
            prompt: Full user prompt.
            schema: Parameter schema with semantic hints.

        Returns:
            Extracted context string (phrase or full prompt if no match).
        """
        prompt_lower = prompt.lower()

        # Look for semantic hints in prompt
        for hint in schema.semantic_hints:
            hint_lower = hint.lower()
            if hint_lower in prompt_lower:
                # Find the phrase containing this hint
                idx = prompt_lower.find(hint_lower)

                # Extract surrounding context (up to 30 chars on each side)
                # But respect word boundaries
                start = max(0, idx - 30)
                end = min(len(prompt), idx + len(hint) + 30)

                # Adjust start to word boundary
                while start > 0 and prompt[start - 1] not in " \t\n,.:;!?":
                    start -= 1

                # Adjust end to word boundary
                while end < len(prompt) and prompt[end] not in " \t\n,.:;!?":
                    end += 1

                context = prompt[start:end].strip()

                # Remove leading/trailing punctuation
                context = re.sub(r"^[,.:;!?\s]+", "", context)
                context = re.sub(r"[,.:;!?\s]+$", "", context)

                if context:
                    return context

        # No hint found in prompt, try to extract relevant phrase
        # by looking for keywords from description
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
                    return sentence.strip()

        # Fallback: return full prompt
        return prompt

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
