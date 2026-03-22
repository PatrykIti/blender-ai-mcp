# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Discovery transform stage scaffold."""

from __future__ import annotations

from typing import Any

from server.adapters.mcp.settings import SurfaceProfileSettings


def build_discovery_transform(surface: SurfaceProfileSettings) -> Any | None:
    """Build the discovery stage for a surface profile.

    TASK-084 and TASK-094 populate this with search- or code-mode-specific
    transforms once the factory baseline is stable.
    """

    return None
