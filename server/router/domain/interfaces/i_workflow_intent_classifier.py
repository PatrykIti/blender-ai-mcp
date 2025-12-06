"""
Workflow Intent Classifier Interface.

Abstract interface for workflow intent classification.
Enables semantic matching and generalization across workflows.

TASK-047-1
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Optional


class IWorkflowIntentClassifier(ABC):
    """Abstract interface for workflow intent classification.

    Enables semantic matching of user prompts to workflow definitions.
    Supports workflow generalization for unknown object types.

    Unlike IIntentClassifier (for tools), this interface:
    - Works with workflow definitions (not tool metadata)
    - Supports generalization (finding similar workflows)
    - Can combine knowledge from multiple workflows
    """

    @abstractmethod
    def load_workflow_embeddings(self, workflows: Dict[str, Any]) -> None:
        """Load and cache workflow embeddings.

        Extracts sample_prompts, trigger_keywords, and descriptions
        from workflow definitions to build embeddings.

        Args:
            workflows: Dictionary of workflow name -> workflow object/definition.
        """
        pass

    @abstractmethod
    def find_similar(
        self,
        prompt: str,
        top_k: int = 3,
        threshold: float = 0.0,
    ) -> List[Tuple[str, float]]:
        """Find workflows semantically similar to prompt.

        Args:
            prompt: User prompt or intent.
            top_k: Number of results to return.
            threshold: Minimum similarity score (0.0 to 1.0).

        Returns:
            List of (workflow_name, similarity_score) tuples,
            sorted by similarity descending.
        """
        pass

    @abstractmethod
    def find_best_match(
        self,
        prompt: str,
        min_confidence: float = 0.5,
    ) -> Optional[Tuple[str, float]]:
        """Find the best matching workflow.

        Args:
            prompt: User prompt.
            min_confidence: Minimum confidence score to return a match.

        Returns:
            (workflow_name, confidence) or None if no match above threshold.
        """
        pass

    @abstractmethod
    def get_generalization_candidates(
        self,
        prompt: str,
        min_similarity: float = 0.3,
        max_candidates: int = 3,
    ) -> List[Tuple[str, float]]:
        """Get workflows that could be generalized for this prompt.

        Used when no exact match exists. Returns workflows that
        share semantic concepts with the prompt and could serve
        as templates for generalization.

        Args:
            prompt: User prompt.
            min_similarity: Minimum similarity to consider.
            max_candidates: Maximum workflows to return.

        Returns:
            List of (workflow_name, similarity) tuples.
        """
        pass

    @abstractmethod
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding vector for a text.

        Args:
            text: Text to embed.

        Returns:
            Embedding vector or None if not available.
        """
        pass

    @abstractmethod
    def similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts.

        Args:
            text1: First text.
            text2: Second text.

        Returns:
            Similarity score (0.0 to 1.0).
        """
        pass

    @abstractmethod
    def is_loaded(self) -> bool:
        """Check if classifier is loaded and ready.

        Returns:
            True if workflow embeddings are loaded.
        """
        pass

    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """Get classifier information.

        Returns:
            Dictionary with model info, status, counts.
        """
        pass

    @abstractmethod
    def clear_cache(self) -> bool:
        """Clear the embedding cache.

        Returns:
            True if cleared successfully.
        """
        pass
