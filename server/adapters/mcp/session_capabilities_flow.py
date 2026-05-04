# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Shared guided-flow helpers used by session capability slices."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Literal

from server.adapters.mcp.contracts.guided_flow import (
    GuidedFlowCheckContract,
    GuidedFlowFamilyLiteral,
    GuidedFlowStateContract,
    GuidedFlowStepLiteral,
    GuidedTargetScopeContract,
)
from server.adapters.mcp.session_capabilities_state import SessionCapabilityState
from server.adapters.mcp.transforms.visibility_policy import get_guided_overlay_family_order

_CREATURE_GOAL_HINTS: tuple[str, ...] = (
    "animal",
    "bird",
    "creature",
    "ears",
    "fox",
    "owl",
    "paw",
    "rabbit",
    "snout",
    "squirrel",
    "tail",
)
_BUILDING_GOAL_HINTS: tuple[str, ...] = (
    "architecture",
    "archway",
    "balcony",
    "building",
    "castle",
    "facade",
    "house",
    "roof",
    "temple",
    "tower",
    "wall",
    "window",
)
_SPATIAL_CONTEXT_CHECKS: tuple[tuple[str, str, str], ...] = (
    (
        "scope_graph",
        "scene_scope_graph",
        "Establish the structural anchor and active object scope before broad edits.",
    ),
    (
        "relation_graph",
        "scene_relation_graph",
        "Establish the current pair relations before attachment/support decisions.",
    ),
    (
        "view_diagnostics",
        "scene_view_diagnostics",
        "Confirm framing, coverage, and occlusion before trusting the current working view.",
    ),
)
_SPATIAL_CONTEXT_TOOL_NAMES = {tool_name for _check_id, tool_name, _reason in _SPATIAL_CONTEXT_CHECKS}
_GUIDED_SCOPE_BINDING_TOOL_NAME = "scene_scope_graph"
_GUIDED_HELPER_OBJECT_HINTS: tuple[str, ...] = ("camera", "light", "lamp", "sun")
_GUIDED_BOOTSTRAP_PLACEHOLDER_OBJECT_HINTS: tuple[str, ...] = (
    "cube",
    "sphere",
    "cone",
    "cylinder",
    "plane",
    "torus",
    "monkey",
)
_GUIDED_BOOTSTRAP_PLACEHOLDER_COLLECTION_NAMES: set[str] = {"collection", "scene collection"}
_SPATIAL_REARM_ALLOWED_STEPS: set[GuidedFlowStepLiteral] = {
    "create_primary_masses",
    "place_secondary_parts",
    "checkpoint_iterate",
    "inspect_validate",
    "finish_or_stop",
}
_SPATIAL_REARM_ALWAYS_BLOCK_REASONS: set[str] = {"scene_clean_scene"}
_SPATIAL_STATE_DIRTY_TOOL_NAMES: set[str] = {
    "scene_clean_scene",
    "scene_duplicate_object",
    "scene_rename_object",
    "modeling_create_primitive",
    "modeling_transform_object",
    "modeling_join_objects",
    "modeling_separate_object",
    "macro_attach_part_to_surface",
    "macro_align_part_with_contact",
    "macro_place_symmetry_pair",
    "macro_place_supported_pair",
    "macro_cleanup_part_intersections",
}
_SPATIAL_STATE_DIRTY_FAMILIES: set[GuidedFlowFamilyLiteral] = {
    "primary_masses",
    "secondary_parts",
    "attachment_alignment",
}
_GOAL_TIME_UNAVAILABLE_GATE_EVIDENCE_KINDS: frozenset[str] = frozenset(
    {
        "reference_understanding",
        "silhouette_analysis",
        "part_segmentation",
        "classification_scores",
    }
)
_GUIDED_FLOW_ITERATION_TOOLS = {
    "reference_compare_stage_checkpoint",
    "reference_iterate_stage_checkpoint",
}
_GUIDED_FLOW_STOPPED_STEPS = {"inspect_validate", "finish_or_stop"}
_GUIDED_ROLE_SUMMARY_PLAN: dict[str, dict[GuidedFlowStepLiteral, dict[str, list[str]]]] = {
    "generic": {
        "understand_goal": {"allowed_roles": [], "required_role_groups": []},
        "bootstrap_primary_workset": {
            "allowed_roles": ["anchor_core", "primary_mass"],
            "required_role_groups": ["primary_masses"],
        },
        "establish_spatial_context": {"allowed_roles": [], "required_role_groups": ["spatial_context"]},
        "establish_reference_context": {"allowed_roles": [], "required_role_groups": ["reference_context"]},
        "create_primary_masses": {
            "allowed_roles": ["anchor_core", "primary_mass"],
            "required_role_groups": ["primary_masses"],
        },
        "place_secondary_parts": {
            "allowed_roles": ["secondary_mass", "support_part"],
            "required_role_groups": ["secondary_parts"],
        },
        "checkpoint_iterate": {"allowed_roles": [], "required_role_groups": ["checkpoint_iterate"]},
        "inspect_validate": {"allowed_roles": [], "required_role_groups": ["inspect_validate"]},
        "finish_or_stop": {"allowed_roles": ["detail_part"], "required_role_groups": ["finish"]},
    },
    "creature": {
        "understand_goal": {"allowed_roles": [], "required_role_groups": []},
        "bootstrap_primary_workset": {
            "allowed_roles": ["body_core", "head_mass", "tail_mass"],
            "required_role_groups": ["primary_masses"],
        },
        "establish_spatial_context": {"allowed_roles": [], "required_role_groups": ["spatial_context"]},
        "establish_reference_context": {"allowed_roles": [], "required_role_groups": ["reference_context"]},
        "create_primary_masses": {
            "allowed_roles": ["body_core", "head_mass", "tail_mass"],
            "required_role_groups": ["primary_masses"],
        },
        "place_secondary_parts": {
            "allowed_roles": ["snout_mass", "ear_pair", "foreleg_pair", "hindleg_pair"],
            "required_role_groups": ["secondary_parts"],
        },
        "checkpoint_iterate": {"allowed_roles": [], "required_role_groups": ["checkpoint_iterate"]},
        "inspect_validate": {"allowed_roles": [], "required_role_groups": ["inspect_validate"]},
        "finish_or_stop": {"allowed_roles": [], "required_role_groups": ["finish"]},
    },
    "building": {
        "understand_goal": {"allowed_roles": [], "required_role_groups": []},
        "bootstrap_primary_workset": {
            "allowed_roles": ["footprint_mass", "main_volume", "roof_mass"],
            "required_role_groups": ["primary_masses"],
        },
        "establish_spatial_context": {"allowed_roles": [], "required_role_groups": ["spatial_context"]},
        "establish_reference_context": {"allowed_roles": [], "required_role_groups": ["reference_context"]},
        "create_primary_masses": {
            "allowed_roles": ["footprint_mass", "main_volume", "roof_mass"],
            "required_role_groups": ["primary_masses"],
        },
        "place_secondary_parts": {
            "allowed_roles": ["facade_opening", "support_element", "detail_element"],
            "required_role_groups": ["secondary_parts"],
        },
        "checkpoint_iterate": {"allowed_roles": [], "required_role_groups": ["checkpoint_iterate"]},
        "inspect_validate": {"allowed_roles": [], "required_role_groups": ["inspect_validate"]},
        "finish_or_stop": {"allowed_roles": [], "required_role_groups": ["finish"]},
    },
}
_GUIDED_ROLE_GROUP_BY_ROLE: dict[str, dict[str, str]] = {
    "generic": {
        "anchor_core": "primary_masses",
        "primary_mass": "primary_masses",
        "secondary_mass": "secondary_parts",
        "support_part": "secondary_parts",
        "detail_part": "finish",
    },
    "creature": {
        "body_core": "primary_masses",
        "head_mass": "primary_masses",
        "tail_mass": "primary_masses",
        "snout_mass": "secondary_parts",
        "ear_pair": "secondary_parts",
        "foreleg_pair": "secondary_parts",
        "hindleg_pair": "secondary_parts",
    },
    "building": {
        "footprint_mass": "primary_masses",
        "main_volume": "primary_masses",
        "roof_mass": "primary_masses",
        "facade_opening": "secondary_parts",
        "support_element": "secondary_parts",
        "detail_element": "secondary_parts",
    },
}
_GUIDED_ROLE_CARDINALITY: dict[str, dict[str, int]] = {
    "generic": {},
    "creature": {
        "ear_pair": 2,
        "foreleg_pair": 2,
        "hindleg_pair": 2,
    },
    "building": {},
}
_GUIDED_PRIMARY_REQUIRED_ROLES: dict[str, tuple[str, ...]] = {
    "generic": ("anchor_core", "primary_mass"),
    "creature": ("body_core", "head_mass"),
    "building": ("footprint_mass", "main_volume"),
}
_GUIDED_SECONDARY_REQUIRED_ROLES: dict[str, tuple[str, ...]] = {
    "generic": ("secondary_mass", "support_part"),
    "creature": ("ear_pair", "foreleg_pair", "hindleg_pair"),
    "building": ("facade_opening", "support_element"),
}


