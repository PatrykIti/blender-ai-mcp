# 32. LanceDB Vector Store

> **TASK-047** | Status: ✅ Done | Priority: 🔴 High

---

## Overview

Replaces pickle-based embedding caches with LanceDB - an embedded vector database optimized for semantic search.

**Before:**
- O(N) linear search on all embeddings
- Separate pickle caches for tools and workflows
- No metadata filtering
- Pickle format security concerns

**After:**
- O(log N) HNSW ANN search
- Unified vector store with namespaces
- Metadata filtering support
- Persistent, folder-based storage

---

## Architecture

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

**Storage path:** `~/.cache/blender-ai-mcp/vector_store/`

---

## Domain Interface

### IVectorStore

```python
# server/router/domain/interfaces/i_vector_store.py

class VectorNamespace(Enum):
    TOOLS = "tools"
    WORKFLOWS = "workflows"

@dataclass
class VectorRecord:
    id: str                          # tool_name or workflow_name
    namespace: VectorNamespace
    vector: List[float]              # 768D for LaBSE
    text: str                        # Original text
    metadata: Dict[str, Any]         # category, mode_required, etc.

@dataclass
class SearchResult:
    id: str
    score: float
    text: str
    metadata: Dict[str, Any]

class IVectorStore(ABC):
    @abstractmethod
    def upsert(self, records: List[VectorRecord]) -> int: ...

    @abstractmethod
    def search(
        self,
        query_vector: List[float],
        namespace: VectorNamespace,
        top_k: int = 5,
        threshold: float = 0.0,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]: ...

    @abstractmethod
    def delete(self, ids: List[str], namespace: VectorNamespace) -> int: ...

    @abstractmethod
    def count(self, namespace: Optional[VectorNamespace] = None) -> int: ...

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]: ...

    @abstractmethod
    def rebuild_index(self) -> bool: ...
```

---

## Implementation

### LanceVectorStore

```python
# server/router/infrastructure/vector_store/lance_store.py

class LanceVectorStore(IVectorStore):
    TABLE_NAME = "embeddings"
    VECTOR_DIM = 768  # LaBSE dimension

    def __init__(self, db_path: Optional[Path] = None):
        self._db_path = db_path or DEFAULT_DB_PATH
        self._db_path.mkdir(parents=True, exist_ok=True)
        self._db = lancedb.connect(str(self._db_path))
        self._ensure_table()

    def search(
        self,
        query_vector: List[float],
        namespace: VectorNamespace,
        top_k: int = 5,
        threshold: float = 0.0,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        # Build WHERE clause
        where = f"namespace = '{namespace.value}'"
        if metadata_filter:
            for key, value in metadata_filter.items():
                where += f" AND json_extract(metadata, '$.{key}') = '{value}'"

        # Execute HNSW search
        results = (
            self._table
            .search(query_vector)
            .where(where)
            .limit(top_k)
            .to_list()
        )

        # Convert distance to similarity score
        return [
            SearchResult(
                id=r["id"],
                score=1.0 - r.get("_distance", 0),
                text=r["text"],
                metadata=json.loads(r["metadata"]) if r["metadata"] else {},
            )
            for r in results
            if 1.0 - r.get("_distance", 0) >= threshold
        ]
```

### In-Memory Fallback

When LanceDB is unavailable, the store uses in-memory storage:

```python
class InMemoryVectorStore(IVectorStore):
    """Fallback when LanceDB not installed."""

    def __init__(self):
        self._records: Dict[str, VectorRecord] = {}

    def search(self, query_vector, namespace, top_k=5, threshold=0.0, **kwargs):
        # O(N) linear search with cosine similarity
        results = []
        for record in self._records.values():
            if record.namespace == namespace:
                score = self._cosine_similarity(query_vector, record.vector)
                if score >= threshold:
                    results.append(SearchResult(
                        id=record.id,
                        score=score,
                        text=record.text,
                        metadata=record.metadata,
                    ))
        return sorted(results, key=lambda x: x.score, reverse=True)[:top_k]
```

---

## Migration

### PickleToLanceMigration

Migrates legacy pickle caches on first run:

