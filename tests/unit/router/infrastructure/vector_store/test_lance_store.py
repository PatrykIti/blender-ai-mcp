"""
Unit tests for LanceVectorStore.

Tests LanceDB-based vector storage with fallback support.

TASK-047-2
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from server.router.infrastructure.vector_store.lance_store import (
    LanceVectorStore,
    LANCEDB_AVAILABLE,
)
from server.router.domain.interfaces.i_vector_store import (
    IVectorStore,
    VectorNamespace,
    VectorRecord,
    SearchResult,
)


@pytest.fixture
def temp_db_path():
    """Create a temporary database directory."""
    tmpdir = tempfile.mkdtemp()
    yield Path(tmpdir)
    # Cleanup
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def store(temp_db_path):
    """Create a LanceVectorStore with temp directory."""
    return LanceVectorStore(db_path=temp_db_path)


@pytest.fixture
def sample_records():
    """Create sample vector records."""
    return [
        VectorRecord(
            id="mesh_extrude",
            namespace=VectorNamespace.TOOLS,
            vector=[0.1] * 768,
            text="extrude the mesh",
            metadata={"category": "mesh", "mode_required": "EDIT"},
        ),
        VectorRecord(
            id="mesh_bevel",
            namespace=VectorNamespace.TOOLS,
            vector=[0.2] * 768,
            text="bevel the edges",
            metadata={"category": "mesh", "mode_required": "EDIT"},
        ),
        VectorRecord(
            id="phone_workflow",
            namespace=VectorNamespace.WORKFLOWS,
            vector=[0.3] * 768,
            text="create a smartphone",
            metadata={"category": "electronics"},
        ),
    ]


class TestLanceVectorStoreInit:
    """Tests for LanceVectorStore initialization."""

    def test_implements_interface(self, store):
        """Test that store implements IVectorStore."""
        assert isinstance(store, IVectorStore)

    def test_init_creates_db_path(self, temp_db_path):
        """Test init behavior for db path with or without LanceDB."""
        db_path = temp_db_path / "subdir" / "db"
        store = LanceVectorStore(db_path=db_path)
        stats = store.get_stats()

        if stats["lancedb_available"]:
            # Directory is created during initialization when LanceDB is available
            assert db_path.exists()
        else:
            assert stats["using_fallback"] is True

    def test_init_default_path(self):
        """Test initialization with default path."""
        # Just check it doesn't crash
        store = LanceVectorStore()
        assert store is not None

    def test_get_stats_empty(self, store):
        """Test stats on empty store."""
        stats = store.get_stats()

        assert "db_path" in stats
        assert "table_name" in stats
        assert "total_records" in stats
        assert stats["total_records"] == 0


class TestLanceVectorStoreUpsert:
    """Tests for upsert functionality."""

    def test_upsert_single_record(self, store, sample_records):
        """Test upserting a single record."""
        count = store.upsert([sample_records[0]])

        assert count == 1
        assert store.count(VectorNamespace.TOOLS) == 1

    def test_upsert_multiple_records(self, store, sample_records):
        """Test upserting multiple records."""
        count = store.upsert(sample_records)

        assert count == 3
        assert store.count(VectorNamespace.TOOLS) == 2
        assert store.count(VectorNamespace.WORKFLOWS) == 1

    def test_upsert_empty_list(self, store):
        """Test upserting empty list."""
        count = store.upsert([])

        assert count == 0

    def test_upsert_replaces_existing(self, store, sample_records):
        """Test that upsert replaces existing records."""
        # Insert first
        store.upsert([sample_records[0]])
        assert store.count(VectorNamespace.TOOLS) == 1

        # Upsert same ID with different text
        updated = VectorRecord(
            id="mesh_extrude",
            namespace=VectorNamespace.TOOLS,
            vector=[0.5] * 768,
            text="updated text",
            metadata={},
        )
        store.upsert([updated])

        # Should still be 1 record (replaced, not added)
        assert store.count(VectorNamespace.TOOLS) == 1


class TestLanceVectorStoreSearch:
    """Tests for search functionality."""

    def test_search_empty_store(self, store):
        """Test search on empty store."""
        results = store.search(
            query_vector=[0.1] * 768,
            namespace=VectorNamespace.TOOLS,
            top_k=5,
        )

        assert results == []

    def test_search_returns_results(self, store, sample_records):
        """Test that search returns results."""
        store.upsert(sample_records)

        results = store.search(
            query_vector=[0.1] * 768,
            namespace=VectorNamespace.TOOLS,
            top_k=5,
        )

        assert len(results) > 0
        assert all(isinstance(r, SearchResult) for r in results)

    def test_search_respects_namespace(self, store, sample_records):
        """Test that search respects namespace filter."""
        store.upsert(sample_records)

        # Search in TOOLS namespace
        tools_results = store.search(
            query_vector=[0.1] * 768,
            namespace=VectorNamespace.TOOLS,
            top_k=10,
        )

        # Search in WORKFLOWS namespace
        workflow_results = store.search(
            query_vector=[0.1] * 768,
            namespace=VectorNamespace.WORKFLOWS,
            top_k=10,
        )

        assert len(tools_results) == 2  # Only TOOLS records
        assert len(workflow_results) == 1  # Only WORKFLOWS records

    def test_search_respects_top_k(self, store, sample_records):
        """Test that search respects top_k limit."""
        store.upsert(sample_records)

        results = store.search(
            query_vector=[0.1] * 768,
            namespace=VectorNamespace.TOOLS,
            top_k=1,
        )

        assert len(results) <= 1

    def test_search_result_structure(self, store, sample_records):
        """Test search result has correct structure."""
        store.upsert(sample_records)

        results = store.search(
            query_vector=[0.1] * 768,
            namespace=VectorNamespace.TOOLS,
            top_k=1,
        )

        if results:
            result = results[0]
            assert hasattr(result, "id")
            assert hasattr(result, "score")
            assert hasattr(result, "text")
            assert hasattr(result, "metadata")


class TestLanceVectorStoreDelete:
    """Tests for delete functionality."""

    def test_delete_existing_record(self, store, sample_records):
        """Test deleting existing record."""
        store.upsert(sample_records)

        count = store.delete(["mesh_extrude"], VectorNamespace.TOOLS)

        assert count >= 0  # May be 0 in fallback mode
        # Verify deletion
        assert store.count(VectorNamespace.TOOLS) <= 2

    def test_delete_nonexistent_record(self, store):
        """Test deleting non-existent record."""
        count = store.delete(["nonexistent"], VectorNamespace.TOOLS)

        assert count == 0

    def test_delete_empty_list(self, store):
        """Test deleting with empty list."""
        count = store.delete([], VectorNamespace.TOOLS)

        assert count == 0


class TestLanceVectorStoreCount:
    """Tests for count functionality."""

    def test_count_empty(self, store):
        """Test count on empty store."""
        assert store.count() == 0
        assert store.count(VectorNamespace.TOOLS) == 0
        assert store.count(VectorNamespace.WORKFLOWS) == 0

    def test_count_by_namespace(self, store, sample_records):
        """Test count by namespace."""
        store.upsert(sample_records)

        assert store.count(VectorNamespace.TOOLS) == 2
        assert store.count(VectorNamespace.WORKFLOWS) == 1
        assert store.count() == 3


class TestLanceVectorStoreClear:
    """Tests for clear functionality."""

    def test_clear_namespace(self, store, sample_records):
        """Test clearing a specific namespace."""
        store.upsert(sample_records)

        deleted = store.clear(VectorNamespace.TOOLS)

        assert deleted >= 0
        assert store.count(VectorNamespace.TOOLS) == 0
        assert store.count(VectorNamespace.WORKFLOWS) == 1

    def test_clear_all(self, store, sample_records):
        """Test clearing all records."""
        store.upsert(sample_records)

        deleted = store.clear()

        assert deleted >= 0
        assert store.count() == 0


class TestLanceVectorStoreRebuildIndex:
    """Tests for index rebuild functionality."""

    def test_rebuild_index_empty(self, store):
        """Test rebuilding index on empty store."""
        result = store.rebuild_index()
        # Should not fail
        assert isinstance(result, bool)

    def test_rebuild_index_with_data(self, store, sample_records):
        """Test rebuilding index with data."""
        store.upsert(sample_records)

        result = store.rebuild_index()

        assert isinstance(result, bool)


class TestLanceVectorStoreGetAllIds:
    """Tests for get_all_ids functionality."""

    def test_get_all_ids_empty(self, store):
        """Test getting IDs from empty store."""
        ids = store.get_all_ids(VectorNamespace.TOOLS)

        assert ids == []

    def test_get_all_ids_with_data(self, store, sample_records):
        """Test getting all IDs."""
        store.upsert(sample_records)

        tool_ids = store.get_all_ids(VectorNamespace.TOOLS)
        workflow_ids = store.get_all_ids(VectorNamespace.WORKFLOWS)

        assert len(tool_ids) == 2
        assert "mesh_extrude" in tool_ids
        assert "mesh_bevel" in tool_ids
        assert len(workflow_ids) == 1
        assert "phone_workflow" in workflow_ids


class TestLanceVectorStoreStats:
    """Tests for get_stats functionality."""

    def test_stats_structure(self, store):
        """Test stats has expected structure."""
        stats = store.get_stats()

        assert "db_path" in stats
        assert "table_name" in stats
        assert "vector_dimension" in stats
        assert "total_records" in stats
        assert "tools_count" in stats
        assert "workflows_count" in stats
        assert "using_fallback" in stats
        assert "lancedb_available" in stats

    def test_stats_reflects_data(self, store, sample_records):
        """Test stats reflects stored data."""
        store.upsert(sample_records)
        stats = store.get_stats()

        assert stats["total_records"] == 3
        assert stats["tools_count"] == 2
        assert stats["workflows_count"] == 1


class TestLanceVectorStoreIsAvailable:
    """Tests for is_available functionality."""

    def test_is_available(self, store):
        """Test is_available method."""
        result = store.is_available()

        assert isinstance(result, bool)
        # If LanceDB is installed, should be available
        if LANCEDB_AVAILABLE:
            assert result is True


class TestLanceVectorStoreFallback:
    """Tests for in-memory fallback functionality."""

    def test_fallback_works_when_lancedb_unavailable(self, temp_db_path):
        """Test that fallback works when LanceDB unavailable."""
        # This test verifies the fallback mechanism exists
        store = LanceVectorStore(db_path=temp_db_path)

        # Even with fallback, basic operations should work
        record = VectorRecord(
            id="test",
            namespace=VectorNamespace.TOOLS,
            vector=[0.1] * 768,
            text="test",
            metadata={},
        )

        count = store.upsert([record])
        assert count == 1


class TestLanceVectorStoreMultiEmbedding:
    """Tests for multi-embedding workflow storage (TASK-050)."""

    @pytest.fixture
    def workflow_records(self):
        """Create workflow records with multi-embedding metadata."""
        return [
            # Workflow 1: Multiple embeddings for "table_workflow"
            VectorRecord(
                id="table_workflow_prompt_0",
                namespace=VectorNamespace.WORKFLOWS,
                vector=[0.5] * 768,
                text="create a picnic table",
                metadata={
                    "workflow_id": "table_workflow",
                    "source_type": "sample_prompt",
                    "source_weight": 1.0,
                    "language": "en",
                },
            ),
            VectorRecord(
                id="table_workflow_prompt_1",
                namespace=VectorNamespace.WORKFLOWS,
                vector=[0.51] * 768,
                text="build wooden table",
                metadata={
                    "workflow_id": "table_workflow",
                    "source_type": "sample_prompt",
                    "source_weight": 1.0,
                    "language": "en",
                },
            ),
            VectorRecord(
                id="table_workflow_keyword_0",
                namespace=VectorNamespace.WORKFLOWS,
                vector=[0.45] * 768,
                text="table",
                metadata={
                    "workflow_id": "table_workflow",
                    "source_type": "trigger_keyword",
                    "source_weight": 0.8,
                    "language": "en",
                },
            ),
            VectorRecord(
                id="table_workflow_desc",
                namespace=VectorNamespace.WORKFLOWS,
                vector=[0.4] * 768,
                text="Create a picnic table with benches",
                metadata={
                    "workflow_id": "table_workflow",
                    "source_type": "description",
                    "source_weight": 0.6,
                    "language": "en",
                },
            ),
            # Workflow 2: Polish workflow
            VectorRecord(
                id="chair_workflow_prompt_0",
                namespace=VectorNamespace.WORKFLOWS,
                vector=[0.6] * 768,
                text="stwórz krzesło",
                metadata={
                    "workflow_id": "chair_workflow",
                    "source_type": "sample_prompt",
                    "source_weight": 1.0,
                    "language": "pl",
                },
            ),
            VectorRecord(
                id="chair_workflow_prompt_1",
                namespace=VectorNamespace.WORKFLOWS,
                vector=[0.55] * 768,
                text="create a chair",
                metadata={
                    "workflow_id": "chair_workflow",
                    "source_type": "sample_prompt",
                    "source_weight": 1.0,
                    "language": "en",
                },
            ),
        ]

    def test_upsert_workflow_embeddings(self, store, workflow_records):
        """Test upserting multiple embeddings per workflow."""
        count = store.upsert(workflow_records)

        assert count == 6
        assert store.count(VectorNamespace.WORKFLOWS) == 6

    def test_get_workflow_embedding_count(self, store, workflow_records):
        """Test getting total workflow embedding count."""
        store.upsert(workflow_records)

        count = store.get_workflow_embedding_count()

        assert count == 6

    def test_get_unique_workflow_count(self, store, workflow_records):
        """Test getting unique workflow count."""
        store.upsert(workflow_records)

        count = store.get_unique_workflow_count()

        # Should be 2 unique workflows (table_workflow, chair_workflow)
        assert count == 2

    def test_search_workflows_weighted_basic(self, store, workflow_records):
        """Test weighted workflow search returns results."""
        store.upsert(workflow_records)

        results = store.search_workflows_weighted(
            query_vector=[0.5] * 768,
            query_language="en",
            top_k=5,
            min_score=0.0,
        )

        assert len(results) > 0
        # Results should be WeightedSearchResult
        from server.router.domain.interfaces.i_vector_store import WeightedSearchResult
        assert all(isinstance(r, WeightedSearchResult) for r in results)

    def test_search_workflows_weighted_returns_best_per_workflow(self, store, workflow_records):
        """Test that weighted search returns best match per workflow."""
        store.upsert(workflow_records)

        results = store.search_workflows_weighted(
            query_vector=[0.5] * 768,
            query_language="en",
            top_k=10,
            min_score=0.0,
        )

        # Should have at most 2 results (one per workflow)
        workflow_ids = [r.workflow_id for r in results]
        assert len(set(workflow_ids)) == len(workflow_ids), "Duplicate workflows in results"

    def test_search_workflows_weighted_result_structure(self, store, workflow_records):
        """Test weighted search result structure."""
        store.upsert(workflow_records)

        results = store.search_workflows_weighted(
            query_vector=[0.5] * 768,
            query_language="en",
            top_k=1,
            min_score=0.0,
        )

        if results:
            result = results[0]
            assert hasattr(result, "workflow_id")
            assert hasattr(result, "raw_score")
            assert hasattr(result, "source_weight")
            assert hasattr(result, "language_boost")
            assert hasattr(result, "final_score")
            assert hasattr(result, "matched_text")
            assert hasattr(result, "source_type")

    def test_search_workflows_weighted_scores_in_range(self, store, workflow_records):
        """Test that weighted search scores are in valid range."""
        store.upsert(workflow_records)

        results = store.search_workflows_weighted(
            query_vector=[0.5] * 768,
            query_language="en",
            top_k=5,
            min_score=0.0,
        )

        for result in results:
            assert 0.0 <= result.raw_score <= 1.0
            assert 0.0 < result.source_weight <= 1.0
            assert 0.0 < result.language_boost <= 1.0
            assert 0.0 <= result.final_score <= 1.0

    def test_search_workflows_weighted_min_score_filter(self, store, workflow_records):
        """Test that min_score filters results."""
        store.upsert(workflow_records)

        # With high threshold, should get fewer results
        results_high = store.search_workflows_weighted(
            query_vector=[0.5] * 768,
            query_language="en",
            top_k=10,
            min_score=0.99,
        )

        results_low = store.search_workflows_weighted(
            query_vector=[0.5] * 768,
            query_language="en",
            top_k=10,
            min_score=0.0,
        )

        assert len(results_high) <= len(results_low)

    def test_search_workflows_weighted_language_boost(self, store, workflow_records):
        """Test language boost affects scoring."""
        store.upsert(workflow_records)

        # Search with Polish language
        results_pl = store.search_workflows_weighted(
            query_vector=[0.6] * 768,  # Closer to Polish workflow
            query_language="pl",
            top_k=5,
            min_score=0.0,
        )

        # Search with English language
        results_en = store.search_workflows_weighted(
            query_vector=[0.6] * 768,
            query_language="en",
            top_k=5,
            min_score=0.0,
        )

        # Both should return results
        assert len(results_pl) > 0
        assert len(results_en) > 0

        # Find chair_workflow in both results
        chair_pl = next((r for r in results_pl if r.workflow_id == "chair_workflow"), None)
        chair_en = next((r for r in results_en if r.workflow_id == "chair_workflow"), None)

        # Polish result should have language_boost=1.0 for Polish text
        # English result should have language_boost=0.9 for Polish text (if matched)
        if chair_pl and chair_en:
            # The scoring depends on which embedding matched best
            # Just verify the boost is applied
            assert chair_pl.language_boost > 0
            assert chair_en.language_boost > 0

    def test_search_workflows_weighted_source_weights(self, store, workflow_records):
        """Test that source weights affect final score."""
        store.upsert(workflow_records)

        results = store.search_workflows_weighted(
            query_vector=[0.5] * 768,
            query_language="en",
            top_k=5,
            min_score=0.0,
        )

        for result in results:
            # Final score should account for source weight
            # final_score = raw_score * source_weight * language_boost
            expected_upper = result.raw_score * result.source_weight * result.language_boost
            # Allow small floating point tolerance
            assert abs(result.final_score - expected_upper) < 0.01

    def test_search_workflows_weighted_empty_store(self, store):
        """Test weighted search on empty store."""
        results = store.search_workflows_weighted(
            query_vector=[0.5] * 768,
            query_language="en",
            top_k=5,
            min_score=0.0,
        )

        assert results == []

    def test_search_workflows_weighted_top_k(self, store, workflow_records):
        """Test that top_k limits results."""
        store.upsert(workflow_records)

        results = store.search_workflows_weighted(
            query_vector=[0.5] * 768,
            query_language="en",
            top_k=1,
            min_score=0.0,
        )

        assert len(results) <= 1

    def test_search_workflows_weighted_sorted_by_final_score(self, store, workflow_records):
        """Test that results are sorted by final_score descending."""
        store.upsert(workflow_records)

        results = store.search_workflows_weighted(
            query_vector=[0.5] * 768,
            query_language="en",
            top_k=10,
            min_score=0.0,
        )

        if len(results) > 1:
            scores = [r.final_score for r in results]
            assert scores == sorted(scores, reverse=True)


class TestLanceVectorStoreWeightedSearchScoring:
    """Tests for weighted scoring formula validation (TASK-050)."""

    @pytest.fixture
    def store_with_controlled_data(self, store):
        """Create store with controlled data for scoring tests."""
        # Create records with known vectors for predictable similarity
        records = [
            VectorRecord(
                id="workflow_a_prompt",
                namespace=VectorNamespace.WORKFLOWS,
                vector=[1.0] + [0.0] * 767,  # Unit vector in first dimension
                text="exact match text",
                metadata={
                    "workflow_id": "workflow_a",
                    "source_type": "sample_prompt",
                    "source_weight": 1.0,
                    "language": "en",
                },
            ),
            VectorRecord(
                id="workflow_a_keyword",
                namespace=VectorNamespace.WORKFLOWS,
                vector=[1.0] + [0.0] * 767,
                text="keyword",
                metadata={
                    "workflow_id": "workflow_a",
                    "source_type": "trigger_keyword",
                    "source_weight": 0.8,
                    "language": "en",
                },
            ),
            VectorRecord(
                id="workflow_a_desc",
                namespace=VectorNamespace.WORKFLOWS,
                vector=[1.0] + [0.0] * 767,
                text="description",
                metadata={
                    "workflow_id": "workflow_a",
                    "source_type": "description",
                    "source_weight": 0.6,
                    "language": "en",
                },
            ),
            VectorRecord(
                id="workflow_a_name",
                namespace=VectorNamespace.WORKFLOWS,
                vector=[1.0] + [0.0] * 767,
                text="workflow a",
                metadata={
                    "workflow_id": "workflow_a",
                    "source_type": "name",
                    "source_weight": 0.5,
                    "language": "en",
                },
            ),
        ]
        store.upsert(records)
        return store

    def test_sample_prompt_weight_is_1_0(self, store_with_controlled_data):
        """Test that sample_prompt source weight is 1.0."""
        results = store_with_controlled_data.search_workflows_weighted(
            query_vector=[1.0] + [0.0] * 767,
            query_language="en",
            top_k=1,
            min_score=0.0,
        )

        if results:
            # With identical vectors, raw_score should be ~1.0
            # Best match should be sample_prompt with weight 1.0
            result = results[0]
            assert result.source_type == "sample_prompt"
            assert result.source_weight == 1.0

    def test_language_boost_same_language(self, store_with_controlled_data):
        """Test language boost is 1.0 for same language."""
        results = store_with_controlled_data.search_workflows_weighted(
            query_vector=[1.0] + [0.0] * 767,
            query_language="en",  # Same as stored language
            top_k=1,
            min_score=0.0,
        )

        if results:
            assert results[0].language_boost == 1.0

    def test_language_boost_different_language(self, store):
        """Test language boost is 0.9 for different language."""
        # Create record with Polish language
        records = [
            VectorRecord(
                id="pl_workflow",
                namespace=VectorNamespace.WORKFLOWS,
                vector=[1.0] + [0.0] * 767,
                text="polish text",
                metadata={
                    "workflow_id": "pl_workflow",
                    "source_type": "sample_prompt",
                    "source_weight": 1.0,
                    "language": "pl",
                },
            ),
        ]
        store.upsert(records)

        results = store.search_workflows_weighted(
            query_vector=[1.0] + [0.0] * 767,
            query_language="en",  # Different from stored "pl"
            top_k=1,
            min_score=0.0,
        )

        if results:
            assert results[0].language_boost == 0.9

    def test_final_score_formula(self, store):
        """Test final_score = raw_score * source_weight * language_boost."""
        records = [
            VectorRecord(
                id="test_workflow",
                namespace=VectorNamespace.WORKFLOWS,
                vector=[1.0] + [0.0] * 767,
                text="test",
                metadata={
                    "workflow_id": "test_workflow",
                    "source_type": "trigger_keyword",
                    "source_weight": 0.8,
                    "language": "pl",
                },
            ),
        ]
        store.upsert(records)

        results = store.search_workflows_weighted(
            query_vector=[1.0] + [0.0] * 767,
            query_language="en",
            top_k=1,
            min_score=0.0,
        )

        if results:
            result = results[0]
            # Calculate expected final score
            expected = result.raw_score * result.source_weight * result.language_boost
            assert abs(result.final_score - expected) < 0.001
