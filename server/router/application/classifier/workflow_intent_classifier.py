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
    WeightedSearchResult,
    WorkflowEmbeddingRecord,
)
from server.router.infrastructure.language_detector import detect_language

# Source type weights for scoring
SOURCE_WEIGHTS = {
    "sample_prompt": 1.0,
    "trigger_keyword": 0.8,
    "description": 0.6,
    "name": 0.5,
}

# TASK-050-5: Confidence levels and thresholds
CONFIDENCE_THRESHOLDS = {
    "HIGH": 0.90,      # >= 0.90: High confidence, direct match
    "MEDIUM": 0.75,    # >= 0.75: Medium confidence, likely match
    "LOW": 0.60,       # >= 0.60: Low confidence, possible match
    "NONE": 0.0,       # < 0.60: No confidence, fallback to generalization
}

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
            import os

            if os.getenv("PYTEST_CURRENT_TEST") is not None:
                logger.info("Skipping LaBSE load under pytest")
                return False

            local_only = os.getenv("HF_HUB_OFFLINE", "").lower() in ("1", "true", "yes")
            logger.info("Loading LaBSE model for workflow classification")
            self._model = SentenceTransformer(
                self._model_name,
                local_files_only=local_only,
            )
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
        # TASK-050-3: Compare unique workflows, not total records (multi-embedding)
        store = self._ensure_vector_store()
        unique_workflows = store.get_unique_workflow_count()

        if unique_workflows >= len(self._workflow_texts):
            logger.info(
                f"Vector store already has {unique_workflows} workflows "
                f"({store.get_workflow_embedding_count()} total embeddings)"
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
        """Extract texts from workflow for embedding (legacy method).

        Args:
            name: Workflow name.
            workflow: Workflow object or definition dict.

        Returns:
            List of texts for embedding.
        """
        # Use new method and extract just texts
        texts_with_meta = self._extract_texts_with_metadata(name, workflow)
        return [text for text, _, _ in texts_with_meta]

    def _extract_texts_with_metadata(
        self,
        name: str,
        workflow: Any,
    ) -> List[Tuple[str, str, float]]:
        """Extract texts from workflow with source type and weight.

        TASK-050-3: Multi-embedding support.

        Args:
            name: Workflow name.
            workflow: Workflow object or definition dict.

        Returns:
            List of (text, source_type, weight) tuples.
        """
        texts_with_meta: List[Tuple[str, str, float]] = []

        # Get sample prompts (highest weight - 1.0)
        sample_prompts = []
        if hasattr(workflow, "sample_prompts"):
            sample_prompts = workflow.sample_prompts
        elif isinstance(workflow, dict) and "sample_prompts" in workflow:
            sample_prompts = workflow["sample_prompts"]

        for prompt in sample_prompts:
            texts_with_meta.append(
                (prompt, "sample_prompt", SOURCE_WEIGHTS["sample_prompt"])
            )

        # Get trigger keywords (weight 0.8)
        trigger_keywords = []
        if hasattr(workflow, "trigger_keywords"):
            trigger_keywords = workflow.trigger_keywords
        elif isinstance(workflow, dict) and "trigger_keywords" in workflow:
            trigger_keywords = workflow["trigger_keywords"]

        for keyword in trigger_keywords:
            texts_with_meta.append(
                (keyword, "trigger_keyword", SOURCE_WEIGHTS["trigger_keyword"])
            )

        # Add workflow name (weight 0.5)
        name_text = name.replace("_", " ")
        texts_with_meta.append(
            (name_text, "name", SOURCE_WEIGHTS["name"])
        )

        # Add description (weight 0.6)
        description = None
        if hasattr(workflow, "description"):
            description = workflow.description
        elif isinstance(workflow, dict) and "description" in workflow:
            description = workflow["description"]

        if description:
            texts_with_meta.append(
                (description, "description", SOURCE_WEIGHTS["description"])
            )

        return texts_with_meta

    def _compute_and_store_embeddings(self, workflows: Dict[str, Any]) -> None:
        """Compute embeddings and store in LanceDB.

        TASK-050-3: Multi-embedding - creates separate embedding for each text.

        Args:
            workflows: Workflow definitions for metadata extraction.
        """
        if self._model is None:
            return

        logger.info(f"Computing multi-embeddings for {len(workflows)} workflows")

        store = self._ensure_vector_store()
        records: List[VectorRecord] = []
        total_embeddings = 0

        for name, workflow in workflows.items():
            try:
                # Extract texts with metadata
                texts_with_meta = self._extract_texts_with_metadata(name, workflow)

                # Extract workflow-level metadata
                category = None
                if hasattr(workflow, "category"):
                    category = workflow.category
                elif isinstance(workflow, dict):
                    category = workflow.get("category")

                # Create separate embedding for each text
                for idx, (text, source_type, weight) in enumerate(texts_with_meta):
                    # Detect language
                    language = detect_language(text)

                    # Compute embedding
                    embedding = self._model.encode(
                        text,
                        convert_to_numpy=True,
                        normalize_embeddings=True,
                        show_progress_bar=False,
                    )

                    # Create unique ID: workflow_name__source_type__index
                    record_id = f"{name}__{source_type}__{idx}"

                    # Build metadata for weighted search
                    metadata = {
                        "workflow_id": name,
                        "source_type": source_type,
                        "source_weight": weight,
                        "language": language,
                    }
                    if category:
                        metadata["category"] = category

                    records.append(
                        VectorRecord(
                            id=record_id,
                            namespace=VectorNamespace.WORKFLOWS,
                            vector=embedding.tolist(),
                            text=text,
                            metadata=metadata,
                        )
                    )
                    total_embeddings += 1

            except Exception as e:
                logger.error(f"Failed to compute embeddings for {name}: {e}")

        if records:
            count = store.upsert(records)
            logger.info(
                f"Stored {count} workflow embeddings "
                f"({total_embeddings} texts from {len(workflows)} workflows)"
            )

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
        """Find similar workflows using LanceDB weighted vector search.

        TASK-050-3/4: Uses multi-embedding with weighted scoring.
        """
        if self._model is None:
            return []

        try:
            # Detect query language for language boost
            query_language = detect_language(prompt)

            # Get prompt embedding
            prompt_embedding = self._model.encode(
                prompt,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )

            # Search using weighted multi-embedding search
            store = self._ensure_vector_store()
            results = store.search_workflows_weighted(
                query_vector=prompt_embedding.tolist(),
                query_language=query_language,
                top_k=top_k,
                min_score=threshold,
            )

            # Return workflow_id and final_score
            return [(r.workflow_id, r.final_score) for r in results]

        except Exception as e:
            logger.error(f"Vector store weighted search failed: {e}")
            # Fallback to legacy search
            return self._find_similar_legacy(prompt, top_k, threshold)

    def _find_similar_legacy(
        self,
        prompt: str,
        top_k: int,
        threshold: float,
    ) -> List[Tuple[str, float]]:
        """Legacy search using simple vector search (fallback)."""
        if self._model is None:
            return []

        try:
            prompt_embedding = self._model.encode(
                prompt,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )

            store = self._ensure_vector_store()
            results = store.search(
                query_vector=prompt_embedding.tolist(),
                namespace=VectorNamespace.WORKFLOWS,
                top_k=top_k * 3,  # Get more since we need to dedupe by workflow
                threshold=threshold,
            )

            # Deduplicate by workflow_id (take best score per workflow)
            workflow_scores: Dict[str, float] = {}
            for r in results:
                # Extract workflow_id from record ID or metadata
                workflow_id = r.metadata.get("workflow_id", r.id.split("__")[0])
                if workflow_id not in workflow_scores:
                    workflow_scores[workflow_id] = r.score

            # Sort by score and return top_k
            sorted_results = sorted(
                workflow_scores.items(),
                key=lambda x: x[1],
                reverse=True,
            )
            return sorted_results[:top_k]

        except Exception as e:
            logger.error(f"Legacy vector search failed: {e}")
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

    def find_best_match_with_confidence(
        self,
        prompt: str,
    ) -> Dict[str, Any]:
        """Find best matching workflow with confidence level and fallback.

        TASK-050-5: Returns detailed match result with confidence classification.

        Confidence levels:
        - HIGH (>= 0.90): Direct match, high confidence
        - MEDIUM (>= 0.75): Likely match, medium confidence
        - LOW (>= 0.60): Possible match, low confidence
        - NONE (< 0.60): No match, use generalization fallback

        Args:
            prompt: User prompt.

        Returns:
            Dict with keys:
            - workflow_id: Matched workflow name (or None)
            - score: Final weighted score
            - confidence_level: HIGH, MEDIUM, LOW, or NONE
            - source_type: What matched (sample_prompt, trigger_keyword, etc.)
            - matched_text: The text that matched
            - fallback_candidates: List of generalization candidates if NONE
            - language_detected: Detected query language
        """
        result = {
            "workflow_id": None,
            "score": 0.0,
            "confidence_level": "NONE",
            "source_type": None,
            "matched_text": None,
            "fallback_candidates": [],
            "language_detected": "en",
        }

        if not self._is_loaded:
            logger.warning("Classifier not loaded")
            return result

        # Detect language
        query_language = detect_language(prompt)
        result["language_detected"] = query_language

        # Get weighted search results
        if EMBEDDINGS_AVAILABLE and self._model is not None:
            try:
                prompt_embedding = self._model.encode(
                    prompt,
                    convert_to_numpy=True,
                    normalize_embeddings=True,
                    show_progress_bar=False,
                )

                store = self._ensure_vector_store()
                weighted_results = store.search_workflows_weighted(
                    query_vector=prompt_embedding.tolist(),
                    query_language=query_language,
                    top_k=5,  # Get multiple for fallback
                    min_score=0.0,  # Get all for analysis
                )

                if weighted_results:
                    best = weighted_results[0]
                    result["workflow_id"] = best.workflow_id
                    result["score"] = best.final_score
                    result["source_type"] = best.source_type
                    result["matched_text"] = best.matched_text

                    # Classify confidence level
                    if best.final_score >= CONFIDENCE_THRESHOLDS["HIGH"]:
                        result["confidence_level"] = "HIGH"
                    elif best.final_score >= CONFIDENCE_THRESHOLDS["MEDIUM"]:
                        result["confidence_level"] = "MEDIUM"
                    elif best.final_score >= CONFIDENCE_THRESHOLDS["LOW"]:
                        result["confidence_level"] = "LOW"
                    else:
                        result["confidence_level"] = "NONE"
                        result["workflow_id"] = None  # Not confident enough

                    # Provide fallback candidates for LOW or NONE
                    if result["confidence_level"] in ("LOW", "NONE"):
                        result["fallback_candidates"] = [
                            {
                                "workflow_id": r.workflow_id,
                                "score": r.final_score,
                                "source_type": r.source_type,
                            }
                            for r in weighted_results[:3]
                        ]

            except Exception as e:
                logger.error(f"Confidence match failed: {e}")

        return result

    def get_confidence_level(self, score: float) -> str:
        """Get confidence level for a score.

        TASK-050-5: Utility method to classify confidence.

        Args:
            score: Weighted similarity score (0.0 to 1.0).

        Returns:
            Confidence level: HIGH, MEDIUM, LOW, or NONE.
        """
        if score >= CONFIDENCE_THRESHOLDS["HIGH"]:
            return "HIGH"
        elif score >= CONFIDENCE_THRESHOLDS["MEDIUM"]:
            return "MEDIUM"
        elif score >= CONFIDENCE_THRESHOLDS["LOW"]:
            return "LOW"
        return "NONE"

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

        TASK-050-3: Updated for multi-embedding stats.

        Returns:
            Dictionary with classifier information.
        """
        store = self._ensure_vector_store()
        stats = store.get_stats()

        # Get multi-embedding specific counts
        unique_workflows = store.get_unique_workflow_count()
        total_embeddings = store.get_workflow_embedding_count()

        return {
            "model_name": self._model_name,
            "embeddings_available": EMBEDDINGS_AVAILABLE,
            "model_loaded": self._model is not None,
            "num_workflows": unique_workflows,
            "num_embeddings": total_embeddings,
            "embeddings_per_workflow": (
                round(total_embeddings / unique_workflows, 1)
                if unique_workflows > 0
                else 0
            ),
            "is_loaded": self._is_loaded,
            "using_fallback": (
                self._is_loaded
                and self._tfidf_vectorizer is not None
            ),
            "multi_embedding_enabled": True,  # TASK-050-3
            "source_weights": SOURCE_WEIGHTS,
            "vector_store": {
                "type": "LanceDB",
                "using_fallback": stats.get("using_fallback", False),
                "total_records": stats.get("total_records", 0),
                "workflows_count": unique_workflows,
                "workflow_embeddings_count": total_embeddings,
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
