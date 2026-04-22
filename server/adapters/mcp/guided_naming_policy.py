# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Deterministic naming policy for guided object registration/build paths."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from server.adapters.mcp.contracts.guided_naming import GuidedNamingDecisionContract
from server.infrastructure.config import get_config

GuidedNamingPolicyMode = Literal["warn", "block_opaque_role_sensitive"]
GuidedNamingDomain = Literal["generic", "creature", "building"]

_PLACEHOLDER_NAME_HINTS: tuple[str, ...] = (
    "object",
    "mesh",
    "part",
    "piece",
    "thing",
    "item",
    "temp",
    "tmp",
    "test",
    "cube",
    "sphere",
    "cone",
    "cylinder",
    "plane",
    "torus",
    "monkey",
)

_WEAK_FORE_HIND_SIDE_TOKEN_HINTS: tuple[str, ...] = (
    "fore",
    "hind",
    "front",
    "rear",
    "back",
    "l",
    "r",
    "left",
    "right",
)


@dataclass(frozen=True)
class _RoleNamingSpec:
    role: str
    canonical_pattern: str
    suggested_names: tuple[str, ...]
    strong_hints: tuple[str, ...]
    weak_hints: tuple[str, ...] = ()


_ROLE_NAMING_SPECS: dict[str, dict[str, _RoleNamingSpec]] = {
    "generic": {
        "anchor_core": _RoleNamingSpec(
            role="anchor_core",
            canonical_pattern="AnchorCore",
            suggested_names=("AnchorCore",),
            strong_hints=("anchor", "core", "root", "base"),
        ),
        "primary_mass": _RoleNamingSpec(
            role="primary_mass",
            canonical_pattern="PrimaryMass",
            suggested_names=("PrimaryMass",),
            strong_hints=("primary", "mass", "core", "main"),
        ),
        "secondary_mass": _RoleNamingSpec(
            role="secondary_mass",
            canonical_pattern="SecondaryMass",
            suggested_names=("SecondaryMass",),
            strong_hints=("secondary", "mass", "submass"),
        ),
        "support_part": _RoleNamingSpec(
            role="support_part",
            canonical_pattern="SupportPart_A",
            suggested_names=("SupportPart_A", "SupportPart_B"),
            strong_hints=("support", "brace", "strut", "leg"),
        ),
        "detail_part": _RoleNamingSpec(
            role="detail_part",
            canonical_pattern="Detail_A",
            suggested_names=("Detail_A",),
            strong_hints=("detail", "trim", "accent"),
        ),
    },
    "creature": {
        "body_core": _RoleNamingSpec(
            role="body_core",
            canonical_pattern="Body",
            suggested_names=("Body",),
            strong_hints=("body", "torso", "trunk"),
        ),
        "head_mass": _RoleNamingSpec(
            role="head_mass",
            canonical_pattern="Head",
            suggested_names=("Head",),
            strong_hints=("head", "skull"),
        ),
        "tail_mass": _RoleNamingSpec(
            role="tail_mass",
            canonical_pattern="Tail",
            suggested_names=("Tail",),
            strong_hints=("tail",),
        ),
        "snout_mass": _RoleNamingSpec(
            role="snout_mass",
            canonical_pattern="Snout",
            suggested_names=("Snout",),
            strong_hints=("snout", "muzzle"),
        ),
        "ear_pair": _RoleNamingSpec(
            role="ear_pair",
            canonical_pattern="EarPair or Ear_L/Ear_R",
            suggested_names=("EarPair", "Ear_L", "Ear_R"),
            strong_hints=("ear", "ears"),
        ),
        "foreleg_pair": _RoleNamingSpec(
            role="foreleg_pair",
            canonical_pattern="ForeLegPair or ForeLeg_L/ForeLeg_R",
            suggested_names=("ForeLegPair", "ForeLeg_L", "ForeLeg_R"),
            strong_hints=("foreleg", "forelegs", "forelimb", "forelimbs", "frontleg", "frontlegs"),
            weak_hints=("forel", "forer", "frontl", "frontr"),
        ),
        "hindleg_pair": _RoleNamingSpec(
            role="hindleg_pair",
            canonical_pattern="HindLegPair or HindLeg_L/HindLeg_R",
            suggested_names=("HindLegPair", "HindLeg_L", "HindLeg_R"),
            strong_hints=("hindleg", "hindlegs", "hindlimb", "hindlimbs", "rearleg", "rearlegs", "backleg"),
            weak_hints=("hindl", "hindr", "rearl", "rearr", "backl", "backr"),
        ),
    },
    "building": {
        "footprint_mass": _RoleNamingSpec(
            role="footprint_mass",
            canonical_pattern="Footprint",
            suggested_names=("Footprint",),
            strong_hints=("footprint", "baseplan", "groundplan"),
        ),
        "main_volume": _RoleNamingSpec(
            role="main_volume",
            canonical_pattern="MainVolume",
            suggested_names=("MainVolume",),
            strong_hints=("mainvolume", "volume", "tower", "core"),
        ),
        "roof_mass": _RoleNamingSpec(
            role="roof_mass",
            canonical_pattern="Roof",
            suggested_names=("Roof",),
            strong_hints=("roof", "gable", "top"),
        ),
        "facade_opening": _RoleNamingSpec(
            role="facade_opening",
            canonical_pattern="WindowOpening_A or DoorOpening_A",
            suggested_names=("WindowOpening_A", "DoorOpening_A"),
            strong_hints=("window", "windows", "door", "opening", "windowcut", "windowcuts", "cutout"),
        ),
        "support_element": _RoleNamingSpec(
            role="support_element",
            canonical_pattern="Support_A",
            suggested_names=("Support_A", "Support_B"),
            strong_hints=("support", "buttress", "buttresses", "brace", "braces", "pillar", "column", "strut"),
        ),
        "detail_element": _RoleNamingSpec(
            role="detail_element",
            canonical_pattern="Detail_A",
            suggested_names=("Detail_A",),
            strong_hints=("detail", "trim", "ornament", "ledge", "accent"),
        ),
    },
}