def describe_guided_flow_feedback(
    before: SessionCapabilityState | None,
    after: SessionCapabilityState | None,
) -> str | None:
    """Return one concise client-facing note when guided flow state changed materially."""

    after_flow = after.guided_flow_state if after is not None else None
    if not isinstance(after_flow, dict):
        return None

    before_flow = before.guided_flow_state if before is not None else None
    before_step = str((before_flow or {}).get("current_step") or "").strip()
    after_step = str(after_flow.get("current_step") or "").strip()
    before_refresh = bool((before_flow or {}).get("spatial_refresh_required"))
    after_refresh = bool(after_flow.get("spatial_refresh_required"))
    before_actions = [str(item) for item in (before_flow or {}).get("next_actions") or [] if str(item).strip()]
    after_actions = [str(item) for item in after_flow.get("next_actions") or [] if str(item).strip()]
    before_families = [str(item) for item in (before_flow or {}).get("allowed_families") or [] if str(item).strip()]
    after_families = [str(item) for item in after_flow.get("allowed_families") or [] if str(item).strip()]
    before_required = [
        str(item.get("tool_name"))
        for item in (before_flow or {}).get("required_checks") or []
        if isinstance(item, dict)
        and str(item.get("status") or "").strip() != "completed"
        and str(item.get("tool_name") or "").strip()
    ]
    after_required = [
        str(item.get("tool_name"))
        for item in after_flow.get("required_checks") or []
        if isinstance(item, dict)
        and str(item.get("status") or "").strip() != "completed"
        and str(item.get("tool_name") or "").strip()
    ]
    scope_names = [
        str(name)
        for name in ((after_flow.get("active_target_scope") or {}).get("object_names") or [])
        if str(name).strip()
    ]

    if (
        before_step == after_step
        and before_refresh == after_refresh
        and before_actions == after_actions
        and before_families == after_families
        and before_required == after_required
    ):
        return None

    parts: list[str] = ["Guided flow updated."]
    if after_step and after_step != before_step:
        parts.append(f"Current step: {after_step}.")
    if after_refresh:
        parts.append("Spatial context refresh required before continuing build tools.")
        if after_required:
            parts.append(f"Run: {', '.join(after_required)}.")
        if scope_names:
            parts.append(f"Active scope: {', '.join(scope_names)}.")
    elif before_refresh and not after_refresh:
        parts.append("Spatial context refresh cleared.")
    if after_actions and after_actions != before_actions:
        parts.append(f"Next action: {', '.join(after_actions)}.")
    if after_families and after_families != before_families:
        parts.append(f"Allowed families now: {', '.join(after_families)}.")
    return " ".join(parts)


