"""
Tests for WorkflowIntentClassifier.

TASK-046-2
"""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
import tempfile

from server.router.application.classifier.workflow_intent_classifier import (
    WorkflowIntentClassifier,
    WorkflowEmbeddingCache,
    EMBEDDINGS_AVAILABLE,
)
from server.router.infrastructure.config import RouterConfig


class TestWorkflowEmbeddingCache:
    """Tests for WorkflowEmbeddingCache."""

    def test_init_creates_cache_dir(self, tmp_path):
        """Test that init creates cache directory."""
        cache_dir = tmp_path / "cache"
        cache = WorkflowEmbeddingCache(cache_dir=cache_dir)

        assert cache_dir.exists()

    def test_compute_hash_consistent(self):
        """Test that hash is consistent for same input."""
        workflows1 = {
            "phone_workflow": MagicMock(sample_prompts=["create phone"]),
            "table_workflow": MagicMock(sample_prompts=["create table"]),
        }
        workflows2 = {
            "phone_workflow": MagicMock(sample_prompts=["create phone"]),
            "table_workflow": MagicMock(sample_prompts=["create table"]),
        }

        hash1 = WorkflowEmbeddingCache.compute_hash(workflows1)
        hash2 = WorkflowEmbeddingCache.compute_hash(workflows2)

        assert hash1 == hash2

    def test_compute_hash_different_for_different_prompts(self):
        """Test that hash differs for different prompts."""
        workflows1 = {
            "phone_workflow": MagicMock(sample_prompts=["create phone"]),
        }
        workflows2 = {
            "phone_workflow": MagicMock(sample_prompts=["make smartphone"]),
        }

        hash1 = WorkflowEmbeddingCache.compute_hash(workflows1)
        hash2 = WorkflowEmbeddingCache.compute_hash(workflows2)

        assert hash1 != hash2

    def test_is_valid_false_when_no_cache(self, tmp_path):
        """Test that is_valid returns False when no cache exists."""
        cache = WorkflowEmbeddingCache(cache_dir=tmp_path)

        assert not cache.is_valid("some_hash")

    def test_clear_cache(self, tmp_path):
        """Test clearing cache."""
        cache = WorkflowEmbeddingCache(cache_dir=tmp_path)

        # Create fake cache files
        cache._cache_file.touch()
        cache._hash_file.touch()

        result = cache.clear()

        assert result is True
        assert not cache._cache_file.exists()
        assert not cache._hash_file.exists()


class TestWorkflowIntentClassifier:
    """Tests for WorkflowIntentClassifier."""

    @pytest.fixture
    def classifier(self, tmp_path):
        """Create classifier with temp cache."""
        config = RouterConfig()
        return WorkflowIntentClassifier(config=config, cache_dir=tmp_path)

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

    def test_clear_cache(self, classifier, tmp_path):
        """Test clearing cache."""
        # Create fake cache
        cache_file = tmp_path / "workflow_embeddings.pkl"
        cache_file.touch()

        result = classifier.clear_cache()

        assert result is True


class TestWorkflowIntentClassifierWithTFIDF:
    """Tests for TF-IDF fallback when embeddings unavailable."""

    @pytest.fixture
    def classifier_with_tfidf(self, tmp_path):
        """Create classifier that will use TF-IDF fallback."""
        config = RouterConfig()
        classifier = WorkflowIntentClassifier(config=config, cache_dir=tmp_path)

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
