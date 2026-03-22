# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Client profile presets for FastMCP guided-mode behavior."""

from __future__ import annotations

from dataclasses import dataclass

from server.adapters.mcp.session_phase import SessionPhase


@dataclass(frozen=True)
class ClientProfilePreset:
    """One bootstrap-time client profile preset."""

    name: str
    guided_mode: bool
    default_phase: SessionPhase
    description: str
    entry_capability_ids: tuple[str, ...]
    search_enabled_by_default: bool = False


CLIENT_PROFILE_PRESETS: dict[str, ClientProfilePreset] = {
    "legacy-flat": ClientProfilePreset(
        name="legacy-flat",
        guided_mode=False,
        default_phase=SessionPhase.BOOTSTRAP,
        description="Compatibility surface exposing the broad legacy tool line.",
        entry_capability_ids=(),
        search_enabled_by_default=False,
    ),
    "llm-guided": ClientProfilePreset(
        name="llm-guided",
        guided_mode=True,
        default_phase=SessionPhase.BOOTSTRAP,
        description="Guided surface starting from small entry capabilities and coarse session phases.",
        entry_capability_ids=("router", "workflow_catalog"),
        search_enabled_by_default=False,
    ),
    "internal-debug": ClientProfilePreset(
        name="internal-debug",
        guided_mode=False,
        default_phase=SessionPhase.BOOTSTRAP,
        description="Debug-oriented surface with broader provider access for maintainers.",
        entry_capability_ids=(),
        search_enabled_by_default=False,
    ),
    "code-mode-pilot": ClientProfilePreset(
        name="code-mode-pilot",
        guided_mode=False,
        default_phase=SessionPhase.BOOTSTRAP,
        description="Experimental code-mode surface; not part of guided visibility rollout.",
        entry_capability_ids=(),
        search_enabled_by_default=False,
    ),
}


def get_client_profile_preset(name: str) -> ClientProfilePreset:
    """Return the configured client profile preset."""

    try:
        return CLIENT_PROFILE_PRESETS[name]
    except KeyError as exc:
        known = ", ".join(sorted(CLIENT_PROFILE_PRESETS))
        raise ValueError(f"Unknown client profile preset '{name}'. Expected one of: {known}") from exc


def list_client_profile_presets() -> tuple[ClientProfilePreset, ...]:
    """Return all known client profile presets."""

    return tuple(CLIENT_PROFILE_PRESETS[name] for name in sorted(CLIENT_PROFILE_PRESETS))