def _goal_contains_hint(goal: str | None, hint: str) -> bool:
    words = str(goal or "").strip().lower()
    if not words:
        return False
    normalized_hint = re.escape(hint)
    return re.search(rf"(?<![a-z0-9]){normalized_hint}(?![a-z0-9])", words) is not None


def _normalize_scope_names(value: Any) -> list[str]:
    if value is None or not isinstance(value, list):
        return []

    names: list[str] = []
    seen: set[str] = set()
    for raw_name in value:
        name = str(raw_name).strip()
        key = name.lower()
        if not name or key in seen:
            continue
        seen.add(key)
        names.append(name)
    return sorted(names, key=str.lower)


def _normalize_guided_target_scope(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None

    try:
        if isinstance(value, dict):
            value = {
                key: value.get(key)
                for key in ("scope_kind", "primary_target", "object_names", "object_count", "collection_name")
                if key in value
            }
        contract = GuidedTargetScopeContract.model_validate(value)
    except Exception:
        return None

    object_names = _normalize_scope_names(contract.object_names)
    primary_target = str(contract.primary_target or "").strip() or None
    collection_name = str(contract.collection_name or "").strip() or None

    if primary_target and primary_target.lower() not in {name.lower() for name in object_names} and not collection_name:
        object_names = sorted([primary_target, *object_names], key=str.lower)

    scope_kind = contract.scope_kind
    if collection_name and scope_kind == "scene":
        scope_kind = "collection"
    elif object_names and scope_kind == "scene":
        scope_kind = "object_set" if len(object_names) > 1 else "single_object"

    normalized = GuidedTargetScopeContract(
        scope_kind=scope_kind,
        primary_target=primary_target,
        object_names=object_names,
        object_count=len(object_names),
        collection_name=collection_name,
    )
    return normalized.model_dump(mode="json", exclude_none=True)


def _build_guided_target_scope_fingerprint(value: Any) -> str | None:
    normalized = _normalize_guided_target_scope(value)
    if normalized is None:
        return None

    fingerprint_payload = {
        "scope_kind": normalized.get("scope_kind"),
        "primary_target": normalized.get("primary_target"),
        "object_names": list(normalized.get("object_names") or []),
        "collection_name": normalized.get("collection_name"),
    }
    encoded = json.dumps(fingerprint_payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:16]


def _build_active_guided_target_scope_fingerprint(contract: GuidedFlowStateContract) -> str | None:
    if contract.active_target_scope is None:
        return None
    active_scope = contract.active_target_scope.model_dump(mode="json")
    return _build_guided_target_scope_fingerprint(active_scope) or contract.spatial_scope_fingerprint


def _looks_like_guided_helper_object(name: str) -> bool:
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name.strip())
    tokens = [token for token in re.split(r"[^a-zA-Z0-9]+", normalized.lower()) if token]
    return any(token in _GUIDED_HELPER_OBJECT_HINTS for token in tokens)


