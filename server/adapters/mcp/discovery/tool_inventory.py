# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Platform-owned discovery inventory for TASK-084."""

from __future__ import annotations

from dataclasses import dataclass

from server.adapters.mcp.platform.capability_manifest import (
    CapabilityManifestEntry,
    get_capability_manifest,
)
from server.adapters.mcp.platform.naming_rules import AUDIENCE_LLM_GUIDED
from server.adapters.mcp.platform.public_contracts import get_public_contract
from server.adapters.mcp.version_policy import CONTRACT_LINE_LLM_GUIDED_V2
from server.router.infrastructure.metadata_loader import MetadataLoader, ToolMetadata

from .taxonomy import normalize_discovery_category


@dataclass(frozen=True)
class DiscoveryEntry:
    """One canonical public discovery entry."""

    internal_name: str
    public_name: str
    capability_id: str
    category: str
    provider_group: str
    tags: tuple[str, ...]
    aliases: tuple[str, ...]
    pinned: bool
    hidden_from_search: bool
    metadata: ToolMetadata | None = None


def _resolve_public_contract(
    entry: CapabilityManifestEntry,
    audience: str,
    contract_line: str | None,
) -> tuple[tuple[str, str], ...]:
    return get_public_contract(
        entry,
        contract_line=contract_line,
        audience=audience,
    ).tool_name_map


def _build_aliases(
    entry: CapabilityManifestEntry,
    internal_name: str,
    public_name: str,
) -> tuple[str, ...]:
    aliases: set[str] = set()
    if internal_name != public_name:
        aliases.add(internal_name)

    for contract in entry.public_contracts:
        for contract_internal, contract_public in contract.tool_name_map:
            if contract_internal == internal_name and contract_public != public_name:
                aliases.add(contract_public)

    return tuple(sorted(aliases))


def build_discovery_inventory(
    *,
    audience: str = AUDIENCE_LLM_GUIDED,
    contract_line: str | None = CONTRACT_LINE_LLM_GUIDED_V2,
    metadata_loader: MetadataLoader | None = None,
) -> tuple[DiscoveryEntry, ...]:
    """Build the canonical discovery inventory for one public audience."""

    manifest = get_capability_manifest()
    loader = metadata_loader or MetadataLoader()

    entries: list[DiscoveryEntry] = []
    seen_public_names: set[str] = set()

    for manifest_entry in manifest:
        tool_name_map = _resolve_public_contract(manifest_entry, audience, contract_line)
        if not tool_name_map:
            continue

        category = normalize_discovery_category(manifest_entry.discovery_category)
        for internal_name, public_name in tool_name_map:
            if public_name in seen_public_names:
                raise ValueError(f"Duplicate public discovery name '{public_name}'")
            seen_public_names.add(public_name)

            entries.append(
                DiscoveryEntry(
                    internal_name=internal_name,
                    public_name=public_name,
                    capability_id=manifest_entry.capability_id,
                    category=category,
                    provider_group=manifest_entry.provider_group,
                    tags=tuple(sorted(set(manifest_entry.tags))),
                    aliases=_build_aliases(manifest_entry, internal_name, public_name),
                    pinned=internal_name in manifest_entry.pinned_tools,
                    hidden_from_search=internal_name in manifest_entry.hidden_from_search_tools,
                    metadata=loader.get_tool(internal_name),
                )
            )

    return tuple(entries)


def build_discovery_entry_map(
    *,
    audience: str = AUDIENCE_LLM_GUIDED,
    contract_line: str | None = CONTRACT_LINE_LLM_GUIDED_V2,
    metadata_loader: MetadataLoader | None = None,
) -> dict[str, DiscoveryEntry]:
    """Return discovery entries keyed by public tool name."""

    return {
        entry.public_name: entry
        for entry in build_discovery_inventory(
            audience=audience,
            contract_line=contract_line,
            metadata_loader=metadata_loader,
        )
    }


def get_pinned_public_tools(
    *,
    audience: str = AUDIENCE_LLM_GUIDED,
    contract_line: str | None = CONTRACT_LINE_LLM_GUIDED_V2,
    metadata_loader: MetadataLoader | None = None,
) -> tuple[str, ...]:
    """Return the pinned public tools for an audience."""

    return tuple(
        entry.public_name
        for entry in build_discovery_inventory(
            audience=audience,
            contract_line=contract_line,
            metadata_loader=metadata_loader,
        )
        if entry.pinned and not entry.hidden_from_search
    )
