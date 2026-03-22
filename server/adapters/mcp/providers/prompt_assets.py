# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Reusable provider builder for MCP prompt assets."""

from __future__ import annotations

from typing import Any, Dict

from server.adapters.mcp.prompts.provider import (
    build_prompt_assets_provider,
    register_prompt_assets,
)


def register_prompt_assets_provider(target: Any) -> Dict[str, Any]:
    """Register prompt assets on a FastMCP-compatible provider target."""

    return register_prompt_assets(target)


__all__ = [
    "build_prompt_assets_provider",
    "register_prompt_assets_provider",
]
