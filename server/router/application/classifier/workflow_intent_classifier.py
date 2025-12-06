"""
Workflow Intent Classifier.

Classifies user prompts to workflows using LaBSE embeddings.
Enables semantic matching and generalization across workflows.
Now uses LanceDB for O(log N) vector search.

TASK-046-2: Initial implementation
TASK-047-4: Integrated with LanceVectorStore, implements IWorkflowIntentClassifier
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

from server.router.domain.interfaces.i_workflow_intent_classifier import (
    IWorkflowIntentClassifier,
)
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
        "Workflow classification will use fallback keyword matching."
    )


# LaBSE model for multilingual embeddings
MODEL_NAME = "sentence-transformers/LaBSE"
EMBEDDING_DIM = 768


class WorkflowIntentClassifier(IWorkflowIntentClassifier):
    """Classifies user prompts to workflows using LaBSE embeddings.

    Implements IWorkflowIntentClassifier interface for Clean Architecture.

    Unlike IntentClassifier (for tools), this classifier:
    - Works with workflow definitions
    - Supports generalization (finding similar workflows)
    - Can combine knowledge from multiple workflows
    - Uses LanceDB for O(log N) vector search
    """

    def __init__(
        self,
        config: Optional[RouterConfig] = None,
        vector_store: Optional[IVectorStore] = None,
        model_name: str = MODEL_NAME,
        model: Optional[Any] = None,
    ):
        """Initialize workflow classifier.

        Args:
            config: Router configuration.
            vector_store: Vector store for embeddings (creates LanceVectorStore if None).
            model_name: Sentence transformer model name.
            model: Pre-loaded SentenceTransformer model (shared via DI).
        """
        self._config = config or RouterConfig()
        self._vector_store = vector_store
        self._model_name = model_name
        self._model: Optional[Any] = model  # Use injected model or load later
        self._workflow_texts: Dict[str, List[str]] = {}
        self._is_loaded = False

        # TF-IDF fallback components
        self._tfidf_vectorizer: Optional[Any] = None
        self._tfidf_matrix: Optional[Any] = None
        self._tfidf_workflow_names: List[str] = []

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
            logger.info("Loading LaBSE model for workflow classification")
            self._model = SentenceTransformer(self._model_name)
            logger.info("LaBSE model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load LaBSE model: {e}")
            return False

    def load_workflow_embeddings(
        self,
        workflows: Dict[str, Any],
    ) -> None:
        """Load and cache workflow embeddings.

        Stores embeddings in LanceDB for fast retrieval.

        Args:
            workflows: Dictionary of workflow name -> workflow object/definition.
        """
        if not workflows:
            logger.warning("No workflows provided for embedding loading")
            return

        # Collect texts for each workflow
        self._workflow_texts = {}
        for name, workflow in workflows.items():
            texts = self._extract_workflow_texts(name, workflow)
            if texts:
                self._workflow_texts[name] = texts

        if not self._workflow_texts:
            logger.warning("No workflow texts extracted for embedding")
            return

        # Check if vector store already has embeddings
        store = self._ensure_vector_store()
        existing_count = store.count(VectorNamespace.WORKFLOWS)

        if existing_count >= len(self._workflow_texts):
            logger.info(
                f"Vector store already has {existing_count} workflow embeddings"
            )
            # Still need to load model for query encoding
            if EMBEDDINGS_AVAILABLE:
                self._load_model()
            self._is_loaded = True
            return

        # Compute and store embeddings if available
        if EMBEDDINGS_AVAILABLE and self._load_model():
            self._compute_and_store_embeddings(workflows)
            if store.count(VectorNamespace.WORKFLOWS) > 0:
                self._is_loaded = True
                return

        # Fallback to TF-IDF
        self._setup_tfidf_fallback()
        self._is_loaded = True

    def _extract_workflow_texts(
        self,
        name: str,
        workflow: Any,
    ) -> List[str]:
        """Extract texts from workflow for embedding.

        Args:
            name: Workflow name.
            workflow: Workflow object or definition dict.

        Returns:
            List of texts for embedding.
        """
        texts = []

        # Get sample prompts (primary source)
        if hasattr(workflow, "sample_prompts"):
            texts.extend(workflow.sample_prompts)
        elif isinstance(workflow, dict) and "sample_prompts" in workflow:
            texts.extend(workflow["sample_prompts"])

        # Get trigger keywords
        if hasattr(workflow, "trigger_keywords"):
            texts.extend(workflow.trigger_keywords)
        elif isinstance(workflow, dict) and "trigger_keywords" in workflow:
            texts.extend(workflow["trigger_keywords"])

        # Add workflow name (replace underscores with spaces)
        texts.append(name.replace("_", " "))

        # Add description
        if hasattr(workflow, "description"):
            texts.append(workflow.description)
        elif isinstance(workflow, dict) and "description" in workflow:
            texts.append(workflow["description"])

        return texts

    def _compute_and_store_embeddings(self, workflows: Dict[str, Any]) -> None:
        """Compute embeddings and store in LanceDB.

        Args:
            workflows: Workflow definitions for metadata extraction.
        """
        if self._model is None:
            return

        logger.info(f"Computing embeddings for {len(self._workflow_texts)} workflows")

        store = self._ensure_vector_store()
        records = []

        for name, texts in self._workflow_texts.items():
            try:
                # Combine all texts and encode
                combined = " ".join(texts)
                embedding = self._model.encode(
                    combined,
                    convert_to_numpy=True,
                    normalize_embeddings=True,
                    show_progress_bar=False,
                )

                # Extract metadata from workflow
                workflow = workflows.get(name, {})
                metadata = {}

                if hasattr(workflow, "category"):
                    metadata["category"] = workflow.category
                elif isinstance(workflow, dict):
                    metadata["category"] = workflow.get("category")

                if hasattr(workflow, "trigger_keywords"):
                    metadata["trigger_keywords"] = workflow.trigger_keywords
                elif isinstance(workflow, dict):
                    metadata["trigger_keywords"] = workflow.get("trigger_keywords", [])

                records.append(
                    VectorRecord(
                        id=name,
                        namespace=VectorNamespace.WORKFLOWS,
                        vector=embedding.tolist(),
                        text=combined,
                        metadata=metadata,
                    )
                )

            except Exception as e:
                logger.error(f"Failed to compute embedding for {name}: {e}")

        if records:
            count = store.upsert(records)
            logger.info(f"Stored {count} workflow embeddings in LanceDB")

    def _setup_tfidf_fallback(self) -> None:
        """Setup TF-IDF fallback when embeddings unavailable."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer

            documents = []
            workflow_names = []

            for name, texts in self._workflow_texts.items():
                combined = " ".join(texts)
                documents.append(combined)
                workflow_names.append(name)

            if not documents:
                return

            self._tfidf_vectorizer = TfidfVectorizer(
                lowercase=True,
                ngram_range=(1, 2),
                max_features=5000,
            )
            self._tfidf_matrix = self._tfidf_vectorizer.fit_transform(documents)
            self._tfidf_workflow_names = workflow_names

            logger.info(
                f"TF-IDF fallback initialized with {len(workflow_names)} workflows"
            )

        except ImportError:
            logger.warning("sklearn not available for TF-IDF fallback")
        except Exception as e:
            logger.error(f"Failed to setup TF-IDF fallback: {e}")

    def find_similar(
        self,
        prompt: str,
        top_k: int = 3,
        threshold: float = 0.0,
    ) -> List[Tuple[str, float]]:
        """Find workflows semantically similar to prompt.

        Uses LanceDB for O(log N) vector search.

        Args:
            prompt: User prompt or intent.
            top_k: Number of results to return.
            threshold: Minimum similarity score.

        Returns:
            List of (workflow_name, similarity_score) tuples.
        """
        if not self._is_loaded:
            logger.warning("Workflow embeddings not loaded, returning empty results")
            return []

        # Use config threshold if none provided
        if threshold == 0.0:
            threshold = self._config.workflow_similarity_threshold

        # Try embeddings first
        if EMBEDDINGS_AVAILABLE and self._model is not None:
            return self._find_similar_with_vector_store(prompt, top_k, threshold)

        # Fallback to TF-IDF
        if self._tfidf_vectorizer is not None:
            return self._find_similar_with_tfidf(prompt, top_k, threshold)

        return []

    def _find_similar_with_vector_store(
        self,
        prompt: str,
        top_k: int,
        threshold: float,
    ) -> List[Tuple[str, float]]:
        """Find similar workflows using LanceDB vector search."""
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
                namespace=VectorNamespace.WORKFLOWS,
                top_k=top_k,
                threshold=threshold,
            )

            return [(r.id, r.score) for r in results]

        except Exception as e:
            logger.error(f"Vector store similarity search failed: {e}")
            return []

    def _find_similar_with_tfidf(
        self,
        prompt: str,
        top_k: int,
        threshold: float,
    ) -> List[Tuple[str, float]]:
        """Find similar workflows using TF-IDF fallback."""
        try:
            from sklearn.metrics.pairwise import cosine_similarity

            prompt_vec = self._tfidf_vectorizer.transform([prompt])
            similarities = cosine_similarity(prompt_vec, self._tfidf_matrix)[0]

            results = []
            for idx, sim in enumerate(similarities):
                if sim >= threshold:
                    results.append((self._tfidf_workflow_names[idx], float(sim)))

            results.sort(key=lambda x: x[1], reverse=True)
            return results[:top_k]

        except Exception as e:
            logger.error(f"TF-IDF similarity search failed: {e}")
            return []

    def find_best_match(
        self,
        prompt: str,
        min_confidence: float = 0.5,
    ) -> Optional[Tuple[str, float]]:
        """Find the best matching workflow.

        Args:
            prompt: User prompt.
            min_confidence: Minimum confidence score.

        Returns:
            (workflow_name, confidence) or None.
        """
        results = self.find_similar(prompt, top_k=1, threshold=min_confidence)
        return results[0] if results else None

    def get_generalization_candidates(
        self,
        prompt: str,
        min_similarity: float = 0.3,
        max_candidates: int = 3,
    ) -> List[Tuple[str, float]]:
        """Get workflows that could be generalized for this prompt.

        Used when no exact match exists. Returns workflows that
        share semantic concepts with the prompt.

        Args:
            prompt: User prompt.
            min_similarity: Minimum similarity to consider.
            max_candidates: Maximum workflows to return.

        Returns:
            List of (workflow_name, similarity) tuples.
        """
        # Use generalization threshold from config if not specified
        if min_similarity == 0.3:
            min_similarity = self._config.generalization_threshold

        return self.find_similar(
            prompt,
            top_k=max_candidates,
            threshold=min_similarity,
        )

    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding vector for a text.

        Args:
            text: Text to embed.

        Returns:
            Embedding vector or None if not available.
        """
        if not EMBEDDINGS_AVAILABLE or self._model is None:
            return None

        try:
            embedding = self._model.encode(
                text,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            return embedding.tolist()
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
            return float(np.dot(embeddings[0], embeddings[1]))
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return 0.0

    def is_loaded(self) -> bool:
        """Check if classifier is loaded.

        Returns:
            True if workflow embeddings are loaded.
        """
        return self._is_loaded

    def get_info(self) -> Dict[str, Any]:
        """Get classifier information.

        Returns:
            Dictionary with classifier information.
        """
        store = self._ensure_vector_store()
        stats = store.get_stats()

        return {
            "model_name": self._model_name,
            "embeddings_available": EMBEDDINGS_AVAILABLE,
            "model_loaded": self._model is not None,
            "num_workflows": stats.get("workflows_count", 0),
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

        Removes all workflow embeddings from LanceDB.

        Returns:
            True if cleared successfully.
        """
        try:
            store = self._ensure_vector_store()
            store.clear(VectorNamespace.WORKFLOWS)
            self._is_loaded = False
            logger.info("Cleared workflow embeddings from vector store")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False
