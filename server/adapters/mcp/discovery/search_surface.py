# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Search-surface helpers for TASK-084 infrastructure."""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from typing import Annotated, Any

from fastmcp.server.context import Context
from fastmcp.server.transforms.search import BM25SearchTransform
from fastmcp.tools.tool import Tool, ToolResult

from server.adapters.mcp.platform.name_resolution import resolve_canonical_tool_name
from server.adapters.mcp.platform.naming_rules import AUDIENCE_LLM_GUIDED
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
        if arguments is None:
            return None

        canonical_name = resolve_canonical_tool_name(name, contract_line=self._contract_line)
        if canonical_name != "scene_clean_scene":
            return arguments

        canonical_arguments = dict(arguments)
        split_keep_lights = canonical_arguments.pop("keep_lights", None)
        split_keep_cameras = canonical_arguments.pop("keep_cameras", None)
        split_present = "keep_lights" in arguments or "keep_cameras" in arguments

        if not split_present:
            return canonical_arguments

        if "keep_lights_and_cameras" in canonical_arguments:
            combined = canonical_arguments["keep_lights_and_cameras"]
            if (
                isinstance(combined, bool)
                and split_keep_lights is not None
                and isinstance(split_keep_lights, bool)
                and split_keep_lights != combined
            ) or (
                isinstance(combined, bool)
                and split_keep_cameras is not None
                and isinstance(split_keep_cameras, bool)
                and split_keep_cameras != combined
            ):
                raise ValueError(
                    "scene_clean_scene(...) uses the canonical public flag "
                    "`keep_lights_and_cameras`. Legacy `keep_lights` / `keep_cameras` "
                    "values must agree with it when both forms are provided."
                )
            return canonical_arguments

        if not isinstance(split_keep_lights, bool) or not isinstance(split_keep_cameras, bool):
            raise ValueError(
                "scene_clean_scene(...) accepts legacy split cleanup flags only when "
                "both `keep_lights` and `keep_cameras` are provided as booleans. "
                "Canonical public form: `keep_lights_and_cameras`."
            )

        if split_keep_lights != split_keep_cameras:
            raise ValueError(
                "scene_clean_scene(...) no longer supports separate light/camera cleanup "
                "choices on `llm-guided`. Use the canonical public flag "
                "`keep_lights_and_cameras`, or provide legacy `keep_lights` and "
                "`keep_cameras` with the same boolean value."
            )

        canonical_arguments["keep_lights_and_cameras"] = split_keep_lights
        return canonical_arguments

    def _make_call_tool(self) -> Tool:
        transform = self

        async def call_tool(
            name: Annotated[str, "The name of the tool to call"],
            arguments: Annotated[dict[str, Any] | None, "Arguments to pass to the tool"] = None,
            ctx: Context = None,  # type: ignore[assignment]
        ) -> ToolResult:
            if name in {transform._call_tool_name, transform._search_tool_name}:
                raise ValueError(f"'{name}' is a synthetic search tool and cannot be called via the call_tool proxy")
            if ctx is None:
                raise RuntimeError("call_tool proxy requires an active FastMCP context")

            canonical_arguments = transform._canonicalize_call_arguments(name, arguments)
            return await ctx.fastmcp.call_tool(name, canonical_arguments)

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
