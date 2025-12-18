"""
Parameter Resolution Interfaces.

Abstract interfaces for parameter storage and resolution components
that enable interactive LLM-driven parameter value discovery.

TASK-055
TASK-055-FIX: Simplified interface - removed list_mappings, delete_mapping
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from server.router.domain.entities.parameter import (
    ParameterResolutionResult,
    ParameterSchema,
    StoredMapping,
)


class IParameterStore(ABC):
    """Abstract interface for parameter mapping storage.

    Provides persistence layer for learned parameter mappings using
    LaBSE embeddings for semantic similarity search.

    TASK-055-FIX: Simplified to core operations only.
    Mappings are auto-managed through router_set_goal flow.

    Implementations should:
    - Store mappings with LaBSE embeddings for semantic retrieval
    - Support similarity-based search across languages
    - Track usage counts for analytics
    - Persist data across sessions (e.g., via LanceDB)
    """

    @abstractmethod
    def find_mapping(
        self,
        prompt: str,
        parameter_name: str,
        workflow_name: str,
        similarity_threshold: float = 0.85,
    ) -> Optional[StoredMapping]:
        """Find semantically similar stored mapping.

        Uses LaBSE embeddings to find previously learned mappings
        that are semantically similar to the current prompt.

        Args:
            prompt: User prompt to match against stored contexts.
            parameter_name: Name of the parameter to find mapping for.
            workflow_name: Name of the current workflow.
            similarity_threshold: Minimum similarity score (0.0-1.0)
                to consider a match. Higher = stricter matching.

        Returns:
            StoredMapping if a similar mapping is found above threshold,
            None otherwise.
        """
        pass

    @abstractmethod
    def store_mapping(
        self,
        context: str,
        parameter_name: str,
        value: Any,
        workflow_name: str,
    ) -> None:
        """Store LLM-provided parameter value with embedding.

        Creates a new learned mapping that can be retrieved via
        semantic similarity search in the future.

        Args:
            context: Original prompt fragment for embedding.
            parameter_name: Name of the resolved parameter.
            value: The parameter value provided by LLM.
            workflow_name: Name of the workflow this belongs to.
        """
        pass

    @abstractmethod
    def increment_usage(self, mapping: StoredMapping) -> None:
        """Increment usage count for a mapping.

        Called when an existing mapping is successfully reused,
        enabling analytics and potential cleanup of unused mappings.

        Args:
            mapping: The mapping that was used.
        """
        pass


class IParameterResolver(ABC):
    """Abstract interface for parameter resolution.

    Implements three-tier resolution system:
    1. YAML modifiers (highest priority) - from ModifierExtractor
    2. Learned mappings - from ParameterStore via LaBSE
    3. LLM interaction - mark as unresolved for LLM input

    Implementations should:
    - Check YAML modifiers first (existing system)
    - Use semantic similarity for learned mapping lookup
    - Only mark as unresolved when prompt relates to parameter
    - Use defaults when prompt doesn't mention parameter
    """

    @abstractmethod
    def resolve(
        self,
        prompt: str,
        workflow_name: str,
        parameters: Dict[str, ParameterSchema],
        existing_modifiers: Dict[str, Any],
    ) -> ParameterResolutionResult:
        """Resolve parameters using three-tier system.

        Args:
            prompt: User prompt for semantic matching.
            workflow_name: Current workflow name.
            parameters: Parameter schemas from workflow definition.
            existing_modifiers: Already extracted modifiers from YAML
                (from ModifierExtractor/EnsembleMatcher).

        Returns:
            ParameterResolutionResult with:
            - resolved: Parameters with known values
            - unresolved: Parameters needing LLM input
            - resolution_sources: Source of each resolved value
        """
        pass

    @abstractmethod
    def calculate_relevance(
        self,
        prompt: str,
        schema: ParameterSchema,
    ) -> float:
        """Calculate how relevant a prompt is to a parameter.

        Uses LaBSE similarity between prompt and parameter description
        plus semantic hints to determine if the prompt mentions this
        parameter.

        Args:
            prompt: User prompt.
            schema: Parameter schema with description and hints.

        Returns:
            Relevance score (0.0-1.0). Higher = more relevant.
        """
        pass

    @abstractmethod
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
        pass
