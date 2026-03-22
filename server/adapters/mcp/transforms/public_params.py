# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Helpers for building public parameter alias transforms."""

from __future__ import annotations

from fastmcp.tools.tool_transform import ArgTransformConfig

from server.adapters.mcp.platform.naming_rules import (
    AUDIENCE_LLM_GUIDED,
    get_public_arg_aliases,
)

HIDDEN_ARGUMENTS: dict[tuple[str, str], set[str]] = {
    (
        AUDIENCE_LLM_GUIDED,
        "scene_inspect",
    ): {
        "detailed",
        "include_disabled",
        "material_filter",
        "include_empty_slots",
        "include_bones",
        "modifier_name",
        "include_node_tree",
    },
    (
        AUDIENCE_LLM_GUIDED,
        "workflow_catalog",
    ): {
        "top_k",
        "threshold",
        "overwrite",
        "content_type",
        "session_id",
        "chunk_data",
        "chunk_index",
        "total_chunks",
    },
    (
        AUDIENCE_LLM_GUIDED,
        "mesh_inspect",
    ): {
        "selected_only",
        "uv_layer",
        "include_deltas",
    },
}


def build_public_param_transforms(
    tool_name: str,
    audience: str,
    *,
    contract_line: str | None = None,
) -> dict[str, ArgTransformConfig]:
    """Build argument transform configs for a public contract audience."""

    if contract_line == "llm-guided-v1":
        return {}

    transforms: dict[str, ArgTransformConfig] = {}

    for internal_arg, public_arg in get_public_arg_aliases(tool_name, audience).items():
        transforms[internal_arg] = ArgTransformConfig(name=public_arg)

    for hidden_arg in HIDDEN_ARGUMENTS.get((audience, tool_name), set()):
        existing = transforms.get(hidden_arg)
        if existing is None:
            transforms[hidden_arg] = ArgTransformConfig(hide=True)
        else:
            transforms[hidden_arg] = ArgTransformConfig(
                name=existing.name,
                description=existing.description,
                default=existing.default,
                hide=True,
                required=existing.required,
                examples=existing.examples,
            )

    return transforms
