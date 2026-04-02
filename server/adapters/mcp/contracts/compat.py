# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Compatibility helpers for structured adapter contracts."""

from __future__ import annotations

from pydantic import BaseModel

CONTRACT_ENABLED_TOOLS = {
    "router_set_goal",
    "router_get_status",
    "workflow_catalog",
    "scene_context",
    "scene_inspect",
    "scene_create",
    "scene_configure",
    "macro_cutout_recess",
    "macro_finish_form",
    "macro_relative_layout",
    "macro_attach_part_to_surface",
    "macro_align_part_with_contact",
    "macro_place_symmetry_pair",
    "macro_adjust_relative_proportion",
    "mesh_select",
    "mesh_select_targeted",
    "mesh_inspect",
}

# Explicit, narrow compatibility exceptions for profiles that still need
# deterministic text-heavy behavior for selected tools.
LEGACY_TEXT_EXCEPTIONS: dict[str, set[str]] = {
    "legacy-manual": set(),
    "legacy-flat": set(),
}


def to_compat_dict(value: BaseModel | dict) -> dict:
    """Convert structured contract payloads to plain dicts when explicitly needed."""

    if isinstance(value, BaseModel):
        return value.model_dump()
    return value


def get_delivery_mode(surface_profile: str) -> str:
    """Return the delivery policy for a surface profile."""

    return "compatibility" if surface_profile in {"legacy-manual", "legacy-flat"} else "structured_first"


def should_prefer_native_structured_delivery(
    surface_profile: str,
    tool_name: str,
) -> bool:
    """Return True when a tool should use structured-first native FastMCP delivery."""

    if tool_name not in CONTRACT_ENABLED_TOOLS:
        return False
    return tool_name not in LEGACY_TEXT_EXCEPTIONS.get(surface_profile, set())
