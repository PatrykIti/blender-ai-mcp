"""
Unit tests for IntentClassifier.

Tests intent classification with mocked embeddings.

TASK-047: Updated for LanceDB integration
"""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
import tempfile

from server.router.application.classifier.intent_classifier import (
    IntentClassifier,
    EMBEDDINGS_AVAILABLE,
)
from server.router.domain.interfaces.i_vector_store import (
    IVectorStore,
    VectorNamespace,
    VectorRecord,
    SearchResult,
)
from server.router.infrastructure.config import RouterConfig


class MockVectorStore(IVectorStore):
    """Mock vector store for testing."""

    def __init__(self):
        self._records = {}
        self._search_results = []

    def upsert(self, records):
        for r in records:
            key = f"{r.namespace.value}:{r.id}"
            self._records[key] = r
        return len(records)

    def search(self, query_vector, namespace, top_k=5, threshold=0.0, metadata_filter=None):
        return self._search_results[:top_k]

    def delete(self, ids, namespace):
        count = 0
        for id_ in ids:
            key = f"{namespace.value}:{id_}"
            if key in self._records:
                del self._records[key]
                count += 1
        return count

    def count(self, namespace=None):
        if namespace is None:
            return len(self._records)
        return sum(1 for k in self._records if k.startswith(namespace.value))

    def get_stats(self):
        return {
            "total_records": len(self._records),
            "tools_count": self.count(VectorNamespace.TOOLS),
            "workflows_count": self.count(VectorNamespace.WORKFLOWS),
        }

    def rebuild_index(self):
        return True

    def clear(self, namespace=None):
        if namespace is None:
            count = len(self._records)
            self._records.clear()
            return count
        to_delete = [k for k in self._records if k.startswith(namespace.value)]
        for k in to_delete:
            del self._records[k]
        return len(to_delete)

    def set_search_results(self, results):
        """Set results to return from search."""
        self._search_results = results

    def search_workflows_weighted(
        self,
        query_vector,
        query_language="en",
        top_k=5,
        min_score=0.5,
    ):
        """Search workflows with weighted scoring (mock implementation)."""
        from server.router.domain.interfaces.i_vector_store import WeightedSearchResult

        results = []
        for r in self._search_results[:top_k]:
            results.append(
                WeightedSearchResult(
                    workflow_id=r.id,
                    raw_score=r.score,
                    source_weight=1.0,
                    language_boost=1.0,
                    final_score=r.score,
                    matched_text=r.text,
                    source_type="sample_prompt",
                )
            )
        return results

    def get_workflow_embedding_count(self):
        """Get count of workflow embeddings."""
        return self.count(VectorNamespace.WORKFLOWS)

    def get_unique_workflow_count(self):
        """Get count of unique workflows."""
        # In mock, just count workflows namespace records
        return self.count(VectorNamespace.WORKFLOWS)


@pytest.fixture
def mock_store():
    """Create a mock vector store."""
    return MockVectorStore()


@pytest.fixture
def classifier(mock_store):
    """Create an IntentClassifier with mock store."""
    return IntentClassifier(vector_store=mock_store)


@pytest.fixture
def sample_metadata():
    """Create sample tool metadata."""
    return {
        "mesh_extrude_region": {
            "sample_prompts": [
                "extrude the selected faces",
                "pull out the geometry",
                "extend the mesh outward",
            ],
            "keywords": ["extrude", "pull", "extend"],
        },
        "mesh_bevel": {
            "sample_prompts": [
                "bevel the edges",
                "round the corners",
                "smooth the edges",
            ],
            "keywords": ["bevel", "round", "smooth"],
        },
        "mesh_subdivide": {
            "sample_prompts": [
                "subdivide the mesh",
                "add more geometry",
                "increase mesh density",
            ],
            "keywords": ["subdivide", "divide", "split"],
        },
    }


class TestIntentClassifierInit:
    """Tests for IntentClassifier initialization."""

    def test_init_default_config(self, classifier):
        """Test initialization with default config."""
        assert classifier._config is not None
        assert classifier._is_loaded is False

    def test_init_custom_config(self, mock_store):
        """Test initialization with custom config."""
        config = RouterConfig(embedding_threshold=0.5)
        classifier = IntentClassifier(config=config, vector_store=mock_store)

        assert classifier._config.embedding_threshold == 0.5

    def test_init_creates_store_lazily(self, mock_store):
        """Test that vector store is injected correctly."""
        classifier = IntentClassifier(vector_store=mock_store)
        assert classifier._vector_store is mock_store


class TestIntentClassifierLoadEmbeddings:
    """Tests for loading tool embeddings."""

    def test_load_empty_metadata(self, classifier):
        """Test loading with empty metadata."""
        classifier.load_tool_embeddings({})
        # Should not crash, but may not be loaded
        assert True

    def test_load_sample_metadata(self, classifier, sample_metadata):
        """Test loading with sample metadata."""
        classifier.load_tool_embeddings(sample_metadata)

        # Should be loaded (either with embeddings or TF-IDF fallback)
        assert classifier.is_loaded() is True

    def test_tool_texts_extracted(self, classifier, sample_metadata):
        """Test that tool texts are extracted from metadata."""
        classifier.load_tool_embeddings(sample_metadata)

        # Check tool texts were extracted
        assert len(classifier._tool_texts) == 3
        assert "mesh_extrude_region" in classifier._tool_texts