def _looks_like_guided_bootstrap_placeholder_object(name: str) -> bool:
    normalized = name.strip().lower()
    return normalized in _GUIDED_BOOTSTRAP_PLACEHOLDER_OBJECT_HINTS


def _is_bindable_guided_target_scope(scope: dict[str, Any] | None) -> bool:
    if scope is None:
        return False

    scope_kind = str(scope.get("scope_kind") or "").strip().lower()
    primary_target = str(scope.get("primary_target") or "").strip()
    collection_name = str(scope.get("collection_name") or "").strip()
    object_names = [str(name).strip() for name in scope.get("object_names") or [] if str(name).strip()]

    if scope_kind == "scene":
        return False
    if not primary_target and not object_names and not collection_name:
        return False
    if (
        collection_name
        and collection_name.strip().lower() in _GUIDED_BOOTSTRAP_PLACEHOLDER_COLLECTION_NAMES
        and not any(
            not _looks_like_guided_helper_object(name) and not _looks_like_guided_bootstrap_placeholder_object(name)
            for name in object_names
        )
    ):
        return False
    if not collection_name and object_names:
        return any(not _looks_like_guided_helper_object(name) for name in object_names)
    return True


def _guided_role_cardinality(domain_profile: Literal["generic", "creature", "building"], role: str) -> int:
    return _GUIDED_ROLE_CARDINALITY.get(domain_profile, {}).get(role, 1)