```python
# server/router/infrastructure/vector_store/migrations.py

LEGACY_CACHE_DIR = Path.home() / ".cache" / "blender-ai-mcp" / "router"
LEGACY_TOOL_CACHE = LEGACY_CACHE_DIR / "tool_embeddings.pkl"
LEGACY_WORKFLOW_CACHE = LEGACY_CACHE_DIR / "workflow_embeddings.pkl"

class PickleToLanceMigration:
    def migrate_all(self) -> Dict[str, int]:
        results = {}

        if LEGACY_TOOL_CACHE.exists():
            count = self._migrate_pickle(LEGACY_TOOL_CACHE, VectorNamespace.TOOLS)
            results["tools"] = count

        if LEGACY_WORKFLOW_CACHE.exists():
            count = self._migrate_pickle(LEGACY_WORKFLOW_CACHE, VectorNamespace.WORKFLOWS)
            results["workflows"] = count

        return results

    def _migrate_pickle(self, pickle_path: Path, namespace: VectorNamespace) -> int:
        with open(pickle_path, "rb") as f:
            data = pickle.load(f)

        records = []
        for key, value in data.items():
            if isinstance(value, np.ndarray) and len(value) == 768:
                records.append(VectorRecord(
                    id=key,
                    namespace=namespace,
                    vector=value.tolist(),
                    text=key.replace("_", " "),
                    metadata={},
                ))

        return self._store.upsert(records)
```

---

## MCP Tool

### vector_db_manage

```python
# server/adapters/mcp/areas/vector_db.py

@mcp.tool()
def vector_db_manage(
    ctx: Context,
    action: Literal["stats", "list", "search_test", "add_workflow", "remove", "rebuild", "clear", "migrate"],
    namespace: Optional[Literal["tools", "workflows"]] = None,
    query: Optional[str] = None,
    workflow_name: Optional[str] = None,
    workflow_data: Optional[Dict[str, Any]] = None,
    top_k: int = 5,
) -> str:
    """
    [SYSTEM][SAFE] Manage vector database for semantic workflow search.

    Actions:
        - stats: Database statistics (counts, size, path)
        - list: List all workflow/tool IDs in namespace
        - search_test: Test semantic search with query
        - add_workflow: Add workflow embeddings to DB
        - remove: Remove workflow/tool from DB
        - rebuild: Rebuild HNSW search index
        - clear: Clear all records in namespace
        - migrate: Migrate legacy pickle caches
    """
```

---

## Testing

### Unit Tests (39 tests)

```bash
PYTHONPATH=. poetry run pytest tests/unit/router/infrastructure/vector_store/ -v
```

Tests cover:
- IVectorStore interface contracts
- LanceVectorStore CRUD operations
- Namespace filtering
- Metadata filtering
- Threshold filtering
- In-memory fallback
- Pickle migration

### Migration Tests (12 tests)

```bash
PYTHONPATH=. poetry run pytest tests/unit/router/infrastructure/vector_store/test_migrations.py -v
```

---

## Performance

| Collection Size | Pickle (O(N)) | LanceDB (O(log N)) |
|-----------------|---------------|---------------------|
| 100 embeddings | ~10ms | ~5ms |
| 1,000 embeddings | ~100ms | ~10ms |
| 10,000 embeddings | ~1s | ~15ms |

---

## Files Created/Modified

### New Files

| File | Purpose |
|------|---------|
| `server/router/domain/interfaces/i_vector_store.py` | IVectorStore interface |
| `server/router/domain/interfaces/i_workflow_intent_classifier.py` | IWorkflowIntentClassifier interface |
| `server/router/infrastructure/vector_store/__init__.py` | Module exports |
| `server/router/infrastructure/vector_store/lance_store.py` | LanceVectorStore implementation |
| `server/router/infrastructure/vector_store/migrations.py` | Pickle migration |
| `server/adapters/mcp/areas/vector_db.py` | MCP tool |
| `tests/unit/router/infrastructure/vector_store/test_lance_store.py` | Unit tests |
| `tests/unit/router/infrastructure/vector_store/test_migrations.py` | Migration tests |

### Modified Files

| File | Changes |
|------|---------|
| `server/router/application/classifier/intent_classifier.py` | Use IVectorStore |
| `server/router/application/classifier/workflow_intent_classifier.py` | Use IVectorStore, implement IWorkflowIntentClassifier |
| `server/router/domain/interfaces/__init__.py` | Export new interfaces |
| `pyproject.toml` | Add lancedb, pyarrow dependencies |

---

## Dependencies

```toml
# pyproject.toml
[project]
dependencies = [
    "lancedb>=0.3.0,<1.0.0",
    "pyarrow>=14.0.0",
]
```

---

## See Also

- [TASK-047](../../_TASKS/TASK-047_Migration_Router_Semantic_Search_To_LanceDB.md) - Full task specification
- [28-workflow-intent-classifier.md](./28-workflow-intent-classifier.md) - Classifier using vector store
- [14-intent-classifier.md](./14-intent-classifier.md) - Original intent classifier
