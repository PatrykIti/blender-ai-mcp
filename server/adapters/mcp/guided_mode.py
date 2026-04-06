# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Guided-mode presets, diagnostics, and session visibility application."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from fastmcp import Context
from fastmcp.utilities.versions import VersionSpec

from server.adapters.mcp.client_profiles import get_client_profile_preset
from server.adapters.mcp.session_phase import SessionPhase, coerce_session_phase
from server.adapters.mcp.transforms.visibility_policy import build_visibility_rules
from server.adapters.mcp.visibility.tags import ENTRY_GUIDED

if TYPE_CHECKING:
    from server.adapters.mcp.platform.capability_manifest import CapabilityManifestEntry


@dataclass(frozen=True)
class VisibilityDiagnostics:
    """Deterministic visibility snapshot for one profile/phase pair."""

    surface_profile: str
    phase: SessionPhase
    guided_mode: bool
    rules: tuple[dict[str, Any], ...]
    visible_capability_ids: tuple[str, ...]
    hidden_capability_ids: tuple[str, ...]
    visible_entry_capability_ids: tuple[str, ...]
    hidden_category_counts: dict[str, int]


def _rule_matches_entry(rule: dict[str, Any], entry: CapabilityManifestEntry) -> bool:
    if rule.get("match_all"):
        return True

    tags = set(rule.get("tags") or ())
    if tags and not tags.intersection(entry.tags):
        return False

    names = set(rule.get("names") or ())
    if names and not names.intersection(entry.tool_names):
        return False

    return True


def _is_capability_visible(entry: CapabilityManifestEntry, rules: list[dict[str, Any]]) -> bool:
    visible = True
    for rule in rules:
        if _rule_matches_entry(rule, entry):
            visible = bool(rule["enabled"])
    return visible


def build_visibility_diagnostics(
    surface_profile: str,
    phase: SessionPhase | str,
    *,
    guided_handoff: dict[str, Any] | None = None,
) -> VisibilityDiagnostics:
    """Build a deterministic visibility snapshot from the current policy model."""

    resolved_phase = coerce_session_phase(phase)
    preset = get_client_profile_preset(surface_profile)
    rules = build_visibility_rules(surface_profile, resolved_phase, guided_handoff=guided_handoff)

    visible_capability_ids: list[str] = []
    hidden_capability_ids: list[str] = []
    visible_entry_capability_ids: list[str] = []
    hidden_category_counts: dict[str, int] = {}

    from server.adapters.mcp.platform.capability_manifest import get_capability_manifest

    for entry in get_capability_manifest():
        if _is_capability_visible(entry, rules):
            visible_capability_ids.append(entry.capability_id)
            if ENTRY_GUIDED in entry.tags:
                visible_entry_capability_ids.append(entry.capability_id)
        else:
            hidden_capability_ids.append(entry.capability_id)
            hidden_category_counts[entry.discovery_category] = (
                hidden_category_counts.get(entry.discovery_category, 0) + 1
            )

    return VisibilityDiagnostics(
        surface_profile=surface_profile,
        phase=resolved_phase,
        guided_mode=preset.guided_mode,
        rules=tuple(rules),
        visible_capability_ids=tuple(visible_capability_ids),
        hidden_capability_ids=tuple(hidden_capability_ids),
        visible_entry_capability_ids=tuple(visible_entry_capability_ids),
        hidden_category_counts=hidden_category_counts,
    )


async def apply_session_visibility(
    ctx: Context,
    *,
    surface_profile: str,
    phase: SessionPhase | str,
    guided_handoff: dict[str, Any] | None = None,
) -> VisibilityDiagnostics:
    """Apply the current visibility policy to one session using native FastMCP APIs."""

    diagnostics = build_visibility_diagnostics(surface_profile, phase, guided_handoff=guided_handoff)
    await ctx.reset_visibility()

    for rule in diagnostics.rules:
        version = None
        if rule.get("version"):
            version = VersionSpec(**rule["version"])

        params = {
            "names": set(rule["names"]) if rule.get("names") else None,
            "keys": set(rule["keys"]) if rule.get("keys") else None,
            "version": version,
            "tags": set(rule["tags"]) if rule.get("tags") else None,
            "components": set(rule["components"]) if rule.get("components") else None,
            "match_all": rule.get("match_all", False),
        }

        if rule["enabled"]:
            await ctx.enable_components(**params)
        else:
            await ctx.disable_components(**params)

    return diagnostics