class TestIntentClassifierPredict:
    """Tests for prediction functionality."""

    def test_predict_not_loaded(self, classifier):
        """Test predict when not loaded returns empty."""
        result = classifier.predict("extrude the face")

        assert result == ("", 0.0)

    def test_predict_top_k_not_loaded(self, classifier):
        """Test predict_top_k when not loaded returns empty."""
        results = classifier.predict_top_k("extrude the face", k=3)

        assert results == []

    def test_predict_after_load(self, classifier, sample_metadata):
        """Test predict after loading metadata."""
        classifier.load_tool_embeddings(sample_metadata)

        tool, confidence = classifier.predict("extrude the selected faces")

        # Should return something (either from embeddings or TF-IDF)
        if classifier.is_loaded():
            # May or may not find a match depending on available backends
            assert isinstance(tool, str)
            assert isinstance(confidence, float)

    def test_predict_top_k_after_load(self, classifier, sample_metadata):
        """Test predict_top_k after loading metadata."""
        classifier.load_tool_embeddings(sample_metadata)

        results = classifier.predict_top_k("bevel the edges", k=3)

        if classifier.is_loaded():
            assert isinstance(results, list)
            # Each result should be (tool_name, confidence)
            for r in results:
                assert len(r) == 2


class TestIntentClassifierIsLoaded:
    """Tests for is_loaded method."""

    def test_not_loaded_initially(self, classifier):
        """Test that classifier is not loaded initially."""
        assert classifier.is_loaded() is False

    def test_loaded_after_load(self, classifier, sample_metadata):
        """Test that classifier is loaded after loading."""
        classifier.load_tool_embeddings(sample_metadata)
        assert classifier.is_loaded() is True


class TestIntentClassifierGetEmbedding:
    """Tests for get_embedding method."""

    def test_get_embedding_no_model(self, classifier):
        """Test get_embedding when model not loaded."""
        result = classifier.get_embedding("test text")

        # Without model, should return None
        if not EMBEDDINGS_AVAILABLE:
            assert result is None


class TestIntentClassifierSimilarity:
    """Tests for similarity method."""

    def test_similarity_no_model(self, classifier):
        """Test similarity when model not loaded."""
        result = classifier.similarity("text1", "text2")

        # Without model, should return 0.0
        if not EMBEDDINGS_AVAILABLE:
            assert result == 0.0


class TestIntentClassifierModelInfo:
    """Tests for get_model_info method."""

    def test_model_info_structure(self, classifier):
        """Test model info has required fields."""
        info = classifier.get_model_info()

        assert "model_name" in info
        assert "embeddings_available" in info
        assert "model_loaded" in info
        assert "num_tools" in info
        assert "is_loaded" in info
        assert "vector_store" in info

    def test_model_info_before_load(self, classifier):
        """Test model info before loading."""
        info = classifier.get_model_info()

        assert info["is_loaded"] is False
        assert info["num_tools"] == 0

    def test_model_info_after_load(self, classifier, sample_metadata):
        """Test model info after loading."""
        classifier.load_tool_embeddings(sample_metadata)
        info = classifier.get_model_info()

        assert info["is_loaded"] is True


class TestIntentClassifierClearCache:
    """Tests for clear_cache method."""

    def test_clear_cache(self, classifier, mock_store, sample_metadata):
        """Test clearing the cache."""
        # Add some records first
        mock_store.upsert([
            VectorRecord(
                id="test_tool",
                namespace=VectorNamespace.TOOLS,
                vector=[0.0] * 768,
                text="test",
                metadata={},
            )
        ])

        result = classifier.clear_cache()

        assert result is True
        assert mock_store.count(VectorNamespace.TOOLS) == 0


class TestTfidfFallback:
    """Tests for TF-IDF fallback functionality."""

    def test_tfidf_setup(self, classifier, sample_metadata):
        """Test that TF-IDF fallback is set up when embeddings unavailable."""
        # This will use TF-IDF if sentence-transformers not installed
        classifier.load_tool_embeddings(sample_metadata)

        info = classifier.get_model_info()
        # Either embeddings or TF-IDF should be working
        assert classifier.is_loaded()


class TestEdgeCases:
    """Tests for edge cases."""

    def test_load_metadata_with_missing_fields(self, classifier):
        """Test loading metadata with missing optional fields."""
        metadata = {
            "tool1": {},  # No sample_prompts or keywords
            "tool2": {"sample_prompts": []},  # Empty prompts
        }

        classifier.load_tool_embeddings(metadata)
        # Should not crash
        assert True

    def test_predict_empty_prompt(self, classifier, sample_metadata):
        """Test prediction with empty prompt."""
        classifier.load_tool_embeddings(sample_metadata)

        tool, confidence = classifier.predict("")
        # Should handle gracefully
        assert isinstance(tool, str)

    def test_predict_very_long_prompt(self, classifier, sample_metadata):
        """Test prediction with very long prompt."""
        classifier.load_tool_embeddings(sample_metadata)

        long_prompt = "extrude " * 1000
        tool, confidence = classifier.predict(long_prompt)
        # Should handle gracefully
        assert isinstance(tool, str)


class TestIntentClassifierInterface:
    """Tests for IIntentClassifier interface compliance."""

    def test_implements_interface(self, mock_store):
        """Test that IntentClassifier implements the interface."""
        from server.router.domain.interfaces.i_intent_classifier import (
            IIntentClassifier,
        )

        classifier = IntentClassifier(vector_store=mock_store)

        assert isinstance(classifier, IIntentClassifier)

    def test_interface_methods_exist(self, mock_store):
        """Test all interface methods are implemented."""
        classifier = IntentClassifier(vector_store=mock_store)

        # Check all required methods exist
        assert hasattr(classifier, 'predict')
        assert hasattr(classifier, 'predict_top_k')
        assert hasattr(classifier, 'load_tool_embeddings')
        assert hasattr(classifier, 'is_loaded')
        assert hasattr(classifier, 'get_embedding')
        assert hasattr(classifier, 'similarity')
        assert hasattr(classifier, 'get_model_info')
        assert hasattr(classifier, 'clear_cache')
