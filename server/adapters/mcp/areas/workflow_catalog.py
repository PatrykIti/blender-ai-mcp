"""
Workflow Catalog MCP Tools.

Utilities for exploring and importing YAML/JSON workflows without executing them.
"""

import json
import logging
from typing import Any, Dict, Literal, Optional

from fastmcp import Context

from server.adapters.mcp.context_utils import ctx_info
from server.adapters.mcp.instance import mcp
from server.infrastructure.di import get_workflow_catalog_handler

logger = logging.getLogger(__name__)


@mcp.tool()
def workflow_catalog(
    ctx: Context,
    action: Literal[
        "list",
        "get",
        "search",
        "import",
        "import_init",
        "import_append",
        "import_finalize",
        "import_abort",
    ],
    workflow_name: Optional[str] = None,
    query: Optional[str] = None,
    top_k: int = 5,
    threshold: float = 0.0,
    filepath: Optional[str] = None,
    overwrite: Optional[bool] = None,
    content: Optional[str] = None,
    content_type: Optional[str] = None,
    source_name: Optional[str] = None,
    session_id: Optional[str] = None,
    chunk_data: Optional[str] = None,
    chunk_index: Optional[int] = None,
    total_chunks: Optional[int] = None,
) -> str:
    """
    [SYSTEM][SAFE] Browse, search, and import workflow definitions (no execution).

    Actions:
      - list: List available workflows with summary metadata
      - get: Get a workflow definition (including steps) by name
      - search: Find workflows similar to a query (semantic when available)
      - import: Import workflow from YAML/JSON file or inline content into the server
      - import_init: Start chunked workflow import session
      - import_append: Append chunk to session
      - import_finalize: Finalize chunked import session
      - import_abort: Abort chunked import session

    Args:
      action: Operation to perform ("list" | "get" | "search" | "import" | "import_init" | "import_append" | "import_finalize" | "import_abort")
      workflow_name: Workflow name for get action
      query: Search query for search action
      top_k: Number of results for search (default 5)
      threshold: Minimum similarity score (0.0 disables filtering)
      filepath: Workflow file path for import action
      overwrite: Overwrite existing workflow if name conflicts (import only)
      content: Inline YAML/JSON workflow definition
      content_type: Optional "yaml" or "json" hint for inline or chunked import
      source_name: Optional label for inline/chunked content
      session_id: Chunked import session ID
      chunk_data: Chunk payload for import_append
      chunk_index: Optional chunk index (0-based) for import_append
      total_chunks: Optional expected chunk count

    Examples:
      workflow_catalog(action="list")
      workflow_catalog(action="get", workflow_name="simple_table_workflow")
      workflow_catalog(action="search", query="low poly medieval well", top_k=5, threshold=0.0)
      workflow_catalog(action="import", filepath="/path/to/workflow.yaml")
      workflow_catalog(action="import", content="<yaml or json>", content_type="yaml")
      workflow_catalog(action="import_init", content_type="yaml", source_name="chair.yaml")
      workflow_catalog(action="import_append", session_id="...", chunk_data="...", chunk_index=0)
      workflow_catalog(action="import_finalize", session_id="...", overwrite=true)
    """
    handler = get_workflow_catalog_handler()

    try:
        if action == "list":
            result: Dict[str, Any] = handler.list_workflows()
            ctx_info(ctx, f"[WORKFLOW_CATALOG] Listed {result.get('count', 0)} workflows")
            return json.dumps(result, indent=2, ensure_ascii=False)

        if action == "get":
            if not workflow_name:
                return json.dumps(
                    {"error": "workflow_name required for get action"},
                    indent=2,
                    ensure_ascii=False,
                )
            result = handler.get_workflow(workflow_name)
            if "error" in result:
                ctx_info(ctx, f"[WORKFLOW_CATALOG] Get failed: {workflow_name}")
            else:
                ctx_info(ctx, f"[WORKFLOW_CATALOG] Fetched: {workflow_name}")
            return json.dumps(result, indent=2, ensure_ascii=False)

        if action == "search":
            if not query:
                return json.dumps(
                    {"error": "query required for search action"},
                    indent=2,
                    ensure_ascii=False,
                )
            result = handler.search_workflows(query=query, top_k=top_k, threshold=threshold)
            ctx_info(ctx, f"[WORKFLOW_CATALOG] Search '{query[:40]}...' -> {result.get('count', 0)} results")
            return json.dumps(result, indent=2, ensure_ascii=False)

        if action == "import":
            if filepath:
                result = handler.import_workflow(filepath=filepath, overwrite=overwrite)
            elif content:
                result = handler.import_workflow_content(
                    content=content,
                    content_type=content_type,
                    overwrite=overwrite,
                    source_name=source_name,
                )
            else:
                return json.dumps(
                    {"error": "filepath or content required for import action"},
                    indent=2,
                    ensure_ascii=False,
                )
            status = result.get("status", "unknown")
            if status == "imported":
                ctx_info(ctx, f"[WORKFLOW_CATALOG] Imported: {result.get('workflow_name')}")
            elif status == "needs_input":
                ctx_info(ctx, f"[WORKFLOW_CATALOG] Import needs input: {result.get('workflow_name')}")
            elif status == "skipped":
                ctx_info(ctx, f"[WORKFLOW_CATALOG] Import skipped: {result.get('workflow_name')}")
            else:
                ctx_info(ctx, f"[WORKFLOW_CATALOG] Import status: {status}")
            return json.dumps(result, indent=2, ensure_ascii=False)

        if action == "import_init":
            result = handler.begin_import_session(
                content_type=content_type,
                source_name=source_name,
                total_chunks=total_chunks,
            )
            ctx_info(ctx, f"[WORKFLOW_CATALOG] Import session: {result.get('session_id')}")
            return json.dumps(result, indent=2, ensure_ascii=False)

        if action == "import_append":
            if not session_id:
                return json.dumps(
                    {"error": "session_id required for import_append"},
                    indent=2,
                    ensure_ascii=False,
                )
            if chunk_data is None:
                return json.dumps(
                    {"error": "chunk_data required for import_append"},
                    indent=2,
                    ensure_ascii=False,
                )
            result = handler.append_import_chunk(
                session_id=session_id,
                chunk_data=chunk_data,
                chunk_index=chunk_index,
                total_chunks=total_chunks,
            )
            return json.dumps(result, indent=2, ensure_ascii=False)

        if action == "import_finalize":
            if not session_id:
                return json.dumps(
                    {"error": "session_id required for import_finalize"},
                    indent=2,
                    ensure_ascii=False,
                )
            result = handler.finalize_import_session(session_id=session_id, overwrite=overwrite)
            status = result.get("status", "unknown")
            if status == "imported":
                ctx_info(ctx, f"[WORKFLOW_CATALOG] Imported: {result.get('workflow_name')}")
            elif status == "needs_input":
                ctx_info(ctx, f"[WORKFLOW_CATALOG] Import needs input: {result.get('workflow_name')}")
            elif status == "skipped":
                ctx_info(ctx, f"[WORKFLOW_CATALOG] Import skipped: {result.get('workflow_name')}")
            else:
                ctx_info(ctx, f"[WORKFLOW_CATALOG] Import status: {status}")
            return json.dumps(result, indent=2, ensure_ascii=False)

        if action == "import_abort":
            if not session_id:
                return json.dumps(
                    {"error": "session_id required for import_abort"},
                    indent=2,
                    ensure_ascii=False,
                )
            result = handler.abort_import_session(session_id=session_id)
            return json.dumps(result, indent=2, ensure_ascii=False)

        return json.dumps({"error": f"Unknown action: {action}"}, indent=2, ensure_ascii=False)

    except Exception as e:
        logger.error(f"workflow_catalog error: {e}")
        return json.dumps({"error": str(e)}, indent=2, ensure_ascii=False)
