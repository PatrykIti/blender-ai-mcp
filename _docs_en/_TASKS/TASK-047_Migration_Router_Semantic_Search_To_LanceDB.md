# TASK-047: Migrate Router Semantic Search to LanceDB

**Priority:** 🔴 High
**Category:** Router Enhancement
**Estimated Effort:** Medium
**Dependencies:** TASK-046 (Router Semantic Generalization)
**Status:** ✅ Done

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

### TASK-047-1: Domain Layer - IVectorStore & IWorkflowIntentClassifier Interfaces

**Status:** ✅ Done

Create the abstract interfaces for vector storage and workflow classification in the domain layer.

#### 1a. IVectorStore Interface

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

#### 1b. IWorkflowIntentClassifier Interface

**New file: `server/router/domain/interfaces/i_workflow_intent_classifier.py`**

> **Note:** This interface ensures Clean Architecture compliance. Currently `WorkflowIntentClassifier`
> does not implement an interface, which violates DIP (Dependency Inversion Principle).

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Optional


class IWorkflowIntentClassifier(ABC):
    """Abstract interface for workflow intent classification.

    Enables semantic matching of user prompts to workflow definitions.
    Supports workflow generalization for unknown object types.
    """

    @abstractmethod
    def load_workflow_embeddings(self, workflows: Dict[str, Any]) -> None:
        """Load and cache workflow embeddings.

        Args:
            workflows: Dictionary of workflow name -> workflow object/definition.
        """
        pass

    @abstractmethod
    def find_similar(
        self,
        prompt: str,
        top_k: int = 3,
        threshold: float = 0.0,
    ) -> List[Tuple[str, float]]:
        """Find workflows semantically similar to prompt.

        Args:
            prompt: User prompt or intent.
            top_k: Number of results to return.
            threshold: Minimum similarity score.

        Returns:
            List of (workflow_name, similarity_score) tuples.
        """
        pass

    @abstractmethod
    def find_best_match(
        self,
        prompt: str,
        min_confidence: float = 0.5,
    ) -> Optional[Tuple[str, float]]:
        """Find the best matching workflow.

        Args:
            prompt: User prompt.
            min_confidence: Minimum confidence score.

        Returns:
            (workflow_name, confidence) or None.
        """
        pass

    @abstractmethod
    def get_generalization_candidates(
        self,
        prompt: str,
        min_similarity: float = 0.3,
        max_candidates: int = 3,
    ) -> List[Tuple[str, float]]:
        """Get workflows that could be generalized for this prompt.

        Args:
            prompt: User prompt.
            min_similarity: Minimum similarity to consider.
            max_candidates: Maximum workflows to return.

        Returns:
            List of (workflow_name, similarity) tuples.
        """
        pass

    @abstractmethod
    def is_loaded(self) -> bool:
        """Check if classifier is loaded."""
        pass

    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """Get classifier information."""
        pass

    @abstractmethod
    def clear_cache(self) -> bool:
        """Clear the embedding cache."""
        pass
```

**Implementation Checklist:**

| Layer | File | What to Create |
|-------|------|----------------|
| Domain | `server/router/domain/interfaces/i_vector_store.py` | IVectorStore + dataclasses |
| Domain | `server/router/domain/interfaces/i_workflow_intent_classifier.py` | IWorkflowIntentClassifier |
| Domain | `server/router/domain/interfaces/__init__.py` | Export all new interfaces |
| Tests | `tests/unit/router/domain/interfaces/test_i_vector_store.py` | Interface contract tests |
| Tests | `tests/unit/router/domain/interfaces/test_i_workflow_intent_classifier.py` | Interface contract tests |

---

### TASK-047-2: Infrastructure Layer - LanceVectorStore

**Status:** ✅ Done

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

**Status:** ✅ Done

Auto-migrate existing pickle caches to LanceDB on first run.

#### Current Pickle Cache Format Analysis

**Actual cache file locations (from current implementation):**
```python
# EmbeddingCache (embedding_cache.py:37-39)
~/.cache/blender-ai-mcp/router/tool_embeddings.pkl
~/.cache/blender-ai-mcp/router/metadata_hash.txt

# WorkflowEmbeddingCache (workflow_intent_classifier.py:56-57)
~/.cache/blender-ai-mcp/router/workflow_embeddings.pkl
~/.cache/blender-ai-mcp/router/workflow_hash.txt
```

**Actual pickle data format:**
```python
# The pickle files contain: Dict[str, numpy.ndarray]
# Key: tool_name or workflow_name
# Value: numpy.ndarray with shape (768,) - the embedding vector directly
#
# NO nested dict structure with "embedding", "text", "metadata" keys!
# The metadata (sample_prompts, keywords) is NOT stored in pickle.
```

**New file: `server/router/infrastructure/vector_store/migrations.py`**

```python
import logging
import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional

import numpy as np

from server.router.domain.interfaces.i_vector_store import (
    VectorNamespace,
    VectorRecord,
)
from server.router.infrastructure.vector_store.lance_store import LanceVectorStore

logger = logging.getLogger(__name__)

