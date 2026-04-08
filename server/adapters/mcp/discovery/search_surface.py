# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Search-surface helpers for TASK-084 infrastructure."""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from typing import Annotated, Any

from fastmcp.exceptions import NotFoundError, ToolError
from fastmcp.server.context import Context
from fastmcp.server.transforms.search import BM25SearchTransform
from fastmcp.tools.tool import Tool, ToolResult

from server.adapters.mcp.guided_contract import canonicalize_guided_tool_arguments
from server.adapters.mcp.platform.naming_rules import AUDIENCE_LLM_GUIDED
from server.adapters.mcp.session_capabilities import (
    apply_visibility_for_session_state,
    get_session_capability_state_async,
)
from server.adapters.mcp.settings import SurfaceProfileSettings
from server.adapters.mcp.version_policy import CONTRACT_LINE_LLM_GUIDED_V2

from .search_documents import build_search_documents
from .tool_inventory import build_discovery_entry_map, get_pinned_public_tools


def _catalog_hash(search_documents: dict[str, str]) -> str:
    key = "|".join(f"{tool_name}:{document}" for tool_name, document in sorted(search_documents.items()))
    return hashlib.sha256(key.encode()).hexdigest()


class BlenderDiscoverySearchTransform(BM25SearchTransform):
    """BM25 search transform using platform-owned enriched discovery documents."""

    def __init__(
        self,
        *,
        max_results: int = 5,
        always_visible: list[str] | None = None,
        entry_map: dict[str, Any] | None = None,
        contract_line: str = CONTRACT_LINE_LLM_GUIDED_V2,
    ) -> None:
        super().__init__(
            max_results=max_results,
            always_visible=always_visible,
        )
        self._entry_map = entry_map or build_discovery_entry_map()
        self._contract_line = contract_line

    async def _search(self, tools: Sequence[Tool], query: str) -> Sequence[Tool]:
        search_documents = build_search_documents(tools, entry_map=self._entry_map)
        current_hash = _catalog_hash(search_documents)
        if current_hash != self._last_hash:
            documents = [search_documents[tool.name] for tool in tools]
            index_cls = type(self._index)
            new_index = index_cls(self._index.k1, self._index.b)
            new_index.build(documents)
            self._index, self._indexed_tools, self._last_hash = (
                new_index,
                tools,
                current_hash,
            )

        indices = self._index.query(query, self._max_results)
        return [self._indexed_tools[i] for i in indices]

    def _canonicalize_call_arguments(self, name: str, arguments: dict[str, Any] | None) -> dict[str, Any] | None:
        return canonicalize_guided_tool_arguments(name, arguments, contract_line=self._contract_line)

    async def _sync_visibility_if_needed(self, ctx: Context | None) -> None:
        """Best-effort visibility refresh before discovery/proxy operations."""

        if ctx is None:
            return

        try:
            session_state = await get_session_capability_state_async(ctx)
            await apply_visibility_for_session_state(ctx, session_state)
        except Exception:
            return

    def _make_search_tool(self) -> Tool:
        transform = self

        async def search_tools(
            query: Annotated[str, "Natural language query to search for tools"],
            ctx: Context = None,  # type: ignore[assignment]
        ) -> str | list[dict[str, Any]]:
            """Search for tools using natural language."""

            if ctx is None:
                raise RuntimeError("search_tools requires an active FastMCP context")
            await transform._sync_visibility_if_needed(ctx)
            hidden = await transform._get_visible_tools(ctx)
            results = await transform._search(hidden, query)
            return await transform._render_results(results)

        return Tool.from_function(fn=search_tools, name=self._search_tool_name)

    def _make_call_tool(self) -> Tool:
        transform = self

        async def call_tool(
            name: Annotated[str | None, "The canonical public name of the tool to call"] = None,
            arguments: Annotated[dict[str, Any] | None, "Arguments to pass to the tool"] = None,
            tool: Annotated[str | None, "Legacy compatibility alias for `name`"] = None,
            params: Annotated[dict[str, Any] | None, "Legacy compatibility alias for `arguments`"] = None,
            ctx: Context = None,  # type: ignore[assignment]
        ) -> ToolResult:
            resolved_name = name or tool
            if name is not None and tool is not None and name != tool:
                raise ValueError("call_tool(...) received both `name` and legacy alias `tool` with different values.")
            if arguments is not None and params is not None and arguments != params:
                raise ValueError(
                    "call_tool(...) received both `arguments` and legacy alias `params` with different values."
                )
            if resolved_name is None:
                raise ValueError(
                    "call_tool(...) requires the canonical public field `name`. "
                    "Legacy compatibility alias `tool` is still accepted when needed."
                )

            if resolved_name in {transform._call_tool_name, transform._search_tool_name}:
                raise ValueError(
                    f"'{resolved_name}' is a synthetic search tool and cannot be called via the call_tool proxy"
                )
            if ctx is None:
                raise RuntimeError("call_tool proxy requires an active FastMCP context")

            await transform._sync_visibility_if_needed(ctx)
            resolved_arguments = arguments if arguments is not None else params
            canonical_arguments = transform._canonicalize_call_arguments(resolved_name, resolved_arguments)
            try:
                return await ctx.fastmcp.call_tool(resolved_name, canonical_arguments)
            except NotFoundError as exc:
                raise ToolError(
                    f"Unknown tool: '{resolved_name}'. On the shaped guided surface, do not guess tool names into "
                    "call_tool(...). Use search_tools(...) first unless the tool is already directly visible."
                ) from exc

        return Tool.from_function(fn=call_tool, name=self._call_tool_name)


def build_search_transform(surface: SurfaceProfileSettings) -> BM25SearchTransform | None:
    """Build the discovery/search transform for a surface profile."""

    if not surface.search_enabled:
        return None

    audience = AUDIENCE_LLM_GUIDED if surface.name == "llm-guided" else AUDIENCE_LLM_GUIDED
    contract_line = surface.default_contract_line or CONTRACT_LINE_LLM_GUIDED_V2
    pinned = list(get_pinned_public_tools(audience=audience, contract_line=contract_line))
    entry_map = build_discovery_entry_map(audience=audience, contract_line=contract_line)

    return BlenderDiscoverySearchTransform(
        max_results=surface.search_max_results,
        always_visible=pinned,
        entry_map=entry_map,
        contract_line=contract_line,
    )
