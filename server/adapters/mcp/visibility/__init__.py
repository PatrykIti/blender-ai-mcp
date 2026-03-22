# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Visibility tags and policy helpers for FastMCP surfaces."""

from .tags import (
    AUDIENCE_LEGACY,
    AUDIENCE_LLM,
    ENTRY_GUIDED,
    capability_phase_tag,
    get_capability_tags,
    phase_tag,
)

__all__ = [
    "AUDIENCE_LEGACY",
    "AUDIENCE_LLM",
    "ENTRY_GUIDED",
    "capability_phase_tag",
    "get_capability_tags",
    "phase_tag",
]
