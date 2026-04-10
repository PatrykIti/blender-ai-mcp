# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Structured contracts for guided object naming policy."""

from __future__ import annotations

from typing import Literal

from server.adapters.mcp.contracts.base import MCPContract


class GuidedNamingDecisionContract(MCPContract):
    """Structured naming-policy decision for guided object names."""

    status: Literal["allowed", "warning", "blocked"]
    reason_code: str | None = None
    message: str | None = None
    suggested_names: list[str] = []
    canonical_pattern: str | None = None
    role: str | None = None
    domain_profile: str | None = None
    current_step: str | None = None
