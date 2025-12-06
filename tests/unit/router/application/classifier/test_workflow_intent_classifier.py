"""
Tests for WorkflowIntentClassifier.

TASK-046-2: Initial tests
TASK-047: Updated for LanceDB integration
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from pathlib import Path
import tempfile

from server.router.application.classifier.workflow_intent_classifier import (
    WorkflowIntentClassifier,
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


class TestWorkflowIntentClassifier:
    """Tests for WorkflowIntentClassifier."""

    @pytest.fixture
    def mock_store(self):
        """Create mock vector store."""
        return MockVectorStore()

    @pytest.fixture
    def classifier(self, mock_store):
        """Create classifier with mock store."""
        config = RouterConfig()
        return WorkflowIntentClassifier(config=config, vector_store=mock_store)

    @pytest.fixture
    def mock_workflows(self):
        """Create mock workflows."""
        phone = MagicMock()
        phone.sample_prompts = ["create a phone", "make smartphone"]
        phone.trigger_keywords = ["phone", "smartphone"]
        phone.description = "Create a smartphone model"

        table = MagicMock()
        table.sample_prompts = ["create a table", "make desk"]
        table.trigger_keywords = ["table", "desk"]
        table.description = "Create a table model"

        return {
            "phone_workflow": phone,
            "table_workflow": table,
        }

    def test_init_creates_classifier(self, classifier):
        """Test classifier initialization."""
        assert classifier is not None
        assert not classifier.is_loaded()

    def test_load_empty_workflows(self, classifier):
        """Test loading with empty workflows."""
        classifier.load_workflow_embeddings({})

        # Should not be loaded with empty workflows
        assert not classifier.is_loaded() or classifier._workflow_texts == {}

    def test_load_extracts_texts(self, classifier, mock_workflows):
        """Test that loading extracts texts from workflows."""
        classifier.load_workflow_embeddings(mock_workflows)

        assert "phone_workflow" in classifier._workflow_texts
        assert "table_workflow" in classifier._workflow_texts

        # Check that sample_prompts are included
        phone_texts = classifier._workflow_texts["phone_workflow"]
        assert "create a phone" in phone_texts
        assert "make smartphone" in phone_texts

    def test_load_with_dict_workflows(self, classifier):
        """Test loading with dict-based workflows."""
        workflows = {
            "phone_workflow": {
                "sample_prompts": ["create phone"],
                "trigger_keywords": ["phone"],
                "description": "Phone workflow",
            }
        }

        classifier.load_workflow_embeddings(workflows)

        assert "phone_workflow" in classifier._workflow_texts
        assert "create phone" in classifier._workflow_texts["phone_workflow"]

    def test_find_similar_not_loaded(self, classifier):
        """Test find_similar when not loaded returns empty."""
        result = classifier.find_similar("create a phone")

        assert result == []

    def test_find_best_match_not_loaded(self, classifier):
        """Test find_best_match when not loaded returns None."""
        result = classifier.find_best_match("create a phone")

        assert result is None

    def test_get_generalization_candidates(self, classifier, mock_workflows):
        """Test getting generalization candidates."""
        classifier.load_workflow_embeddings(mock_workflows)

        # Should return candidates (may be empty if no embeddings)
        result = classifier.get_generalization_candidates("create a chair")

        assert isinstance(result, list)

    def test_get_info(self, classifier):
        """Test get_info returns expected structure."""
        info = classifier.get_info()

        assert "model_name" in info
        assert "embeddings_available" in info
        assert "model_loaded" in info
        assert "num_workflows" in info
        assert "is_loaded" in info
        assert "vector_store" in info

    def test_clear_cache(self, classifier, mock_store):
        """Test clearing cache."""
        # Add some records
        mock_store.upsert([
            VectorRecord(
                id="test_workflow",
                namespace=VectorNamespace.WORKFLOWS,
                vector=[0.0] * 768,
                text="test",
                metadata={},
            )
        ])

        result = classifier.clear_cache()

        assert result is True
        assert mock_store.count(VectorNamespace.WORKFLOWS) == 0

    def test_find_similar_with_mock_results(self, classifier, mock_store, mock_workflows):
        """Test find_similar returns mock search results."""
        # Setup mock results
        mock_store.set_search_results([
            SearchResult(id="phone_workflow", score=0.9, text="phone", metadata={}),
            SearchResult(id="table_workflow", score=0.7, text="table", metadata={}),
        ])

        # Load workflows to set _is_loaded
        classifier.load_workflow_embeddings(mock_workflows)

        # If embeddings are available, test would work with real model
        # Otherwise we test TF-IDF fallback
        result = classifier.find_similar("create a phone", top_k=2)

        assert isinstance(result, list)

    def test_similarity_returns_float(self, classifier):
        """Test similarity method returns float."""
        result = classifier.similarity("text1", "text2")

        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_get_embedding_returns_none_without_model(self, classifier):
        """Test get_embedding returns None when model not available."""
        if not EMBEDDINGS_AVAILABLE:
            result = classifier.get_embedding("test text")
            assert result is None


class TestWorkflowIntentClassifierWithTFIDF:
    """Tests for TF-IDF fallback when embeddings unavailable."""

    @pytest.fixture
    def classifier_with_tfidf(self):
        """Create classifier that will use TF-IDF fallback."""
        mock_store = MockVectorStore()
        config = RouterConfig()
        classifier = WorkflowIntentClassifier(config=config, vector_store=mock_store)

        # Force TF-IDF fallback
        workflows = {
            "phone_workflow": MagicMock(
                sample_prompts=["create a phone", "make smartphone", "build mobile device"],
                trigger_keywords=["phone", "smartphone"],
                description="Phone workflow",
            ),
            "table_workflow": MagicMock(
                sample_prompts=["create a table", "make desk", "build furniture"],
                trigger_keywords=["table", "desk"],
                description="Table workflow",
            ),
        }

        # Patch to force TF-IDF fallback
        with patch.object(classifier, '_load_model', return_value=False):
            classifier.load_workflow_embeddings(workflows)

        return classifier

    def test_tfidf_fallback_initialized(self, classifier_with_tfidf):
        """Test that TF-IDF fallback is initialized."""
        # If sklearn is available, TF-IDF should be set up
        if classifier_with_tfidf._tfidf_vectorizer is not None:
            assert classifier_with_tfidf._tfidf_matrix is not None
            assert len(classifier_with_tfidf._tfidf_workflow_names) == 2

    def test_tfidf_find_similar(self, classifier_with_tfidf):
        """Test find_similar with TF-IDF fallback."""
        if classifier_with_tfidf._tfidf_vectorizer is None:
            pytest.skip("sklearn not available")

        results = classifier_with_tfidf.find_similar("create a phone", top_k=2)

        assert isinstance(results, list)
        # Should find something related to phone
        if results:
            assert results[0][0] in ["phone_workflow", "table_workflow"]
            assert 0.0 <= results[0][1] <= 1.0


class TestWorkflowIntentClassifierInterface:
    """Tests for IWorkflowIntentClassifier interface compliance."""

    def test_implements_interface(self):
        """Test that WorkflowIntentClassifier implements the interface."""
        from server.router.domain.interfaces.i_workflow_intent_classifier import (
            IWorkflowIntentClassifier,
        )

        mock_store = MockVectorStore()
        classifier = WorkflowIntentClassifier(vector_store=mock_store)

        assert isinstance(classifier, IWorkflowIntentClassifier)

    def test_interface_methods_exist(self):
        """Test all interface methods are implemented."""
        mock_store = MockVectorStore()
        classifier = WorkflowIntentClassifier(vector_store=mock_store)

        # Check all required methods exist
        assert hasattr(classifier, 'load_workflow_embeddings')
        assert hasattr(classifier, 'find_similar')
        assert hasattr(classifier, 'find_best_match')
        assert hasattr(classifier, 'get_generalization_candidates')
        assert hasattr(classifier, 'get_embedding')
        assert hasattr(classifier, 'similarity')
        assert hasattr(classifier, 'is_loaded')
        assert hasattr(classifier, 'get_info')
        assert hasattr(classifier, 'clear_cache')
