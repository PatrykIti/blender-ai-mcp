# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Settings and profile data for FastMCP server factory composition."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Literal


ProviderBuilder = Callable[[], Any]
DeliveryMode = Literal["structured_first", "compatibility"]


@dataclass(frozen=True)
class SurfaceProfileSettings:
    """Bootstrap-time surface profile settings for FastMCP composition."""

    name: str
    server_name: str
    provider_builders: tuple[ProviderBuilder, ...]
    list_page_size: int = 50
    tasks_enabled: bool = False
    instructions: str | None = None
    transform_builders: tuple[Callable[[], Any], ...] = field(default_factory=tuple)
    delivery_mode: DeliveryMode = "structured_first"
    search_enabled: bool = False
    search_max_results: int = 5
