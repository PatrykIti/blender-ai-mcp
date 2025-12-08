"""
Parameter Store Implementation.

LanceDB-based store for learned parameter mappings with LaBSE embeddings.
Enables semantic similarity search across languages for parameter value reuse.

TASK-055-2
TASK-055-FIX: Simplified to core operations only - removed list_mappings, delete_mapping, get_stats.
Mappings are auto-managed through router_set_goal flow.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from server.router.domain.entities.parameter import StoredMapping
from server.router.domain.interfaces.i_parameter_resolver import IParameterStore
from server.router.domain.interfaces.i_vector_store import (
    IVectorStore,
    VectorNamespace,
    VectorRecord,
)
from server.router.domain.interfaces.i_workflow_intent_classifier import (
    IWorkflowIntentClassifier,
)

logger = logging.getLogger(__name__)


class ParameterStore(IParameterStore):
    """LanceDB-based store for learned parameter mappings.

    Uses LaBSE embeddings for multilingual semantic search,
    enabling parameter value reuse across languages.

    Features:
    - Semantic similarity search via LaBSE embeddings
    - Workflow and parameter-level filtering
    - Usage tracking for analytics
    - Persistent storage via LanceDB
    """

    def __init__(
        self,
        classifier: IWorkflowIntentClassifier,
        vector_store: IVectorStore,
        similarity_threshold: float = 0.85,
    ):
        """Initialize parameter store.

        Args:
            classifier: LaBSE classifier for generating embeddings.
            vector_store: Vector store for persistence.
            similarity_threshold: Default threshold for similarity matching.
        """
        self._classifier = classifier
        self._vector_store = vector_store
        self._similarity_threshold = similarity_threshold

        logger.info(
            f"ParameterStore initialized with threshold={similarity_threshold}"
        )

    def _generate_record_id(
        self,
        context: str,
        parameter_name: str,
        workflow_name: str,
    ) -> str:
        """Generate unique record ID for a mapping.

        Args:
            context: Original prompt context.
            parameter_name: Parameter name.
            workflow_name: Workflow name.

        Returns:
            Unique identifier string.
        """
        # Use hash of context + param + workflow for uniqueness
        import hashlib

        key = f"{workflow_name}:{parameter_name}:{context}"
        hash_suffix = hashlib.md5(key.encode()).hexdigest()[:8]
        return f"param_{workflow_name}_{parameter_name}_{hash_suffix}"

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
        # Generate embedding for context
        embedding = self._classifier.get_embedding(context)

        # Create record ID
        record_id = self._generate_record_id(context, parameter_name, workflow_name)

        # Prepare metadata
        metadata = {
            "context": context,
            "parameter_name": parameter_name,
            "workflow_name": workflow_name,
            "value": value,
            "value_type": type(value).__name__,
            "usage_count": 1,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        # Create vector record
        record = VectorRecord(
            id=record_id,
            namespace=VectorNamespace.PARAMETERS,
            vector=embedding,
            text=context,
            metadata=metadata,
        )

        # Upsert to vector store
        self._vector_store.upsert([record])

        logger.info(
            f"Stored mapping: '{context}' -> {parameter_name}={value} "
            f"(workflow: {workflow_name})"
        )

    def find_mapping(
        self,
        prompt: str,
        parameter_name: str,
        workflow_name: str,
        similarity_threshold: Optional[float] = None,
    ) -> Optional[StoredMapping]:
        """Find semantically similar stored mapping.

        Uses LaBSE embeddings to find previously learned mappings
        that are semantically similar to the current prompt.

        Args:
            prompt: User prompt to match against stored contexts.
            parameter_name: Name of the parameter to find mapping for.
            workflow_name: Name of the current workflow.
            similarity_threshold: Minimum similarity score (0.0-1.0).
                Uses default if not specified.

        Returns:
            StoredMapping if a similar mapping is found above threshold,
            None otherwise.
        """
        threshold = (
            similarity_threshold
            if similarity_threshold is not None
            else self._similarity_threshold
        )

        # Generate embedding for prompt
        query_embedding = self._classifier.get_embedding(prompt)

        # Search with metadata filter for parameter and workflow
        metadata_filter = {
            "parameter_name": parameter_name,
            "workflow_name": workflow_name,
        }

        results = self._vector_store.search(
            query_vector=query_embedding,
            namespace=VectorNamespace.PARAMETERS,
            top_k=1,
            threshold=threshold,
            metadata_filter=metadata_filter,
        )

        if not results:
            logger.debug(
                f"No mapping found for '{prompt}' -> {parameter_name} "
                f"(workflow: {workflow_name}, threshold: {threshold})"
            )
            return None

        result = results[0]
        metadata = result.metadata

        # Parse created_at if present
        created_at = None
        if metadata.get("created_at"):
            try:
                created_at = datetime.fromisoformat(metadata["created_at"])
            except (ValueError, TypeError):
                pass

        mapping = StoredMapping(
            context=metadata.get("context", result.text),
            value=metadata.get("value"),
            similarity=result.score,
            workflow_name=metadata.get("workflow_name", workflow_name),
            parameter_name=metadata.get("parameter_name", parameter_name),
            usage_count=metadata.get("usage_count", 1),
            created_at=created_at,
        )

        logger.debug(
            f"Found mapping: '{mapping.context}' -> {parameter_name}={mapping.value} "
            f"(similarity: {mapping.similarity:.3f})"
        )

        return mapping

    def increment_usage(self, mapping: StoredMapping) -> None:
        """Increment usage count for a mapping.

        Updates the usage count and last used timestamp for analytics.

        Args:
            mapping: The mapping that was used.
        """
        # Generate record ID to find the record
        record_id = self._generate_record_id(
            mapping.context,
            mapping.parameter_name,
            mapping.workflow_name,
        )

        # Get current embedding
        embedding = self._classifier.get_embedding(mapping.context)

        # Update metadata with incremented usage
        metadata = {
            "context": mapping.context,
            "parameter_name": mapping.parameter_name,
            "workflow_name": mapping.workflow_name,
            "value": mapping.value,
            "value_type": type(mapping.value).__name__,
            "usage_count": mapping.usage_count + 1,
            "created_at": (
                mapping.created_at.isoformat() if mapping.created_at else None
            ),
            "updated_at": datetime.now().isoformat(),
        }

        # Create updated record
        record = VectorRecord(
            id=record_id,
            namespace=VectorNamespace.PARAMETERS,
            vector=embedding,
            text=mapping.context,
            metadata=metadata,
        )

        # Upsert to update
        self._vector_store.upsert([record])

        logger.debug(
            f"Incremented usage for '{mapping.context}' -> "
            f"{mapping.parameter_name} (count: {mapping.usage_count + 1})"
        )

    def clear(self) -> int:
        """Clear all stored parameter mappings.

        Used primarily for testing purposes.

        Returns:
            Number of mappings deleted.
        """
        return self._vector_store.clear(VectorNamespace.PARAMETERS)
