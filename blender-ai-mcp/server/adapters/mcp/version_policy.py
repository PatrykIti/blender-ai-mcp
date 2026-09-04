# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Version policy and surface matrix for TASK-091."""

from __future__ import annotations

from dataclasses import dataclass

from server.adapters.mcp.platform.naming_rules import AUDIENCE_LEGACY, AUDIENCE_LLM_GUIDED

CONTRACT_LINE_LEGACY_V1 = "legacy-v1"
CONTRACT_LINE_LLM_GUIDED_V1 = "llm-guided-v1"
CONTRACT_LINE_LLM_GUIDED_V2 = "llm-guided-v2"


@dataclass(frozen=True)
class ContractLineSpec:
    """One public contract line and its optional version-filter policy."""

    contract_line: str
    audience: str
    version: str
    version_gte: str | None = None
    version_lt: str | None = None
    include_unversioned: bool = True


CONTRACT_LINE_SPECS: dict[str, ContractLineSpec] = {
    CONTRACT_LINE_LEGACY_V1: ContractLineSpec(
        contract_line=CONTRACT_LINE_LEGACY_V1,
        audience=AUDIENCE_LEGACY,
        version="1",
        version_lt="2",
        include_unversioned=True,
    ),
    CONTRACT_LINE_LLM_GUIDED_V1: ContractLineSpec(
        contract_line=CONTRACT_LINE_LLM_GUIDED_V1,
        audience=AUDIENCE_LLM_GUIDED,
        version="1",
        version_lt="2",
        include_unversioned=True,
    ),
    CONTRACT_LINE_LLM_GUIDED_V2: ContractLineSpec(
        contract_line=CONTRACT_LINE_LLM_GUIDED_V2,
        audience=AUDIENCE_LLM_GUIDED,
        version="2",
        version_gte="2",
        version_lt="3",
        include_unversioned=True,
    ),
}


SURFACE_DEFAULT_CONTRACT_LINES: dict[str, str] = {
    "legacy-manual": CONTRACT_LINE_LEGACY_V1,
    "legacy-flat": CONTRACT_LINE_LEGACY_V1,
    "llm-guided": CONTRACT_LINE_LLM_GUIDED_V2,
    "internal-debug": CONTRACT_LINE_LLM_GUIDED_V2,
    "code-mode-pilot": CONTRACT_LINE_LLM_GUIDED_V2,
}


SURFACE_ALLOWED_CONTRACT_LINES: dict[str, tuple[str, ...]] = {
    "legacy-manual": (CONTRACT_LINE_LEGACY_V1,),
    "legacy-flat": (CONTRACT_LINE_LEGACY_V1,),
    "llm-guided": (CONTRACT_LINE_LLM_GUIDED_V1, CONTRACT_LINE_LLM_GUIDED_V2),
    "internal-debug": (
        CONTRACT_LINE_LEGACY_V1,
        CONTRACT_LINE_LLM_GUIDED_V1,
        CONTRACT_LINE_LLM_GUIDED_V2,
    ),
    "code-mode-pilot": (
        CONTRACT_LINE_LEGACY_V1,
        CONTRACT_LINE_LLM_GUIDED_V1,
        CONTRACT_LINE_LLM_GUIDED_V2,
    ),
}


VERSIONED_TOOL_VERSIONS: dict[str, tuple[str, ...]] = {
    "scene_context": ("1", "2"),
    "scene_inspect": ("1", "2"),
    "workflow_catalog": ("1", "2"),
}


def get_contract_line_spec(contract_line: str) -> ContractLineSpec:
    """Return the contract-line spec or fail loudly."""

    try:
        return CONTRACT_LINE_SPECS[contract_line]
    except KeyError as exc:
        known = ", ".join(sorted(CONTRACT_LINE_SPECS))
        raise ValueError(f"Unknown contract line '{contract_line}'. Expected one of: {known}") from exc


def get_default_contract_line(surface_profile: str) -> str:
    """Return the default contract line for one surface profile."""

    try:
        return SURFACE_DEFAULT_CONTRACT_LINES[surface_profile]
    except KeyError as exc:
        known = ", ".join(sorted(SURFACE_DEFAULT_CONTRACT_LINES))
        raise ValueError(
            f"Unknown surface profile '{surface_profile}' for contract-line selection. Expected one of: {known}"
        ) from exc


def resolve_contract_line(surface_profile: str, override: str | None = None) -> str:
    """Resolve the active contract line for one surface profile."""

    selected = override or get_default_contract_line(surface_profile)
    allowed = SURFACE_ALLOWED_CONTRACT_LINES.get(surface_profile, ())
    if selected not in allowed:
        allowed_str = ", ".join(allowed)
        raise ValueError(
            f"Contract line '{selected}' is not allowed for surface profile '{surface_profile}'. "
            f"Expected one of: {allowed_str}"
        )
    return selected


def get_versioned_tool_versions(tool_name: str) -> tuple[str, ...]:
    """Return the explicit component versions for tools that need coexistence."""

    return VERSIONED_TOOL_VERSIONS.get(tool_name, ())
