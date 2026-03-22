# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Search-surface helpers for TASK-084 infrastructure."""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from typing import Any

from fastmcp.server.transforms.search import BM25SearchTransform
from fastmcp.tools.tool import Tool

from server.adapters.mcp.platform.naming_rules import AUDIENCE_LLM_GUIDED
from server.adapters.mcp.settings import SurfaceProfileSettings
from server.adapters.mcp.version_policy import CONTRACT_LINE_LLM_GUIDED_V2

from .search_documents import build_search_documents
from .tool_inventory import build_discovery_entry_map, get_pinned_public_tools


def _catalog_hash(search_documents: dict[str, str]) -> str:
    key = "|".join(
        f"{tool_name}:{document}"
        for tool_name, document in sorted(search_documents.items())
    )
    return hashlib.sha256(key.encode()).hexdigest()


class BlenderDiscoverySearchTransform(BM25SearchTransform):
    """BM25 search transform using platform-owned enriched discovery documents."""

    def __init__(
        self,
        *,
        max_results: int = 5,
        always_visible: list[str] | None = None,
        entry_map: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            max_results=max_results,
            always_visible=always_visible,
        )
        self._entry_map = entry_map or build_discovery_entry_map()

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
    )
