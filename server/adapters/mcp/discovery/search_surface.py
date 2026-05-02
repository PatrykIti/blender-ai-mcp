# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Search-surface helpers for TASK-084 infrastructure."""

from __future__ import annotations

import hashlib
import json
import logging
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
from server.adapters.mcp.transforms.visibility_policy import visible_tools_for_gate_plan
from server.adapters.mcp.version_policy import CONTRACT_LINE_LLM_GUIDED_V2

from .search_documents import build_search_documents
from .tool_inventory import build_discovery_entry_map, get_pinned_public_tools

logger = logging.getLogger(__name__)

_GATE_RECOVERY_QUERY_HINTS = (
    "attach",
    "contact",
    "deadlock",
    "floating",
    "gap",
    "gate",
    "repair",
    "reset goal",
    "seam",
    "stuck",
    "support",
)


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

    def _exact_match_tools(self, tools: Sequence[Tool], query: str) -> Sequence[Tool]:
        normalized_query = query.strip().lower()
        if not normalized_query:
            return ()

        matches: list[Tool] = []
        for tool in tools:
            entry = self._entry_map.get(tool.name)
            exact_names = {tool.name.lower()}
            if entry is not None:
                exact_names.add(entry.internal_name.lower())
                exact_names.update(alias.lower() for alias in entry.aliases)
            if normalized_query in exact_names:
                matches.append(tool)
        return matches

    def _serialize_results(self, tools: Sequence[Tool]) -> list[dict[str, Any]]:
        rendered: list[dict[str, Any]] = []
        for tool in tools:
            entry = self._entry_map.get(tool.name)
            description = (tool.description or "").strip().replace("\n", " ")
            if len(description) > 220:
                description = f"{description[:217].rstrip()}..."
            item: dict[str, Any] = {
                "name": tool.name,
                "description": description,
            }
            if entry is not None:
                item["category"] = entry.category
                item["capability_id"] = entry.capability_id
                if entry.aliases:
                    item["aliases"] = list(entry.aliases)
            rendered.append(item)
        return rendered

    async def _search(self, tools: Sequence[Tool], query: str) -> Sequence[Tool]:
        exact_matches = self._exact_match_tools(tools, query)
        if exact_matches:
            return tuple(exact_matches[: self._max_results])

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

    async def _active_gate_recovery_tools(
        self,
        ctx: Context,
        tools: Sequence[Tool],
        query: str,
    ) -> Sequence[Tool]:
        normalized_query = query.strip().lower()
        if not normalized_query or not any(hint in normalized_query for hint in _GATE_RECOVERY_QUERY_HINTS):
            return ()

        try:
            session_state = await get_session_capability_state_async(ctx)
        except Exception:
            return ()
        gate_tools = visible_tools_for_gate_plan(session_state.gate_plan)
        if not gate_tools:
            return ()

        tools_by_name = {tool.name: tool for tool in tools}
        preferred_order = [
            "scene_relation_graph",
            "scene_measure_gap",
            "scene_assert_contact",
            "macro_attach_part_to_surface",
            "macro_align_part_with_contact",
            "macro_place_supported_pair",
            "macro_place_symmetry_pair",
            "macro_adjust_relative_proportion",
            "mesh_inspect",
            "macro_adjust_segment_chain_arc",
            "scene_view_diagnostics",
        ]
        selected = [tools_by_name[name] for name in preferred_order if name in gate_tools and name in tools_by_name]
        if selected:
            return tuple(selected[: self._max_results])
        return tuple(
            tools_by_name[name] for name in sorted(gate_tools.intersection(tools_by_name))[: self._max_results]
        )

    async def _render_results(self, tools: Sequence[Tool]) -> list[dict[str, Any]]:
        return self._serialize_results(tools)

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
            gate_override = await transform._active_gate_recovery_tools(ctx, hidden, query)
            if gate_override:
                return await transform._render_results(gate_override)
            results = await transform._search(hidden, query)
            return await transform._render_results(results)

        return Tool.from_function(fn=search_tools, name=self._search_tool_name)

    def _make_call_tool(self) -> Tool:
        transform = self

        async def call_tool(
            name: Annotated[str | None, "The canonical public name of the tool to call"] = None,
            arguments: Annotated[dict[str, Any] | str | None, "Arguments to pass to the tool"] = None,
            tool: Annotated[str | None, "Legacy compatibility alias for `name`"] = None,
            params: Annotated[dict[str, Any] | str | None, "Legacy compatibility alias for `arguments`"] = None,
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
            if isinstance(resolved_arguments, str):
                try:
                    parsed_arguments = json.loads(resolved_arguments)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        "call_tool(..., arguments=...) must be a dictionary or a JSON object string."
                    ) from exc
                if not isinstance(parsed_arguments, dict):
                    raise ValueError("call_tool(..., arguments=...) JSON string must decode to an object/dict.")
                resolved_arguments = parsed_arguments
            canonical_arguments = transform._canonicalize_call_arguments(resolved_name, resolved_arguments)
            logger.info(
                "[CALL_TOOL_PROXY] name=%s canonical_arg_keys=%s",
                resolved_name,
                sorted(canonical_arguments.keys()) if isinstance(canonical_arguments, dict) else [],
            )
            try:
                return await ctx.fastmcp.call_tool(resolved_name, canonical_arguments)
            except NotFoundError as exc:
                logger.warning(
                    "[CALL_TOOL_PROXY] unknown_tool name=%s canonical_arg_keys=%s",
                    resolved_name,
                    sorted(canonical_arguments.keys()) if isinstance(canonical_arguments, dict) else [],
                )
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
