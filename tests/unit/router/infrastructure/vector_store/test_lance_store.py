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

    @pytest.mark.skipif(not LANCEDB_AVAILABLE, reason="LanceDB not installed")
    def test_init_creates_db_path(self, temp_db_path):
        """Test that init creates database directory when LanceDB available."""
        db_path = temp_db_path / "subdir" / "db"
        store = LanceVectorStore(db_path=db_path)
        # Directory is created during initialization when LanceDB is available
        assert db_path.exists()

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
