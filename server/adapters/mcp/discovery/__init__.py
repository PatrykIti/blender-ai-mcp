# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Discovery inventory and search helpers for TASK-084."""

from .search_documents import build_search_document, build_search_documents
from .search_surface import BlenderDiscoverySearchTransform, build_search_transform
from .taxonomy import DISCOVERY_CATEGORIES, normalize_discovery_category
from .tool_inventory import (
    DiscoveryEntry,
    build_discovery_entry_map,
    build_discovery_inventory,
    get_pinned_public_tools,
)

__all__ = [
    "BlenderDiscoverySearchTransform",
    "DISCOVERY_CATEGORIES",
    "DiscoveryEntry",
    "build_discovery_entry_map",
    "build_discovery_inventory",
    "build_search_document",
    "build_search_documents",
    "build_search_transform",
    "get_pinned_public_tools",
    "normalize_discovery_category",
]
