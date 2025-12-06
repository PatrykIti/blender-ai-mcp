"""
Unit tests for Pickle to LanceDB migration.

TASK-047-3
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import pickle

from server.router.infrastructure.vector_store.migrations import (
    PickleToLanceMigration,
    LEGACY_CACHE_DIR,
    LEGACY_TOOL_CACHE,
    LEGACY_WORKFLOW_CACHE,
    NUMPY_AVAILABLE,
)
from server.router.domain.interfaces.i_vector_store import (
    VectorNamespace,
    VectorRecord,
)


# Mock vector store for testing
class MockVectorStore:
    """Mock vector store for migration tests."""

    def __init__(self):
        self._records = {}

    def upsert(self, records):
        for r in records:
            key = f"{r.namespace.value}:{r.id}"
            self._records[key] = r
        return len(records)

    def count(self, namespace=None):
        if namespace is None:
            return len(self._records)
        return sum(1 for k in self._records if k.startswith(namespace.value))

    def clear(self, namespace=None):
        if namespace is None:
            count = len(self._records)
            self._records.clear()
            return count
        to_delete = [k for k in self._records if k.startswith(namespace.value)]
        for k in to_delete:
            del self._records[k]
        return len(to_delete)


@pytest.fixture
def mock_store():
    """Create a mock vector store."""
    return MockVectorStore()


@pytest.fixture
def temp_legacy_dir(monkeypatch):
    """Create temp directory and mock legacy cache paths."""
    tmpdir = tempfile.mkdtemp()
    legacy_dir = Path(tmpdir) / "legacy"
    legacy_dir.mkdir()

    # Monkeypatch the legacy paths
    monkeypatch.setattr(
        "server.router.infrastructure.vector_store.migrations.LEGACY_CACHE_DIR",
        legacy_dir,
    )
    monkeypatch.setattr(
        "server.router.infrastructure.vector_store.migrations.LEGACY_TOOL_CACHE",
        legacy_dir / "tool_embeddings.pkl",
    )
    monkeypatch.setattr(
        "server.router.infrastructure.vector_store.migrations.LEGACY_TOOL_HASH",
        legacy_dir / "metadata_hash.txt",
    )
    monkeypatch.setattr(
        "server.router.infrastructure.vector_store.migrations.LEGACY_WORKFLOW_CACHE",
        legacy_dir / "workflow_embeddings.pkl",
    )
    monkeypatch.setattr(
        "server.router.infrastructure.vector_store.migrations.LEGACY_WORKFLOW_HASH",
        legacy_dir / "workflow_hash.txt",
    )

    yield legacy_dir

    # Cleanup
    shutil.rmtree(tmpdir, ignore_errors=True)


def create_pickle_file(path, data):
    """Helper to create pickle file with data."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(data, f)


class TestPickleToLanceMigrationNeedsMigration:
    """Tests for needs_migration method."""

    def test_no_migration_needed_when_no_files(self, mock_store, temp_legacy_dir):
        """Test no migration needed when no legacy files exist."""
        migration = PickleToLanceMigration(mock_store)

        # Reimport to get monkeypatched paths
        from server.router.infrastructure.vector_store import migrations

        assert not migration.needs_migration()

    @pytest.mark.skipif(not NUMPY_AVAILABLE, reason="NumPy not available")
    def test_migration_needed_when_tool_cache_exists(self, mock_store, temp_legacy_dir):
        """Test migration needed when tool cache exists."""
        import numpy as np

        # Create fake tool cache
        from server.router.infrastructure.vector_store import migrations

        tool_cache_path = migrations.LEGACY_TOOL_CACHE
        create_pickle_file(
            tool_cache_path,
            {"mesh_extrude": np.array([0.1] * 768)},
        )

        migration = PickleToLanceMigration(mock_store)

        assert migration.needs_migration()

    @pytest.mark.skipif(not NUMPY_AVAILABLE, reason="NumPy not available")
    def test_migration_needed_when_workflow_cache_exists(
        self, mock_store, temp_legacy_dir
    ):
        """Test migration needed when workflow cache exists."""
        import numpy as np

        from server.router.infrastructure.vector_store import migrations

        workflow_cache_path = migrations.LEGACY_WORKFLOW_CACHE
        create_pickle_file(
            workflow_cache_path,
            {"phone_workflow": np.array([0.3] * 768)},
        )

        migration = PickleToLanceMigration(mock_store)

        assert migration.needs_migration()


