# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Session-scoped capability state for adaptive FastMCP surfaces."""

from __future__ import annotations

import asyncio
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Any, Literal

from fastmcp import Context

from server.adapters.mcp.contracts.guided_flow import (
    GuidedFlowCheckContract,
    GuidedFlowFamilyLiteral,
    GuidedFlowStateContract,
    GuidedFlowStepLiteral,
    GuidedTargetScopeContract,
)
from server.adapters.mcp.session_phase import SessionPhase, coerce_session_phase
from server.adapters.mcp.session_state import (
    get_session_value,
    get_session_value_async,
    set_session_value,
    set_session_value_async,
)
from server.adapters.mcp.transforms.visibility_policy import get_guided_overlay_family_order
from server.router.application.session_phase_hints import derive_phase_hint_from_router_result

if TYPE_CHECKING:
    from server.adapters.mcp.guided_mode import VisibilityDiagnostics

SESSION_GOAL_KEY = "goal"
SESSION_PENDING_CLARIFICATION_KEY = "pending_clarification"
SESSION_LAST_ROUTER_STATUS_KEY = "last_router_status"
SESSION_POLICY_CONTEXT_KEY = "policy_context"
SESSION_SURFACE_PROFILE_KEY = "surface_profile"
SESSION_CONTRACT_VERSION_KEY = "contract_version"
SESSION_PENDING_ELICITATION_ID_KEY = "pending_elicitation_id"
SESSION_PENDING_WORKFLOW_NAME_KEY = "pending_workflow_name"
SESSION_PARTIAL_ANSWERS_KEY = "partial_answers"
SESSION_PENDING_QUESTION_SET_ID_KEY = "pending_question_set_id"
SESSION_LAST_ELICITATION_ACTION_KEY = "last_elicitation_action"
SESSION_LAST_ROUTER_DISPOSITION_KEY = "last_router_disposition"
SESSION_LAST_ROUTER_ERROR_KEY = "last_router_error"
SESSION_REFERENCE_IMAGES_KEY = "reference_images"
SESSION_GUIDED_HANDOFF_KEY = "guided_handoff"
SESSION_GUIDED_FLOW_STATE_KEY = "guided_flow_state"
SESSION_PENDING_REFERENCE_IMAGES_KEY = "pending_reference_images"
_GENERIC_PENDING_GOAL = "__pending_goal__"

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
_GUIDED_FLOW_ITERATION_TOOLS = {
    "reference_compare_stage_checkpoint",
    "reference_iterate_stage_checkpoint",
}
_GUIDED_FLOW_STOPPED_STEPS = {"inspect_validate", "finish_or_stop"}
SESSION_GUIDED_PART_REGISTRY_KEY = "guided_part_registry"
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


_GUIDED_SECONDARY_REQUIRED_ROLES: dict[str, tuple[str, ...]] = {
    "generic": ("secondary_mass", "support_part"),
    "creature": ("ear_pair", "foreleg_pair", "hindleg_pair"),
    "building": ("facade_opening", "support_element"),
}


@dataclass(frozen=True)
class GuidedPartRegistryItem:
    """Internal session-scoped record describing one guided part role."""

    object_name: str
    role: str
    role_group: str
    status: str = "registered"
    created_in_step: GuidedFlowStepLiteral | None = None


@dataclass(frozen=True)
class SessionCapabilityState:
    """Serializable session state used by phase-aware visibility decisions."""

    phase: SessionPhase
    goal: str | None = None
    pending_clarification: dict[str, Any] | None = None
    last_router_status: str | None = None
    policy_context: dict[str, Any] | None = None
    surface_profile: str | None = None
    contract_version: str | None = None
    pending_elicitation_id: str | None = None
    pending_workflow_name: str | None = None
    partial_answers: dict[str, Any] | None = None
    pending_question_set_id: str | None = None
    last_elicitation_action: str | None = None
    last_router_disposition: str | None = None
    last_router_error: str | None = None
    reference_images: list[dict[str, Any]] | None = None
    guided_handoff: dict[str, Any] | None = None
    guided_flow_state: dict[str, Any] | None = None
    guided_part_registry: list[dict[str, Any]] | None = None
    pending_reference_images: list[dict[str, Any]] | None = None


GuidedReferenceBlockingReason = Literal[
    "active_goal_required",
    "goal_input_pending",
    "pending_references_detected",
    "reference_images_required",
    "reference_session_not_ready",
]
GuidedReferenceNextAction = Literal[
    "call_router_set_goal",
    "answer_pending_goal_questions",
    "attach_reference_images",
    "call_router_get_status",
]


@dataclass(frozen=True)
class GuidedReferenceReadinessState:
    """Serializable readiness state for guided reference compare/iterate flows."""

    status: Literal["ready", "blocked"] = "blocked"
    goal: str | None = None
    has_active_goal: bool = False
    goal_input_pending: bool = False
    attached_reference_count: int = 0
    pending_reference_count: int = 0
    compare_ready: bool = False
    iterate_ready: bool = False
    blocking_reason: GuidedReferenceBlockingReason | None = None
    next_action: GuidedReferenceNextAction | None = None


def infer_phase_from_router_status(
    status: str | None,
    *,
    current_phase: SessionPhase | None = None,
) -> SessionPhase:
    """Map coarse router statuses onto the first-pass phase set."""

    if current_phase == SessionPhase.INSPECT_VALIDATE:
        return current_phase

    mapping = {
        "ready": SessionPhase.BUILD,
        "needs_input": SessionPhase.PLANNING,
        "no_match": SessionPhase.PLANNING,
        "disabled": SessionPhase.PLANNING,
        "error": SessionPhase.PLANNING,
    }
    return mapping.get(status or "", current_phase or SessionPhase.BOOTSTRAP)


def _goal_contains_hint(goal: str | None, hint: str) -> bool:
    words = str(goal or "").strip().lower()
    if not words:
        return False
    import re

    normalized_hint = re.escape(hint)
    return re.search(rf"(?<![a-z0-9]){normalized_hint}(?![a-z0-9])", words) is not None


