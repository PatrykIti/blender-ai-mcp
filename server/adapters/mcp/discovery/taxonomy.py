# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Canonical discovery taxonomy helpers for TASK-084."""

from __future__ import annotations

DISCOVERY_CATEGORIES = {
    "scene",
    "mesh",
    "modeling",
    "material",
    "reference",
    "uv",
    "collection",
    "curve",
    "lattice",
    "sculpt",
    "baking",
    "text",
    "armature",
    "system",
    "extraction",
    "router",
    "workflow",
}


def normalize_discovery_category(category: str) -> str:
    """Return the canonical discovery category."""

    normalized = category.strip().lower().replace("-", "_")
    if normalized not in DISCOVERY_CATEGORIES:
        raise ValueError(f"Unknown discovery category '{category}'")
    return normalized
