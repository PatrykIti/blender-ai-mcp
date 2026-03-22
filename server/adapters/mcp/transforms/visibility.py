# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Visibility transform stage scaffold."""

from __future__ import annotations

from typing import Any

from fastmcp.server.transforms.visibility import create_visibility_transforms

from server.adapters.mcp.session_phase import SessionPhase
from server.adapters.mcp.settings import SurfaceProfileSettings
from server.adapters.mcp.transforms.visibility_policy import build_visibility_rules


def build_visibility_transform(surface: SurfaceProfileSettings) -> Any | None:
    """Build the visibility stage for a surface profile.

    TASK-085 populates this with profile/static visibility rules and later
    session-driven visibility controls.
    """

    rules = build_visibility_rules(surface.name, SessionPhase.BOOTSTRAP)
    if not rules:
        return None
    return create_visibility_transforms(rules)
