# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Reusable execution context model for adapter-side MCP calls."""

from __future__ import annotations

from typing import Any

from server.adapters.mcp.contracts.base import MCPContract


class MCPExecutionContext(MCPContract):
    """Normalized execution context for one adapter-level tool call."""

    tool_name: str
    params: dict[str, Any]
    prompt: str | None = None
    session_phase: str | None = None
    surface_profile: str | None = None
