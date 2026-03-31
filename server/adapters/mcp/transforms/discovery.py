# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Discovery transform stage scaffold."""

from __future__ import annotations

import importlib
from typing import Any

from fastmcp.experimental.transforms.code_mode import CodeMode, GetSchemas, GetTags, MontySandboxProvider, Search

from server.adapters.mcp.discovery import build_search_transform
from server.adapters.mcp.settings import SurfaceProfileSettings


def _build_code_mode_transform(surface: SurfaceProfileSettings) -> CodeMode:
    """Build the experimental Code Mode transform with explicit dependency guardrails."""

    try:
        importlib.import_module("pydantic_monty")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "The 'code-mode-pilot' surface requires pydantic-monty. "
            "Install it via the FastMCP code-mode extra or add the dependency explicitly."
        ) from exc

    return CodeMode(
        sandbox_provider=MontySandboxProvider(
            limits={
                "max_duration_secs": 5.0,
                "max_memory": 32_000_000,
                "max_recursion_depth": 32,
            }
        ),
        discovery_tools=[
            Search(default_detail="brief", default_limit=surface.search_max_results),
            GetSchemas(default_detail="detailed"),
            GetTags(default_detail="brief"),
        ],
        execute_tool_name="execute",
        execute_description=(
            "Experimental read-only code-mode executor. "
            "Use `await call_tool(name, params)` only with the visible read-only MCP surface. "
            "Return the final answer from one Python block."
        ),
    )


def build_discovery_transform(surface: SurfaceProfileSettings) -> Any | None:
    """Build the discovery stage for a surface profile.

    TASK-084 populates this with the search-first discovery infrastructure.
    Default rollout can stay disabled at the surface-profile level until the
    product-level rollout gate is intentionally opened.
    """

    if surface.code_mode_enabled:
        return _build_code_mode_transform(surface)

    return build_search_transform(surface)
