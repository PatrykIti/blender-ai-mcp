# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Canonical tool-name resolution between public aliases and internal ids."""

from __future__ import annotations

from server.adapters.mcp.platform.naming_rules import AUDIENCE_LLM_GUIDED
from server.adapters.mcp.platform.public_contracts import (
    get_public_to_internal_tool_map,
    resolve_internal_tool_name,
)


def get_llm_guided_alias_map() -> dict[str, str]:
    """Return the current public alias -> internal tool mapping for llm-guided."""

    from server.adapters.mcp.platform.capability_manifest import get_capability_manifest

    return get_public_to_internal_tool_map(
        get_capability_manifest(),
        audience=AUDIENCE_LLM_GUIDED,
    )


def resolve_canonical_tool_name(tool_name: str) -> str:
    """Resolve any known public alias to the canonical internal tool id."""

    from server.adapters.mcp.platform.capability_manifest import get_capability_manifest

    return resolve_internal_tool_name(
        get_capability_manifest(),
        tool_name,
        audience=AUDIENCE_LLM_GUIDED,
    )
