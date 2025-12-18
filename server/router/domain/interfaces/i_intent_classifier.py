"""
Intent Classifier Interface.

Abstract interface for classifying user intent to tools.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Optional


class IIntentClassifier(ABC):
    """Abstract interface for intent classification.

    Classifies natural language prompts to tool names using embeddings.
    """

    @abstractmethod
    def predict(self, prompt: str) -> Tuple[str, float]:
        """Predict the best matching tool for a prompt.

        Args:
            prompt: Natural language prompt.

        Returns:
            Tuple of (tool_name, confidence_score).
        """
        pass

    @abstractmethod
    def predict_top_k(
        self,
        prompt: str,
        k: int = 5,
    ) -> List[Tuple[str, float]]:
        """Predict top K matching tools for a prompt.

        Args:
            prompt: Natural language prompt.
            k: Number of results to return.

        Returns:
            List of (tool_name, confidence_score) tuples.
        """
        pass

    @abstractmethod
    def load_tool_embeddings(self, metadata: Dict[str, Any]) -> None:
        """Load and cache tool embeddings from metadata.

        Args:
            metadata: Tool metadata with sample_prompts.
        """
        pass

    @abstractmethod
    def is_loaded(self) -> bool:
        """Check if embeddings are loaded.

        Returns:
            True if tool embeddings are loaded.
        """
        pass

    @abstractmethod
    def get_embedding(self, text: str) -> Optional[Any]:
        """Get embedding for a text.

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
