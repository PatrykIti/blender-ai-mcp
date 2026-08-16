# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Prompt bridge transform stage scaffold."""

from __future__ import annotations

from typing import Any

from server.adapters.mcp.settings import SurfaceProfileSettings
from server.infrastructure.config import get_config


def build_prompts_bridge_transform(
    surface: SurfaceProfileSettings,
    *,
    provider: Any | None = None,
) -> Any | None:
    """Build the prompts/resources bridge stage for a surface profile.

    TASK-090 populates this using FastMCP's native prompts-as-tools bridge.
    """

    if not get_config().MCP_PROMPTS_AS_TOOLS_ENABLED:
        return None

    if provider is None:
        return None

    from fastmcp.server.transforms.prompts_as_tools import PromptsAsTools

    return PromptsAsTools(provider)