def _normalize_guided_flow_state(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    try:
        return GuidedFlowStateContract.model_validate(value).model_dump(mode="json", exclude_none=True)
    except Exception:
        return None


def _normalize_guided_part_registry(value: Any) -> list[dict[str, Any]] | None:
    if value is None:
        return None
    if not isinstance(value, list):
        return None

    items: list[dict[str, Any]] = []
    for raw_item in value:
        try:
            if isinstance(raw_item, GuidedPartRegistryItem):
                items.append(asdict(raw_item))
                continue
            if not isinstance(raw_item, dict):
                return None
            items.append(asdict(GuidedPartRegistryItem(**raw_item)))
        except Exception:
            return None
    return items or None


def _normalize_scope_names(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
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


def _scene_object_names() -> set[str]:
    from server.infrastructure.di import get_scene_handler

    objects = get_scene_handler().list_objects()
    names: set[str] = set()
    for item in objects:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        if isinstance(name, str) and name.strip():
            names.add(name.strip())
    return names


def _normalize_guided_object_name(object_name: str) -> str:
    normalized_object_name = str(object_name or "").strip()
    if not normalized_object_name:
        raise ValueError("guided_register_part(...) requires a non-empty `object_name`.")
    return normalized_object_name


def require_existing_scene_object_name(object_name: str) -> str:
    normalized_object_name = _normalize_guided_object_name(object_name)

    try:
        object_names = _scene_object_names()
    except Exception as exc:
        raise ValueError(
            f"guided_register_part(...) could not validate object '{normalized_object_name}' against the Blender scene: {exc}"
        ) from exc

    if normalized_object_name not in object_names:
        raise ValueError(
            f"guided_register_part(...) requires an existing Blender object named '{normalized_object_name}'."
        )

    return normalized_object_name


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
    if contract.last_spatial_mutation_reason == "scene_rename_object":
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


def _update_guided_flow_role_summary_dict(
    flow_state: dict[str, Any],
    *,
    part_registry: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    contract = GuidedFlowStateContract.model_validate(flow_state)
    role_summary = _build_role_summary(
        domain_profile=contract.domain_profile,
        current_step=contract.current_step,
        part_registry=part_registry,
        completed_role_hints=contract.completed_roles,
    )
    _apply_role_summary(contract, role_summary)
    return contract.model_dump(mode="json")


def _maybe_advance_guided_flow_from_part_registry_dict(
    flow_state: dict[str, Any],
    *,
    part_registry: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    contract = GuidedFlowStateContract.model_validate(flow_state)
    current_role_summary = _build_role_summary(
        domain_profile=contract.domain_profile,
        current_step=contract.current_step,
        part_registry=part_registry,
        completed_role_hints=contract.completed_roles,
    )
    completed_roles = set(current_role_summary["completed_roles"])

    if contract.current_step in {"bootstrap_primary_workset", "create_primary_masses"}:
        required_roles = _GUIDED_PRIMARY_REQUIRED_ROLES[contract.domain_profile]
        if all(role in completed_roles for role in required_roles):
            if (
                contract.current_step == "bootstrap_primary_workset"
                and "bootstrap_primary_workset" not in contract.completed_steps
            ):
                contract.completed_steps.append("bootstrap_primary_workset")
            if "create_primary_masses" not in contract.completed_steps:
                contract.completed_steps.append("create_primary_masses")
            contract.current_step = "place_secondary_parts"
            contract.blocked_families = []
            _flow_state_for_current_step(contract, part_registry=part_registry)
            _apply_spatial_refresh_gate(contract, part_registry=part_registry, force=True)
    elif contract.current_step == "place_secondary_parts":
        required_roles = _GUIDED_SECONDARY_REQUIRED_ROLES[contract.domain_profile]
        if all(role in completed_roles for role in required_roles):
            if "place_secondary_parts" not in contract.completed_steps:
                contract.completed_steps.append("place_secondary_parts")
            contract.current_step = "checkpoint_iterate"
            contract.blocked_families = []
            _flow_state_for_current_step(contract, part_registry=part_registry)
            _apply_spatial_refresh_gate(contract, part_registry=part_registry, force=True)

    role_summary = _build_role_summary(
        domain_profile=contract.domain_profile,
        current_step=contract.current_step,
        part_registry=part_registry,
        completed_role_hints=contract.completed_roles,
    )
    _apply_role_summary(contract, role_summary)
    return contract.model_dump(mode="json")


def _get_valid_guided_roles(domain_profile: Literal["generic", "creature", "building"]) -> list[str]:
    return sorted(_GUIDED_ROLE_GROUP_BY_ROLE[domain_profile].keys())


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
    active_fingerprint = contract.spatial_scope_fingerprint or _build_guided_target_scope_fingerprint(active_scope)
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


def _resolve_guided_role_group(
    *,
    domain_profile: Literal["generic", "creature", "building"],
    role: str,
    role_group: str | None = None,
) -> str:
    if role_group is not None and role_group.strip():
        return role_group.strip()

    mapping = _GUIDED_ROLE_GROUP_BY_ROLE[domain_profile]
    resolved = mapping.get(role)
    if resolved is None:
        known = ", ".join(_get_valid_guided_roles(domain_profile))
        raise ValueError(
            f"Unknown guided part role '{role}' for domain profile '{domain_profile}'. Expected one of: {known}"
        )
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


def _build_initial_guided_flow_state(
    *,
    goal: str,
    router_result: dict[str, Any],
    previous_flow_state: dict[str, Any] | None = None,
    part_registry: list[dict[str, Any]] | None = None,
    preserve_existing: bool = False,
) -> dict[str, Any] | None:
    status = str(router_result.get("status") or "")
    if status == "disabled":
        return None

    guided_handoff = router_result.get("guided_handoff")
    domain_profile = _select_guided_flow_domain_profile(goal=goal, guided_handoff=guided_handoff)

    if preserve_existing and previous_flow_state is not None:
        previous_contract = GuidedFlowStateContract.model_validate(previous_flow_state)
        if (
            previous_contract.domain_profile == domain_profile
            and previous_contract.current_step not in _GUIDED_FLOW_STOPPED_STEPS
            and status != "needs_input"
            and previous_contract.current_step != "understand_goal"
        ):
            return previous_contract.model_dump(mode="json")

    if status == "needs_input":
        current_step: GuidedFlowStepLiteral = "understand_goal"
        next_actions = ["answer_router_questions"]
        blocked_families = ["build", "late_refinement", "finish"]
        step_status = "blocked"
        required_checks: list[dict[str, Any]] = []
    else:
        current_step = "establish_spatial_context"
        next_actions = ["run_required_checks"]
        blocked_families = ["build", "late_refinement", "finish"]
        required_checks = _build_required_checks(domain_profile=domain_profile, current_step=current_step)
        step_status = "blocked" if required_checks else "ready"

    completed_steps: list[GuidedFlowStepLiteral] = []
    if (
        previous_flow_state is not None
        and status != "needs_input"
        and previous_flow_state.get("current_step") == "understand_goal"
    ):
        completed_steps.append("understand_goal")

    required_prompts, preferred_prompts = _build_required_prompt_bundle(
        domain_profile=domain_profile,
        current_step=current_step,
    )
    flow_id = f"guided_{domain_profile}_flow"
    role_summary = _build_role_summary(
        domain_profile=domain_profile,
        current_step=current_step,
        part_registry=part_registry,
    )

    return GuidedFlowStateContract(
        flow_id=flow_id,
        domain_profile=domain_profile,
        current_step=current_step,  # type: ignore[arg-type]
        completed_steps=completed_steps,
        required_checks=[GuidedFlowCheckContract.model_validate(item) for item in required_checks],
        required_prompts=required_prompts,
        preferred_prompts=preferred_prompts,
        next_actions=next_actions,
        blocked_families=blocked_families,
        allowed_families=_build_allowed_families(domain_profile=domain_profile, current_step=current_step),
        allowed_roles=role_summary["allowed_roles"],
        completed_roles=role_summary["completed_roles"],
        missing_roles=role_summary["missing_roles"],
        required_role_groups=role_summary["required_role_groups"],
        step_status=step_status,  # type: ignore[arg-type]
    ).model_dump(mode="json")


def get_session_capability_state(ctx: Context) -> SessionCapabilityState:
    """Read the canonical session capability state from Context storage."""

    return SessionCapabilityState(
        phase=coerce_session_phase(get_session_value(ctx, "phase", SessionPhase.BOOTSTRAP)),
        goal=get_session_value(ctx, SESSION_GOAL_KEY),
        pending_clarification=get_session_value(ctx, SESSION_PENDING_CLARIFICATION_KEY),
        last_router_status=get_session_value(ctx, SESSION_LAST_ROUTER_STATUS_KEY),
        policy_context=get_session_value(ctx, SESSION_POLICY_CONTEXT_KEY),
        surface_profile=get_session_value(ctx, SESSION_SURFACE_PROFILE_KEY),
        contract_version=get_session_value(ctx, SESSION_CONTRACT_VERSION_KEY),
        pending_elicitation_id=get_session_value(ctx, SESSION_PENDING_ELICITATION_ID_KEY),
        pending_workflow_name=get_session_value(ctx, SESSION_PENDING_WORKFLOW_NAME_KEY),
        partial_answers=get_session_value(ctx, SESSION_PARTIAL_ANSWERS_KEY),
        pending_question_set_id=get_session_value(ctx, SESSION_PENDING_QUESTION_SET_ID_KEY),
        last_elicitation_action=get_session_value(ctx, SESSION_LAST_ELICITATION_ACTION_KEY),
        last_router_disposition=get_session_value(ctx, SESSION_LAST_ROUTER_DISPOSITION_KEY),
        last_router_error=get_session_value(ctx, SESSION_LAST_ROUTER_ERROR_KEY),
        reference_images=get_session_value(ctx, SESSION_REFERENCE_IMAGES_KEY),
        guided_handoff=get_session_value(ctx, SESSION_GUIDED_HANDOFF_KEY),
        guided_flow_state=_normalize_guided_flow_state(get_session_value(ctx, SESSION_GUIDED_FLOW_STATE_KEY)),
        guided_part_registry=_normalize_guided_part_registry(get_session_value(ctx, SESSION_GUIDED_PART_REGISTRY_KEY)),
        pending_reference_images=get_session_value(ctx, SESSION_PENDING_REFERENCE_IMAGES_KEY),
    )


async def get_session_capability_state_async(ctx: Context) -> SessionCapabilityState:
    """Async variant of session capability state lookup for native FastMCP Context."""

    return SessionCapabilityState(
        phase=coerce_session_phase(await get_session_value_async(ctx, "phase", SessionPhase.BOOTSTRAP)),
        goal=await get_session_value_async(ctx, SESSION_GOAL_KEY),
        pending_clarification=await get_session_value_async(ctx, SESSION_PENDING_CLARIFICATION_KEY),
        last_router_status=await get_session_value_async(ctx, SESSION_LAST_ROUTER_STATUS_KEY),
        policy_context=await get_session_value_async(ctx, SESSION_POLICY_CONTEXT_KEY),
        surface_profile=await get_session_value_async(ctx, SESSION_SURFACE_PROFILE_KEY),
        contract_version=await get_session_value_async(ctx, SESSION_CONTRACT_VERSION_KEY),
        pending_elicitation_id=await get_session_value_async(ctx, SESSION_PENDING_ELICITATION_ID_KEY),
        pending_workflow_name=await get_session_value_async(ctx, SESSION_PENDING_WORKFLOW_NAME_KEY),
        partial_answers=await get_session_value_async(ctx, SESSION_PARTIAL_ANSWERS_KEY),
        pending_question_set_id=await get_session_value_async(ctx, SESSION_PENDING_QUESTION_SET_ID_KEY),
        last_elicitation_action=await get_session_value_async(ctx, SESSION_LAST_ELICITATION_ACTION_KEY),
        last_router_disposition=await get_session_value_async(ctx, SESSION_LAST_ROUTER_DISPOSITION_KEY),
        last_router_error=await get_session_value_async(ctx, SESSION_LAST_ROUTER_ERROR_KEY),
        reference_images=await get_session_value_async(ctx, SESSION_REFERENCE_IMAGES_KEY),
        guided_handoff=await get_session_value_async(ctx, SESSION_GUIDED_HANDOFF_KEY),
        guided_flow_state=_normalize_guided_flow_state(
            await get_session_value_async(ctx, SESSION_GUIDED_FLOW_STATE_KEY)
        ),
        guided_part_registry=_normalize_guided_part_registry(
            await get_session_value_async(ctx, SESSION_GUIDED_PART_REGISTRY_KEY)
        ),
        pending_reference_images=await get_session_value_async(ctx, SESSION_PENDING_REFERENCE_IMAGES_KEY),
    )


async def bootstrap_guided_empty_scene_primary_workset_async(ctx: Context) -> SessionCapabilityState:
    """Move an empty guided scene from spatial bootstrap to first primary workset creation."""

    current = await get_session_capability_state_async(ctx)
    if current.guided_flow_state is None:
        return current

    contract = GuidedFlowStateContract.model_validate(current.guided_flow_state)
    if contract.current_step != "establish_spatial_context":
        return current

    contract.current_step = "bootstrap_primary_workset"
    contract.blocked_families = []
    contract.required_checks = []
    contract.active_target_scope = None
    contract.spatial_scope_fingerprint = None
    contract.spatial_refresh_required = False
    contract.spatial_state_stale = False
    contract.last_spatial_check_version = None
    _flow_state_for_current_step(contract, part_registry=current.guided_part_registry)

    state = SessionCapabilityState(
        phase=current.phase,
        goal=current.goal,
        pending_clarification=current.pending_clarification,
        last_router_status=current.last_router_status,
        policy_context=current.policy_context,
        surface_profile=current.surface_profile,
        contract_version=current.contract_version,
        pending_elicitation_id=current.pending_elicitation_id,
        pending_workflow_name=current.pending_workflow_name,
        partial_answers=current.partial_answers,
        pending_question_set_id=current.pending_question_set_id,
        last_elicitation_action=current.last_elicitation_action,
        last_router_disposition=current.last_router_disposition,
        last_router_error=current.last_router_error,
        reference_images=current.reference_images,
        guided_handoff=current.guided_handoff,
        guided_flow_state=contract.model_dump(mode="json"),
        guided_part_registry=current.guided_part_registry,
        pending_reference_images=current.pending_reference_images,
    )
    await set_session_capability_state_async(ctx, state)
    return state


def set_session_capability_state(ctx: Context, state: SessionCapabilityState) -> None:
    """Persist the canonical session capability state to Context storage."""

    set_session_value(ctx, "phase", state.phase.value)
    set_session_value(ctx, SESSION_GOAL_KEY, state.goal)
    set_session_value(ctx, SESSION_PENDING_CLARIFICATION_KEY, state.pending_clarification)
    set_session_value(ctx, SESSION_LAST_ROUTER_STATUS_KEY, state.last_router_status)
    set_session_value(ctx, SESSION_POLICY_CONTEXT_KEY, state.policy_context)
    set_session_value(ctx, SESSION_SURFACE_PROFILE_KEY, state.surface_profile)
    set_session_value(ctx, SESSION_CONTRACT_VERSION_KEY, state.contract_version)
    set_session_value(ctx, SESSION_PENDING_ELICITATION_ID_KEY, state.pending_elicitation_id)
    set_session_value(ctx, SESSION_PENDING_WORKFLOW_NAME_KEY, state.pending_workflow_name)
    set_session_value(ctx, SESSION_PARTIAL_ANSWERS_KEY, state.partial_answers)
    set_session_value(ctx, SESSION_PENDING_QUESTION_SET_ID_KEY, state.pending_question_set_id)
    set_session_value(ctx, SESSION_LAST_ELICITATION_ACTION_KEY, state.last_elicitation_action)
    set_session_value(ctx, SESSION_LAST_ROUTER_DISPOSITION_KEY, state.last_router_disposition)
    set_session_value(ctx, SESSION_LAST_ROUTER_ERROR_KEY, state.last_router_error)
    set_session_value(ctx, SESSION_REFERENCE_IMAGES_KEY, state.reference_images)
    set_session_value(ctx, SESSION_GUIDED_HANDOFF_KEY, state.guided_handoff)
    set_session_value(ctx, SESSION_GUIDED_FLOW_STATE_KEY, state.guided_flow_state)
    set_session_value(ctx, SESSION_GUIDED_PART_REGISTRY_KEY, state.guided_part_registry)
    set_session_value(ctx, SESSION_PENDING_REFERENCE_IMAGES_KEY, state.pending_reference_images)


async def set_session_capability_state_async(ctx: Context, state: SessionCapabilityState) -> None:
    """Async variant of session capability state persistence."""

    await set_session_value_async(ctx, "phase", state.phase.value)
    await set_session_value_async(ctx, SESSION_GOAL_KEY, state.goal)
    await set_session_value_async(ctx, SESSION_PENDING_CLARIFICATION_KEY, state.pending_clarification)
    await set_session_value_async(ctx, SESSION_LAST_ROUTER_STATUS_KEY, state.last_router_status)
    await set_session_value_async(ctx, SESSION_POLICY_CONTEXT_KEY, state.policy_context)
    await set_session_value_async(ctx, SESSION_SURFACE_PROFILE_KEY, state.surface_profile)
    await set_session_value_async(ctx, SESSION_CONTRACT_VERSION_KEY, state.contract_version)
    await set_session_value_async(ctx, SESSION_PENDING_ELICITATION_ID_KEY, state.pending_elicitation_id)
    await set_session_value_async(ctx, SESSION_PENDING_WORKFLOW_NAME_KEY, state.pending_workflow_name)
    await set_session_value_async(ctx, SESSION_PARTIAL_ANSWERS_KEY, state.partial_answers)
    await set_session_value_async(ctx, SESSION_PENDING_QUESTION_SET_ID_KEY, state.pending_question_set_id)
    await set_session_value_async(ctx, SESSION_LAST_ELICITATION_ACTION_KEY, state.last_elicitation_action)
    await set_session_value_async(ctx, SESSION_LAST_ROUTER_DISPOSITION_KEY, state.last_router_disposition)
    await set_session_value_async(ctx, SESSION_LAST_ROUTER_ERROR_KEY, state.last_router_error)
    await set_session_value_async(ctx, SESSION_REFERENCE_IMAGES_KEY, state.reference_images)
    await set_session_value_async(ctx, SESSION_GUIDED_HANDOFF_KEY, state.guided_handoff)
    await set_session_value_async(ctx, SESSION_GUIDED_FLOW_STATE_KEY, state.guided_flow_state)
    await set_session_value_async(ctx, SESSION_GUIDED_PART_REGISTRY_KEY, state.guided_part_registry)
    await set_session_value_async(ctx, SESSION_PENDING_REFERENCE_IMAGES_KEY, state.pending_reference_images)


def _split_pending_reference_images_for_goal(
    pending_reference_images: list[dict[str, Any]] | None,
    *,
    goal: str,
) -> tuple[list[dict[str, Any]] | None, list[dict[str, Any]] | None]:
    """Split pending references into adopted items and goal-mismatched leftovers."""

    if not pending_reference_images:
        return None, None

    adopted: list[dict[str, Any]] = []
    remaining: list[dict[str, Any]] = []
    for item in pending_reference_images:
        recorded_goal = str(item.get("goal") or "").strip()
        if recorded_goal not in {"", _GENERIC_PENDING_GOAL, goal}:
            remaining.append(dict(item))
            continue
        adopted_item = dict(item)
        adopted_item["goal"] = goal
        adopted.append(adopted_item)
    return adopted or None, remaining or None


def _merge_reference_images(
    current_reference_images: list[dict[str, Any]] | None,
    adopted_reference_images: list[dict[str, Any]] | None,
) -> list[dict[str, Any]] | None:
    """Merge active and newly adopted reference images without losing order."""

    merged: list[dict[str, Any]] = []
    seen_reference_ids: set[str] = set()

    for item in [*list(current_reference_images or []), *list(adopted_reference_images or [])]:
        reference_id = item.get("reference_id")
        if isinstance(reference_id, str) and reference_id:
            if reference_id in seen_reference_ids:
                continue
            seen_reference_ids.add(reference_id)
        merged.append(item)

    return merged or None


def router_result_has_ready_guided_reference_goal(router_result: dict[str, Any]) -> bool:
    """Return True when a router_set_goal result establishes a usable guided goal state."""

    status = str(router_result.get("status") or "")
    return status in {"ready", "no_match"}


def session_has_ready_guided_reference_goal(session: SessionCapabilityState) -> bool:
    """Return True when the session is coherent enough for staged reference work."""

    if not session.goal:
        return False

    if session.last_router_status in {"ready", "no_match"}:
        return True
    return False


def build_guided_reference_readiness(session: SessionCapabilityState) -> GuidedReferenceReadinessState:
    """Compute one explicit readiness contract for guided stage compare/iterate flows."""

    attached_reference_count = len(session.reference_images or [])
    has_active_goal = session.goal is not None
    goal_input_pending = bool(session.pending_clarification) or session.last_router_status == "needs_input"
    session_ready = session_has_ready_guided_reference_goal(session)
    relevant_pending_reference_count = 0

    if session.goal:
        relevant_pending_references, _ = _split_pending_reference_images_for_goal(
            session.pending_reference_images,
            goal=session.goal,
        )
        relevant_pending_reference_count = len(relevant_pending_references or [])

    if not has_active_goal:
        blocking_reason: GuidedReferenceBlockingReason | None = "active_goal_required"
        next_action: GuidedReferenceNextAction | None = "call_router_set_goal"
    elif goal_input_pending:
        blocking_reason = "goal_input_pending"
        next_action = "answer_pending_goal_questions"
    elif not session_ready:
        blocking_reason = "reference_session_not_ready"
        next_action = "call_router_get_status"
    elif relevant_pending_reference_count > 0:
        blocking_reason = "pending_references_detected"
        next_action = "call_router_get_status"
    elif attached_reference_count == 0:
        blocking_reason = "reference_images_required"
        next_action = "attach_reference_images"
    else:
        blocking_reason = None
        next_action = None

    compare_ready = blocking_reason is None
    return GuidedReferenceReadinessState(
        status="ready" if compare_ready else "blocked",
        goal=session.goal,
        has_active_goal=has_active_goal,
        goal_input_pending=goal_input_pending,
        attached_reference_count=attached_reference_count,
        pending_reference_count=relevant_pending_reference_count,
        compare_ready=compare_ready,
        iterate_ready=compare_ready,
        blocking_reason=blocking_reason,
        next_action=next_action,
    )


def build_guided_reference_readiness_payload(session: SessionCapabilityState) -> dict[str, Any]:
    """Return a serializable readiness payload for MCP contracts and tests."""

    return asdict(build_guided_reference_readiness(session))


def update_session_from_router_goal(
    ctx: Context,
    goal: str,
    router_result: dict[str, Any],
    *,
    provided_answers: dict[str, Any] | None = None,
    surface_profile: str | None = None,
    contract_version: str | None = None,
) -> SessionCapabilityState:
    """Update session capability state from a router_set_goal response."""

    current = get_session_capability_state(ctx)
    status = router_result.get("status")
    pending = router_result.get("unresolved") if status == "needs_input" else None
    hinted_phase = router_result.get("phase_hint") or derive_phase_hint_from_router_result(router_result)
    phase = coerce_session_phase(hinted_phase or infer_phase_from_router_status(status, current_phase=current.phase))
    clarification = router_result.get("clarification") or {}
    current_partial_answers = dict(current.partial_answers or {})
    current_partial_answers.update(provided_answers or {})
    same_goal = current.goal == goal
    retained_guided_part_registry = current.guided_part_registry if same_goal else None
    previous_flow_state = _normalize_guided_flow_state(current.guided_flow_state)
    guided_flow_state = (
        _build_initial_guided_flow_state(
            goal=goal,
            router_result=router_result,
            previous_flow_state=previous_flow_state,
            part_registry=retained_guided_part_registry,
            preserve_existing=same_goal,
        )
        if (surface_profile or current.surface_profile or "legacy-flat") == "llm-guided"
        else None
    )

    if status == "needs_input":
        pending_elicitation_id = (
            f"elic_{clarification.get('question_set_id')}"
            if clarification.get("question_set_id")
            else current.pending_elicitation_id
        )
        pending_workflow_name = router_result.get("workflow") or current.pending_workflow_name
        pending_question_set_id = clarification.get("question_set_id") or current.pending_question_set_id
        last_elicitation_action = router_result.get("elicitation_action") or current.last_elicitation_action
        partial_answers = current_partial_answers or None
    else:
        pending_elicitation_id = None
        pending_workflow_name = None
        pending_question_set_id = None
        last_elicitation_action = None
        partial_answers = None

    goal_ready = router_result_has_ready_guided_reference_goal(router_result)
    adopted_reference_images, remaining_pending_reference_images = _split_pending_reference_images_for_goal(
        current.pending_reference_images,
        goal=goal,
    )
    reference_images = (
        _merge_reference_images(current.reference_images if same_goal else None, adopted_reference_images)
        if goal_ready
        else (current.reference_images if same_goal else None)
    )
    pending_reference_images = remaining_pending_reference_images if goal_ready else current.pending_reference_images

    state = SessionCapabilityState(
        phase=phase,
        goal=goal,
        pending_clarification=pending,
        last_router_status=status,
        policy_context=router_result.get("policy_context"),
        surface_profile=surface_profile or current.surface_profile,
        contract_version=contract_version or current.contract_version,
        pending_elicitation_id=pending_elicitation_id,
        pending_workflow_name=pending_workflow_name,
        partial_answers=partial_answers,
        pending_question_set_id=pending_question_set_id,
        last_elicitation_action=last_elicitation_action,
        last_router_disposition=current.last_router_disposition,
        last_router_error=current.last_router_error,
        reference_images=reference_images,
        guided_handoff=router_result.get("guided_handoff"),
        guided_flow_state=guided_flow_state,
        guided_part_registry=retained_guided_part_registry,
        pending_reference_images=pending_reference_images,
    )
    set_session_capability_state(ctx, state)
    return state


async def update_session_from_router_goal_async(
    ctx: Context,
    goal: str,
    router_result: dict[str, Any],
    *,
    provided_answers: dict[str, Any] | None = None,
    surface_profile: str | None = None,
    contract_version: str | None = None,
) -> SessionCapabilityState:
    """Async variant of router goal state persistence for native FastMCP Context."""

    current = await get_session_capability_state_async(ctx)
    status = router_result.get("status")
    pending = router_result.get("unresolved") if status == "needs_input" else None
    hinted_phase = router_result.get("phase_hint") or derive_phase_hint_from_router_result(router_result)
    phase = coerce_session_phase(hinted_phase or infer_phase_from_router_status(status, current_phase=current.phase))
    clarification = router_result.get("clarification") or {}
    current_partial_answers = dict(current.partial_answers or {})
    current_partial_answers.update(provided_answers or {})
    same_goal = current.goal == goal
    retained_guided_part_registry = current.guided_part_registry if same_goal else None
    previous_flow_state = _normalize_guided_flow_state(current.guided_flow_state)
    guided_flow_state = (
        _build_initial_guided_flow_state(
            goal=goal,
            router_result=router_result,
            previous_flow_state=previous_flow_state,
            part_registry=retained_guided_part_registry,
            preserve_existing=same_goal,
        )
        if (surface_profile or current.surface_profile or "legacy-flat") == "llm-guided"
        else None
    )

    if status == "needs_input":
        pending_elicitation_id = (
            f"elic_{clarification.get('question_set_id')}"
            if clarification.get("question_set_id")
            else current.pending_elicitation_id
        )
        pending_workflow_name = router_result.get("workflow") or current.pending_workflow_name
        pending_question_set_id = clarification.get("question_set_id") or current.pending_question_set_id
        last_elicitation_action = router_result.get("elicitation_action") or current.last_elicitation_action
        partial_answers = current_partial_answers or None
    else:
        pending_elicitation_id = None
        pending_workflow_name = None
        pending_question_set_id = None
        last_elicitation_action = None
        partial_answers = None

    goal_ready = router_result_has_ready_guided_reference_goal(router_result)
    adopted_reference_images, remaining_pending_reference_images = _split_pending_reference_images_for_goal(
        current.pending_reference_images,
        goal=goal,
    )
    reference_images = (
        _merge_reference_images(current.reference_images if same_goal else None, adopted_reference_images)
        if goal_ready
        else (current.reference_images if same_goal else None)
    )
    pending_reference_images = remaining_pending_reference_images if goal_ready else current.pending_reference_images

    state = SessionCapabilityState(
        phase=phase,
        goal=goal,
        pending_clarification=pending,
        last_router_status=status,
        policy_context=router_result.get("policy_context"),
        surface_profile=surface_profile or current.surface_profile,
        contract_version=contract_version or current.contract_version,
        pending_elicitation_id=pending_elicitation_id,
        pending_workflow_name=pending_workflow_name,
        partial_answers=partial_answers,
        pending_question_set_id=pending_question_set_id,
        last_elicitation_action=last_elicitation_action,
        last_router_disposition=current.last_router_disposition,
        last_router_error=current.last_router_error,
        reference_images=reference_images,
        guided_handoff=router_result.get("guided_handoff"),
        guided_flow_state=guided_flow_state,
        guided_part_registry=retained_guided_part_registry,
        pending_reference_images=pending_reference_images,
    )
    await set_session_capability_state_async(ctx, state)
    return state


def clear_session_goal_state(
    ctx: Context,
    *,
    surface_profile: str | None = None,
    contract_version: str | None = None,
) -> SessionCapabilityState:
    """Clear goal-specific session state and return the session to planning."""

    current = get_session_capability_state(ctx)
    state = SessionCapabilityState(
        phase=SessionPhase.PLANNING,
        goal=None,
        pending_clarification=None,
        last_router_status=None,
        policy_context=None,
        surface_profile=surface_profile or current.surface_profile,
        contract_version=contract_version or current.contract_version,
        pending_elicitation_id=None,
        pending_workflow_name=None,
        partial_answers=None,
        pending_question_set_id=None,
        last_elicitation_action=None,
        last_router_disposition=current.last_router_disposition,
        last_router_error=current.last_router_error,
        reference_images=None,
        guided_handoff=None,
        guided_flow_state=None,
        guided_part_registry=None,
        pending_reference_images=None,
    )
    set_session_capability_state(ctx, state)
    return state


async def clear_session_goal_state_async(
    ctx: Context,
    *,
    surface_profile: str | None = None,
    contract_version: str | None = None,
) -> SessionCapabilityState:
    """Async variant of goal reset for native FastMCP Context."""

    current = await get_session_capability_state_async(ctx)
    state = SessionCapabilityState(
        phase=SessionPhase.PLANNING,
        goal=None,
        pending_clarification=None,
        last_router_status=None,
        policy_context=None,
        surface_profile=surface_profile or current.surface_profile,
        contract_version=contract_version or current.contract_version,
        pending_elicitation_id=None,
        pending_workflow_name=None,
        partial_answers=None,
        pending_question_set_id=None,
        last_elicitation_action=None,
        last_router_disposition=current.last_router_disposition,
        last_router_error=current.last_router_error,
        reference_images=None,
        guided_handoff=None,
        guided_flow_state=None,
        guided_part_registry=None,
        pending_reference_images=None,
    )
    await set_session_capability_state_async(ctx, state)
    return state


def merge_resolved_params_with_session_answers(
    ctx: Context,
    resolved_params: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Merge explicit resolved params with any persisted partial answers."""

    current = get_session_capability_state(ctx)
    merged = dict(current.partial_answers or {})
    merged.update(resolved_params or {})
    return merged or None


async def merge_resolved_params_with_session_answers_async(
    ctx: Context,
    resolved_params: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Async variant of partial-answer merge for native FastMCP Context."""

    current = await get_session_capability_state_async(ctx)
    merged = dict(current.partial_answers or {})
    merged.update(resolved_params or {})
    return merged or None


async def apply_visibility_for_session_state(
    ctx: Context,
    state: SessionCapabilityState,
) -> VisibilityDiagnostics:
    """Apply native session visibility rules for the current capability state."""

    from server.adapters.mcp.guided_mode import apply_session_visibility

    surface_profile = state.surface_profile or "legacy-flat"
    return await apply_session_visibility(
        ctx,
        surface_profile=surface_profile,
        phase=state.phase,
        guided_handoff=state.guided_handoff,
        guided_flow_state=state.guided_flow_state,
    )


def refresh_visibility_for_session_state(
    ctx: Context,
    state: SessionCapabilityState,
) -> None:
    """Best-effort sync wrapper for applying session visibility after sync tool calls."""

    if state.guided_flow_state is None:
        return

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(apply_visibility_for_session_state(ctx, state))
        return

    asyncio.create_task(apply_visibility_for_session_state(ctx, state))


def replace_session_reference_images(
    ctx: Context,
    reference_images: list[dict[str, Any]] | None,
) -> SessionCapabilityState:
    """Replace the goal-scoped reference images kept in session state."""

    current = get_session_capability_state(ctx)
    state = SessionCapabilityState(
        phase=current.phase,
        goal=current.goal,
        pending_clarification=current.pending_clarification,
        last_router_status=current.last_router_status,
        policy_context=current.policy_context,
        surface_profile=current.surface_profile,
        contract_version=current.contract_version,
        pending_elicitation_id=current.pending_elicitation_id,
        pending_workflow_name=current.pending_workflow_name,
        partial_answers=current.partial_answers,
        pending_question_set_id=current.pending_question_set_id,
        last_elicitation_action=current.last_elicitation_action,
        last_router_disposition=current.last_router_disposition,
        last_router_error=current.last_router_error,
        reference_images=reference_images or None,
        guided_handoff=current.guided_handoff,
        guided_flow_state=current.guided_flow_state,
        guided_part_registry=current.guided_part_registry,
        pending_reference_images=current.pending_reference_images,
    )
    set_session_capability_state(ctx, state)
    return state


async def replace_session_reference_images_async(
    ctx: Context,
    reference_images: list[dict[str, Any]] | None,
) -> SessionCapabilityState:
    """Async variant of goal-scoped reference-image replacement."""

    current = await get_session_capability_state_async(ctx)
    state = SessionCapabilityState(
        phase=current.phase,
        goal=current.goal,
        pending_clarification=current.pending_clarification,
        last_router_status=current.last_router_status,
        policy_context=current.policy_context,
        surface_profile=current.surface_profile,
        contract_version=current.contract_version,
        pending_elicitation_id=current.pending_elicitation_id,
        pending_workflow_name=current.pending_workflow_name,
        partial_answers=current.partial_answers,
        pending_question_set_id=current.pending_question_set_id,
        last_elicitation_action=current.last_elicitation_action,
        last_router_disposition=current.last_router_disposition,
        last_router_error=current.last_router_error,
        reference_images=reference_images or None,
        guided_handoff=current.guided_handoff,
        guided_flow_state=current.guided_flow_state,
        guided_part_registry=current.guided_part_registry,
        pending_reference_images=current.pending_reference_images,
    )
    await set_session_capability_state_async(ctx, state)
    return state


def record_router_execution_outcome(
    ctx: Context,
    *,
    router_disposition: str,
    error: str | None = None,
) -> SessionCapabilityState:
    """Persist the last router execution outcome for diagnostics surfaces.

    Keep this write path narrowly scoped. Routed sync tools run through
    threadpool-backed FastMCP execution, so rewriting the full session snapshot
    here would risk clobbering unrelated goal/reference state if a sync-state
    read falls back or races. Diagnostics only need these two keys.
    """

    set_session_value(ctx, SESSION_LAST_ROUTER_DISPOSITION_KEY, router_disposition)
    set_session_value(ctx, SESSION_LAST_ROUTER_ERROR_KEY, error)

    current = get_session_capability_state(ctx)
    if current.last_router_disposition == router_disposition and current.last_router_error == error:
        return current

    return SessionCapabilityState(
        phase=current.phase,
        goal=current.goal,
        pending_clarification=current.pending_clarification,
        last_router_status=current.last_router_status,
        policy_context=current.policy_context,
        surface_profile=current.surface_profile,
        contract_version=current.contract_version,
        pending_elicitation_id=current.pending_elicitation_id,
        pending_workflow_name=current.pending_workflow_name,
        partial_answers=current.partial_answers,
        pending_question_set_id=current.pending_question_set_id,
        last_elicitation_action=current.last_elicitation_action,
        last_router_disposition=router_disposition,
        last_router_error=error,
        reference_images=current.reference_images,
        guided_handoff=current.guided_handoff,
        guided_flow_state=current.guided_flow_state,
        guided_part_registry=current.guided_part_registry,
        pending_reference_images=current.pending_reference_images,
    )


def replace_session_pending_reference_images(
    ctx: Context,
    pending_reference_images: list[dict[str, Any]] | None,
) -> SessionCapabilityState:
    """Replace the pending reference images kept before a goal is active."""

    current = get_session_capability_state(ctx)
    state = SessionCapabilityState(
        phase=current.phase,
        goal=current.goal,
        pending_clarification=current.pending_clarification,
        last_router_status=current.last_router_status,
        policy_context=current.policy_context,
        surface_profile=current.surface_profile,
        contract_version=current.contract_version,
        pending_elicitation_id=current.pending_elicitation_id,
        pending_workflow_name=current.pending_workflow_name,
        partial_answers=current.partial_answers,
        pending_question_set_id=current.pending_question_set_id,
        last_elicitation_action=current.last_elicitation_action,
        last_router_disposition=current.last_router_disposition,
        last_router_error=current.last_router_error,
        reference_images=current.reference_images,
        guided_handoff=current.guided_handoff,
        guided_flow_state=current.guided_flow_state,
        guided_part_registry=current.guided_part_registry,
        pending_reference_images=pending_reference_images or None,
    )
    set_session_capability_state(ctx, state)
    return state


async def replace_session_pending_reference_images_async(
    ctx: Context,
    pending_reference_images: list[dict[str, Any]] | None,
) -> SessionCapabilityState:
    """Async variant of pending reference-image replacement."""

    current = await get_session_capability_state_async(ctx)
    state = SessionCapabilityState(
        phase=current.phase,
        goal=current.goal,
        pending_clarification=current.pending_clarification,
        last_router_status=current.last_router_status,
        policy_context=current.policy_context,
        surface_profile=current.surface_profile,
        contract_version=current.contract_version,
        pending_elicitation_id=current.pending_elicitation_id,
        pending_workflow_name=current.pending_workflow_name,
        partial_answers=current.partial_answers,
        pending_question_set_id=current.pending_question_set_id,
        last_elicitation_action=current.last_elicitation_action,
        last_router_disposition=current.last_router_disposition,
        last_router_error=current.last_router_error,
        reference_images=current.reference_images,
        guided_handoff=current.guided_handoff,
        guided_flow_state=current.guided_flow_state,
        guided_part_registry=current.guided_part_registry,
        pending_reference_images=pending_reference_images or None,
    )
    await set_session_capability_state_async(ctx, state)
    return state


def _mark_guided_spatial_state_stale_dict(
    flow_state: dict[str, Any],
    *,
    tool_name: str,
    reason: str,
    part_registry: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    contract = GuidedFlowStateContract.model_validate(flow_state)

    if (
        tool_name != "scene_clean_scene"
        and contract.active_target_scope is None
        and contract.last_spatial_check_version is None
    ):
        return contract.model_dump(mode="json")

    contract.spatial_state_version += 1
    contract.spatial_state_stale = True
    contract.last_spatial_mutation_reason = reason

    if tool_name == "scene_clean_scene":
        contract.current_step = "bootstrap_primary_workset"
        contract.completed_steps = [
            step
            for step in contract.completed_steps
            if step in {"understand_goal", "establish_reference_context", "bootstrap_primary_workset"}
        ]
        contract.completed_roles = []
        contract.role_counts = {}
        contract.role_cardinality = {}
        contract.role_objects = {}
        contract.active_target_scope = None
        contract.spatial_scope_fingerprint = None
        contract.last_spatial_check_version = None
        contract.spatial_refresh_required = False
        contract.spatial_state_stale = False
        contract.required_checks = []
        contract.blocked_families = []
        _flow_state_for_current_step(contract, part_registry=part_registry)
        return contract.model_dump(mode="json")

    _apply_spatial_refresh_gate(contract, part_registry=part_registry)
    role_summary = _build_role_summary(
        domain_profile=contract.domain_profile,
        current_step=contract.current_step,
        part_registry=part_registry,
        completed_role_hints=contract.completed_roles,
    )
    _apply_role_summary(contract, role_summary)
    return contract.model_dump(mode="json")


def mark_guided_spatial_state_stale(
    ctx: Context,
    *,
    tool_name: str,
    family: str | None = None,
    reason: str | None = None,
) -> SessionCapabilityState:
    """Mark the active guided flow's spatial facts stale after one scene mutation."""

    dirty_family = family in _SPATIAL_STATE_DIRTY_FAMILIES if isinstance(family, str) else False
    if tool_name not in _SPATIAL_STATE_DIRTY_TOOL_NAMES and not dirty_family:
        return get_session_capability_state(ctx)

    current = get_session_capability_state(ctx)
    if current.guided_flow_state is None:
        return current

    updated_registry = None if tool_name == "scene_clean_scene" else current.guided_part_registry
    updated_flow_state = _mark_guided_spatial_state_stale_dict(
        current.guided_flow_state,
        tool_name=tool_name,
        reason=reason or tool_name,
        part_registry=updated_registry,
    )
    state = SessionCapabilityState(
        phase=current.phase,
        goal=current.goal,
        pending_clarification=current.pending_clarification,
        last_router_status=current.last_router_status,
        policy_context=current.policy_context,
        surface_profile=current.surface_profile,
        contract_version=current.contract_version,
        pending_elicitation_id=current.pending_elicitation_id,
        pending_workflow_name=current.pending_workflow_name,
        partial_answers=current.partial_answers,
        pending_question_set_id=current.pending_question_set_id,
        last_elicitation_action=current.last_elicitation_action,
        last_router_disposition=current.last_router_disposition,
        last_router_error=current.last_router_error,
        reference_images=current.reference_images,
        guided_handoff=current.guided_handoff,
        guided_flow_state=updated_flow_state,
        guided_part_registry=updated_registry,
        pending_reference_images=current.pending_reference_images,
    )
    set_session_capability_state(ctx, state)
    return state


async def register_guided_part_role_async(
    ctx: Context,
    *,
    object_name: str,
    role: str,
    role_group: str | None = None,
) -> SessionCapabilityState:
    """Register or update one guided part role for the active guided session."""

    current = await get_session_capability_state_async(ctx)
    if current.guided_flow_state is None:
        raise ValueError("guided_register_part(...) requires an active guided flow session.")

    flow_state = GuidedFlowStateContract.model_validate(current.guided_flow_state)
    domain_profile = flow_state.domain_profile
    resolved_role = role.strip()
    if not resolved_role:
        raise ValueError("guided_register_part(...) requires a non-empty `role`.")
    resolved_role_group = _resolve_guided_role_group(
        domain_profile=domain_profile,
        role=resolved_role,
        role_group=role_group,
    )
    normalized_object_name = _normalize_guided_object_name(object_name)
    updated_registry = [
        item
        for item in list(current.guided_part_registry or [])
        if isinstance(item, dict) and item.get("object_name") != normalized_object_name
    ]
    updated_registry.append(
        asdict(
            GuidedPartRegistryItem(
                object_name=normalized_object_name,
                role=resolved_role,
                role_group=resolved_role_group,
                status="registered",
                created_in_step=flow_state.current_step,
            )
        )
    )
    updated_flow_state = _update_guided_flow_role_summary_dict(
        current.guided_flow_state,
        part_registry=updated_registry,
    )
    updated_flow_state = _maybe_advance_guided_flow_from_part_registry_dict(
        updated_flow_state,
        part_registry=updated_registry,
    )
    state = SessionCapabilityState(
        phase=current.phase,
        goal=current.goal,
        pending_clarification=current.pending_clarification,
        last_router_status=current.last_router_status,
        policy_context=current.policy_context,
        surface_profile=current.surface_profile,
        contract_version=current.contract_version,
        pending_elicitation_id=current.pending_elicitation_id,
        pending_workflow_name=current.pending_workflow_name,
        partial_answers=current.partial_answers,
        pending_question_set_id=current.pending_question_set_id,
        last_elicitation_action=current.last_elicitation_action,
        last_router_disposition=current.last_router_disposition,
        last_router_error=current.last_router_error,
        reference_images=current.reference_images,
        guided_handoff=current.guided_handoff,
        guided_flow_state=updated_flow_state,
        guided_part_registry=updated_registry,
        pending_reference_images=current.pending_reference_images,
    )
    await set_session_capability_state_async(ctx, state)
    return state


def register_guided_part_role(
    ctx: Context,
    *,
    object_name: str,
    role: str,
    role_group: str | None = None,
) -> SessionCapabilityState:
    """Sync variant of guided part-role registration for synchronous tool wrappers."""

    current = get_session_capability_state(ctx)
    if current.guided_flow_state is None:
        raise ValueError("guided_register_part(...) requires an active guided flow session.")

    flow_state = GuidedFlowStateContract.model_validate(current.guided_flow_state)
    domain_profile = flow_state.domain_profile
    resolved_role = role.strip()
    if not resolved_role:
        raise ValueError("guided_register_part(...) requires a non-empty `role`.")
    resolved_role_group = _resolve_guided_role_group(
        domain_profile=domain_profile,
        role=resolved_role,
        role_group=role_group,
    )
    normalized_object_name = _normalize_guided_object_name(object_name)
    updated_registry = [
        item
        for item in list(current.guided_part_registry or [])
        if isinstance(item, dict) and item.get("object_name") != normalized_object_name
    ]
    updated_registry.append(
        asdict(
            GuidedPartRegistryItem(
                object_name=normalized_object_name,
                role=resolved_role,
                role_group=resolved_role_group,
                status="registered",
                created_in_step=flow_state.current_step,
            )
        )
    )
    updated_flow_state = _update_guided_flow_role_summary_dict(
        current.guided_flow_state,
        part_registry=updated_registry,
    )
    updated_flow_state = _maybe_advance_guided_flow_from_part_registry_dict(
        updated_flow_state,
        part_registry=updated_registry,
    )
    state = SessionCapabilityState(
        phase=current.phase,
        goal=current.goal,
        pending_clarification=current.pending_clarification,
        last_router_status=current.last_router_status,
        policy_context=current.policy_context,
        surface_profile=current.surface_profile,
        contract_version=current.contract_version,
        pending_elicitation_id=current.pending_elicitation_id,
        pending_workflow_name=current.pending_workflow_name,
        partial_answers=current.partial_answers,
        pending_question_set_id=current.pending_question_set_id,
        last_elicitation_action=current.last_elicitation_action,
        last_router_disposition=current.last_router_disposition,
        last_router_error=current.last_router_error,
        reference_images=current.reference_images,
        guided_handoff=current.guided_handoff,
        guided_flow_state=updated_flow_state,
        guided_part_registry=updated_registry,
        pending_reference_images=current.pending_reference_images,
    )
    set_session_capability_state(ctx, state)
    return state


def rename_guided_part_registration(
    ctx: Context,
    *,
    old_name: str,
    new_name: str,
) -> SessionCapabilityState:
    """Keep guided part registration aligned with one successful scene object rename."""

    current = get_session_capability_state(ctx)
    if current.guided_part_registry is None:
        return current

    normalized_old_name = str(old_name or "").strip()
    normalized_new_name = require_existing_scene_object_name(new_name)
    if not normalized_old_name or normalized_old_name == normalized_new_name:
        return current

    changed = False
    updated_registry: list[dict[str, Any]] = []
    for item in list(current.guided_part_registry or []):
        if not isinstance(item, dict):
            continue
        updated_item = dict(item)
        if updated_item.get("object_name") == normalized_old_name:
            updated_item["object_name"] = normalized_new_name
            changed = True
        updated_registry.append(updated_item)

    if not changed:
        return current

    updated_flow_state = (
        _update_guided_flow_role_summary_dict(current.guided_flow_state, part_registry=updated_registry)
        if current.guided_flow_state is not None
        else None
    )
    state = SessionCapabilityState(
        phase=current.phase,
        goal=current.goal,
        pending_clarification=current.pending_clarification,
        last_router_status=current.last_router_status,
        policy_context=current.policy_context,
        surface_profile=current.surface_profile,
        contract_version=current.contract_version,
        pending_elicitation_id=current.pending_elicitation_id,
        pending_workflow_name=current.pending_workflow_name,
        partial_answers=current.partial_answers,
        pending_question_set_id=current.pending_question_set_id,
        last_elicitation_action=current.last_elicitation_action,
        last_router_disposition=current.last_router_disposition,
        last_router_error=current.last_router_error,
        reference_images=current.reference_images,
        guided_handoff=current.guided_handoff,
        guided_flow_state=updated_flow_state,
        guided_part_registry=updated_registry,
        pending_reference_images=current.pending_reference_images,
    )
    set_session_capability_state(ctx, state)
    return state


def remove_guided_part_registrations(
    ctx: Context,
    *,
    object_names: list[str],
) -> SessionCapabilityState:
    """Remove guided part registrations for objects whose topology/identity changed materially."""

    current = get_session_capability_state(ctx)
    if current.guided_part_registry is None:
        return current

    names_to_remove = {str(name).strip() for name in object_names if str(name).strip()}
    if not names_to_remove:
        return current

    updated_registry = [
        dict(item)
        for item in list(current.guided_part_registry or [])
        if isinstance(item, dict) and str(item.get("object_name") or "").strip() not in names_to_remove
    ]
    if len(updated_registry) == len(list(current.guided_part_registry or [])):
        return current

    updated_flow_state = None
    if current.guided_flow_state is not None:
        contract = GuidedFlowStateContract.model_validate(current.guided_flow_state)
        contract.completed_roles = []
        contract.role_counts = {}
        contract.role_cardinality = {}
        contract.role_objects = {}
        updated_flow_state = _update_guided_flow_role_summary_dict(
            contract.model_dump(mode="json"),
            part_registry=updated_registry or None,
        )
    state = SessionCapabilityState(
        phase=current.phase,
        goal=current.goal,
        pending_clarification=current.pending_clarification,
        last_router_status=current.last_router_status,
        policy_context=current.policy_context,
        surface_profile=current.surface_profile,
        contract_version=current.contract_version,
        pending_elicitation_id=current.pending_elicitation_id,
        pending_workflow_name=current.pending_workflow_name,
        partial_answers=current.partial_answers,
        pending_question_set_id=current.pending_question_set_id,
        last_elicitation_action=current.last_elicitation_action,
        last_router_disposition=current.last_router_disposition,
        last_router_error=current.last_router_error,
        reference_images=current.reference_images,
        guided_handoff=current.guided_handoff,
        guided_flow_state=updated_flow_state,
        guided_part_registry=updated_registry or None,
        pending_reference_images=current.pending_reference_images,
    )
    set_session_capability_state(ctx, state)
    return state


def _mark_guided_flow_check_completed_dict(
    flow_state: dict[str, Any],
    *,
    tool_name: str,
    resolved_scope: dict[str, Any] | None = None,
    part_registry: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    contract = GuidedFlowStateContract.model_validate(flow_state)
    normalized_scope = _normalize_guided_target_scope(resolved_scope)
    resolved_scope_fingerprint = _build_guided_target_scope_fingerprint(normalized_scope)
    changed = False

    if normalized_scope is None:
        for check in contract.required_checks:
            if check.tool_name == tool_name and check.status != "completed":
                check.status = "completed"
                changed = True

        if (
            changed
            and contract.required_checks
            and all(check.status == "completed" for check in contract.required_checks)
        ):
            if contract.spatial_refresh_required:
                _clear_spatial_refresh_gate(contract, part_registry=part_registry)
            elif contract.current_step == "establish_spatial_context":
                if "establish_spatial_context" not in contract.completed_steps:
                    contract.completed_steps.append("establish_spatial_context")
                contract.current_step = "create_primary_masses"
                contract.last_spatial_check_version = contract.spatial_state_version
                contract.spatial_state_stale = False
                contract.blocked_families = []
                _flow_state_for_current_step(contract, part_registry=part_registry)
        return contract.model_dump(mode="json")

    if tool_name == _GUIDED_SCOPE_BINDING_TOOL_NAME and normalized_scope is not None:
        should_rebind = contract.active_target_scope is None or contract.spatial_refresh_required
        if should_rebind and _is_bindable_guided_target_scope(normalized_scope):
            contract.active_target_scope = GuidedTargetScopeContract.model_validate(normalized_scope)
            contract.spatial_scope_fingerprint = resolved_scope_fingerprint

    if contract.active_target_scope is None:
        return contract.model_dump(mode="json")
    if contract.spatial_refresh_required and tool_name != _GUIDED_SCOPE_BINDING_TOOL_NAME:
        scope_check = next(
            (check for check in contract.required_checks if check.tool_name == _GUIDED_SCOPE_BINDING_TOOL_NAME),
            None,
        )
        if scope_check is not None and scope_check.status != "completed":
            return contract.model_dump(mode="json")

    active_scope_fingerprint = contract.spatial_scope_fingerprint or _build_guided_target_scope_fingerprint(
        contract.active_target_scope.model_dump(mode="json")
    )
    if active_scope_fingerprint is None:
        return contract.model_dump(mode="json")
    contract.spatial_scope_fingerprint = active_scope_fingerprint

    if resolved_scope_fingerprint is None or resolved_scope_fingerprint != active_scope_fingerprint:
        return contract.model_dump(mode="json")

    for check in contract.required_checks:
        if check.tool_name == tool_name and check.status != "completed":
            check.status = "completed"
            changed = True

    if changed and contract.required_checks and all(check.status == "completed" for check in contract.required_checks):
        if contract.spatial_refresh_required:
            _clear_spatial_refresh_gate(contract, part_registry=part_registry)
        elif contract.current_step == "establish_spatial_context":
            if "establish_spatial_context" not in contract.completed_steps:
                contract.completed_steps.append("establish_spatial_context")
            contract.current_step = "create_primary_masses"
            contract.last_spatial_check_version = contract.spatial_state_version
            contract.spatial_state_stale = False
            contract.blocked_families = []
            _flow_state_for_current_step(contract, part_registry=part_registry)

    return contract.model_dump(mode="json")


def record_guided_flow_spatial_check_completion(
    ctx: Context,
    *,
    tool_name: str,
    resolved_scope: dict[str, Any] | None = None,
) -> SessionCapabilityState:
    """Mark one spatial-context check as completed and advance the flow when ready."""

    if tool_name not in _SPATIAL_CONTEXT_TOOL_NAMES:
        return get_session_capability_state(ctx)

    current = get_session_capability_state(ctx)
    if current.guided_flow_state is None:
        return current

    updated_flow_state = _mark_guided_flow_check_completed_dict(
        current.guided_flow_state,
        tool_name=tool_name,
        resolved_scope=resolved_scope,
        part_registry=current.guided_part_registry,
    )
    state = SessionCapabilityState(
        phase=current.phase,
        goal=current.goal,
        pending_clarification=current.pending_clarification,
        last_router_status=current.last_router_status,
        policy_context=current.policy_context,
        surface_profile=current.surface_profile,
        contract_version=current.contract_version,
        pending_elicitation_id=current.pending_elicitation_id,
        pending_workflow_name=current.pending_workflow_name,
        partial_answers=current.partial_answers,
        pending_question_set_id=current.pending_question_set_id,
        last_elicitation_action=current.last_elicitation_action,
        last_router_disposition=current.last_router_disposition,
        last_router_error=current.last_router_error,
        reference_images=current.reference_images,
        guided_handoff=current.guided_handoff,
        guided_flow_state=updated_flow_state,
        guided_part_registry=current.guided_part_registry,
        pending_reference_images=current.pending_reference_images,
    )
    set_session_capability_state(ctx, state)
    return state


async def record_guided_flow_spatial_check_completion_async(
    ctx: Context,
    *,
    tool_name: str,
    resolved_scope: dict[str, Any] | None = None,
) -> SessionCapabilityState:
    """Async variant of spatial-check completion recording."""

    if tool_name not in _SPATIAL_CONTEXT_TOOL_NAMES:
        return await get_session_capability_state_async(ctx)

    current = await get_session_capability_state_async(ctx)
    if current.guided_flow_state is None:
        return current

    updated_flow_state = _mark_guided_flow_check_completed_dict(
        current.guided_flow_state,
        tool_name=tool_name,
        resolved_scope=resolved_scope,
        part_registry=current.guided_part_registry,
    )
    state = SessionCapabilityState(
        phase=current.phase,
        goal=current.goal,
        pending_clarification=current.pending_clarification,
        last_router_status=current.last_router_status,
        policy_context=current.policy_context,
        surface_profile=current.surface_profile,
        contract_version=current.contract_version,
        pending_elicitation_id=current.pending_elicitation_id,
        pending_workflow_name=current.pending_workflow_name,
        partial_answers=current.partial_answers,
        pending_question_set_id=current.pending_question_set_id,
        last_elicitation_action=current.last_elicitation_action,
        last_router_disposition=current.last_router_disposition,
        last_router_error=current.last_router_error,
        reference_images=current.reference_images,
        guided_handoff=current.guided_handoff,
        guided_flow_state=updated_flow_state,
        guided_part_registry=current.guided_part_registry,
        pending_reference_images=current.pending_reference_images,
    )
    await set_session_capability_state_async(ctx, state)
    return state


def _advance_guided_flow_for_iteration_dict(
    flow_state: dict[str, Any],
    *,
    loop_disposition: str,
    part_registry: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    contract = GuidedFlowStateContract.model_validate(flow_state)
    current_step = contract.current_step
    if current_step not in contract.completed_steps and current_step not in _GUIDED_FLOW_STOPPED_STEPS:
        contract.completed_steps.append(current_step)

    if loop_disposition == "inspect_validate":
        contract.current_step = "inspect_validate"
        contract.blocked_families = ["late_refinement", "finish"]
    elif loop_disposition == "stop":
        contract.current_step = "finish_or_stop"
        contract.blocked_families = []
    else:
        if current_step == "create_primary_masses":
            contract.current_step = "place_secondary_parts"
        else:
            contract.current_step = "checkpoint_iterate"
        contract.blocked_families = []
    _flow_state_for_current_step(contract, part_registry=part_registry)
    if contract.spatial_state_stale:
        _apply_spatial_refresh_gate(contract, part_registry=part_registry, force=True)
    return contract.model_dump(mode="json")


async def advance_guided_flow_from_iteration_async(
    ctx: Context,
    *,
    loop_disposition: str,
) -> SessionCapabilityState:
    """Advance the guided flow state from a compare/iterate loop result."""

    current = await get_session_capability_state_async(ctx)
    if current.guided_flow_state is None:
        return current

    updated_flow_state = _advance_guided_flow_for_iteration_dict(
        current.guided_flow_state,
        loop_disposition=loop_disposition,
        part_registry=current.guided_part_registry,
    )
    next_phase = current.phase
    if loop_disposition == "inspect_validate":
        next_phase = SessionPhase.INSPECT_VALIDATE
    elif current.phase == SessionPhase.INSPECT_VALIDATE and loop_disposition != "inspect_validate":
        next_phase = SessionPhase.BUILD
    state = SessionCapabilityState(
        phase=next_phase,
        goal=current.goal,
        pending_clarification=current.pending_clarification,
        last_router_status=current.last_router_status,
        policy_context=current.policy_context,
        surface_profile=current.surface_profile,
        contract_version=current.contract_version,
        pending_elicitation_id=current.pending_elicitation_id,
        pending_workflow_name=current.pending_workflow_name,
        partial_answers=current.partial_answers,
        pending_question_set_id=current.pending_question_set_id,
        last_elicitation_action=current.last_elicitation_action,
        last_router_disposition=current.last_router_disposition,
        last_router_error=current.last_router_error,
        reference_images=current.reference_images,
        guided_handoff=current.guided_handoff,
        guided_flow_state=updated_flow_state,
        guided_part_registry=current.guided_part_registry,
        pending_reference_images=current.pending_reference_images,
    )
    await set_session_capability_state_async(ctx, state)
    return state