class TestPickleToLanceMigrationMigrateAll:
    """Tests for migrate_all method."""

    def test_migrate_empty(self, mock_store, temp_legacy_dir):
        """Test migration with no legacy files."""
        migration = PickleToLanceMigration(mock_store)

        results = migration.migrate_all()

        assert results == {}

    @pytest.mark.skipif(not NUMPY_AVAILABLE, reason="NumPy not available")
    def test_migrate_tool_embeddings(self, mock_store, temp_legacy_dir):
        """Test migrating tool embeddings."""
        import numpy as np

        from server.router.infrastructure.vector_store import migrations

        # Create tool cache
        tool_cache_path = migrations.LEGACY_TOOL_CACHE
        create_pickle_file(
            tool_cache_path,
            {
                "mesh_extrude": np.array([0.1] * 768),
                "mesh_bevel": np.array([0.2] * 768),
            },
        )

        migration = PickleToLanceMigration(mock_store)
        results = migration.migrate_all()

        assert "tools" in results
        assert results["tools"] == 2
        assert mock_store.count(VectorNamespace.TOOLS) == 2

    @pytest.mark.skipif(not NUMPY_AVAILABLE, reason="NumPy not available")
    def test_migrate_workflow_embeddings(self, mock_store, temp_legacy_dir):
        """Test migrating workflow embeddings."""
        import numpy as np

        from server.router.infrastructure.vector_store import migrations

        # Create workflow cache
        workflow_cache_path = migrations.LEGACY_WORKFLOW_CACHE
        create_pickle_file(
            workflow_cache_path,
            {"phone_workflow": np.array([0.3] * 768)},
        )

        migration = PickleToLanceMigration(mock_store)
        results = migration.migrate_all()

        assert "workflows" in results
        assert results["workflows"] == 1
        assert mock_store.count(VectorNamespace.WORKFLOWS) == 1

    @pytest.mark.skipif(not NUMPY_AVAILABLE, reason="NumPy not available")
    def test_migrate_both(self, mock_store, temp_legacy_dir):
        """Test migrating both tools and workflows."""
        import numpy as np

        from server.router.infrastructure.vector_store import migrations

        # Create both caches
        create_pickle_file(
            migrations.LEGACY_TOOL_CACHE,
            {"mesh_extrude": np.array([0.1] * 768)},
        )
        create_pickle_file(
            migrations.LEGACY_WORKFLOW_CACHE,
            {"phone_workflow": np.array([0.3] * 768)},
        )

        migration = PickleToLanceMigration(mock_store)
        results = migration.migrate_all()

        assert results["tools"] == 1
        assert results["workflows"] == 1

    @pytest.mark.skipif(not NUMPY_AVAILABLE, reason="NumPy not available")
    def test_migrate_skips_wrong_dimension(self, mock_store, temp_legacy_dir):
        """Test that migration skips vectors with wrong dimension."""
        import numpy as np

        from server.router.infrastructure.vector_store import migrations

        # Create cache with wrong dimension
        create_pickle_file(
            migrations.LEGACY_TOOL_CACHE,
            {
                "good_tool": np.array([0.1] * 768),
                "bad_tool": np.array([0.1] * 100),  # Wrong dimension
            },
        )

        migration = PickleToLanceMigration(mock_store)
        results = migration.migrate_all()

        assert results["tools"] == 1  # Only good_tool migrated


class TestPickleToLanceMigrationCleanup:
    """Tests for cleanup_legacy method."""

    @pytest.mark.skipif(not NUMPY_AVAILABLE, reason="NumPy not available")
    def test_cleanup_removes_files(self, mock_store, temp_legacy_dir):
        """Test cleanup removes legacy files."""
        import numpy as np

        from server.router.infrastructure.vector_store import migrations

        # Create legacy files
        create_pickle_file(
            migrations.LEGACY_TOOL_CACHE,
            {"test": np.array([0.1] * 768)},
        )
        migrations.LEGACY_TOOL_HASH.write_text("hash123")

        migration = PickleToLanceMigration(mock_store)
        removed = migration.cleanup_legacy()

        assert len(removed) == 2
        assert not migrations.LEGACY_TOOL_CACHE.exists()
        assert not migrations.LEGACY_TOOL_HASH.exists()

    def test_cleanup_no_files(self, mock_store, temp_legacy_dir):
        """Test cleanup with no files to remove."""
        migration = PickleToLanceMigration(mock_store)
        removed = migration.cleanup_legacy()

        assert removed == []


class TestPickleToLanceMigrationSummary:
    """Tests for get_migration_summary method."""

    def test_summary_structure(self, mock_store, temp_legacy_dir):
        """Test migration summary has expected structure."""
        migration = PickleToLanceMigration(mock_store)
        summary = migration.get_migration_summary()

        assert "needs_migration" in summary
        assert "legacy_tool_cache_exists" in summary
        assert "legacy_workflow_cache_exists" in summary
        assert "migrated_tools" in summary
        assert "migrated_workflows" in summary
        assert "legacy_cache_dir" in summary

    @pytest.mark.skipif(not NUMPY_AVAILABLE, reason="NumPy not available")
    def test_summary_after_migration(self, mock_store, temp_legacy_dir):
        """Test summary reflects migration results."""
        import numpy as np

        from server.router.infrastructure.vector_store import migrations

        create_pickle_file(
            migrations.LEGACY_TOOL_CACHE,
            {"test": np.array([0.1] * 768)},
        )

        migration = PickleToLanceMigration(mock_store)
        migration.migrate_all()
        summary = migration.get_migration_summary()

        assert summary["migrated_tools"] == 1
        assert summary["legacy_tool_cache_exists"] is True