def _guided_role_instance_count(
    *,
    domain_profile: Literal["generic", "creature", "building"],
    role: str,
    object_name: str,
) -> int:
    cardinality = _guided_role_cardinality(domain_profile, role)
    if cardinality <= 1:
        return 1
    normalized = object_name.strip().lower()
    aggregate_tokens = {
        "ear_pair": ("ears", "ear_pair", "earpair"),
        "foreleg_pair": ("forelegs", "fore_legs", "frontlegs", "front_legs", "foreleg_pair", "forelegpair"),
        "hindleg_pair": ("hindlegs", "hind_legs", "backlegs", "back_legs", "hindleg_pair", "hindlegpair"),
    }.get(role, ())
    if any(token in normalized for token in aggregate_tokens):
        return cardinality
    return 1


def _build_required_prompt_bundle(
    *,
    domain_profile: Literal["generic", "creature", "building"],
    current_step: str,
) -> tuple[list[str], list[str]]:
    required_prompts = ["guided_session_start"]
    preferred_prompts = ["workflow_router_first"]

    if domain_profile == "creature":
        required_prompts.append("reference_guided_creature_build")
    elif current_step == "understand_goal":
        preferred_prompts.append("recommended_prompts")

    return required_prompts, preferred_prompts


def _build_required_checks(
    *,
    domain_profile: Literal["generic", "creature", "building"],
    current_step: str,
    force_spatial_context: bool = False,
) -> list[dict[str, Any]]:
    if current_step != "establish_spatial_context" and not force_spatial_context:
        return []

    allowed_check_ids = {"scope_graph", "view_diagnostics"} if domain_profile == "building" else None
    return [
        GuidedFlowCheckContract(
            check_id=check_id,
            tool_name=tool_name,
            reason=reason,
            status="pending",
            priority="high",
        ).model_dump(mode="json")
        for check_id, tool_name, reason in _SPATIAL_CONTEXT_CHECKS
        if allowed_check_ids is None or check_id in allowed_check_ids
    ]


def _build_allowed_families(
    *,
    domain_profile: Literal["generic", "creature", "building"],
    current_step: GuidedFlowStepLiteral,
) -> list[GuidedFlowFamilyLiteral]:
    order = list(get_guided_overlay_family_order(domain_profile))
    known = set(order)
    by_step: dict[GuidedFlowStepLiteral, list[GuidedFlowFamilyLiteral]] = {
        "understand_goal": ["reference_context", "utility"],
        "bootstrap_primary_workset": (
            ["primary_masses", "reference_context"] if domain_profile == "creature" else ["primary_masses"]
        ),
        "establish_spatial_context": (
            ["spatial_context", "reference_context"] if domain_profile == "creature" else ["spatial_context"]
        ),
        "establish_reference_context": ["reference_context"],
        "create_primary_masses": (
            ["primary_masses", "reference_context"] if domain_profile == "creature" else ["primary_masses"]
        ),
        "place_secondary_parts": (
            ["primary_masses", "secondary_parts", "attachment_alignment", "reference_context"]
            if domain_profile == "creature"
            else ["primary_masses", "secondary_parts"]
        ),
        "checkpoint_iterate": (
            ["primary_masses", "secondary_parts", "attachment_alignment", "checkpoint_iterate", "reference_context"]
            if domain_profile == "creature"
            else ["primary_masses", "secondary_parts", "checkpoint_iterate", "reference_context"]
        ),
        "inspect_validate": (
            ["inspect_validate", "spatial_context", "checkpoint_iterate", "attachment_alignment"]
            if domain_profile == "creature"
            else ["inspect_validate", "spatial_context", "checkpoint_iterate"]
        ),
        "finish_or_stop": ["finish", "inspect_validate"],
    }
    allowed = by_step[current_step]
    return [family for family in allowed if family in known]


