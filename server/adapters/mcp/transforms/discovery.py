# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Discovery transform stage scaffold."""

from __future__ import annotations

from typing import Any

from server.adapters.mcp.discovery import build_search_transform
from server.adapters.mcp.settings import SurfaceProfileSettings


def build_discovery_transform(surface: SurfaceProfileSettings) -> Any | None:
    """Build the discovery stage for a surface profile.

    TASK-084 populates this with the search-first discovery infrastructure.
    Default rollout can stay disabled at the surface-profile level until the
    product-level rollout gate is intentionally opened.
    """

    return build_search_transform(surface)
