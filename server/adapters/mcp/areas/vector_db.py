"""
Vector Database MCP Tools.

Provides LLM access to manage the vector database for semantic workflow search.
LanceDB-based vector storage with HNSW indexing for O(log N) search.

TASK-047-5: Implementation of vector_db_manage MCP tool.
TASK-050-7: Updated for multi-embedding workflow support.
"""

import json
import logging
from typing import Dict, Any, Optional, Literal, List

from fastmcp import Context

from server.adapters.mcp.instance import mcp
from server.router.domain.interfaces.i_vector_store import (
    VectorNamespace,
    VectorRecord,
)

logger = logging.getLogger(__name__)

# Lazy-loaded shared store instance
_store = None


def _get_store():
    """Get or create the vector store instance."""
    global _store
    if _store is None:
        from server.router.infrastructure.vector_store.lance_store import (
            LanceVectorStore,
        )

        _store = LanceVectorStore()
    return _store


def _get_embedding_model():
    """Get the sentence transformer model for embeddings."""
    try:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer("sentence-transformers/LaBSE")
    except ImportError:
        return None


@mcp.tool()
def vector_db_manage(
    ctx: Context,
    action: Literal[
        "stats",
        "list",
        "search_test",
        "add_workflow",
        "remove",
        "rebuild",
        "clear",
        "migrate",
    ],
    namespace: Optional[Literal["tools", "workflows"]] = None,
    query: Optional[str] = None,
    workflow_name: Optional[str] = None,
    workflow_data: Optional[Dict[str, Any]] = None,
    top_k: int = 5,
    threshold: float = 0.0,
) -> str:
    """
    [SYSTEM][SAFE] Manage vector database for semantic workflow search.

    LLM uses this tool to:
    - View database statistics and contents
    - Add new workflows discovered from project analysis
    - Search for similar existing workflows
    - Manage embeddings and indexes

    Actions:
        - stats: Database statistics (counts, size, path)
        - list: List all workflow/tool IDs in namespace
        - search_test: Test semantic search with query
        - add_workflow: Add workflow embeddings to DB
        - remove: Remove workflow/tool from DB
        - rebuild: Rebuild HNSW search index
        - clear: Clear all records in namespace
        - migrate: Migrate legacy pickle caches to LanceDB

    Args:
        action: Operation to perform
        namespace: Target namespace ("tools" or "workflows")
        query: Search query for search_test action
        workflow_name: Workflow name for add_workflow/remove
        workflow_data: Dict with description, sample_prompts, trigger_keywords
        top_k: Number of results for search_test (default 5)
        threshold: Minimum similarity score for search_test (default 0.0)

    Examples:
        vector_db_manage(action="stats")
        vector_db_manage(action="list", namespace="workflows")
        vector_db_manage(action="search_test", namespace="workflows", query="furniture table")
        vector_db_manage(action="add_workflow", workflow_name="chair_v2",
                         workflow_data={"description": "...", "sample_prompts": [...]})
        vector_db_manage(action="remove", namespace="workflows", workflow_name="old_workflow")
        vector_db_manage(action="rebuild")
        vector_db_manage(action="clear", namespace="workflows")
        vector_db_manage(action="migrate")
    """
    store = _get_store()

    try:
        if action == "stats":
            return _action_stats(store)

        elif action == "list":
            return _action_list(store, namespace)

        elif action == "search_test":
            return _action_search_test(store, namespace, query, top_k, threshold)

        elif action == "add_workflow":
            return _action_add_workflow(store, workflow_name, workflow_data)

        elif action == "remove":
            return _action_remove(store, namespace, workflow_name)

        elif action == "rebuild":
            return _action_rebuild(store)

        elif action == "clear":
            return _action_clear(store, namespace)

        elif action == "migrate":
            return _action_migrate(store)

        else:
            return json.dumps({"error": f"Unknown action: {action}"}, indent=2)

    except Exception as e:
        logger.error(f"vector_db_manage error: {e}")
        return json.dumps({"error": str(e)}, indent=2)


def _action_stats(store) -> str:
    """Get database statistics with multi-embedding info."""
    stats = store.get_stats()

    # Add multi-embedding specific stats (TASK-050-7)
    unique_workflows = store.get_unique_workflow_count()
    total_embeddings = store.get_workflow_embedding_count()

    stats["multi_embedding"] = {
        "unique_workflows": unique_workflows,
        "total_workflow_embeddings": total_embeddings,
        "avg_embeddings_per_workflow": (
            round(total_embeddings / unique_workflows, 1)
            if unique_workflows > 0
            else 0
        ),
    }

    return json.dumps(stats, indent=2)


