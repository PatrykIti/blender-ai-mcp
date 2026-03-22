# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Public surface contract metadata for FastMCP capability entries."""

from __future__ import annotations

from dataclasses import dataclass

from server.adapters.mcp.platform.naming_rules import (
    AUDIENCE_LEGACY,
    AUDIENCE_LLM_GUIDED,
    get_public_tool_name,
)


@dataclass(frozen=True)
class CapabilityPublicContract:
    """One public contract line for a capability surface."""

    contract_line: str
    audience: str
    version: str
    tool_name_map: tuple[tuple[str, str], ...]


def build_capability_public_contracts(
    capability_id: str,
    tool_names: tuple[str, ...],
) -> tuple[CapabilityPublicContract, ...]:
    """Build the initial public contract metadata for a capability."""

    legacy_contract = CapabilityPublicContract(
        contract_line=f"{capability_id}.legacy.v1",
        audience=AUDIENCE_LEGACY,
        version="1",
        tool_name_map=tuple(
            (tool_name, get_public_tool_name(tool_name, AUDIENCE_LEGACY))
            for tool_name in tool_names
        ),
    )
    llm_contract = CapabilityPublicContract(
        contract_line=f"{capability_id}.llm_guided.v1",
        audience=AUDIENCE_LLM_GUIDED,
        version="1",
        tool_name_map=tuple(
            (tool_name, get_public_tool_name(tool_name, AUDIENCE_LLM_GUIDED))
            for tool_name in tool_names
        ),
    )
    return (legacy_contract, llm_contract)


def get_public_to_internal_tool_map(
    manifest_entries,
    *,
    audience: str | None = None,
) -> dict[str, str]:
    """Build a public-name to internal-name mapping from manifest contracts."""

    mapping: dict[str, str] = {}
    for entry in manifest_entries:
        for contract in entry.public_contracts:
            if audience is not None and contract.audience != audience:
                continue
            for internal_name, public_name in contract.tool_name_map:
                mapping[public_name] = internal_name
    return mapping


def resolve_internal_tool_name(
    manifest_entries,
    tool_name: str,
    *,
    audience: str | None = None,
) -> str:
    """Resolve a public alias back to the canonical internal tool name."""

    return get_public_to_internal_tool_map(
        manifest_entries,
        audience=audience,
    ).get(tool_name, tool_name)
