"""
Pickle to LanceDB Migration.

Auto-migrates existing pickle-based embedding caches to LanceDB.
Run automatically on first startup after upgrade.

TASK-047-3
"""

import logging
import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional

from server.router.domain.interfaces.i_vector_store import (
    IVectorStore,
    VectorNamespace,
    VectorRecord,
)

logger = logging.getLogger(__name__)

# Try to import numpy for array handling
try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None  # type: ignore

# Legacy pickle cache paths (actual paths from current implementation)
LEGACY_CACHE_DIR = Path.home() / ".cache" / "blender-ai-mcp" / "router"
LEGACY_TOOL_CACHE = LEGACY_CACHE_DIR / "tool_embeddings.pkl"
LEGACY_TOOL_HASH = LEGACY_CACHE_DIR / "metadata_hash.txt"
LEGACY_WORKFLOW_CACHE = LEGACY_CACHE_DIR / "workflow_embeddings.pkl"
LEGACY_WORKFLOW_HASH = LEGACY_CACHE_DIR / "workflow_hash.txt"


class PickleToLanceMigration:
    """Migrates pickle-based embedding caches to LanceDB.

    The legacy pickle format stores Dict[str, numpy.ndarray] where:
    - Key: tool_name or workflow_name
    - Value: 768-dimensional numpy array (LaBSE embedding)

    Note: Original text and metadata are NOT stored in pickle files.
    They are reconstructed from the key names.
    """

    def __init__(self, vector_store: IVectorStore):
        """Initialize migration.

        Args:
            vector_store: Target LanceDB store.
        """
        self._store = vector_store
        self._migrated_tools = 0
        self._migrated_workflows = 0

    def needs_migration(self) -> bool:
        """Check if legacy caches exist and need migration.

        Returns:
            True if any legacy pickle files exist.
        """
        return LEGACY_TOOL_CACHE.exists() or LEGACY_WORKFLOW_CACHE.exists()

    def migrate_all(self, cleanup: bool = False) -> Dict[str, int]:
        """Migrate all legacy caches.

        Args:
            cleanup: If True, remove legacy files after successful migration.

        Returns:
            Dict with migration counts per namespace.
        """
        results = {}

        # Migrate tools
        if LEGACY_TOOL_CACHE.exists():
            count = self._migrate_pickle(LEGACY_TOOL_CACHE, VectorNamespace.TOOLS)
            results["tools"] = count
            self._migrated_tools = count
            if count > 0:
                logger.info(f"Migrated {count} tool embeddings to LanceDB")

        # Migrate workflows
        if LEGACY_WORKFLOW_CACHE.exists():
            count = self._migrate_pickle(LEGACY_WORKFLOW_CACHE, VectorNamespace.WORKFLOWS)
            results["workflows"] = count
            self._migrated_workflows = count
            if count > 0:
                logger.info(f"Migrated {count} workflow embeddings to LanceDB")

        # Cleanup if requested and migration successful
        if cleanup and (results.get("tools", 0) > 0 or results.get("workflows", 0) > 0):
            removed = self.cleanup_legacy()
            results["cleaned_files"] = len(removed)

        return results

    def _migrate_pickle(
        self,
        pickle_path: Path,
        namespace: VectorNamespace,
    ) -> int:
        """Migrate a single pickle file.

        Args:
            pickle_path: Path to pickle file.
            namespace: Target namespace.

        Returns:
            Number of records migrated.
        """
        if not NUMPY_AVAILABLE:
            logger.warning("NumPy not available, cannot migrate pickle files")
            return 0

        try:
            with open(pickle_path, "rb") as f:
                data = pickle.load(f)

            if not isinstance(data, dict):
                logger.warning(f"Unexpected pickle format in {pickle_path}")
                return 0

            records = []
            for key, value in data.items():
                vector = self._extract_vector(value)

                if vector is None:
                    logger.warning(f"Skipping {key}: could not extract vector")
                    continue

                if len(vector) != 768:
                    logger.warning(
                        f"Skipping {key}: wrong vector dimension {len(vector)}"
                    )
                    continue

                records.append(
                    VectorRecord(
                        id=key,
                        namespace=namespace,
                        vector=vector,
                        text=key.replace("_", " "),  # Fallback: use name as text
                        metadata={},  # Metadata not stored in legacy pickle
                    )
                )

            if records:
                return self._store.upsert(records)

            return 0

        except Exception as e:
            logger.error(f"Failed to migrate {pickle_path}: {e}")
            return 0

    def _extract_vector(self, value: Any) -> Optional[List[float]]:
        """Extract vector from pickle value.

        Handles both numpy arrays and lists.

        Args:
            value: Value from pickle dict.

        Returns:
            Vector as list of floats, or None if invalid.
        """
        try:
            if isinstance(value, np.ndarray):
                return value.tolist()
            elif isinstance(value, list):
                return [float(v) for v in value]
            elif hasattr(value, "__iter__"):
                return [float(v) for v in value]
            else:
                return None
        except (TypeError, ValueError) as e:
            logger.debug(f"Could not convert value to vector: {e}")
            return None

    def cleanup_legacy(self) -> List[str]:
        """Remove legacy pickle files after successful migration.

        Returns:
            List of removed file paths.
        """
        removed = []
        legacy_files = [
            LEGACY_TOOL_CACHE,
            LEGACY_TOOL_HASH,
            LEGACY_WORKFLOW_CACHE,
            LEGACY_WORKFLOW_HASH,
        ]

        for path in legacy_files:
            if path.exists():
                try:
                    path.unlink()
                    removed.append(str(path))
                    logger.info(f"Removed legacy cache: {path}")
                except Exception as e:
                    logger.error(f"Failed to remove {path}: {e}")

        return removed

    def get_migration_summary(self) -> Dict[str, Any]:
        """Get summary of migration state.

        Returns:
            Dict with migration status information.
        """
        return {
            "needs_migration": self.needs_migration(),
            "legacy_tool_cache_exists": LEGACY_TOOL_CACHE.exists(),
            "legacy_workflow_cache_exists": LEGACY_WORKFLOW_CACHE.exists(),
            "migrated_tools": self._migrated_tools,
            "migrated_workflows": self._migrated_workflows,
            "legacy_cache_dir": str(LEGACY_CACHE_DIR),
        }


def auto_migrate_if_needed(vector_store: IVectorStore) -> Dict[str, int]:
    """Automatically migrate legacy caches if they exist.

    Called during router initialization.

    Args:
        vector_store: Target vector store.

    Returns:
        Migration results (empty dict if no migration needed).
    """
    migration = PickleToLanceMigration(vector_store)

    if migration.needs_migration():
        logger.info("Legacy pickle caches detected, starting migration...")
        results = migration.migrate_all(cleanup=False)  # Don't cleanup automatically
        logger.info(f"Migration complete: {results}")
        return results

    return {}
