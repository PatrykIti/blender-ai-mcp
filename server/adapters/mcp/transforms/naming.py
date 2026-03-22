# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Naming transform stage scaffold."""

from __future__ import annotations

from typing import Any

from fastmcp.server.transforms import ToolTransform
from fastmcp.tools.tool_transform import ToolTransformConfig

from server.adapters.mcp.platform.naming_rules import AUDIENCE_LLM_GUIDED
from server.adapters.mcp.platform.capability_manifest import get_capability_manifest
from server.adapters.mcp.platform.public_contracts import get_public_contract
from server.adapters.mcp.settings import SurfaceProfileSettings
from server.adapters.mcp.transforms.public_params import build_public_param_transforms


def build_naming_transform(surface: SurfaceProfileSettings) -> Any | None:
    """Build the naming stage for a surface profile.

    TASK-086 populates this with real ToolTransform / ArgTransform rules.
    """

    if surface.name != "llm-guided":
        return None

    transforms: dict[str, ToolTransformConfig] = {}

    for entry in get_capability_manifest():
        contract = get_public_contract(
            entry,
            contract_line=surface.default_contract_line,
            audience=AUDIENCE_LLM_GUIDED,
        )
        for internal_name, public_name in contract.tool_name_map:
            arg_transforms = build_public_param_transforms(
                internal_name,
                AUDIENCE_LLM_GUIDED,
                contract_line=surface.default_contract_line,
            )
            if public_name == internal_name and not arg_transforms:
                continue
            transforms[internal_name] = ToolTransformConfig(
                name=public_name,
                arguments=arg_transforms,
            )

    if not transforms:
        return None

    return ToolTransform(transforms)
