# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Helpers for registering existing MCP tool functions on reusable targets."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping


def register_existing_tools(
    module_globals: Mapping[str, Any],
    target: Any,
    tool_names: Iterable[str],
    *,
    tags: Iterable[str] | None = None,
) -> Dict[str, Any]:
    """Register existing FastMCP tool functions on a server/provider target."""

    registered: Dict[str, Any] = {}
    tag_set = set(tags) if tags is not None else None

    for tool_name in tool_names:
        tool = module_globals[tool_name]
        fn = getattr(tool, "fn", tool)
        kwargs = {"name": tool_name}
        if tag_set:
            kwargs["tags"] = set(tag_set)
        registered[tool_name] = target.tool(fn, **kwargs)

    return registered
