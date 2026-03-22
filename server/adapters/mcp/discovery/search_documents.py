# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Search document enrichment for TASK-084."""

from __future__ import annotations

from collections.abc import Sequence

from fastmcp.tools.tool import Tool

from .tool_inventory import DiscoveryEntry, build_discovery_entry_map


def _get_param_descriptions(tool: Tool) -> tuple[str, ...]:
    schema = tool.parameters or {}
    properties = schema.get("properties", {})

    descriptions: list[str] = []
    for param_name, param_info in properties.items():
        descriptions.append(param_name)
        if isinstance(param_info, dict):
            description = param_info.get("description")
            if description:
                descriptions.append(str(description))
    return tuple(descriptions)


def build_search_document(tool: Tool, entry: DiscoveryEntry | None) -> str:
    """Build one enriched search document for a tool."""

    parts: list[str] = [tool.name]

    if tool.description:
        parts.append(tool.description)

    parts.extend(_get_param_descriptions(tool))

    if entry is not None:
        parts.extend(
            filter(
                None,
                (
                    entry.internal_name,
                    entry.capability_id,
                    entry.category,
                    *entry.tags,
                    *entry.aliases,
                ),
            )
        )
        if entry.metadata is not None:
            parts.extend(
                filter(
                    None,
                    (
                        entry.metadata.description,
                        *entry.metadata.keywords,
                        *entry.metadata.sample_prompts,
                        *entry.metadata.related_tools,
                        *entry.metadata.patterns,
                    ),
                )
            )

    return " ".join(str(part) for part in parts if part)


def build_search_documents(
    tools: Sequence[Tool],
    *,
    entry_map: dict[str, DiscoveryEntry] | None = None,
) -> dict[str, str]:
    """Build enriched search text keyed by public tool name."""

    resolved_entry_map = entry_map or build_discovery_entry_map()
    return {
        tool.name: build_search_document(tool, resolved_entry_map.get(tool.name))
        for tool in tools
    }
