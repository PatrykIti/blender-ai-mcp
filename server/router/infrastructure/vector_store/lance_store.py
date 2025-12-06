"""
LanceDB Vector Store Implementation.

Provides O(log N) semantic search with HNSW indexing.
Replaces pickle-based embedding caches.

TASK-047-2
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from server.router.domain.interfaces.i_vector_store import (
    IVectorStore,
    VectorNamespace,
    VectorRecord,
    SearchResult,
)

logger = logging.getLogger(__name__)

# Try to import LanceDB
try:
    import lancedb
    import pyarrow as pa

    LANCEDB_AVAILABLE = True
except ImportError:
    LANCEDB_AVAILABLE = False
    lancedb = None  # type: ignore
    pa = None  # type: ignore
    logger.warning(
        "lancedb or pyarrow not installed. "
        "Vector store will use in-memory fallback."
    )

DEFAULT_DB_PATH = Path.home() / ".cache" / "blender-ai-mcp" / "vector_store"


class LanceVectorStore(IVectorStore):
    """LanceDB implementation with HNSW indexing.

    Features:
    - O(log N) approximate nearest neighbor search
    - Namespace isolation (tools vs workflows)
    - Metadata filtering
    - Persistent storage
    - Automatic index management
    """

    TABLE_NAME = "embeddings"
    VECTOR_DIM = 768  # LaBSE dimension

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize LanceDB connection.

        Args:
            db_path: Path to database directory.
                     Default: ~/.cache/blender-ai-mcp/vector_store/
        """
        self._db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self._db: Optional[Any] = None
        self._table: Optional[Any] = None

        # In-memory fallback when LanceDB unavailable
        self._fallback_store: Dict[str, VectorRecord] = {}
        self._use_fallback = not LANCEDB_AVAILABLE

        if not self._use_fallback:
            self._initialize_db()

    def _initialize_db(self) -> None:
        """Initialize LanceDB connection and table."""
        try:
            self._db_path.mkdir(parents=True, exist_ok=True)
            self._db = lancedb.connect(str(self._db_path))
            self._ensure_table()
            logger.info(f"LanceDB initialized at {self._db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize LanceDB: {e}")
            self._use_fallback = True

    def _ensure_table(self) -> None:
        """Create table if it doesn't exist."""
        if self._db is None:
            return

        try:
            if self.TABLE_NAME in self._db.table_names():
                self._table = self._db.open_table(self.TABLE_NAME)
            else:
                # Create empty table with schema
                schema = pa.schema(
                    [
                        pa.field("id", pa.string()),
                        pa.field("namespace", pa.string()),
                        pa.field("vector", pa.list_(pa.float32(), self.VECTOR_DIM)),
                        pa.field("text", pa.string()),
                        pa.field("metadata", pa.string()),  # JSON string
                    ]
                )
                self._table = self._db.create_table(self.TABLE_NAME, schema=schema)
                logger.info(f"Created LanceDB table: {self.TABLE_NAME}")
        except Exception as e:
            logger.error(f"Failed to ensure table: {e}")
            self._use_fallback = True

    def upsert(self, records: List[VectorRecord]) -> int:
        """Insert or update records."""
        if not records:
            return 0

        if self._use_fallback:
            return self._upsert_fallback(records)

        try:
            # Convert to dicts for LanceDB
            data = []
            for r in records:
                data.append(
                    {
                        "id": r.id,
                        "namespace": r.namespace.value,
                        "vector": r.vector,
                        "text": r.text,
                        "metadata": json.dumps(r.metadata),
                    }
                )

            # Delete existing records with same IDs in same namespace
            for r in records:
                try:
                    self._table.delete(
                        f"id = '{r.id}' AND namespace = '{r.namespace.value}'"
                    )
                except Exception:
                    pass  # Record may not exist

            # Insert new records
            self._table.add(data)
            logger.debug(f"Upserted {len(records)} records")
            return len(records)

        except Exception as e:
            logger.error(f"Failed to upsert records: {e}")
            return self._upsert_fallback(records)

    def _upsert_fallback(self, records: List[VectorRecord]) -> int:
        """Fallback upsert using in-memory store."""
        for r in records:
            key = f"{r.namespace.value}:{r.id}"
            self._fallback_store[key] = r
        return len(records)

    def search(
        self,
        query_vector: List[float],
        namespace: VectorNamespace,
        top_k: int = 5,
        threshold: float = 0.0,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search for similar vectors using HNSW."""
        if self._use_fallback:
            return self._search_fallback(
                query_vector, namespace, top_k, threshold, metadata_filter
            )

        try:
            # Build WHERE clause for namespace filter
            where = f"namespace = '{namespace.value}'"

            # Add metadata filters if provided
            if metadata_filter:
                for key, value in metadata_filter.items():
                    if isinstance(value, str):
                        where += f" AND json_extract(metadata, '$.{key}') = '{value}'"
                    else:
                        where += f" AND json_extract(metadata, '$.{key}') = {value}"

            # Execute search
            results = (
                self._table.search(query_vector)
                .where(where)
                .limit(top_k)
                .to_list()
            )

            # Convert to SearchResult
            output = []
            for r in results:
                # LanceDB returns _distance (L2 squared for normalized vectors)
                # For normalized vectors: L2² = 2 - 2*cosine_similarity
                # Therefore: cosine_similarity = 1 - (L2² / 2)
                distance = r.get("_distance", 0)
                score = max(0.0, 1.0 - (distance / 2.0))

                if score >= threshold:
                    metadata = {}
                    if r.get("metadata"):
                        try:
                            metadata = json.loads(r["metadata"])
                        except (json.JSONDecodeError, TypeError):
                            pass

                    output.append(
                        SearchResult(
                            id=r["id"],
                            score=score,
                            text=r.get("text", ""),
                            metadata=metadata,
                        )
                    )

            return output

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return self._search_fallback(
                query_vector, namespace, top_k, threshold, metadata_filter
            )

    def _search_fallback(
        self,
        query_vector: List[float],
        namespace: VectorNamespace,
        top_k: int,
        threshold: float,
        metadata_filter: Optional[Dict[str, Any]],
    ) -> List[SearchResult]:
        """Fallback search using linear scan."""
        try:
            import numpy as np

            query = np.array(query_vector)
            query_norm = np.linalg.norm(query)
            if query_norm > 0:
                query = query / query_norm

            results = []
            for key, record in self._fallback_store.items():
                if record.namespace != namespace:
                    continue

                # Apply metadata filter
                if metadata_filter:
                    match = True
                    for k, v in metadata_filter.items():
                        if record.metadata.get(k) != v:
                            match = False
                            break
                    if not match:
                        continue

                # Calculate cosine similarity
                vec = np.array(record.vector)
                vec_norm = np.linalg.norm(vec)
                if vec_norm > 0:
                    vec = vec / vec_norm

                score = float(np.dot(query, vec))

                if score >= threshold:
                    results.append(
                        SearchResult(
                            id=record.id,
                            score=score,
                            text=record.text,
                            metadata=record.metadata,
                        )
                    )

            # Sort by score descending
            results.sort(key=lambda x: x.score, reverse=True)
            return results[:top_k]

        except ImportError:
            logger.error("NumPy not available for fallback search")
            return []

    def delete(self, ids: List[str], namespace: VectorNamespace) -> int:
        """Delete records by IDs."""
        if not ids:
            return 0

        if self._use_fallback:
            return self._delete_fallback(ids, namespace)

        try:
            count = 0
            for id_ in ids:
                try:
                    before = self._table.count_rows(
                        f"id = '{id_}' AND namespace = '{namespace.value}'"
                    )
                    self._table.delete(
                        f"id = '{id_}' AND namespace = '{namespace.value}'"
                    )
                    count += before
                except Exception:
                    pass

            logger.debug(f"Deleted {count} records")
            return count

        except Exception as e:
            logger.error(f"Failed to delete records: {e}")
            return self._delete_fallback(ids, namespace)

    def _delete_fallback(self, ids: List[str], namespace: VectorNamespace) -> int:
        """Fallback delete using in-memory store."""
        count = 0
        for id_ in ids:
            key = f"{namespace.value}:{id_}"
            if key in self._fallback_store:
                del self._fallback_store[key]
                count += 1
        return count

    def count(self, namespace: Optional[VectorNamespace] = None) -> int:
        """Count records in namespace."""
        if self._use_fallback:
            return self._count_fallback(namespace)

        try:
            if namespace:
                return self._table.count_rows(f"namespace = '{namespace.value}'")
            return self._table.count_rows()
        except Exception as e:
            logger.error(f"Failed to count records: {e}")
            return self._count_fallback(namespace)

    def _count_fallback(self, namespace: Optional[VectorNamespace]) -> int:
        """Fallback count using in-memory store."""
        if namespace is None:
            return len(self._fallback_store)

        count = 0
        for record in self._fallback_store.values():
            if record.namespace == namespace:
                count += 1
        return count

    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        return {
            "db_path": str(self._db_path),
            "table_name": self.TABLE_NAME,
            "vector_dimension": self.VECTOR_DIM,
            "total_records": self.count(),
            "tools_count": self.count(VectorNamespace.TOOLS),
            "workflows_count": self.count(VectorNamespace.WORKFLOWS),
            "using_fallback": self._use_fallback,
            "lancedb_available": LANCEDB_AVAILABLE,
        }

    def rebuild_index(self) -> bool:
        """Rebuild HNSW index for optimal search performance."""
        if self._use_fallback:
            return True  # No index to rebuild

        try:
            # LanceDB auto-manages indexes, but we can force optimization
            self._table.create_index(
                metric="cosine",
                num_partitions=256,
                num_sub_vectors=96,
                replace=True,
            )
            logger.info("Rebuilt HNSW index")
            return True
        except Exception as e:
            logger.error(f"Failed to rebuild index: {e}")
            return False

    def clear(self, namespace: Optional[VectorNamespace] = None) -> int:
        """Clear all records from namespace."""
        if self._use_fallback:
            return self._clear_fallback(namespace)

        try:
            before = self.count(namespace)

            if namespace:
                self._table.delete(f"namespace = '{namespace.value}'")
            else:
                # Delete all records
                self._table.delete("id IS NOT NULL")

            after = self.count(namespace)
            deleted = before - after
            logger.info(f"Cleared {deleted} records from {namespace or 'all'}")
            return deleted

        except Exception as e:
            logger.error(f"Failed to clear records: {e}")
            return self._clear_fallback(namespace)

    def _clear_fallback(self, namespace: Optional[VectorNamespace]) -> int:
        """Fallback clear using in-memory store."""
        if namespace is None:
            count = len(self._fallback_store)
            self._fallback_store.clear()
            return count

        to_delete = []
        for key, record in self._fallback_store.items():
            if record.namespace == namespace:
                to_delete.append(key)

        for key in to_delete:
            del self._fallback_store[key]

        return len(to_delete)

    def get_all_ids(self, namespace: VectorNamespace) -> List[str]:
        """Get all record IDs in a namespace.

        Args:
            namespace: Namespace to query.

        Returns:
            List of record IDs.
        """
        if self._use_fallback:
            return [
                r.id
                for r in self._fallback_store.values()
                if r.namespace == namespace
            ]

        try:
            # Query all records in namespace
            results = (
                self._table.search()
                .where(f"namespace = '{namespace.value}'")
                .select(["id"])
                .limit(10000)
                .to_list()
            )
            return [r["id"] for r in results]
        except Exception as e:
            logger.error(f"Failed to get IDs: {e}")
            return []

    def is_available(self) -> bool:
        """Check if vector store is available and working.

        Returns:
            True if store is operational.
        """
        return LANCEDB_AVAILABLE and not self._use_fallback
