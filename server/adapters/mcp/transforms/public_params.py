# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Helpers for building public parameter alias transforms."""

from __future__ import annotations

from fastmcp.tools.tool_transform import ArgTransformConfig

from server.adapters.mcp.platform.naming_rules import get_public_arg_aliases


def build_public_param_transforms(
    tool_name: str,
    audience: str,
) -> dict[str, ArgTransformConfig]:
    """Build argument transform configs for a public contract audience."""

    return {
        internal_arg: ArgTransformConfig(name=public_arg)
        for internal_arg, public_arg in get_public_arg_aliases(tool_name, audience).items()
    }