def _build_role_summary(
    *,
    domain_profile: Literal["generic", "creature", "building"],
    current_step: GuidedFlowStepLiteral,
    part_registry: list[dict[str, Any]] | None = None,
    completed_role_hints: list[str] | None = None,
) -> dict[str, Any]:
    plan = _GUIDED_ROLE_SUMMARY_PLAN[domain_profile][current_step]
    allowed_roles = list(plan["allowed_roles"])
    role_counts: dict[str, int] = {}
    role_objects: dict[str, list[str]] = {}
    for item in part_registry or []:
        if not isinstance(item, dict):
            continue
        role = str(item.get("role") or "").strip()
        object_name = str(item.get("object_name") or "").strip()
        if not role:
            continue
        role_counts[role] = role_counts.get(role, 0) + _guided_role_instance_count(
            domain_profile=domain_profile,
            role=role,
            object_name=object_name,
        )
        if object_name:
            role_objects.setdefault(role, [])
            if object_name not in role_objects[role]:
                role_objects[role].append(object_name)

    for role in completed_role_hints or []:
        normalized_role = str(role).strip()
        if not normalized_role or normalized_role in role_counts:
            continue
        role_counts[normalized_role] = _guided_role_cardinality(domain_profile, normalized_role)

    known_roles = sorted(set(_GUIDED_ROLE_GROUP_BY_ROLE[domain_profile]) | set(role_counts) | set(allowed_roles))
    role_cardinality = {role: _guided_role_cardinality(domain_profile, role) for role in known_roles}
    completed_roles = sorted(
        role for role, count in role_counts.items() if count >= _guided_role_cardinality(domain_profile, role)
    )
    if current_step in {"place_secondary_parts", "checkpoint_iterate"}:
        primary_roles = list(_GUIDED_ROLE_SUMMARY_PLAN[domain_profile]["create_primary_masses"]["allowed_roles"])
        missing_primary_roles = [role for role in primary_roles if role not in completed_roles]
        allowed_roles = [*missing_primary_roles, *allowed_roles]
    if current_step == "checkpoint_iterate":
        secondary_roles = list(_GUIDED_ROLE_SUMMARY_PLAN[domain_profile]["place_secondary_parts"]["allowed_roles"])
        missing_secondary_roles = [role for role in secondary_roles if role not in completed_roles]
        allowed_roles = [*allowed_roles, *missing_secondary_roles]
    allowed_roles = list(dict.fromkeys(role for role in allowed_roles if role not in completed_roles))
    missing_roles = [role for role in allowed_roles if role not in completed_roles]
    return {
        "allowed_roles": allowed_roles,
        "completed_roles": completed_roles,
        "missing_roles": missing_roles,
        "required_role_groups": list(plan["required_role_groups"]),
        "role_counts": {role: min(count, role_cardinality.get(role, 1)) for role, count in sorted(role_counts.items())},
        "role_cardinality": role_cardinality,
        "role_objects": {role: sorted(objects) for role, objects in sorted(role_objects.items())},
    }


def _apply_role_summary(contract: GuidedFlowStateContract, role_summary: dict[str, Any]) -> None:
    contract.allowed_roles = list(role_summary["allowed_roles"])
    contract.completed_roles = list(role_summary["completed_roles"])
    contract.missing_roles = list(role_summary["missing_roles"])
    contract.required_role_groups = list(role_summary["required_role_groups"])
    contract.role_counts = dict(role_summary.get("role_counts") or {})
    contract.role_cardinality = dict(role_summary.get("role_cardinality") or {})
    contract.role_objects = {
        str(role): list(objects) for role, objects in dict(role_summary.get("role_objects") or {}).items()
    }


def _build_spatial_refresh_allowed_families(
    *,
    domain_profile: Literal["generic", "creature", "building"],
    current_step: GuidedFlowStepLiteral,
) -> list[GuidedFlowFamilyLiteral]:
    allowed = _build_allowed_families(
        domain_profile=domain_profile,
        current_step="establish_spatial_context",
    )
    if current_step == "inspect_validate" and "inspect_validate" not in allowed:
        allowed.append("inspect_validate")
    return allowed


