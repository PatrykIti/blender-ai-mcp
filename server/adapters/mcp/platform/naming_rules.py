# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Public naming conventions for FastMCP surface contracts."""

from __future__ import annotations


AUDIENCE_LEGACY = "legacy"
AUDIENCE_LLM_GUIDED = "llm_guided"


TOOL_NAME_OVERRIDES: dict[tuple[str, str], str] = {
    (AUDIENCE_LLM_GUIDED, "scene_context"): "check_scene",
    (AUDIENCE_LLM_GUIDED, "scene_inspect"): "inspect_scene",
    (AUDIENCE_LLM_GUIDED, "workflow_catalog"): "browse_workflows",
}
ARGUMENT_NAME_OVERRIDES: dict[tuple[str, str, str], str] = {
    (AUDIENCE_LLM_GUIDED, "scene_context", "action"): "query",
    (AUDIENCE_LLM_GUIDED, "scene_inspect", "object_name"): "target_object",
    (AUDIENCE_LLM_GUIDED, "workflow_catalog", "workflow_name"): "name",
    (AUDIENCE_LLM_GUIDED, "workflow_catalog", "query"): "search_query",
}


def get_public_tool_name(internal_name: str, audience: str) -> str:
    """Return the public tool name for a given audience contract."""

    return TOOL_NAME_OVERRIDES.get((audience, internal_name), internal_name)


def get_public_arg_name(tool_name: str, arg_name: str, audience: str) -> str:
    """Return the public argument name for a given audience contract."""

    return ARGUMENT_NAME_OVERRIDES.get((audience, tool_name, arg_name), arg_name)


def get_public_arg_aliases(tool_name: str, audience: str) -> dict[str, str]:
    """Return all public argument aliases for a tool/audience contract."""

    aliases: dict[str, str] = {}
    for (override_audience, override_tool, internal_arg), public_arg in ARGUMENT_NAME_OVERRIDES.items():
        if override_audience == audience and override_tool == tool_name:
            aliases[internal_arg] = public_arg
    return aliases