def _action_list(store, namespace: Optional[str]) -> str:
    """List all IDs in namespace."""
    if not namespace:
        return json.dumps(
            {"error": "namespace required for list action (tools or workflows)"},
            indent=2,
        )

    ns = VectorNamespace(namespace)
    ids = store.get_all_ids(ns)

    return json.dumps(
        {
            "namespace": namespace,
            "ids": ids,
            "count": len(ids),
        },
        indent=2,
    )


def _action_search_test(
    store,
    namespace: Optional[str],
    query: Optional[str],
    top_k: int,
    threshold: float,
) -> str:
    """Test semantic search with a query.

    TASK-050-7: Uses weighted search for workflows namespace.
    """
    if not query:
        return json.dumps({"error": "query required for search_test"}, indent=2)

    if not namespace:
        return json.dumps(
            {"error": "namespace required for search_test (tools or workflows)"},
            indent=2,
        )

    # Get embedding model
    model = _get_embedding_model()
    if model is None:
        return json.dumps(
            {
                "error": "sentence-transformers not installed. "
                "Cannot perform semantic search."
            },
            indent=2,
        )

    try:
        # Encode query
        query_vector = model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        # Use weighted search for workflows (TASK-050-7)
        if namespace == "workflows":
            from server.router.infrastructure.language_detector import detect_language

            query_language = detect_language(query)

            weighted_results = store.search_workflows_weighted(
                query_vector=query_vector.tolist(),
                query_language=query_language,
                top_k=top_k,
                min_score=threshold,
            )

            # Format weighted results
            formatted = []
            for r in weighted_results:
                formatted.append(
                    {
                        "workflow_id": r.workflow_id,
                        "final_score": round(r.final_score, 4),
                        "raw_score": round(r.raw_score, 4),
                        "source_type": r.source_type,
                        "source_weight": r.source_weight,
                        "language_boost": r.language_boost,
                        "matched_text": (
                            r.matched_text[:80] + "..."
                            if len(r.matched_text) > 80
                            else r.matched_text
                        ),
                    }
                )

            return json.dumps(
                {
                    "query": query,
                    "namespace": namespace,
                    "query_language": query_language,
                    "search_type": "weighted_multi_embedding",
                    "results": formatted,
                    "count": len(formatted),
                },
                indent=2,
            )

        # Regular search for tools
        ns = VectorNamespace(namespace)
        results = store.search(
            query_vector=query_vector.tolist(),
            namespace=ns,
            top_k=top_k,
            threshold=threshold,
        )

        # Format results
        formatted = []
        for r in results:
            formatted.append(
                {
                    "id": r.id,
                    "score": round(r.score, 4),
                    "text": r.text[:100] + "..." if len(r.text) > 100 else r.text,
                }
            )

        return json.dumps(
            {
                "query": query,
                "namespace": namespace,
                "search_type": "standard",
                "results": formatted,
                "count": len(formatted),
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps({"error": f"Search failed: {e}"}, indent=2)


def _action_add_workflow(
    store,
    workflow_name: Optional[str],
    workflow_data: Optional[Dict[str, Any]],
) -> str:
    """Add a workflow to the database with multi-embedding.

    TASK-050-7: Creates separate embeddings for each text source.
    """
    if not workflow_name:
        return json.dumps({"error": "workflow_name required"}, indent=2)

    if not workflow_data:
        return json.dumps(
            {
                "error": "workflow_data required. Provide dict with: "
                "description, sample_prompts, trigger_keywords"
            },
            indent=2,
        )

    # Get embedding model
    model = _get_embedding_model()
    if model is None:
        return json.dumps(
            {
                "error": "sentence-transformers not installed. "
                "Cannot generate embeddings."
            },
            indent=2,
        )

    try:
        from server.router.infrastructure.language_detector import detect_language
        from server.router.application.classifier.workflow_intent_classifier import (
            SOURCE_WEIGHTS,
        )

        records = []
        texts_with_meta = []

        # Sample prompts (weight 1.0)
        for idx, prompt in enumerate(workflow_data.get("sample_prompts", [])):
            texts_with_meta.append((prompt, "sample_prompt", SOURCE_WEIGHTS["sample_prompt"], idx))

        # Trigger keywords (weight 0.8)
        for idx, keyword in enumerate(workflow_data.get("trigger_keywords", [])):
            texts_with_meta.append((keyword, "trigger_keyword", SOURCE_WEIGHTS["trigger_keyword"], idx))

        # Workflow name (weight 0.5)
        name_text = workflow_name.replace("_", " ")
        texts_with_meta.append((name_text, "name", SOURCE_WEIGHTS["name"], 0))

        # Description (weight 0.6)
        if "description" in workflow_data:
            texts_with_meta.append(
                (workflow_data["description"], "description", SOURCE_WEIGHTS["description"], 0)
            )

        if not texts_with_meta:
            return json.dumps(
                {"error": "No text content found in workflow_data"}, indent=2
            )

        # Create separate embedding for each text (multi-embedding)
        category = workflow_data.get("category")

        for text, source_type, weight, idx in texts_with_meta:
            language = detect_language(text)
            vector = model.encode(
                text,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )

            record_id = f"{workflow_name}__{source_type}__{idx}"

            record = VectorRecord(
                id=record_id,
                namespace=VectorNamespace.WORKFLOWS,
                vector=vector.tolist(),
                text=text,
                metadata={
                    "workflow_id": workflow_name,
                    "source_type": source_type,
                    "source_weight": weight,
                    "language": language,
                    "category": category,
                },
            )
            records.append(record)

        # Upsert all records
        count = store.upsert(records)

        return json.dumps(
            {
                "success": True,
                "workflow_name": workflow_name,
                "multi_embedding": True,
                "embeddings_created": len(records),
                "records_upserted": count,
                "source_breakdown": {
                    "sample_prompts": len(workflow_data.get("sample_prompts", [])),
                    "trigger_keywords": len(workflow_data.get("trigger_keywords", [])),
                    "name": 1,
                    "description": 1 if "description" in workflow_data else 0,
                },
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps({"error": f"Failed to add workflow: {e}"}, indent=2)


def _action_remove(
    store,
    namespace: Optional[str],
    workflow_name: Optional[str],
) -> str:
    """Remove a record from the database.

    TASK-050-7: For workflows, removes all multi-embedding records.
    """
    if not workflow_name:
        return json.dumps({"error": "workflow_name required for remove"}, indent=2)

    if not namespace:
        return json.dumps(
            {"error": "namespace required for remove (tools or workflows)"}, indent=2
        )

    ns = VectorNamespace(namespace)

    # For workflows, find and delete all multi-embedding records
    if namespace == "workflows":
        all_ids = store.get_all_ids(ns)
        ids_to_delete = [
            id_ for id_ in all_ids
            if id_ == workflow_name or id_.startswith(f"{workflow_name}__")
        ]

        if ids_to_delete:
            count = store.delete(ids_to_delete, ns)
        else:
            count = 0

        return json.dumps(
            {
                "success": count > 0,
                "deleted_count": count,
                "workflow_name": workflow_name,
                "namespace": namespace,
                "multi_embedding_records_deleted": len(ids_to_delete),
            },
            indent=2,
        )

    # For tools, simple delete
    count = store.delete([workflow_name], ns)

    return json.dumps(
        {
            "success": count > 0,
            "deleted_count": count,
            "id": workflow_name,
            "namespace": namespace,
        },
        indent=2,
    )


def _action_rebuild(store) -> str:
    """Rebuild the HNSW search index."""
    success = store.rebuild_index()

    return json.dumps(
        {
            "success": success,
            "message": "HNSW index rebuilt" if success else "Index rebuild failed",
        },
        indent=2,
    )


def _action_clear(store, namespace: Optional[str]) -> str:
    """Clear all records in namespace."""
    if not namespace:
        return json.dumps(
            {
                "error": "namespace required for clear (tools or workflows). "
                "This is a safety measure to prevent accidental data loss."
            },
            indent=2,
        )

    ns = VectorNamespace(namespace)
    before = store.count(ns)
    deleted = store.clear(ns)

    return json.dumps(
        {
            "success": True,
            "namespace": namespace,
            "deleted_count": deleted,
            "previous_count": before,
        },
        indent=2,
    )


def _action_migrate(store) -> str:
    """Migrate legacy pickle caches to LanceDB."""
    from server.router.infrastructure.vector_store.migrations import (
        PickleToLanceMigration,
    )

    migration = PickleToLanceMigration(store)

    if not migration.needs_migration():
        return json.dumps(
            {
                "success": True,
                "message": "No legacy pickle caches found. Nothing to migrate.",
                "summary": migration.get_migration_summary(),
            },
            indent=2,
        )

    # Perform migration
    results = migration.migrate_all(cleanup=False)

    return json.dumps(
        {
            "success": True,
            "migrated": results,
            "message": "Migration complete. Use clear action to clean up legacy files.",
            "summary": migration.get_migration_summary(),
        },
        indent=2,
    )
