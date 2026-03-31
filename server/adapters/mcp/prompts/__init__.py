# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Prompt asset catalog, rendering, and provider helpers for TASK-090."""

from server.adapters.mcp.prompts.prompt_catalog import (
    PromptCatalogEntry,
    get_prompt_catalog,
    get_prompt_catalog_entry,
    get_recommended_prompt_entries,
)
from server.adapters.mcp.prompts.provider import (
    build_prompt_assets_provider,
    register_prompt_assets,
)
from server.adapters.mcp.prompts.rendering import (
    render_prompt_asset,
    render_recommended_prompts,
)

__all__ = [
    "PromptCatalogEntry",
    "build_prompt_assets_provider",
    "get_prompt_catalog",
    "get_prompt_catalog_entry",
    "get_recommended_prompt_entries",
    "register_prompt_assets",
    "render_prompt_asset",
    "render_recommended_prompts",
]
