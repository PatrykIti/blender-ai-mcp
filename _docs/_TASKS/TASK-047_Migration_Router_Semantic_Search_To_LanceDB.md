# TASK-047: Migrate Router Semantic Search to LanceDB

**Priority:** 🔴 High
**Category:** Router Enhancement
**Estimated Effort:** Medium
**Dependencies:** TASK-046 (Router Semantic Generalization)
**Status:** 🚧 In Progress

---

## Overview

Replace the pickle-based embedding cache in Router Supervisor with LanceDB - an embedded vector database.

**Current Problems:**
```
EmbeddingCache (pickle)     WorkflowEmbeddingCache (pickle)
       ↓                              ↓
IntentClassifier            WorkflowIntentClassifier
       ↓                              ↓
   O(N) linear search on all embeddings
```

**Issues with current implementation:**
- **O(N) linear search** - slow for large embedding collections
- **Pickle format** - not portable, security concerns
- **Dual caches** - separate caches for tools and workflows
- **No metadata filtering** - cannot filter by category, mode, etc.
- **No persistence guarantees** - pickle files can corrupt

**Target State:**
```
              LanceVectorStore (LanceDB)
                 ├── namespace: "tools"
                 └── namespace: "workflows"
                        ↓
         IVectorStore interface (domain layer)
                        ↓
    IntentClassifier    WorkflowIntentClassifier
           ↓                      ↓
      O(log N) HNSW ANN search + metadata filters
```

---

## Why LanceDB?

| Feature | Benefit |
|---------|---------|
| **Embedded-first** | No external server required (critical for MCP!) |
| **Native sentence-transformers** | Automatic embedding generation |
| **HNSW indexing** | O(log N) instead of O(N) linear search |
| **Metadata filtering** | Search with filters (category="furniture") |
| **Persistence** | Folder-based, survives restarts |
| **Actively maintained** | Nov 2025, version 0.25.3 |
| **Parquet export** | Portable backup format |

---

## Architecture

### Unified Vector Store with Namespaces

```
┌────────────────────────────────────────────────────────────────┐
│                    LanceVectorStore                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Table: embeddings                                        │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │ id | namespace | vector[768] | text | metadata      │ │  │
│  │  ├─────────────────────────────────────────────────────┤ │  │
│  │  │ "mesh_bevel" | "tools" | [...] | "..." | {...}      │ │  │
│  │  │ "phone_workflow" | "workflows" | [...] | "..." | {} │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                     │
│              HNSW Index (IVF-PQ for large scale)               │
└────────────────────────────────────────────────────────────────┘
         │                              │
         ▼                              ▼
   IntentClassifier          WorkflowIntentClassifier
   (namespace="tools")       (namespace="workflows")
```

**Storage path:** `~/.cache/blender-ai-mcp/vector_store/embeddings.lance/`

---

## Sub-Tasks

### TASK-047-1: Domain Layer - IVectorStore Interface

**Status:** 🚧 Pending

Create the abstract interface for vector storage in the domain layer.

**New file: `server/router/domain/interfaces/i_vector_store.py`**

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional


class VectorNamespace(Enum):
    """Namespace for vector storage."""
    TOOLS = "tools"
    WORKFLOWS = "workflows"


@dataclass
class VectorRecord:
    """A single vector record."""
    id: str                          # tool_name or workflow_name
    namespace: VectorNamespace
    vector: List[float]              # 768D for LaBSE
    text: str                        # Original text
    metadata: Dict[str, Any] = field(default_factory=dict)  # category, mode_required, etc.


