# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Structured contracts for workflow catalog MCP tools."""

from __future__ import annotations

from typing import Any

from server.adapters.mcp.contracts.base import MCPContract
from server.adapters.mcp.elicitation_contracts import ClarificationFallbackPayload


class WorkflowCatalogResponseContract(MCPContract):
    """Structured response contract for workflow_catalog."""

    action: str
    count: int | None = None
    workflows_dir: str | None = None
    workflows: list[dict[str, Any]] | None = None
    workflow_name: str | None = None
    workflow: dict[str, Any] | None = None
    results: list[dict[str, Any]] | None = None
    query: str | None = None
    search_type: str | None = None
    status: str | None = None
    message: str | None = None
    source_type: str | None = None
    content_type: str | None = None
    filepath: str | None = None
    available: list[str] | None = None
    suggestions: list[str] | None = None
    session_id: str | None = None
    clarification: ClarificationFallbackPayload | None = None
    error: str | None = None
