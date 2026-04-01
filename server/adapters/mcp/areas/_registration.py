# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Helpers for registering plain MCP tool callables on reusable targets."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping


def register_existing_tools(
    module_globals: Mapping[str, Any],
    target: Any,
    tool_names: Iterable[str],
    *,
    tags: Iterable[str] | None = None,
) -> Dict[str, Any]:
    """Register existing tool callables on a server/provider target."""

    registered: Dict[str, Any] = {}
    tag_set = set(tags) if tags is not None else None

    for tool_name in tool_names:
        tool = module_globals[tool_name]
        fn = getattr(tool, "fn", tool)
        kwargs: Dict[str, Any] = {"name": tool_name}
        if tag_set:
            kwargs["tags"] = set(tag_set)
        registered[tool_name] = target.tool(fn, **kwargs)

    return registered
