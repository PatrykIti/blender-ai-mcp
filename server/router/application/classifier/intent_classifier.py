"""
Intent Classifier Implementation.

Classifies user prompts to tool names using LaBSE embeddings.
Now uses LanceDB for O(log N) vector search.

TASK-047-4: Integrated with LanceVectorStore
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

from server.router.domain.interfaces.i_intent_classifier import IIntentClassifier
from server.router.domain.interfaces.i_vector_store import (
    IVectorStore,
    VectorNamespace,
    VectorRecord,
)
from server.router.infrastructure.config import RouterConfig

logger = logging.getLogger(__name__)

# Try to import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np

    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    np = None  # type: ignore
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

    Now uses LanceDB for O(log N) vector search instead of linear scan.
    """

    def __init__(
        self,
        config: Optional[RouterConfig] = None,
        vector_store: Optional[IVectorStore] = None,
        model_name: str = MODEL_NAME,
        model: Optional[Any] = None,
    ):
        """Initialize intent classifier.

        Args:
            config: Router configuration (uses defaults if None).
            vector_store: Vector store for embeddings (creates LanceVectorStore if None).
            model_name: Sentence transformer model name.
            model: Pre-loaded SentenceTransformer model (shared via DI).
        """
        self._config = config or RouterConfig()
        self._vector_store = vector_store
        self._model_name = model_name
        self._model: Optional[Any] = model  # Use injected model or load later
        self._tool_texts: Dict[str, List[str]] = {}
        self._is_loaded = False

        # TF-IDF fallback components (used when embeddings unavailable)
        self._tfidf_vectorizer: Optional[Any] = None
        self._tfidf_matrix: Optional[Any] = None
        self._tfidf_tool_names: List[str] = []

    def _ensure_vector_store(self) -> IVectorStore:
        """Lazily create vector store if not injected.

        Returns:
            The vector store instance.
        """
        if self._vector_store is None:
            from server.router.infrastructure.vector_store.lance_store import (
                LanceVectorStore,
            )

            self._vector_store = LanceVectorStore()
        return self._vector_store

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

        Uses LanceDB for O(log N) vector search.

        Args:
            prompt: Natural language prompt.
            k: Number of results to return.

        Returns:
            List of (tool_name, confidence_score) tuples.
        """
        if not self._is_loaded:
            logger.warning("Embeddings not loaded, returning empty results")
            return []

        # Fallback to TF-IDF if embeddings unavailable
        if self._tfidf_vectorizer is not None:
            return self._predict_with_tfidf(prompt, k)

        # Use LanceDB vector search
        if EMBEDDINGS_AVAILABLE and self._model is not None:
            return self._predict_with_vector_store(prompt, k)

        return []

    def _predict_with_vector_store(
        self,
        prompt: str,
        k: int,
    ) -> List[Tuple[str, float]]:
        """Predict using LanceDB vector search.

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
                show_progress_bar=False,
            )

            # Search using LanceDB
            store = self._ensure_vector_store()
            results = store.search(
                query_vector=prompt_embedding.tolist(),
                namespace=VectorNamespace.TOOLS,
                top_k=k,
                threshold=self._config.embedding_threshold,
            )

            return [(r.id, r.score) for r in results]

        except Exception as e:
            logger.error(f"Vector store prediction failed: {e}")
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
                    results.append(
                        (self._tfidf_tool_names[idx], float(similarities[idx]))
                    )

            return results

        except Exception as e:
            logger.error(f"TF-IDF prediction failed: {e}")
            return []

    def load_tool_embeddings(self, metadata: Dict[str, Any]) -> None:
        """Load and cache tool embeddings from metadata.

        Stores embeddings in LanceDB for fast retrieval.

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

        # Check if vector store already has embeddings
        store = self._ensure_vector_store()
        existing_count = store.count(VectorNamespace.TOOLS)

        if existing_count >= len(self._tool_texts):
            logger.info(
                f"Vector store already has {existing_count} tool embeddings"
            )
            self._is_loaded = True
            return

        # Compute and store embeddings if available
        if EMBEDDINGS_AVAILABLE and self._load_model():
            self._compute_and_store_embeddings(metadata)
            if store.count(VectorNamespace.TOOLS) > 0:
                self._is_loaded = True
                return

        # Fallback to TF-IDF
        self._setup_tfidf_fallback()
        self._is_loaded = True

    def _compute_and_store_embeddings(self, metadata: Dict[str, Any]) -> None:
        """Compute embeddings and store in LanceDB.

        Args:
            metadata: Tool metadata for storing alongside vectors.
        """
        if self._model is None:
            return

        logger.info(f"Computing embeddings for {len(self._tool_texts)} tools")

        store = self._ensure_vector_store()
        records = []

        for tool_name, texts in self._tool_texts.items():
            try:
                # Combine texts and encode
                combined = " ".join(texts)
                embedding = self._model.encode(
                    combined,
                    convert_to_numpy=True,
                    normalize_embeddings=True,
                    show_progress_bar=False,
                )

                # Get metadata for this tool
                tool_meta = metadata.get(tool_name, {})

                records.append(
                    VectorRecord(
                        id=tool_name,
                        namespace=VectorNamespace.TOOLS,
                        vector=embedding.tolist(),
                        text=combined,
                        metadata={
                            "keywords": tool_meta.get("keywords", []),
                            "mode_required": tool_meta.get("mode_required"),
                            "category": tool_meta.get("category"),
                        },
                    )
                )

            except Exception as e:
                logger.error(f"Failed to compute embedding for {tool_name}: {e}")

        if records:
            count = store.upsert(records)
            logger.info(f"Stored {count} tool embeddings in LanceDB")

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
                show_progress_bar=False,
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
        if not EMBEDDINGS_AVAILABLE or self._model is None or np is None:
            return 0.0

        try:
            embeddings = self._model.encode(
                [text1, text2],
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
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
        store = self._ensure_vector_store()
        stats = store.get_stats()

        return {
            "model_name": self._model_name,
            "embeddings_available": EMBEDDINGS_AVAILABLE,
            "model_loaded": self._model is not None,
            "num_tools": stats.get("tools_count", 0),
            "is_loaded": self._is_loaded,
            "using_fallback": (
                self._is_loaded
                and self._tfidf_vectorizer is not None
            ),
            "vector_store": {
                "type": "LanceDB",
                "using_fallback": stats.get("using_fallback", False),
                "total_records": stats.get("total_records", 0),
            },
        }

    def clear_cache(self) -> bool:
        """Clear the embedding cache.

        Removes all tool embeddings from LanceDB.

        Returns:
            True if cleared successfully.
        """
        try:
            store = self._ensure_vector_store()
            store.clear(VectorNamespace.TOOLS)
            self._is_loaded = False
            logger.info("Cleared tool embeddings from vector store")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False
