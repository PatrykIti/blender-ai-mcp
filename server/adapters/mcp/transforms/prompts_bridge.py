# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Prompt bridge transform stage scaffold."""

from __future__ import annotations

from typing import Any

from server.adapters.mcp.settings import SurfaceProfileSettings


def build_prompts_bridge_transform(surface: SurfaceProfileSettings) -> Any | None:
    """Build the prompts/resources bridge stage for a surface profile.

    TASK-090 populates this when prompt-capable and tool-only surfaces diverge.
    """

    return None
