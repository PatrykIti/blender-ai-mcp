# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Visibility transform stage scaffold."""

from __future__ import annotations

from typing import Any

from server.adapters.mcp.settings import SurfaceProfileSettings


def build_visibility_transform(surface: SurfaceProfileSettings) -> Any | None:
    """Build the visibility stage for a surface profile.

    TASK-085 populates this with profile/static visibility rules and later
    session-driven visibility controls.
    """

    return None
