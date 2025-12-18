"""
Vector Store Interface.

Abstract interface for vector storage operations.
Enables O(log N) semantic search with metadata filtering.

TASK-047-1
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional


class VectorNamespace(Enum):
    """Namespace for vector storage.

    Separates tool embeddings from workflow embeddings
    in the same vector database.
    """

    TOOLS = "tools"
    WORKFLOWS = "workflows"
    PARAMETERS = "parameters"  # TASK-055: Learned parameter mappings


@dataclass
class VectorRecord:
    """A single vector record for storage.

    Attributes:
        id: Unique identifier (tool_name or workflow_name).
        namespace: Target namespace (TOOLS or WORKFLOWS).
        vector: Embedding vector (768D for LaBSE).
        text: Original text that was embedded.
        metadata: Additional metadata for filtering.
    """

    id: str
    namespace: VectorNamespace
    vector: List[float]
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowEmbeddingRecord(VectorRecord):
    """Extended record for multi-embedding workflow storage.

    Stores multiple embeddings per workflow with source metadata
    for weighted scoring.

    Attributes:
        workflow_id: Parent workflow name (multiple records share this).
        source_type: Origin of text (sample_prompt, trigger_keyword, description, name).
        source_weight: Weight for scoring (1.0 for prompts, 0.8 for keywords, etc.).
        language: Detected language code (en, pl, de, fr, etc.).
    """

    workflow_id: str = ""
    source_type: str = "sample_prompt"  # sample_prompt | trigger_keyword | description | name
    source_weight: float = 1.0
    language: str = "en"


@dataclass
class WeightedSearchResult:
    """Result from weighted workflow search.

    Attributes:
        workflow_id: Parent workflow identifier.
        raw_score: Raw cosine similarity (0.0 to 1.0).
        source_weight: Weight of matched text source.
        language_boost: Language match boost (1.0 same, 0.9 different).
        final_score: Combined weighted score.
        matched_text: The text that matched best.
        source_type: Type of source that matched.
    """

    workflow_id: str
    raw_score: float
    source_weight: float
    language_boost: float
    final_score: float
    matched_text: str
    source_type: str


@dataclass
class SearchResult:
    """Result from vector similarity search.

    Attributes:
        id: Record identifier.
        score: Similarity score (0.0 to 1.0, higher is better).
        text: Original text.
        metadata: Associated metadata.
    """

    id: str
    score: float
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class IVectorStore(ABC):
    """Abstract interface for vector storage.

    Provides CRUD operations and similarity search
    with namespace isolation and metadata filtering.
    """

    @abstractmethod
    def upsert(self, records: List[VectorRecord]) -> int:
        """Insert or update records.

        If a record with the same ID exists in the namespace,
        it will be replaced.

        Args:
            records: List of records to upsert.

        Returns:
            Number of records affected.
        """
        pass

    @abstractmethod
    def search(
        self,
        query_vector: List[float],
        namespace: VectorNamespace,
        top_k: int = 5,
        threshold: float = 0.0,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search for similar vectors.

        Args:
            query_vector: Query embedding vector.
            namespace: Namespace to search in.
            top_k: Maximum number of results.
            threshold: Minimum similarity score (0.0 to 1.0).
            metadata_filter: Optional metadata constraints.

        Returns:
            List of search results sorted by similarity.
        """
        pass

    @abstractmethod
    def delete(self, ids: List[str], namespace: VectorNamespace) -> int:
        """Delete records by IDs.

        Args:
            ids: List of record IDs to delete.
            namespace: Namespace to delete from.

        Returns:
            Number of records deleted.
        """
        pass

    @abstractmethod
    def count(self, namespace: Optional[VectorNamespace] = None) -> int:
        """Count records in namespace.

        Args:
            namespace: Namespace to count (None for all).

        Returns:
            Number of records.
        """
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics.

        Returns:
            Dictionary with stats (path, counts, etc.).
        """
        pass

    @abstractmethod
    def rebuild_index(self) -> bool:
        """Rebuild the search index.

        Should be called after bulk operations for
        optimal search performance.

        Returns:
            True if rebuild succeeded.
        """
        pass

    @abstractmethod
    def clear(self, namespace: Optional[VectorNamespace] = None) -> int:
        """Clear all records from namespace.

        Args:
            namespace: Namespace to clear (None for all).

        Returns:
            Number of records deleted.
        """
        pass

    @abstractmethod
    def search_workflows_weighted(
        self,
        query_vector: List[float],
        query_language: str = "en",
        top_k: int = 5,
        min_score: float = 0.5,
    ) -> List["WeightedSearchResult"]:
        """Search workflows with weighted scoring.

        Returns best match per workflow using multi-embedding
        with source weight and language boost.

        Scoring formula:
            final_score = raw_cosine_score * source_weight * language_boost

        Where:
            - source_weight: 1.0 (prompt), 0.8 (keyword), 0.6 (desc), 0.5 (name)
            - language_boost: 1.0 (same language), 0.9 (different)

        Args:
            query_vector: Query embedding vector (768D).
            query_language: Detected language of query.
            top_k: Number of workflows to return.
            min_score: Minimum final score threshold.

        Returns:
            List of WeightedSearchResult sorted by final_score.
        """
        pass

    @abstractmethod
    def get_workflow_embedding_count(self) -> int:
        """Get count of workflow embeddings (multiple per workflow).

        Returns:
            Total number of workflow embedding records.
        """
        pass

    @abstractmethod
    def get_unique_workflow_count(self) -> int:
        """Get count of unique workflows.

        Returns:
            Number of distinct workflow_ids.
        """
        pass