@dataclass
class SearchResult:
    """Result from vector search."""
    id: str
    score: float
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class IVectorStore(ABC):
    """Abstract interface for vector storage."""

    @abstractmethod
    def upsert(self, records: List[VectorRecord]) -> int:
        """Insert or update records. Returns count of affected records."""
        pass

    @abstractmethod
    def search(
        self,
        query_vector: List[float],
        namespace: VectorNamespace,
        top_k: int = 5,
        threshold: float = 0.0,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search for similar vectors."""
        pass

    @abstractmethod
    def delete(self, ids: List[str], namespace: VectorNamespace) -> int:
        """Delete records by IDs. Returns count of deleted records."""
        pass

    @abstractmethod
    def count(self, namespace: Optional[VectorNamespace] = None) -> int:
        """Count records in namespace (or all if None)."""
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        pass

    @abstractmethod
    def rebuild_index(self) -> bool:
        """Rebuild the search index."""
        pass
```

**Implementation Checklist:**

| Layer | File | What to Create |
|-------|------|----------------|
| Domain | `server/router/domain/interfaces/i_vector_store.py` | Full implementation above |
| Domain | `server/router/domain/interfaces/__init__.py` | Export `IVectorStore`, `VectorNamespace`, etc. |
| Tests | `tests/unit/router/domain/interfaces/test_i_vector_store.py` | Interface contract tests |

---

### TASK-047-2: Infrastructure Layer - LanceVectorStore

**Status:** 🚧 Pending

Implement the LanceDB-based vector store.

**New file: `server/router/infrastructure/vector_store/lance_store.py`**

```python
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

import lancedb
import pyarrow as pa

from server.router.domain.interfaces.i_vector_store import (
    IVectorStore,
    VectorNamespace,
    VectorRecord,
    SearchResult,
)

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = Path.home() / ".cache" / "blender-ai-mcp" / "vector_store"


class LanceVectorStore(IVectorStore):
    """LanceDB implementation with HNSW indexing."""

    TABLE_NAME = "embeddings"
    VECTOR_DIM = 768  # LaBSE dimension

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize LanceDB connection.

        Args:
            db_path: Path to database directory. Default: ~/.cache/blender-ai-mcp/vector_store/
        """
        self._db_path = db_path or DEFAULT_DB_PATH
        self._db_path.mkdir(parents=True, exist_ok=True)
        self._db = lancedb.connect(str(self._db_path))
        self._table = None
        self._ensure_table()

    def _ensure_table(self) -> None:
        """Create table if it doesn't exist."""
        if self.TABLE_NAME in self._db.table_names():
            self._table = self._db.open_table(self.TABLE_NAME)
        else:
            # Create empty table with schema
            schema = pa.schema([
                pa.field("id", pa.string()),
                pa.field("namespace", pa.string()),
                pa.field("vector", pa.list_(pa.float32(), self.VECTOR_DIM)),
                pa.field("text", pa.string()),
                pa.field("metadata", pa.string()),  # JSON string
            ])
            self._table = self._db.create_table(self.TABLE_NAME, schema=schema)

    def upsert(self, records: List[VectorRecord]) -> int:
        """Insert or update records."""
        if not records:
            return 0

        # Convert to dicts
        data = []
        for r in records:
            data.append({
                "id": r.id,
                "namespace": r.namespace.value,
                "vector": r.vector,
                "text": r.text,
                "metadata": json.dumps(r.metadata),
            })

        # Delete existing records with same IDs
        ids = [r.id for r in records]
        self._table.delete(f"id IN {tuple(ids)}" if len(ids) > 1 else f"id = '{ids[0]}'")

        # Insert new records
        self._table.add(data)
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
        # Build WHERE clause
        where = f"namespace = '{namespace.value}'"
        if metadata_filter:
            for key, value in metadata_filter.items():
                where += f" AND json_extract(metadata, '$.{key}') = '{value}'"

        # Execute search
        results = (
            self._table
            .search(query_vector)
            .where(where)
            .limit(top_k)
            .to_list()
        )

        # Convert to SearchResult
        output = []
        for r in results:
            score = 1.0 - r.get("_distance", 0)  # Convert distance to similarity
            if score >= threshold:
                output.append(SearchResult(
                    id=r["id"],
                    score=score,
                    text=r["text"],
                    metadata=json.loads(r["metadata"]) if r["metadata"] else {},
                ))

        return output

    def delete(self, ids: List[str], namespace: VectorNamespace) -> int:
        """Delete records by IDs."""
        if not ids:
            return 0

        where = f"namespace = '{namespace.value}' AND "
        where += f"id IN {tuple(ids)}" if len(ids) > 1 else f"id = '{ids[0]}'"

        before = self.count(namespace)
        self._table.delete(where)
        after = self.count(namespace)

        return before - after

    def count(self, namespace: Optional[VectorNamespace] = None) -> int:
        """Count records."""
        if namespace:
            return self._table.count_rows(f"namespace = '{namespace.value}'")
        return self._table.count_rows()

    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        return {
            "db_path": str(self._db_path),
            "table_name": self.TABLE_NAME,
            "total_records": self.count(),
            "tools_count": self.count(VectorNamespace.TOOLS),
            "workflows_count": self.count(VectorNamespace.WORKFLOWS),
            "vector_dimension": self.VECTOR_DIM,
        }

    def rebuild_index(self) -> bool:
        """Rebuild HNSW index."""
        try:
            self._table.create_index(
                metric="cosine",
                num_partitions=256,
                num_sub_vectors=96,
                replace=True,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to rebuild index: {e}")
            return False
```

**Implementation Checklist:**

| Layer | File | What to Create |
|-------|------|----------------|
| Infrastructure | `server/router/infrastructure/vector_store/__init__.py` | Exports |
| Infrastructure | `server/router/infrastructure/vector_store/lance_store.py` | Full implementation |
| Tests | `tests/unit/router/infrastructure/vector_store/test_lance_store.py` | Unit tests (25+) |

---

### TASK-047-3: Pickle Migration

**Status:** 🚧 Pending

Auto-migrate existing pickle caches to LanceDB on first run.

**New file: `server/router/infrastructure/vector_store/migrations.py`**

```python
import logging
import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional

from server.router.domain.interfaces.i_vector_store import (
    VectorNamespace,
    VectorRecord,
)
from server.router.infrastructure.vector_store.lance_store import LanceVectorStore

logger = logging.getLogger(__name__)

# Legacy pickle cache paths
LEGACY_TOOL_CACHE = Path.home() / ".cache" / "blender-mcp" / "router" / "embedding_cache.pkl"
LEGACY_WORKFLOW_CACHE = Path.home() / ".cache" / "blender-mcp" / "router" / "workflow_embedding_cache.pkl"


class PickleToLanceMigration:
    """Migrates pickle-based embedding caches to LanceDB."""

    def __init__(self, vector_store: LanceVectorStore):
        """Initialize migration.

        Args:
            vector_store: Target LanceDB store.
        """
        self._store = vector_store

    def migrate_all(self) -> Dict[str, int]:
        """Migrate all legacy caches.

        Returns:
            Dict with migration counts per namespace.
        """
        results = {}

        # Migrate tools
        if LEGACY_TOOL_CACHE.exists():
            count = self._migrate_pickle(LEGACY_TOOL_CACHE, VectorNamespace.TOOLS)
            results["tools"] = count
            logger.info(f"Migrated {count} tool embeddings")

        # Migrate workflows
        if LEGACY_WORKFLOW_CACHE.exists():
            count = self._migrate_pickle(LEGACY_WORKFLOW_CACHE, VectorNamespace.WORKFLOWS)
            results["workflows"] = count
            logger.info(f"Migrated {count} workflow embeddings")

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
        try:
            with open(pickle_path, "rb") as f:
                data = pickle.load(f)

            records = []
            for key, value in data.items():
                # Handle different pickle formats
                if isinstance(value, dict):
                    vector = value.get("embedding", value.get("vector", []))
                    text = value.get("text", key)
                    metadata = value.get("metadata", {})
                else:
                    # Assume value is the vector directly
                    vector = list(value) if hasattr(value, "__iter__") else []
                    text = key
                    metadata = {}

                if vector:
                    records.append(VectorRecord(
                        id=key,
                        namespace=namespace,
                        vector=vector,
                        text=text,
                        metadata=metadata,
                    ))

            if records:
                return self._store.upsert(records)

            return 0

        except Exception as e:
            logger.error(f"Failed to migrate {pickle_path}: {e}")
            return 0

    def cleanup_legacy(self) -> List[str]:
        """Remove legacy pickle files after successful migration.

        Returns:
            List of removed file paths.
        """
        removed = []
        for path in [LEGACY_TOOL_CACHE, LEGACY_WORKFLOW_CACHE]:
            if path.exists():
                path.unlink()
                removed.append(str(path))
                logger.info(f"Removed legacy cache: {path}")

        return removed
```

**Implementation Checklist:**

| Layer | File | What to Create |
|-------|------|----------------|
| Infrastructure | `server/router/infrastructure/vector_store/migrations.py` | Full implementation |
| Tests | `tests/unit/router/infrastructure/vector_store/test_migrations.py` | Migration tests (10+) |

---

### TASK-047-4: Classifier Integration

**Status:** 🚧 Pending

Modify IntentClassifier and WorkflowIntentClassifier to use LanceVectorStore.

**Changes to `server/router/application/classifier/intent_classifier.py`:**

```python
# Add to imports
from server.router.infrastructure.vector_store.lance_store import LanceVectorStore
from server.router.domain.interfaces.i_vector_store import VectorNamespace, VectorRecord

class IntentClassifier:
    def __init__(
        self,
        config: Optional[RouterConfig] = None,
        vector_store: Optional[LanceVectorStore] = None,  # NEW
    ):
        self._config = config or RouterConfig()
        self._vector_store = vector_store or LanceVectorStore()  # LanceDB required
        # ... rest of init

    def _load_tool_embeddings(self) -> None:
        """Load tool embeddings into vector store."""
        # Check if already populated
        if self._vector_store.count(VectorNamespace.TOOLS) > 0:
            return

        # Get all tool metadata
        tools = self._get_tool_metadata()

        # Build records
        records = []
        for tool_name, metadata in tools.items():
            text = self._build_tool_text(tool_name, metadata)
            vector = self._model.encode(text, normalize_embeddings=True)
            records.append(VectorRecord(
                id=tool_name,
                namespace=VectorNamespace.TOOLS,
                vector=vector.tolist(),
                text=text,
                metadata=metadata,
            ))

        self._vector_store.upsert(records)

    def classify(self, prompt: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Classify prompt to tools using vector search."""
        query_vector = self._model.encode(prompt, normalize_embeddings=True)

        results = self._vector_store.search(
            query_vector=query_vector.tolist(),
            namespace=VectorNamespace.TOOLS,
            top_k=top_k,
            threshold=self._config.tool_similarity_threshold,
        )

        return [(r.id, r.score) for r in results]
```

**Similar changes to `server/router/application/classifier/workflow_intent_classifier.py`**

**Implementation Checklist:**

| Layer | File | What to Change |
|-------|------|----------------|
| Classifier | `server/router/application/classifier/intent_classifier.py` | Replace pickle with LanceDB |
| Classifier | `server/router/application/classifier/workflow_intent_classifier.py` | Replace pickle with LanceDB |
| Config | `server/router/infrastructure/config.py` | Add vector store settings |
| Tests | `tests/unit/router/application/classifier/test_intent_classifier_lance.py` | Integration tests |

---

### TASK-047-5: MCP Tool - vector_db_manage

**Status:** 🚧 Pending

Create MCP mega tool for vector database management.

**New file: `server/adapters/mcp/areas/vector_db.py`**

```python
"""
Vector Database MCP Tool.

Provides LLM access to manage the vector database for semantic workflow search.
"""

import json
from typing import Dict, Any, Optional, Literal
from fastmcp import Context

from server.router.infrastructure.vector_store.lance_store import LanceVectorStore
from server.router.domain.interfaces.i_vector_store import VectorNamespace, VectorRecord


def register_vector_db_tools(mcp):
    """Register vector database MCP tools."""

    # Shared store instance
    _store: Optional[LanceVectorStore] = None

    def get_store() -> LanceVectorStore:
        nonlocal _store
        if _store is None:
            _store = LanceVectorStore()
        return _store

    @mcp.tool()
    def vector_db_manage(
        ctx: Context,
        action: Literal[
            "stats",           # Database statistics
            "list",            # List IDs in namespace
            "search_test",     # Test semantic search
            "add_workflow",    # Add workflow to database
            "remove",          # Remove from database
            "export",          # Export to Parquet
            "import",          # Import from Parquet
            "rebuild"          # Rebuild HNSW index
        ],
        namespace: Optional[Literal["tools", "workflows"]] = None,
        query: Optional[str] = None,
        workflow_name: Optional[str] = None,
        workflow_data: Optional[Dict[str, Any]] = None,
        file_path: Optional[str] = None,
        top_k: int = 5,
    ) -> str:
        """
        [SYSTEM][SAFE] Manage vector database for semantic workflow search.

        LLM uses this tool to:
        - Add new workflows discovered from project analysis
        - Search for similar existing workflows
        - Export/import workflow embeddings

        Actions:
            - stats: Database statistics (counts, size, path)
            - list: List all workflow/tool IDs in namespace
            - search_test: Test semantic search with query
            - add_workflow: Add workflow embeddings to DB
            - remove: Remove workflow/tool from DB
            - export: Export namespace to Parquet file
            - import: Import from Parquet file
            - rebuild: Rebuild HNSW search index

        Args:
            action: Operation to perform
            namespace: Target namespace ("tools" or "workflows")
            query: Search query for search_test action
            workflow_name: Workflow name for add_workflow/remove
            workflow_data: Dict with description, sample_prompts, keywords
            file_path: Path for export/import operations
            top_k: Number of results for search_test

        Examples:
            vector_db_manage(action="stats")
            vector_db_manage(action="search_test", namespace="workflows", query="furniture table")
            vector_db_manage(action="add_workflow", workflow_name="chair_v2",
                             workflow_data={"description": "...", "sample_prompts": [...]})
            vector_db_manage(action="export", namespace="workflows", file_path="/tmp/backup.parquet")
        """
        store = get_store()

        if action == "stats":
            return json.dumps(store.get_stats(), indent=2)

        elif action == "list":
            if not namespace:
                return "Error: namespace required for list action"
            ns = VectorNamespace(namespace)
            # Get all records in namespace
            results = store.search(
                query_vector=[0.0] * 768,  # Dummy vector
                namespace=ns,
                top_k=1000,
                threshold=0.0,
            )
            ids = [r.id for r in results]
            return json.dumps({"namespace": namespace, "ids": ids, "count": len(ids)})

        elif action == "search_test":
            if not query or not namespace:
                return "Error: query and namespace required for search_test"
            # This would need the embedding model
            return json.dumps({"message": "search_test requires embedding model integration"})

        elif action == "add_workflow":
            if not workflow_name or not workflow_data:
                return "Error: workflow_name and workflow_data required"
            # Would need to generate embeddings
            return json.dumps({"message": "add_workflow requires embedding model integration"})

        elif action == "remove":
            if not workflow_name or not namespace:
                return "Error: workflow_name and namespace required"
            ns = VectorNamespace(namespace)
            count = store.delete([workflow_name], ns)
            return json.dumps({"deleted": count, "id": workflow_name})

        elif action == "export":
            if not namespace or not file_path:
                return "Error: namespace and file_path required"
            # Export to Parquet
            return json.dumps({"message": "Export not yet implemented"})

        elif action == "import":
            if not file_path:
                return "Error: file_path required"
            return json.dumps({"message": "Import not yet implemented"})

        elif action == "rebuild":
            success = store.rebuild_index()
            return json.dumps({"success": success})

        return json.dumps({"error": f"Unknown action: {action}"})
```

**Implementation Checklist:**

| Layer | File | What to Create/Change |
|-------|------|----------------------|
| Adapter | `server/adapters/mcp/areas/vector_db.py` | Full implementation |
| Server | `server/adapters/mcp/server.py` | Import and register vector_db_tools |
| Tests | `tests/e2e/router/test_vector_db_tool.py` | E2E tests (15+) |

---

## Testing Requirements

- [ ] Unit tests for IVectorStore interface contracts
- [ ] Unit tests for LanceVectorStore (25+ tests)
  - [ ] Test upsert operations
  - [ ] Test search with different thresholds
  - [ ] Test namespace filtering
  - [ ] Test metadata filtering
  - [ ] Test delete operations
  - [ ] Test count operations
  - [ ] Test index rebuild
- [ ] Unit tests for Pickle migration (10+ tests)
  - [ ] Test migration of tool embeddings
  - [ ] Test migration of workflow embeddings
  - [ ] Test handling of corrupt pickle files
  - [ ] Test cleanup of legacy files
- [ ] Integration tests for classifiers with LanceDB (15+ tests)
- [ ] E2E tests for vector_db_manage MCP tool (15+ tests)
- [ ] Performance tests comparing pickle vs LanceDB search times

---

## New Files to Create

### Server Side

```
server/router/domain/interfaces/i_vector_store.py
server/router/infrastructure/vector_store/__init__.py
server/router/infrastructure/vector_store/lance_store.py
server/router/infrastructure/vector_store/migrations.py
server/adapters/mcp/areas/vector_db.py
```

### Tests

```
tests/unit/router/domain/interfaces/test_i_vector_store.py
tests/unit/router/infrastructure/vector_store/__init__.py
tests/unit/router/infrastructure/vector_store/test_lance_store.py
tests/unit/router/infrastructure/vector_store/test_migrations.py
tests/unit/router/application/classifier/test_intent_classifier_lance.py
tests/e2e/router/test_vector_db_tool.py
```

---

## Files to Modify

| File | What to Change |
|------|----------------|
| `server/router/application/classifier/intent_classifier.py` | Replace EmbeddingCache with LanceVectorStore |
| `server/router/application/classifier/workflow_intent_classifier.py` | Replace WorkflowEmbeddingCache with LanceVectorStore |
| `server/router/application/classifier/__init__.py` | Update exports |
| `server/router/infrastructure/config.py` | Add vector store settings |
| `server/adapters/mcp/server.py` | Register vector_db_manage tool |
| `pyproject.toml` | Add lancedb and pyarrow dependencies |

---

## Files to Delete (After Migration)

| File | Reason |
|------|--------|
| `server/router/application/classifier/embedding_cache.py` | Replaced by LanceVectorStore |
| (workflow embedding cache file if exists) | Replaced by LanceVectorStore |

---

## Dependencies

```toml
# pyproject.toml
[project]
dependencies = [
    # existing...
    "lancedb>=0.3.0,<1.0.0",   # REQUIRED - Vector DB
    "pyarrow>=14.0.0",          # REQUIRED - Parquet export
]
```

---

## Documentation Updates Required

| File | What to Update |
|------|----------------|
| `_docs/_TASKS/TASK-047_Migration_Router_Semantic_Search_To_LanceDB.md` | This file |
| `_docs/_TASKS/README.md` | Add TASK-047 to task list |
| `_docs/_ROUTER/README.md` | Add vector store section |
| `_docs/_ROUTER/IMPLEMENTATION/32-lance-vector-store.md` | Create implementation doc |
| `_docs/_CHANGELOG/{NN}-lancedb-migration.md` | Create changelog entry |
| `_docs/_MCP_SERVER/README.md` | Add vector_db_manage tool |
| `_docs/AVAILABLE_TOOLS_SUMMARY.md` | Add vector_db_manage |
| `README.md` | Update Router section, add to autoApprove |

---

## Implementation Order

1. **TASK-047-1** - Domain interface (foundation)
2. **TASK-047-2** - LanceVectorStore (core implementation)
3. **TASK-047-3** - Pickle migration (data migration)
4. **TASK-047-4** - Classifier integration (use new store)
5. **TASK-047-5** - MCP tool (LLM access)

---

## Expected Results

After implementation:

```python
# Before: O(N) linear search
# After: O(log N) HNSW search

# Performance improvement
# 100 embeddings: ~2x faster
# 1000 embeddings: ~10x faster
# 10000 embeddings: ~100x faster

# New capabilities
store.search(
    query_vector=embedding,
    namespace=VectorNamespace.WORKFLOWS,
    top_k=5,
    threshold=0.5,
    metadata_filter={"category": "furniture"},  # NEW!
)

# MCP tool for LLM
vector_db_manage(action="stats")
# → {"total_records": 150, "tools_count": 120, "workflows_count": 30, ...}

vector_db_manage(action="search_test", namespace="workflows", query="create a chair")
# → [{"id": "table_workflow", "score": 0.72}, ...]
```