def get_guided_naming_policy_mode() -> GuidedNamingPolicyMode:
    """Return the configured guided naming policy mode."""

    return get_config().MCP_GUIDED_NAMING_POLICY_MODE  # type: ignore[return-value]


def _normalize_name(object_name: str) -> str:
    return re.sub(r"\s+", "", object_name.strip().lower())


def _name_tokens(object_name: str) -> tuple[str, ...]:
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", object_name.strip())
    return tuple(token for token in re.split(r"[^a-zA-Z0-9]+", normalized.lower()) if token)


def _looks_like_placeholder_name(object_name: str) -> bool:
    tokens = _name_tokens(object_name)
    normalized = _normalize_name(object_name)
    if not normalized:
        return True
    if re.fullmatch(r"(object|mesh|part|piece|item|thing|temp|tmp|test)[0-9_]*", normalized):
        return True
    if re.fullmatch(r"(cube|sphere|cone|cylinder|plane|torus|monkey)[0-9_]*", normalized):
        return True
    return any(token in _PLACEHOLDER_NAME_HINTS for token in tokens)


def _matches_strong_semantic_name(object_name: str, spec: _RoleNamingSpec) -> bool:
    tokens = _name_tokens(object_name)
    joined = "".join(tokens)
    for hint in spec.strong_hints:
        normalized_hint = _normalize_name(hint)
        if not normalized_hint:
            continue
        if normalized_hint in tokens or normalized_hint == joined:
            return True
    return False


def _matches_weak_semantic_name(object_name: str, spec: _RoleNamingSpec) -> bool:
    normalized = _normalize_name(object_name)
    tokens = _name_tokens(object_name)
    if any(hint in normalized for hint in spec.weak_hints):
        return True
    if spec.role in {"foreleg_pair", "hindleg_pair"}:
        directional = any(token in {"fore", "hind", "front", "rear", "back"} for token in tokens)
        side = any(token in {"l", "r", "left", "right"} for token in tokens)
        return directional and side and not _matches_strong_semantic_name(object_name, spec)
    return False


