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
    action: Literal["list", "get", "search", "import"],
    workflow_name: Optional[str] = None,
    query: Optional[str] = None,
    top_k: int = 5,
    threshold: float = 0.0,
    filepath: Optional[str] = None,
    overwrite: Optional[bool] = None,
) -> str:
    """
    [SYSTEM][SAFE] Browse, search, and import workflow definitions (no execution).

    Actions:
      - list: List available workflows with summary metadata
      - get: Get a workflow definition (including steps) by name
      - search: Find workflows similar to a query (semantic when available)
      - import: Import workflow from YAML/JSON file into the server

    Args:
      action: Operation to perform ("list" | "get" | "search" | "import")
      workflow_name: Workflow name for get action
      query: Search query for search action
      top_k: Number of results for search (default 5)
      threshold: Minimum similarity score (0.0 disables filtering)
      filepath: Workflow file path for import action
      overwrite: Overwrite existing workflow if name conflicts (import only)

    Examples:
      workflow_catalog(action="list")
      workflow_catalog(action="get", workflow_name="simple_table_workflow")
      workflow_catalog(action="search", query="low poly medieval well", top_k=5, threshold=0.0)
      workflow_catalog(action="import", filepath="/path/to/workflow.yaml")
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
            if not filepath:
                return json.dumps(
                    {"error": "filepath required for import action"},
                    indent=2,
                    ensure_ascii=False,
                )
            result = handler.import_workflow(filepath=filepath, overwrite=overwrite)
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

        return json.dumps({"error": f"Unknown action: {action}"}, indent=2, ensure_ascii=False)

    except Exception as e:
        logger.error(f"workflow_catalog error: {e}")
        return json.dumps({"error": str(e)}, indent=2, ensure_ascii=False)