# Legacy pickle cache paths (CORRECTED)
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
    They must be reconstructed from tool/workflow definitions.
    """

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
                # Current format: value is numpy.ndarray directly
                if isinstance(value, np.ndarray):
                    vector = value.tolist()
                elif hasattr(value, "__iter__"):
                    vector = list(value)
                else:
                    logger.warning(f"Skipping {key}: unexpected value type {type(value)}")
                    continue

                if len(vector) != 768:
                    logger.warning(f"Skipping {key}: wrong vector dimension {len(vector)}")
                    continue

                records.append(VectorRecord(
                    id=key,
                    namespace=namespace,
                    vector=vector,
                    text=key.replace("_", " "),  # Fallback: use name as text
                    metadata={},  # Metadata not stored in legacy pickle
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
        legacy_files = [
            LEGACY_TOOL_CACHE,
            LEGACY_TOOL_HASH,
            LEGACY_WORKFLOW_CACHE,
            LEGACY_WORKFLOW_HASH,
        ]

        for path in legacy_files:
            if path.exists():
                path.unlink()
                removed.append(str(path))
                logger.info(f"Removed legacy cache: {path}")

        return removed

    def needs_migration(self) -> bool:
        """Check if legacy caches exist and need migration.

        Returns:
            True if any legacy pickle files exist.
        """
        return LEGACY_TOOL_CACHE.exists() or LEGACY_WORKFLOW_CACHE.exists()
```

**Implementation Checklist:**

| Layer | File | What to Create |
|-------|------|----------------|
| Infrastructure | `server/router/infrastructure/vector_store/migrations.py` | Full implementation |
| Tests | `tests/unit/router/infrastructure/vector_store/test_migrations.py` | Migration tests (10+) |

---

### TASK-047-4: Classifier Integration

**Status:** ✅ Done

Modify IntentClassifier and WorkflowIntentClassifier to use LanceVectorStore.

#### Current Config Field Names (from `config.py`)

```python
# RouterConfig currently has:
embedding_threshold: float = 0.40              # For tool classification
workflow_similarity_threshold: float = 0.5    # For workflow matching
generalization_threshold: float = 0.3         # For workflow generalization
```

#### Changes to IntentClassifier

**File: `server/router/application/classifier/intent_classifier.py`**

```python
# Add to imports
from server.router.domain.interfaces.i_vector_store import (
    IVectorStore,
    VectorNamespace,
    VectorRecord,
)

class IntentClassifier(IIntentClassifier):
    """Implementation using LanceDB vector store."""

    def __init__(
        self,
        config: Optional[RouterConfig] = None,
        vector_store: Optional[IVectorStore] = None,  # NEW: inject via interface
        model_name: str = MODEL_NAME,
    ):
        self._config = config or RouterConfig()
        self._vector_store = vector_store  # Will be injected or created lazily
        self._model_name = model_name
        self._model: Optional[Any] = None
        self._is_loaded = False

    def _ensure_vector_store(self) -> IVectorStore:
        """Lazily create vector store if not injected."""
        if self._vector_store is None:
            from server.router.infrastructure.vector_store.lance_store import LanceVectorStore
            self._vector_store = LanceVectorStore()
        return self._vector_store

    def load_tool_embeddings(self, metadata: Dict[str, Any]) -> None:
        """Load tool embeddings into vector store."""
        store = self._ensure_vector_store()

        # Check if already populated
        if store.count(VectorNamespace.TOOLS) > 0:
            self._is_loaded = True
            return

        if not EMBEDDINGS_AVAILABLE or not self._load_model():
            self._setup_tfidf_fallback()
            self._is_loaded = True
            return

        # Build records
        records = []
        for tool_name, tool_meta in metadata.items():
            text = self._build_tool_text(tool_name, tool_meta)
            vector = self._model.encode(text, normalize_embeddings=True)
            records.append(VectorRecord(
                id=tool_name,
                namespace=VectorNamespace.TOOLS,
                vector=vector.tolist(),
                text=text,
                metadata=tool_meta,
            ))

        store.upsert(records)
        self._is_loaded = True

    def predict_top_k(
        self,
        prompt: str,
        k: int = 5,
    ) -> List[Tuple[str, float]]:
        """Classify prompt to tools using vector search."""
        if not self._is_loaded:
            return []

        # Fallback to TF-IDF if embeddings unavailable
        if self._tfidf_vectorizer is not None:
            return self._predict_with_tfidf(prompt, k)

        if self._model is None:
            return []

        store = self._ensure_vector_store()
        query_vector = self._model.encode(prompt, normalize_embeddings=True)

        results = store.search(
            query_vector=query_vector.tolist(),
            namespace=VectorNamespace.TOOLS,
            top_k=k,
            threshold=self._config.embedding_threshold,  # CORRECT field name
        )

        return [(r.id, r.score) for r in results]
```

#### Changes to WorkflowIntentClassifier

**File: `server/router/application/classifier/workflow_intent_classifier.py`**

```python
# Add import
from server.router.domain.interfaces.i_workflow_intent_classifier import IWorkflowIntentClassifier
from server.router.domain.interfaces.i_vector_store import (
    IVectorStore,
    VectorNamespace,
    VectorRecord,
)

class WorkflowIntentClassifier(IWorkflowIntentClassifier):
    """Implementation using LanceDB vector store.

    Now implements IWorkflowIntentClassifier interface for Clean Architecture compliance.
    """

    def __init__(
        self,
        config: Optional[RouterConfig] = None,
        vector_store: Optional[IVectorStore] = None,  # NEW: inject via interface
        model_name: str = MODEL_NAME,
    ):
        self._config = config or RouterConfig()
        self._vector_store = vector_store
        self._model_name = model_name
        self._model: Optional[Any] = None
        self._is_loaded = False

    def find_similar(
        self,
        prompt: str,
        top_k: int = 3,
        threshold: float = 0.0,
    ) -> List[Tuple[str, float]]:
        """Find similar workflows using vector search."""
        if not self._is_loaded or self._model is None:
            return []

        store = self._ensure_vector_store()
        query_vector = self._model.encode(prompt, normalize_embeddings=True)

        # Use config threshold if none provided
        if threshold == 0.0:
            threshold = self._config.workflow_similarity_threshold  # CORRECT field name

        results = store.search(
            query_vector=query_vector.tolist(),
            namespace=VectorNamespace.WORKFLOWS,
            top_k=top_k,
            threshold=threshold,
        )

        return [(r.id, r.score) for r in results]
```

**Implementation Checklist:**

| Layer | File | What to Change |
|-------|------|----------------|
| Classifier | `server/router/application/classifier/intent_classifier.py` | Replace pickle with LanceDB, use `embedding_threshold` |
| Classifier | `server/router/application/classifier/workflow_intent_classifier.py` | Replace pickle with LanceDB, implement `IWorkflowIntentClassifier`, use `workflow_similarity_threshold` |
| Domain | `server/router/domain/interfaces/__init__.py` | Export `IWorkflowIntentClassifier` |
| Config | `server/router/infrastructure/config.py` | Add `vector_store_path` setting (optional) |
| Tests | `tests/unit/router/application/classifier/test_intent_classifier_lance.py` | Integration tests |
| Tests | `tests/unit/router/application/classifier/test_workflow_intent_classifier_lance.py` | Integration tests |

---

### TASK-047-5: MCP Tool - vector_db_manage

**Status:** ✅ Done

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

- [x] Unit tests for IVectorStore interface contracts
- [x] Unit tests for LanceVectorStore (27+ tests)
  - [x] Test upsert operations
  - [x] Test search with different thresholds
  - [x] Test namespace filtering
  - [x] Test metadata filtering
  - [x] Test delete operations
  - [x] Test count operations
  - [x] Test index rebuild
  - [x] Test fallback when LanceDB unavailable
- [x] Unit tests for Pickle migration (12 tests)
  - [x] Test migration of tool embeddings
  - [x] Test migration of workflow embeddings
  - [x] Test handling of wrong dimension vectors
  - [x] Test cleanup of legacy files
  - [x] Test migration summary
- [x] Integration tests for classifiers with LanceDB (updated existing tests)
- [ ] E2E tests for vector_db_manage MCP tool (future enhancement)
- [ ] Performance tests comparing pickle vs LanceDB search times (future enhancement)

---

## New Files to Create

### Server Side

```
server/router/domain/interfaces/i_vector_store.py
server/router/domain/interfaces/i_workflow_intent_classifier.py
server/router/infrastructure/vector_store/__init__.py
server/router/infrastructure/vector_store/lance_store.py
server/router/infrastructure/vector_store/migrations.py
server/adapters/mcp/areas/vector_db.py
```

### Tests

```
tests/unit/router/domain/interfaces/test_i_vector_store.py
tests/unit/router/domain/interfaces/test_i_workflow_intent_classifier.py
tests/unit/router/infrastructure/vector_store/__init__.py
tests/unit/router/infrastructure/vector_store/test_lance_store.py
tests/unit/router/infrastructure/vector_store/test_migrations.py
tests/unit/router/application/classifier/test_intent_classifier_lance.py
tests/unit/router/application/classifier/test_workflow_intent_classifier_lance.py
tests/e2e/router/test_vector_db_tool.py
```

---

## Files to Modify

| File | What to Change |
|------|----------------|
| `server/router/application/classifier/intent_classifier.py` | Replace EmbeddingCache with LanceVectorStore, use `embedding_threshold` |
| `server/router/application/classifier/workflow_intent_classifier.py` | Replace WorkflowEmbeddingCache with LanceVectorStore, implement `IWorkflowIntentClassifier`, use `workflow_similarity_threshold` |
| `server/router/application/classifier/__init__.py` | Update exports |
| `server/router/domain/interfaces/__init__.py` | Export `IVectorStore`, `IWorkflowIntentClassifier`, `VectorNamespace`, `VectorRecord`, `SearchResult` |
| `server/router/infrastructure/config.py` | Add `vector_store_path: Optional[Path] = None` setting |
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