def _get_role_naming_spec(domain_profile: GuidedNamingDomain, role: str) -> _RoleNamingSpec | None:
    return _ROLE_NAMING_SPECS.get(domain_profile, {}).get(role)


def evaluate_guided_object_name(
    *,
    object_name: str,
    role: str,
    domain_profile: GuidedNamingDomain,
    current_step: str | None = None,
    mode: GuidedNamingPolicyMode | None = None,
) -> GuidedNamingDecisionContract:
    """Evaluate one role-sensitive object name against the guided naming policy."""

    effective_mode = mode or get_guided_naming_policy_mode()
    normalized_name = object_name.strip()
    spec = _get_role_naming_spec(domain_profile, role)
    if spec is None:
        return GuidedNamingDecisionContract(
            status="allowed",
            role=role,
            domain_profile=domain_profile,
            current_step=current_step,
        )

    if _looks_like_placeholder_name(normalized_name):
        return GuidedNamingDecisionContract(
            status="blocked",
            reason_code="placeholder_name",
            message=(
                f"Guided naming blocked object name '{normalized_name}' for role '{role}'. "
                f"Use a semantic name matching {spec.canonical_pattern}; for example: {', '.join(spec.suggested_names)}."
            ),
            suggested_names=list(spec.suggested_names),
            canonical_pattern=spec.canonical_pattern,
            role=role,
            domain_profile=domain_profile,
            current_step=current_step,
        )

    if _matches_strong_semantic_name(normalized_name, spec):
        return GuidedNamingDecisionContract(
            status="allowed",
            reason_code="semantic_name",
            suggested_names=list(spec.suggested_names),
            canonical_pattern=spec.canonical_pattern,
            role=role,
            domain_profile=domain_profile,
            current_step=current_step,
        )

    if _matches_weak_semantic_name(normalized_name, spec):
        status: Literal["warning", "blocked"] = (
            "blocked" if effective_mode == "block_opaque_role_sensitive" else "warning"
        )
        reason_code = "opaque_abbreviation" if status == "blocked" else "weak_abbreviation"
        message_prefix = "blocked" if status == "blocked" else "warning"
        return GuidedNamingDecisionContract(
            status=status,
            reason_code=reason_code,
            message=(
                f"Guided naming {message_prefix} for object '{normalized_name}' with role '{role}'. "
                f"Prefer a semantic name matching {spec.canonical_pattern}; for example: {', '.join(spec.suggested_names)}."
            ),
            suggested_names=list(spec.suggested_names),
            canonical_pattern=spec.canonical_pattern,
            role=role,
            domain_profile=domain_profile,
            current_step=current_step,
        )

    if effective_mode == "block_opaque_role_sensitive":
        return GuidedNamingDecisionContract(
            status="blocked",
            reason_code="no_role_signal",
            message=(
                f"Guided naming blocked object name '{normalized_name}' for role '{role}'. "
                f"Use a semantic name matching {spec.canonical_pattern}; for example: {', '.join(spec.suggested_names)}."
            ),
            suggested_names=list(spec.suggested_names),
            canonical_pattern=spec.canonical_pattern,
            role=role,
            domain_profile=domain_profile,
            current_step=current_step,
        )

    return GuidedNamingDecisionContract(
        status="warning",
        reason_code="no_role_signal",
        message=(
            f"Guided naming warning for object '{normalized_name}' with role '{role}'. "
            f"Prefer a semantic name matching {spec.canonical_pattern}; for example: {', '.join(spec.suggested_names)}."
        ),
        suggested_names=list(spec.suggested_names),
        canonical_pattern=spec.canonical_pattern,
        role=role,
        domain_profile=domain_profile,
        current_step=current_step,
    )
