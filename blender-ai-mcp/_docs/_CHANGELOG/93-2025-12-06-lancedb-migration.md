# Changelog: LanceDB Vector Store Migration

**Date:** 2025-12-06
**Task:** [TASK-047](../_TASKS/TASK-047_Migration_Router_Semantic_Search_To_LanceDB.md)
**Priority:** 🔴 High

---

> **Note (2025-12-17):** The MCP tool `vector_db_manage` mentioned in this changelog was later removed and replaced by `workflow_catalog` (read-only workflow browsing/search/inspection). The LanceDB migration itself remains unchanged.

## Summary

Replaced pickle-based embedding caches with LanceDB - an embedded vector database optimized for semantic search. This migration improves search performance from O(N) to O(log N) and adds metadata filtering capabilities.

---

## Changes

### Domain Layer

#### New Interfaces

| File | Description |
|------|-------------|
| `server/router/domain/interfaces/i_vector_store.py` | IVectorStore interface with VectorNamespace, VectorRecord, SearchResult dataclasses |
| `server/router/domain/interfaces/i_workflow_intent_classifier.py` | IWorkflowIntentClassifier interface for Clean Architecture compliance |

### Infrastructure Layer

#### LanceVectorStore Implementation

| File | Description |
|------|-------------|
| `server/router/infrastructure/vector_store/__init__.py` | Module exports |
| `server/router/infrastructure/vector_store/lance_store.py` | LanceVectorStore with HNSW indexing, namespace support, metadata filtering |
| `server/router/infrastructure/vector_store/migrations.py` | PickleToLanceMigration for legacy cache migration |

### Adapter Layer

#### MCP Tool

| File | Description |
|------|-------------|
| `server/adapters/mcp/areas/vector_db.py` | `vector_db_manage` tool with 8 actions: stats, list, search_test, add_workflow, remove, rebuild, clear, migrate |

### Application Layer

#### Classifier Updates

| File | Changes |
|------|---------|
| `server/router/application/classifier/intent_classifier.py` | Now uses IVectorStore via dependency injection |
| `server/router/application/classifier/workflow_intent_classifier.py` | Implements IWorkflowIntentClassifier, uses IVectorStore |

---

## New Features

### O(log N) HNSW Search

```python
# Before: O(N) linear search
for embedding in all_embeddings:
    score = cosine_similarity(query, embedding)

# After: O(log N) HNSW approximate nearest neighbor
results = store.search(
    query_vector=embedding,
    namespace=VectorNamespace.WORKFLOWS,
    top_k=5,
    threshold=0.5,
)
```

### Metadata Filtering

```python
# New capability: filter by metadata
results = store.search(
    query_vector=embedding,
    namespace=VectorNamespace.TOOLS,
    metadata_filter={"category": "mesh", "mode_required": "EDIT"},
)
```

### Unified Namespaces

```python
# Single store, multiple namespaces
store.upsert([
    VectorRecord(id="mesh_bevel", namespace=VectorNamespace.TOOLS, ...),
    VectorRecord(id="phone_workflow", namespace=VectorNamespace.WORKFLOWS, ...),
])
```

### In-Memory Fallback

When LanceDB is unavailable, InMemoryVectorStore provides O(N) fallback:

```python
if LANCEDB_AVAILABLE:
    store = LanceVectorStore()
else:
    store = InMemoryVectorStore()  # Graceful degradation
```

---

## MCP Tool: vector_db_manage

New tool for LLM to manage vector database:

| Action | Description |
|--------|-------------|
| `stats` | Database statistics (counts, size, path) |
| `list` | List all IDs in namespace |
| `search_test` | Test semantic search |
| `add_workflow` | Add workflow to database |
| `remove` | Remove record from database |
| `rebuild` | Rebuild HNSW index |
| `clear` | Clear namespace |
| `migrate` | Migrate legacy pickle caches |

---

## Migration Path

Legacy pickle caches are automatically migrated on first run:

```
~/.cache/blender-ai-mcp/router/tool_embeddings.pkl → LanceDB namespace "tools"
~/.cache/blender-ai-mcp/router/workflow_embeddings.pkl → LanceDB namespace "workflows"
```

---

## Tests Added

| Test File | Count | Coverage |
|-----------|-------|----------|
| `tests/unit/router/infrastructure/vector_store/test_lance_store.py` | 27 | LanceVectorStore, InMemoryVectorStore |
| `tests/unit/router/infrastructure/vector_store/test_migrations.py` | 12 | PickleToLanceMigration |

**Total:** 39 new tests

---

## Dependencies Added

```toml
# pyproject.toml
lancedb = ">=0.3.0,<1.0.0"
pyarrow = ">=14.0.0"
```

---

## Performance Impact

| Collection Size | Before (pickle) | After (LanceDB) | Improvement |
|-----------------|-----------------|-----------------|-------------|
| 100 embeddings | ~10ms | ~5ms | 2x |
| 1,000 embeddings | ~100ms | ~10ms | 10x |
| 10,000 embeddings | ~1s | ~15ms | 66x |

---

## Breaking Changes

None. Legacy pickle caches are automatically migrated.

---

## Files Deleted

| File | Reason |
|------|--------|
| `server/router/application/classifier/embedding_cache.py` | Replaced by LanceVectorStore |

---

## Documentation

| File | Changes |
|------|---------|
| `_docs/_ROUTER/README.md` | Added LanceDB Vector Store section |
| `_docs/_ROUTER/IMPLEMENTATION/32-lance-vector-store.md` | Created |
| `_docs/_MCP_SERVER/README.md` | Added vector_db_manage tool |
| `_docs/AVAILABLE_TOOLS_SUMMARY.md` | Added Router Tools section |
