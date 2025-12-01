"""
Intent Classifier Implementation.

Classifies user prompts to tool names using LaBSE embeddings.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

from server.router.domain.interfaces.i_intent_classifier import IIntentClassifier
from server.router.application.classifier.embedding_cache import EmbeddingCache
from server.router.infrastructure.config import RouterConfig

logger = logging.getLogger(__name__)

# Try to import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logger.warning(
        "sentence-transformers not installed. "
        "Intent classification will use fallback TF-IDF matching."
    )


# LaBSE model for multilingual embeddings
MODEL_NAME = "sentence-transformers/LaBSE"
EMBEDDING_DIM = 768


class IntentClassifier(IIntentClassifier):
    """Implementation of intent classification using LaBSE embeddings.

    Uses Language-agnostic BERT Sentence Embedding (LaBSE) for
    multilingual semantic similarity matching against tool descriptions.
    """

    def __init__(
        self,
        config: Optional[RouterConfig] = None,
        cache_dir: Optional[Path] = None,
        model_name: str = MODEL_NAME,
    ):
        """Initialize intent classifier.

        Args:
            config: Router configuration (uses defaults if None).
            cache_dir: Directory for embedding cache.
            model_name: Sentence transformer model name.
        """
        self._config = config or RouterConfig()
        self._cache = EmbeddingCache(cache_dir)
        self._model_name = model_name
        self._model: Optional[Any] = None
        self._tool_embeddings: Dict[str, Any] = {}
        self._tool_texts: Dict[str, List[str]] = {}
        self._is_loaded = False

        # TF-IDF fallback components
        self._tfidf_vectorizer: Optional[Any] = None
        self._tfidf_matrix: Optional[Any] = None
        self._tfidf_tool_names: List[str] = []

    def _load_model(self) -> bool:
        """Load the sentence transformer model.

        Returns:
            True if model loaded successfully.
        """
        if not EMBEDDINGS_AVAILABLE:
            return False

        if self._model is not None:
            return True

        try:
            logger.info(f"Loading sentence transformer model: {self._model_name}")
            self._model = SentenceTransformer(self._model_name)
            logger.info("Model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False

    def predict(self, prompt: str) -> Tuple[str, float]:
        """Predict the best matching tool for a prompt.

        Args:
            prompt: Natural language prompt.

        Returns:
            Tuple of (tool_name, confidence_score).
        """
        results = self.predict_top_k(prompt, k=1)
        if results:
            return results[0]
        return ("", 0.0)

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
        if not self._is_loaded:
            logger.warning("Embeddings not loaded, returning empty results")
            return []

        # Try embeddings first
        if EMBEDDINGS_AVAILABLE and self._model is not None and self._tool_embeddings:
            return self._predict_with_embeddings(prompt, k)

        # Fallback to TF-IDF
        if self._tfidf_vectorizer is not None:
            return self._predict_with_tfidf(prompt, k)

        return []

    def _predict_with_embeddings(
        self,
        prompt: str,
        k: int,
    ) -> List[Tuple[str, float]]:
        """Predict using LaBSE embeddings.

        Args:
            prompt: Natural language prompt.
            k: Number of results.

        Returns:
            List of (tool_name, confidence_score) tuples.
        """
        if self._model is None:
            return []

        try:
            # Get prompt embedding
            prompt_embedding = self._model.encode(
                prompt,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )

            # Calculate similarities
            similarities = []
            for tool_name, tool_embedding in self._tool_embeddings.items():
                # Cosine similarity (embeddings are normalized)
                sim = float(np.dot(prompt_embedding, tool_embedding))
                similarities.append((tool_name, sim))

            # Sort by similarity
            similarities.sort(key=lambda x: x[1], reverse=True)

            # Apply threshold
            threshold = self._config.embedding_threshold
            filtered = [(t, s) for t, s in similarities if s >= threshold]

            return filtered[:k]

        except Exception as e:
            logger.error(f"Embedding prediction failed: {e}")
            return []

    def _predict_with_tfidf(
        self,
        prompt: str,
        k: int,
    ) -> List[Tuple[str, float]]:
        """Predict using TF-IDF fallback.

        Args:
            prompt: Natural language prompt.
            k: Number of results.

        Returns:
            List of (tool_name, confidence_score) tuples.
        """
        try:
            from sklearn.metrics.pairwise import cosine_similarity

            # Transform prompt
            prompt_vec = self._tfidf_vectorizer.transform([prompt])

            # Calculate similarities
            similarities = cosine_similarity(prompt_vec, self._tfidf_matrix)[0]

            # Get top k
            top_indices = similarities.argsort()[::-1][:k]

            results = []
            for idx in top_indices:
                if similarities[idx] > 0:
                    results.append((self._tfidf_tool_names[idx], float(similarities[idx])))

            return results

        except Exception as e:
            logger.error(f"TF-IDF prediction failed: {e}")
            return []

    def load_tool_embeddings(self, metadata: Dict[str, Any]) -> None:
        """Load and cache tool embeddings from metadata.

        Args:
            metadata: Tool metadata with sample_prompts.
        """
        if not metadata:
            logger.warning("No metadata provided for embedding loading")
            return

        # Collect texts for each tool
        self._tool_texts = {}
        for tool_name, tool_meta in metadata.items():
            texts = []

            # Add sample prompts
            sample_prompts = tool_meta.get("sample_prompts", [])
            texts.extend(sample_prompts)

            # Add keywords as text
            keywords = tool_meta.get("keywords", [])
            if keywords:
                texts.append(" ".join(keywords))

            # Add tool name (replace underscores with spaces)
            texts.append(tool_name.replace("_", " "))

            if texts:
                self._tool_texts[tool_name] = texts

        # Try to load from cache
        metadata_hash = EmbeddingCache.compute_metadata_hash(metadata)
        if self._cache.is_valid(metadata_hash):
            cached = self._cache.load()
            if cached:
                self._tool_embeddings = cached
                self._is_loaded = True
                logger.info(f"Loaded {len(cached)} tool embeddings from cache")
                return

        # Compute embeddings if available
        if EMBEDDINGS_AVAILABLE and self._load_model():
            self._compute_embeddings()
            if self._tool_embeddings:
                self._cache.save(self._tool_embeddings, metadata_hash)
                self._is_loaded = True
                return

        # Fallback to TF-IDF
        self._setup_tfidf_fallback()
        self._is_loaded = True

    def _compute_embeddings(self) -> None:
        """Compute embeddings for all tools."""
        if self._model is None:
            return

        logger.info(f"Computing embeddings for {len(self._tool_texts)} tools")

        for tool_name, texts in self._tool_texts.items():
            try:
                # Combine texts and encode
                combined = " ".join(texts)
                embedding = self._model.encode(
                    combined,
                    convert_to_numpy=True,
                    normalize_embeddings=True,
                )
                self._tool_embeddings[tool_name] = embedding

            except Exception as e:
                logger.error(f"Failed to compute embedding for {tool_name}: {e}")

        logger.info(f"Computed {len(self._tool_embeddings)} tool embeddings")

    def _setup_tfidf_fallback(self) -> None:
        """Setup TF-IDF fallback when embeddings unavailable."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer

            # Prepare documents
            documents = []
            tool_names = []

            for tool_name, texts in self._tool_texts.items():
                combined = " ".join(texts)
                documents.append(combined)
                tool_names.append(tool_name)

            if not documents:
                return

            # Fit TF-IDF
            self._tfidf_vectorizer = TfidfVectorizer(
                lowercase=True,
                ngram_range=(1, 2),
                max_features=5000,
            )
            self._tfidf_matrix = self._tfidf_vectorizer.fit_transform(documents)
            self._tfidf_tool_names = tool_names

            logger.info(f"TF-IDF fallback initialized with {len(tool_names)} tools")

        except ImportError:
            logger.warning("sklearn not available for TF-IDF fallback")
        except Exception as e:
            logger.error(f"Failed to setup TF-IDF fallback: {e}")

    def is_loaded(self) -> bool:
        """Check if embeddings are loaded.

        Returns:
            True if tool embeddings are loaded.
        """
        return self._is_loaded

    def get_embedding(self, text: str) -> Optional[Any]:
        """Get embedding for a text.

        Args:
            text: Text to embed.

        Returns:
            Embedding vector or None if not available.
        """
        if not EMBEDDINGS_AVAILABLE or self._model is None:
            return None

        try:
            return self._model.encode(
                text,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )
        except Exception as e:
            logger.error(f"Failed to get embedding: {e}")
            return None

    def similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts.

        Args:
            text1: First text.
            text2: Second text.

        Returns:
            Similarity score (0.0 to 1.0).
        """
        if not EMBEDDINGS_AVAILABLE or self._model is None:
            return 0.0

        try:
            embeddings = self._model.encode(
                [text1, text2],
                convert_to_numpy=True,
                normalize_embeddings=True,
            )
            # Cosine similarity of normalized vectors
            return float(np.dot(embeddings[0], embeddings[1]))
        except Exception as e:
            logger.error(f"Failed to compute similarity: {e}")
            return 0.0

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model.

        Returns:
            Dictionary with model information.
        """
        return {
            "model_name": self._model_name,
            "embeddings_available": EMBEDDINGS_AVAILABLE,
            "model_loaded": self._model is not None,
            "num_tools": len(self._tool_embeddings),
            "is_loaded": self._is_loaded,
            "using_fallback": (
                self._is_loaded
                and not self._tool_embeddings
                and self._tfidf_vectorizer is not None
            ),
            "cache_size_bytes": self._cache.get_cache_size(),
        }

    def clear_cache(self) -> bool:
        """Clear the embedding cache.

        Returns:
            True if cleared successfully.
        """
        return self._cache.clear()