def _default_next_actions_for_step(current_step: GuidedFlowStepLiteral) -> list[str]:
    return {
        "understand_goal": ["answer_router_questions"],
        "bootstrap_primary_workset": ["create_primary_workset"],
        "establish_spatial_context": ["run_required_checks"],
        "establish_reference_context": ["attach_reference_images"],
        "create_primary_masses": ["begin_primary_masses"],
        "place_secondary_parts": ["begin_secondary_parts"],
        "checkpoint_iterate": ["run_checkpoint_iterate"],
        "inspect_validate": ["switch_to_inspect_validate"],
        "finish_or_stop": ["stop_or_finalize"],
    }.get(current_step, ["continue_build"])


def _default_step_status_for_step(
    current_step: GuidedFlowStepLiteral,
    *,
    required_checks: list[GuidedFlowCheckContract] | None = None,
) -> Literal["ready", "blocked", "needs_checkpoint", "needs_validation"]:
    if current_step == "establish_spatial_context":
        return "blocked" if required_checks else "ready"
    if current_step == "checkpoint_iterate":
        return "needs_checkpoint"
    if current_step == "inspect_validate":
        return "needs_validation"
    return "ready"


def _flow_state_for_current_step(
    contract: GuidedFlowStateContract,
    *,
    part_registry: list[dict[str, Any]] | None,
) -> None:
    required_prompts, preferred_prompts = _build_required_prompt_bundle(
        domain_profile=contract.domain_profile,
        current_step=contract.current_step,
    )
    contract.required_prompts = required_prompts
    contract.preferred_prompts = preferred_prompts
    contract.allowed_families = _build_allowed_families(
        domain_profile=contract.domain_profile,
        current_step=contract.current_step,
    )
    role_summary = _build_role_summary(
        domain_profile=contract.domain_profile,
        current_step=contract.current_step,
        part_registry=part_registry,
        completed_role_hints=contract.completed_roles,
    )
    _apply_role_summary(contract, role_summary)
    contract.next_actions = _default_next_actions_for_step(contract.current_step)
    contract.step_status = _default_step_status_for_step(contract.current_step)
    contract.required_checks = []


def _should_rearm_spatial_gate(contract: GuidedFlowStateContract, *, force: bool = False) -> bool:
    if force:
        return True
    if not contract.spatial_state_stale:
        return False
    if contract.current_step not in _SPATIAL_REARM_ALLOWED_STEPS:
        return False
    if contract.last_spatial_mutation_reason in _SPATIAL_REARM_ALWAYS_BLOCK_REASONS:
        return True
    if contract.last_spatial_mutation_reason in {"scene_rename_object", "scene_duplicate_object"}:
        return True
    if (
        contract.current_step == "place_secondary_parts"
        and contract.last_spatial_mutation_reason == "modeling_create_primitive"
    ):
        return False
    if contract.current_step == "checkpoint_iterate" and contract.last_spatial_mutation_reason in {
        "modeling_create_primitive",
        "modeling_transform_object",
    }:
        return False
    return contract.current_step in {
        "place_secondary_parts",
        "checkpoint_iterate",
        "inspect_validate",
        "finish_or_stop",
    }


def _apply_spatial_refresh_gate(
    contract: GuidedFlowStateContract,
    *,
    part_registry: list[dict[str, Any]] | None,
    force: bool = False,
) -> None:
    if not _should_rearm_spatial_gate(contract, force=force):
        return

    contract.spatial_refresh_required = True
    contract.required_checks = [
        GuidedFlowCheckContract.model_validate(item)
        for item in _build_required_checks(
            domain_profile=contract.domain_profile,
            current_step=contract.current_step,
            force_spatial_context=True,
        )
    ]
    contract.allowed_families = _build_spatial_refresh_allowed_families(
        domain_profile=contract.domain_profile,
        current_step=contract.current_step,
    )
    contract.next_actions = ["refresh_spatial_context"]
    contract.step_status = "blocked"
    role_summary = _build_role_summary(
        domain_profile=contract.domain_profile,
        current_step=contract.current_step,
        part_registry=part_registry,
        completed_role_hints=contract.completed_roles,
    )
    _apply_role_summary(contract, role_summary)


