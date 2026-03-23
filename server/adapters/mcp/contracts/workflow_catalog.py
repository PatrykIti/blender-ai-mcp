# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Structured contracts for workflow catalog MCP tools."""

from __future__ import annotations

from typing import Any

from server.adapters.mcp.contracts.base import MCPContract
from server.adapters.mcp.elicitation_contracts import ClarificationFallbackPayload
from server.adapters.mcp.sampling.result_types import RepairSuggestionAssistantContract


class WorkflowCatalogResponseContract(MCPContract):
    """Structured response contract for workflow_catalog."""

    action: str
    count: int | None = None
    total: int | None = None
    returned: int | None = None
    offset: int | None = None
    limit: int | None = None
    has_more: bool | None = None
    workflows_dir: str | None = None
    workflows: list[dict[str, Any]] | None = None
    workflow_name: str | None = None
    steps_count: int | None = None
    workflow: dict[str, Any] | None = None
    results: list[dict[str, Any]] | None = None
    query: str | None = None
    search_type: str | None = None
    status: str | None = None
    message: str | None = None
    source_type: str | None = None
    source_name: str | None = None
    content_type: str | None = None
    filepath: str | None = None
    source_path: str | None = None
    saved_path: str | None = None
    overwritten: bool | None = None
    removed_files: list[str] | None = None
    removed_embeddings: int | None = None
    embeddings_reloaded: bool | None = None
    conflicts: dict[str, Any] | None = None
    available: list[str] | None = None
    suggestions: list[str] | None = None
    session_id: str | None = None
    total_chunks: int | None = None
    received_chunks: int | None = None
    bytes_received: int | None = None
    missing_indices: list[int] | None = None
    clarification: ClarificationFallbackPayload | None = None
    repair_suggestion: RepairSuggestionAssistantContract | None = None
    error: str | None = None
