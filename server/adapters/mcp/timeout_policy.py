# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Shared timeout policy for MCP, RPC, and addon execution boundaries."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MCPTimeoutPolicy:
    """Explicit timeout contract across runtime boundaries."""

    tool_timeout_seconds: float
    task_timeout_seconds: float
    rpc_timeout_seconds: float
    addon_execution_timeout_seconds: float

    @property
    def boundary_names(self) -> tuple[str, ...]:
        """Return the canonical timeout boundary names."""

        return (
            "mcp_tool",
            "mcp_task",
            "rpc_client",
            "addon_execution",
        )

    def to_dict(self) -> dict[str, float | tuple[str, ...]]:
        """Return a diagnostics-friendly representation."""

        return {
            "tool_timeout_seconds": self.tool_timeout_seconds,
            "task_timeout_seconds": self.task_timeout_seconds,
            "rpc_timeout_seconds": self.rpc_timeout_seconds,
            "addon_execution_timeout_seconds": self.addon_execution_timeout_seconds,
            "boundary_names": self.boundary_names,
        }


def build_timeout_policy(
    *,
    tool_timeout_seconds: float,
    task_timeout_seconds: float,
    rpc_timeout_seconds: float,
    addon_execution_timeout_seconds: float,
) -> MCPTimeoutPolicy:
    """Build a validated timeout policy."""

    return MCPTimeoutPolicy(
        tool_timeout_seconds=tool_timeout_seconds,
        task_timeout_seconds=task_timeout_seconds,
        rpc_timeout_seconds=rpc_timeout_seconds,
        addon_execution_timeout_seconds=addon_execution_timeout_seconds,
    )