def _clear_spatial_refresh_gate(
    contract: GuidedFlowStateContract,
    *,
    part_registry: list[dict[str, Any]] | None,
) -> None:
    contract.spatial_refresh_required = False
    contract.spatial_state_stale = False
    contract.last_spatial_check_version = contract.spatial_state_version
    _flow_state_for_current_step(contract, part_registry=part_registry)


def _select_guided_flow_domain_profile(
    *,
    goal: str,
    guided_handoff: dict[str, Any] | None,
) -> Literal["generic", "creature", "building"]:
    recipe_id = str((guided_handoff or {}).get("recipe_id") or "").strip().lower()
    normalized_goal = str(goal or "").strip().lower()

    if recipe_id == "low_poly_creature_blockout" or any(
        _goal_contains_hint(normalized_goal, hint) for hint in _CREATURE_GOAL_HINTS
    ):
        return "creature"
    if any(_goal_contains_hint(normalized_goal, hint) for hint in _BUILDING_GOAL_HINTS):
        return "building"
    return "generic"


def _get_valid_guided_roles(domain_profile: Literal["generic", "creature", "building"]) -> list[str]:
    return sorted(_GUIDED_ROLE_GROUP_BY_ROLE[domain_profile].keys())


def _resolve_guided_role_group(
    *,
    domain_profile: Literal["generic", "creature", "building"],
    role: str,
    role_group: str | None = None,
) -> str:
    mapping = _GUIDED_ROLE_GROUP_BY_ROLE[domain_profile]
    resolved = mapping.get(role)
    if resolved is None:
        known = ", ".join(_get_valid_guided_roles(domain_profile))
        raise ValueError(
            f"Unknown guided part role '{role}' for domain profile '{domain_profile}'. Expected one of: {known}"
        )
    if role_group is not None and role_group.strip() and role_group.strip() != resolved:
        raise ValueError(f"Guided role '{role}' belongs to role_group '{resolved}', not '{role_group.strip()}'.")
    return resolved


def resolve_guided_role_group_for_domain(
    domain_profile: Literal["generic", "creature", "building"],
    role: str,
    role_group: str | None = None,
) -> str:
    """Public helper for deriving one guided role group from overlay + role."""

    return _resolve_guided_role_group(
        domain_profile=domain_profile,
        role=role,
        role_group=role_group,
    )


def describe_guided_scope_mismatch(
    flow_state: dict[str, Any] | None,
    *,
    tool_name: str,
    resolved_scope: dict[str, Any] | None,
) -> str | None:
    """Return actionable guidance when a spatial read used the wrong active guided scope."""

    if flow_state is None:
        return None
    try:
        contract = GuidedFlowStateContract.model_validate(flow_state)
    except Exception:
        return None
    if contract.active_target_scope is None:
        return None
    if contract.current_step != "establish_spatial_context" and not contract.spatial_refresh_required:
        return None
    resolved_fingerprint = _build_guided_target_scope_fingerprint(resolved_scope)
    active_scope = contract.active_target_scope.model_dump(mode="json")
    active_fingerprint = _build_active_guided_target_scope_fingerprint(contract)
    if resolved_fingerprint is None or active_fingerprint is None or resolved_fingerprint == active_fingerprint:
        return None

    active_objects = list(active_scope.get("object_names") or [])
    active_collection = active_scope.get("collection_name")
    if active_collection:
        expected = f"collection_name={active_collection!r}"
    elif active_objects:
        expected = f"target_objects={active_objects!r}"
    else:
        expected = f"target_object={active_scope.get('primary_target')!r}"
    return (
        f"{tool_name}(...) was read-only but did not satisfy the active guided spatial scope. "
        f"Active scope is {expected}; rerun this check with that scope before relying on it for the guided gate."
    )
