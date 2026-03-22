# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Reusable execution report objects for MCP adapter flows."""

from __future__ import annotations

from typing import Any

from server.adapters.mcp.contracts.base import MCPContract
from server.adapters.mcp.execution_context import MCPExecutionContext


class ExecutionStep(MCPContract):
    """One executed tool step in a router-aware call path."""

    tool_name: str
    params: dict[str, Any]
    result: Any
    error: str | None = None


class MCPExecutionReport(MCPContract):
    """Structured report for one adapter-level tool execution."""

    context: MCPExecutionContext
    router_enabled: bool
    router_applied: bool
    steps: tuple[ExecutionStep, ...] = ()
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a structured dict representation."""

        return self.model_dump()

    def to_legacy_text(self) -> str:
        """Render the report as the existing string-based MCP adapter contract."""

        if self.error:
            return self.error

        if not self.steps:
            return "No operations performed."

        if len(self.steps) == 1:
            result = self.steps[0].result
            return result if isinstance(result, str) else str(result)

        combined_parts = []
        for index, step in enumerate(self.steps, 1):
            rendered = step.result if isinstance(step.result, str) else str(step.result)
            combined_parts.append(f"[Step {index}: {step.tool_name}] {rendered}")

        return "\n".join(combined_parts)
