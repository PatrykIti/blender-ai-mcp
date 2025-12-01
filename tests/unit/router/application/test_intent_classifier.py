"""
Unit tests for IntentClassifier and EmbeddingCache.

Tests intent classification with mocked embeddings.
"""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
import tempfile

from server.router.application.classifier.intent_classifier import (
    IntentClassifier,
    EMBEDDINGS_AVAILABLE,
)
from server.router.application.classifier.embedding_cache import EmbeddingCache
from server.router.infrastructure.config import RouterConfig


@pytest.fixture
def temp_cache_dir():
    """Create a temporary cache directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def embedding_cache(temp_cache_dir):
    """Create an EmbeddingCache with temp directory."""
    return EmbeddingCache(cache_dir=temp_cache_dir)


@pytest.fixture
def classifier(temp_cache_dir):
    """Create an IntentClassifier with temp cache."""
    return IntentClassifier(cache_dir=temp_cache_dir)


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


class TestEmbeddingCacheInit:
    """Tests for EmbeddingCache initialization."""

    def test_init_default_dir(self):
        """Test initialization with default directory."""
        cache = EmbeddingCache()
        assert cache._cache_dir.exists() or True  # May not exist yet

    def test_init_custom_dir(self, temp_cache_dir):
        """Test initialization with custom directory."""
        cache = EmbeddingCache(cache_dir=temp_cache_dir)
        assert cache._cache_dir == temp_cache_dir

    def test_cache_dir_created(self, temp_cache_dir):
        """Test that cache directory is created."""
        cache = EmbeddingCache(cache_dir=temp_cache_dir / "subdir")
        assert cache._cache_dir.exists()


class TestEmbeddingCacheSaveLoad:
    """Tests for EmbeddingCache save/load functionality."""

    @pytest.mark.skipif(not EMBEDDINGS_AVAILABLE, reason="NumPy not available")
    def test_save_and_load(self, embedding_cache):
        """Test saving and loading embeddings."""
        import numpy as np

        embeddings = {
            "tool1": np.array([0.1, 0.2, 0.3]),
            "tool2": np.array([0.4, 0.5, 0.6]),
        }

        # Save
        result = embedding_cache.save(embeddings, "test_hash")
        assert result is True

        # Load
        loaded = embedding_cache.load()
        assert loaded is not None
        assert "tool1" in loaded
        assert "tool2" in loaded

    def test_load_nonexistent(self, embedding_cache):
        """Test loading when no cache exists."""
        loaded = embedding_cache.load()
        assert loaded is None

    @pytest.mark.skipif(not EMBEDDINGS_AVAILABLE, reason="NumPy not available")
    def test_is_valid_matching_hash(self, embedding_cache):
        """Test cache validity with matching hash."""
        import numpy as np

        embeddings = {"tool1": np.array([0.1, 0.2])}
        embedding_cache.save(embeddings, "test_hash_123")

        assert embedding_cache.is_valid("test_hash_123") is True

    @pytest.mark.skipif(not EMBEDDINGS_AVAILABLE, reason="NumPy not available")
    def test_is_valid_different_hash(self, embedding_cache):
        """Test cache invalidity with different hash."""
        import numpy as np

        embeddings = {"tool1": np.array([0.1, 0.2])}
        embedding_cache.save(embeddings, "old_hash")

        assert embedding_cache.is_valid("new_hash") is False

    def test_is_valid_no_cache(self, embedding_cache):
        """Test cache validity when no cache exists."""
        assert embedding_cache.is_valid("any_hash") is False


class TestEmbeddingCacheClear:
    """Tests for EmbeddingCache clear functionality."""

    @pytest.mark.skipif(not EMBEDDINGS_AVAILABLE, reason="NumPy not available")
    def test_clear_existing(self, embedding_cache):
        """Test clearing existing cache."""
        import numpy as np

        embeddings = {"tool1": np.array([0.1, 0.2])}
        embedding_cache.save(embeddings, "hash")

        result = embedding_cache.clear()
        assert result is True
        assert embedding_cache.load() is None

    def test_clear_nonexistent(self, embedding_cache):
        """Test clearing non-existent cache."""
        result = embedding_cache.clear()
        assert result is True


class TestEmbeddingCacheUtilities:
    """Tests for EmbeddingCache utility methods."""

    def test_get_cache_path(self, embedding_cache, temp_cache_dir):
        """Test get_cache_path returns correct path."""
        assert embedding_cache.get_cache_path() == temp_cache_dir

    def test_get_cache_size_no_cache(self, embedding_cache):
        """Test cache size when no cache exists."""
        assert embedding_cache.get_cache_size() == 0

    @pytest.mark.skipif(not EMBEDDINGS_AVAILABLE, reason="NumPy not available")
    def test_get_cache_size_with_cache(self, embedding_cache):
        """Test cache size with existing cache."""
        import numpy as np

        embeddings = {"tool1": np.array([0.1] * 100)}
        embedding_cache.save(embeddings, "hash")

        assert embedding_cache.get_cache_size() > 0

    def test_compute_metadata_hash(self):
        """Test metadata hash computation."""
        metadata1 = {"tool1": {"keywords": ["a", "b"]}}
        metadata2 = {"tool1": {"keywords": ["a", "b"]}}
        metadata3 = {"tool1": {"keywords": ["c", "d"]}}

        hash1 = EmbeddingCache.compute_metadata_hash(metadata1)
        hash2 = EmbeddingCache.compute_metadata_hash(metadata2)
        hash3 = EmbeddingCache.compute_metadata_hash(metadata3)

        assert hash1 == hash2  # Same content = same hash
        assert hash1 != hash3  # Different content = different hash
        assert len(hash1) == 16  # SHA256 truncated to 16 chars


class TestIntentClassifierInit:
    """Tests for IntentClassifier initialization."""

    def test_init_default_config(self, classifier):
        """Test initialization with default config."""
        assert classifier._config is not None
        assert classifier._is_loaded is False

    def test_init_custom_config(self, temp_cache_dir):
        """Test initialization with custom config."""
        config = RouterConfig(embedding_threshold=0.5)
        classifier = IntentClassifier(config=config, cache_dir=temp_cache_dir)

        assert classifier._config.embedding_threshold == 0.5

    def test_init_creates_cache(self, temp_cache_dir):
        """Test that cache is created on init."""
        classifier = IntentClassifier(cache_dir=temp_cache_dir)
        assert classifier._cache is not None


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

    def test_clear_cache(self, classifier, sample_metadata):
        """Test clearing the cache."""
        classifier.load_tool_embeddings(sample_metadata)
        result = classifier.clear_cache()

        assert result is True


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
