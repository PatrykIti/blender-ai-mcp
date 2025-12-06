"""
Workflow Intent Classifier.

Classifies user prompts to workflows using LaBSE embeddings.
Enables semantic matching and generalization across workflows.

TASK-046-2
"""

import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Union

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


class WorkflowEmbeddingCache:
    """Cache for workflow embeddings.

    Separate from tool embedding cache to avoid conflicts.
    """

    def __init__(self, cache_dir: Optional[Path] = None, prefix: str = "workflow_"):
        """Initialize embedding cache.

        Args:
            cache_dir: Directory for cache files.
            prefix: Prefix for cache files.
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".cache" / "blender-ai-mcp" / "router"
        self._cache_dir = Path(cache_dir)
        self._prefix = prefix
        self._cache_file = self._cache_dir / f"{prefix}embeddings.pkl"
        self._hash_file = self._cache_dir / f"{prefix}hash.txt"
        self._ensure_cache_dir()

    def _ensure_cache_dir(self) -> None:
        """Ensure cache directory exists."""
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def save(self, embeddings: Dict[str, Any], metadata_hash: str) -> bool:
        """Save embeddings to cache."""
        if not EMBEDDINGS_AVAILABLE:
            return False

        try:
            import pickle

            with open(self._cache_file, "wb") as f:
                pickle.dump(embeddings, f)

            with open(self._hash_file, "w") as f:
                f.write(metadata_hash)

            logger.info(f"Saved {len(embeddings)} workflow embeddings to cache")
            return True

        except Exception as e:
            logger.error(f"Failed to save workflow embeddings cache: {e}")
            return False

    def load(self) -> Optional[Dict[str, Any]]:
        """Load embeddings from cache."""
        if not EMBEDDINGS_AVAILABLE or not self._cache_file.exists():
            return None

        try:
            import pickle

            with open(self._cache_file, "rb") as f:
                embeddings = pickle.load(f)

            logger.info(f"Loaded {len(embeddings)} workflow embeddings from cache")
            return embeddings

        except Exception as e:
            logger.error(f"Failed to load workflow embeddings cache: {e}")
            return None

    def is_valid(self, metadata_hash: str) -> bool:
        """Check if cache is valid for given metadata."""
        if not self._cache_file.exists() or not self._hash_file.exists():
            return False

        try:
            with open(self._hash_file, "r") as f:
                cached_hash = f.read().strip()
            return cached_hash == metadata_hash

        except Exception:
            return False

    def clear(self) -> bool:
        """Clear the cache."""
        try:
            if self._cache_file.exists():
                self._cache_file.unlink()
            if self._hash_file.exists():
                self._hash_file.unlink()
            logger.info("Cleared workflow embeddings cache")
            return True
        except Exception as e:
            logger.error(f"Failed to clear workflow cache: {e}")
            return False

    @staticmethod
    def compute_hash(workflows: Dict[str, Any]) -> str:
        """Compute hash of workflows for cache validation."""
        # Create a string representation of workflow sample_prompts
        content_parts = []
        for name in sorted(workflows.keys()):
            workflow = workflows[name]
            prompts = []
            if hasattr(workflow, "sample_prompts"):
                prompts = workflow.sample_prompts
            elif isinstance(workflow, dict) and "sample_prompts" in workflow:
                prompts = workflow["sample_prompts"]
            content_parts.append(f"{name}:{','.join(sorted(prompts))}")

        content = "|".join(content_parts)
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class WorkflowIntentClassifier:
    """Classifies user prompts to workflows using LaBSE embeddings.

    Unlike IntentClassifier (for tools), this classifier:
    - Works with workflow definitions
    - Supports generalization (finding similar workflows)
    - Can combine knowledge from multiple workflows
    - Uses separate cache from tool embeddings
    """

    def __init__(
        self,
        config: Optional[RouterConfig] = None,
        cache_dir: Optional[Path] = None,
        model_name: str = MODEL_NAME,
    ):
        """Initialize workflow classifier.

        Args:
            config: Router configuration.
            cache_dir: Directory for embedding cache.
            model_name: Sentence transformer model name.
        """
        self._config = config or RouterConfig()
        self._cache = WorkflowEmbeddingCache(cache_dir, prefix="workflow_")
        self._model_name = model_name
        self._model: Optional[Any] = None
        self._workflow_embeddings: Dict[str, Any] = {}
        self._workflow_texts: Dict[str, List[str]] = {}
        self._is_loaded = False

        # TF-IDF fallback components
        self._tfidf_vectorizer: Optional[Any] = None
        self._tfidf_matrix: Optional[Any] = None
        self._tfidf_workflow_names: List[str] = []

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
            logger.info(f"Loading LaBSE model for workflow classification")
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

        # Try to load from cache
        metadata_hash = WorkflowEmbeddingCache.compute_hash(workflows)
        if self._cache.is_valid(metadata_hash):
            cached = self._cache.load()
            if cached:
                self._workflow_embeddings = cached
                self._is_loaded = True
                logger.info(
                    f"Loaded {len(cached)} workflow embeddings from cache"
                )
                return

        # Compute embeddings if available
        if EMBEDDINGS_AVAILABLE and self._load_model():
            self._compute_embeddings()
            if self._workflow_embeddings:
                self._cache.save(self._workflow_embeddings, metadata_hash)
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

    def _compute_embeddings(self) -> None:
        """Compute embeddings for all workflows."""
        if self._model is None:
            return

        logger.info(f"Computing embeddings for {len(self._workflow_texts)} workflows")

        for name, texts in self._workflow_texts.items():
            try:
                # Combine all texts and encode
                combined = " ".join(texts)
                embedding = self._model.encode(
                    combined,
                    convert_to_numpy=True,
                    normalize_embeddings=True,
                )
                self._workflow_embeddings[name] = embedding

            except Exception as e:
                logger.error(f"Failed to compute embedding for {name}: {e}")

        logger.info(f"Computed {len(self._workflow_embeddings)} workflow embeddings")

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

        # Try embeddings first
        if EMBEDDINGS_AVAILABLE and self._model is not None and self._workflow_embeddings:
            return self._find_similar_with_embeddings(prompt, top_k, threshold)

        # Fallback to TF-IDF
        if self._tfidf_vectorizer is not None:
            return self._find_similar_with_tfidf(prompt, top_k, threshold)

        return []

    def _find_similar_with_embeddings(
        self,
        prompt: str,
        top_k: int,
        threshold: float,
    ) -> List[Tuple[str, float]]:
        """Find similar workflows using LaBSE embeddings."""
        if self._model is None or np is None:
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
            for name, workflow_embedding in self._workflow_embeddings.items():
                # Cosine similarity (embeddings are normalized)
                sim = float(np.dot(prompt_embedding, workflow_embedding))
                if sim >= threshold:
                    similarities.append((name, sim))

            # Sort by similarity
            similarities.sort(key=lambda x: x[1], reverse=True)

            return similarities[:top_k]

        except Exception as e:
            logger.error(f"Embedding similarity search failed: {e}")
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
        return self.find_similar(
            prompt,
            top_k=max_candidates,
            threshold=min_similarity,
        )

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
        if not EMBEDDINGS_AVAILABLE or self._model is None or np is None:
            return 0.0

        try:
            embeddings = self._model.encode(
                [text1, text2],
                convert_to_numpy=True,
                normalize_embeddings=True,
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
        return {
            "model_name": self._model_name,
            "embeddings_available": EMBEDDINGS_AVAILABLE,
            "model_loaded": self._model is not None,
            "num_workflows": len(self._workflow_embeddings),
            "is_loaded": self._is_loaded,
            "using_fallback": (
                self._is_loaded
                and not self._workflow_embeddings
                and self._tfidf_vectorizer is not None
            ),
        }

    def clear_cache(self) -> bool:
        """Clear the embedding cache.

        Returns:
            True if cleared successfully.
        """
        return self._cache.clear()
