"""
Vector Database MCP Tools.

Provides LLM access to manage the vector database for semantic workflow search.
LanceDB-based vector storage with HNSW indexing for O(log N) search.

TASK-047-5: Implementation of vector_db_manage MCP tool.
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
    """Get database statistics."""
    stats = store.get_stats()
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
    """Test semantic search with a query."""
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

        # Search
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
    """Add a workflow to the database."""
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
        # Build text from workflow data
        texts = []

        # Add description
        if "description" in workflow_data:
            texts.append(workflow_data["description"])

        # Add sample prompts
        if "sample_prompts" in workflow_data:
            texts.extend(workflow_data["sample_prompts"])

        # Add trigger keywords
        if "trigger_keywords" in workflow_data:
            texts.extend(workflow_data["trigger_keywords"])

        # Add workflow name (spaces instead of underscores)
        texts.append(workflow_name.replace("_", " "))

        if not texts:
            return json.dumps(
                {"error": "No text content found in workflow_data"}, indent=2
            )

        # Combine and encode
        combined_text = " ".join(texts)
        vector = model.encode(
            combined_text,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        # Create record
        record = VectorRecord(
            id=workflow_name,
            namespace=VectorNamespace.WORKFLOWS,
            vector=vector.tolist(),
            text=combined_text,
            metadata={
                "category": workflow_data.get("category"),
                "trigger_keywords": workflow_data.get("trigger_keywords", []),
            },
        )

        # Upsert
        count = store.upsert([record])

        return json.dumps(
            {
                "success": True,
                "workflow_name": workflow_name,
                "text_length": len(combined_text),
                "records_added": count,
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
    """Remove a record from the database."""
    if not workflow_name:
        return json.dumps({"error": "workflow_name required for remove"}, indent=2)

    if not namespace:
        return json.dumps(
            {"error": "namespace required for remove (tools or workflows)"}, indent=2
        )

    ns = VectorNamespace(namespace)
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
