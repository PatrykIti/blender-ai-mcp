# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Reusable execution report objects for MCP adapter flows."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from server.adapters.mcp.execution_context import MCPExecutionContext


@dataclass(frozen=True)
class ExecutionStep:
    """One executed tool step in a router-aware call path."""

    tool_name: str
    params: dict[str, Any]
    result: str
    error: str | None = None


@dataclass(frozen=True)
class MCPExecutionReport:
    """Structured report for one adapter-level tool execution."""

    context: MCPExecutionContext
    router_enabled: bool
    router_applied: bool
    steps: tuple[ExecutionStep, ...] = field(default_factory=tuple)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a structured dict representation."""

        return asdict(self)

    def to_legacy_text(self) -> str:
        """Render the report as the existing string-based MCP adapter contract."""

        if self.error:
            return self.error

        if not self.steps:
            return "No operations performed."

        if len(self.steps) == 1:
            return self.steps[0].result

        combined_parts = []
        for index, step in enumerate(self.steps, 1):
            combined_parts.append(f"[Step {index}: {step.tool_name}] {step.result}")

        return "\n".join(combined_parts)
