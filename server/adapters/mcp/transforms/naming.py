# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Naming transform stage scaffold."""

from __future__ import annotations

from typing import Any

from server.adapters.mcp.settings import SurfaceProfileSettings


def build_naming_transform(surface: SurfaceProfileSettings) -> Any | None:
    """Build the naming stage for a surface profile.

    TASK-086 populates this with real ToolTransform / ArgTransform rules.
    """

    return None
