"""
Router Helper for MCP Tools.

Provides utilities for routing tool calls through SupervisorRouter.
"""

import logging
import re
from ast import literal_eval
from typing import Any, Callable, Dict, List, Literal, Optional, cast

from server.adapters.mcp.context_utils import ctx_warning
from server.adapters.mcp.contracts.correction_audit import (
    CorrectionAuditEventContract,
    CorrectionExecutionContract,
    CorrectionIntentContract,
    CorrectionVerificationContract,
)
from server.adapters.mcp.dispatcher import get_dispatcher
from server.adapters.mcp.execution_context import MCPExecutionContext
from server.adapters.mcp.execution_report import ExecutionStep, MCPExecutionReport
from server.adapters.mcp.guided_naming_policy import evaluate_guided_object_name
from server.adapters.mcp.session_capabilities import (
    get_session_capability_state,
    is_guided_spatial_state_dirtying_operation,
    mark_guided_spatial_state_stale,
    record_router_execution_outcome,
    remove_guided_part_registrations,
    rename_guided_part_registration,
    resolve_guided_role_group_for_domain,
)
from server.adapters.mcp.session_state import set_session_value
from server.adapters.mcp.transforms.visibility_policy import GUIDED_SPATIAL_SUPPORT_TOOLS, resolve_guided_tool_family
from server.infrastructure.config import get_config
from server.infrastructure.di import get_postcondition_registry, get_router, get_scene_handler, is_router_enabled
from server.router.domain.entities.correction_policy import CorrectionCategory
from server.router.infrastructure.logger import get_router_logger

logger = logging.getLogger(__name__)

SESSION_LAST_ROUTER_DISPOSITION_KEY = "last_router_disposition"
SESSION_LAST_ROUTER_ERROR_KEY = "last_router_error"
ROUTER_BYPASS_PREFIXES: tuple[str, ...] = ("scene_",)
_GUIDED_ROLE_REQUIRED_TOOLS: tuple[str, ...] = (
    "modeling_create_primitive",
    "modeling_transform_object",
)
_GUIDED_UNMAPPED_MUTATING_PREFIXES: tuple[str, ...] = (
    "modeling_",
    "mesh_",
    "macro_",
    "material_",
    "uv_",
)
_GUIDED_UNMAPPED_NON_MUTATING_TOOLS: frozenset[str] = frozenset(
    {
        "modeling_list_modifiers",
        "mesh_inspect",
        "mesh_list_groups",
        "material_list",
        "material_list_by_object",
        "material_inspect_nodes",
        "uv_list_maps",
    }
)
_GUIDED_UNMAPPED_NON_MUTATING_PREFIXES: tuple[str, ...] = (
    "mesh_get_",
    "mesh_select",
)
_GUIDED_POLICY_ONLY_PARAM_NAMES: frozenset[str] = frozenset({"guided_role", "role_group"})
_GUIDED_PINNED_SPATIAL_HELPER_TOOLS: frozenset[str] = frozenset(GUIDED_SPATIAL_SUPPORT_TOOLS)
_CREATED_OBJECT_RESULT_PATTERN = re.compile(r"^Created .+ named '(.+?)'$")
_TRANSFORMED_OBJECT_RESULT_PATTERN = re.compile(r"^Transformed object '(.+?)'$")
_JOINED_OBJECT_RESULT_PATTERN = re.compile(r"^Objects .+ joined into '(.+?)'\. Joined count: \d+$")
_RENAMED_OBJECT_RESULT_PATTERN = re.compile(r"^Renamed '.*' to '(.+?)'(?: .*)?$")


def _is_unmapped_guided_mutating_tool(tool_name: str) -> bool:
    """Return True when a guided mutator has no family and must fail closed."""

    if resolve_guided_tool_family(tool_name) is not None:
        return False
    if tool_name in _GUIDED_UNMAPPED_NON_MUTATING_TOOLS:
        return False
    if tool_name.startswith(_GUIDED_UNMAPPED_NON_MUTATING_PREFIXES):
        return False
    return tool_name.startswith(_GUIDED_UNMAPPED_MUTATING_PREFIXES)


def _strip_guided_policy_params_for_dispatch(params: Dict[str, Any]) -> Dict[str, Any]:
    """Remove MCP guided policy-only fields before application-handler dispatch."""

    if not any(name in params for name in _GUIDED_POLICY_ONLY_PARAM_NAMES):
        return params
    return {key: value for key, value in params.items() if key not in _GUIDED_POLICY_ONLY_PARAM_NAMES}


def _result_represents_success(tool_name: str, result: Any) -> bool:
    if result is None:
        return False

    if isinstance(result, str):
        text = result.strip()
        if tool_name == "scene_clean_scene":
            return text.lower().startswith("scene cleaned")
        if tool_name == "modeling_create_primitive":
            return _CREATED_OBJECT_RESULT_PATTERN.fullmatch(text) is not None
        if tool_name == "modeling_transform_object":
            return _TRANSFORMED_OBJECT_RESULT_PATTERN.fullmatch(text) is not None
        if tool_name == "scene_duplicate_object":
            try:
                parsed = literal_eval(text)
            except (SyntaxError, ValueError):
                return False
            return isinstance(parsed, dict) and bool(parsed.get("new_object") or parsed.get("name"))
        if tool_name == "scene_rename_object":
            return _RENAMED_OBJECT_RESULT_PATTERN.fullmatch(text) is not None
        if tool_name == "modeling_join_objects":
            return _JOINED_OBJECT_RESULT_PATTERN.fullmatch(text) is not None
        if tool_name == "modeling_separate_object":
            try:
                parsed = literal_eval(text)
            except (SyntaxError, ValueError):
                return False
            return isinstance(parsed, list) and all(isinstance(item, str) for item in parsed)
        mesh_success_prefixes = {
            "mesh_extrude_region": ("extruded region",),
            "mesh_loop_cut": ("subdivided selected geometry",),
            "mesh_bevel": ("bevel applied",),
            "mesh_symmetrize": ("symmetrized mesh",),
            "mesh_merge_by_distance": ("merged vertices by distance",),
            "mesh_dissolve": (
                "limited dissolve",
                "dissolved selected vertices",
                "dissolved selected edges",
                "dissolved selected faces",
            ),
        }
        prefixes = mesh_success_prefixes.get(tool_name)
        if prefixes is not None:
            return text.lower().startswith(prefixes)
        return False

    if isinstance(result, dict):
        status = str(result.get("status") or "").strip().lower()
        if status in {"failed", "blocked", "error"}:
            return False
        if status == "partial":
            return True
        if result.get("objects_modified"):
            return True
        if result.get("error") is not None:
            return False
        return True

    status = str(getattr(result, "status", "") or "").strip().lower()
    if status in {"failed", "blocked", "error"}:
        return False
    if status == "partial":
        return True
    if getattr(result, "objects_modified", None):
        return True
    if getattr(result, "error", None) is not None:
        return False
    return True


def _maybe_mark_guided_spatial_state_stale_from_report(report: MCPExecutionReport) -> None:
    """Mark guided spatial state stale after one successful scene mutation."""

    if report.error is not None or not report.steps:
        return

    dirty_step: ExecutionStep | None = None
    dirty_family: str | None = None
    for step in report.steps:
        if step.error is not None:
            continue
        if not _result_represents_success(step.tool_name, step.result):
            continue
        step_family = resolve_guided_tool_family(step.tool_name)
        if not is_guided_spatial_state_dirtying_operation(tool_name=step.tool_name, family=step_family):
            continue
        dirty_step = step
        dirty_family = step_family
        break

    if dirty_step is None:
        return

    current_ctx = _get_active_context()
    if current_ctx is None:
        return

    try:
        mark_guided_spatial_state_stale(
            current_ctx,
            tool_name=dirty_step.tool_name,
            family=dirty_family,
            reason=dirty_step.tool_name,
        )
    except Exception:
        return


def _renamed_object_name_from_result(result: Any) -> str | None:
    if not isinstance(result, str):
        return None
    match = _RENAMED_OBJECT_RESULT_PATTERN.match(result.strip())
    if match is None:
        return None
    object_name = match.group(1).strip()
    return object_name or None


def _maybe_sync_guided_part_registry_from_report(report: MCPExecutionReport) -> None:
    """Update guided part registration after successful scene-identity mutations."""

    if report.error is not None or not report.steps:
        return

    final_step = report.steps[-1]
    if final_step.tool_name not in {"scene_rename_object", "modeling_join_objects", "modeling_separate_object"}:
        return
    if final_step.error is not None:
        return
    if not _result_represents_success(final_step.tool_name, final_step.result):
        return

    current_ctx = _get_active_context()
    if current_ctx is None:
        return

    if final_step.tool_name == "scene_rename_object":
        old_name = final_step.params.get("old_name")
        new_name = _renamed_object_name_from_result(final_step.result) or final_step.params.get("new_name")
        if not isinstance(old_name, str) or not old_name.strip():
            return
        if not isinstance(new_name, str) or not new_name.strip():
            return

        try:
            rename_guided_part_registration(
                current_ctx,
                old_name=old_name,
                new_name=new_name,
            )
        except Exception:
            return
        return

    if final_step.tool_name == "modeling_join_objects":
        object_names = final_step.params.get("object_names")
        if not isinstance(object_names, list):
            return
        try:
            remove_guided_part_registrations(
                current_ctx,
                object_names=[str(name) for name in object_names if str(name).strip()],
            )
        except Exception:
            return
        return

    source_name = final_step.params.get("name")
    if not isinstance(source_name, str) or not source_name.strip():
        return
    try:
        remove_guided_part_registrations(
            current_ctx,
            object_names=[source_name],
        )
    except Exception:
        return


def _get_active_surface_profile() -> str:
    """Return the active surface profile for the current tool call."""

    try:
        from fastmcp.server.context import _current_context  # type: ignore

        current_ctx = _current_context.get(None)
        if current_ctx is not None:
            server = current_ctx.fastmcp
            return getattr(server, "_bam_surface_profile", get_config().MCP_SURFACE_PROFILE)
    except Exception:
        pass

    return get_config().MCP_SURFACE_PROFILE


def _should_fail_closed_on_router_error(surface_profile: str) -> bool:
    """Guided/product surfaces fail closed; explicit compatibility stays fail-open."""

    return surface_profile != "legacy-flat"


def _should_bypass_router_for_tool(tool_name: str) -> bool:
    """Return True when one public tool family should never be workflow-triggered."""

    return any(tool_name.startswith(prefix) for prefix in ROUTER_BYPASS_PREFIXES)


def _build_correction_audit_events(
    *,
    original_tool_name: str,
    original_params: Dict[str, Any],
    corrected_tools: List[Dict[str, Any]],
    steps: List[ExecutionStep],
    policy_context: dict[str, Any] | None = None,
) -> tuple[CorrectionAuditEventContract, ...]:
    """Build coarse audit events for router-applied sequence changes."""

    if not corrected_tools or not steps:
        return ()

    events: list[CorrectionAuditEventContract] = []
    for index, (tool, step) in enumerate(zip(corrected_tools, steps), 1):
        corrected_tool_name = tool["tool"]
        corrected_params = tool["params"]

        if corrected_tool_name == "system_set_mode" and original_tool_name != "system_set_mode":
            category = "precondition_mode"
        elif corrected_tool_name in {"mesh_select", "mesh_select_targeted"} and original_tool_name not in {
            "mesh_select",
            "mesh_select_targeted",
        }:
            category = "precondition_selection"
        elif corrected_tool_name == "scene_set_active_object" and original_tool_name != "scene_set_active_object":
            category = "precondition_active_object"
        elif len(corrected_tools) > 1 and corrected_tool_name != original_tool_name:
            category = "workflow_expansion"
        elif corrected_tool_name != original_tool_name:
            category = "tool_override"
        elif corrected_params != original_params:
            category = "parameter_rewrite"
        else:
            continue

        events.append(
            CorrectionAuditEventContract(
                event_id=f"audit_{index}",
                decision=policy_context.get("decision") if policy_context else None,
                reason=policy_context.get("reason") if policy_context else None,
                confidence=policy_context,
                intent=CorrectionIntentContract(
                    original_tool_name=original_tool_name,
                    original_params=original_params,
                    corrected_tool_name=corrected_tool_name,
                    corrected_params=corrected_params,
                    category=category,
                ),
                execution=CorrectionExecutionContract(
                    tool_name=step.tool_name,
                    params=step.params,
                    result=step.result,
                    error=step.error,
                ),
                verification=CorrectionVerificationContract(),
            )
        )
    return tuple(events)


def _extract_audit_ids(
    audit_events: tuple[CorrectionAuditEventContract, ...],
) -> tuple[str, ...]:
    """Return stable audit identifiers for exposure in reports and logs."""

    return tuple(event.event_id for event in audit_events)


def _log_audit_exposure(report: MCPExecutionReport) -> None:
    """Emit one structured log line for correction audit visibility."""

    if not report.audit_ids and report.router_disposition in {"bypassed", "direct"}:
        return

    get_router_logger().log_execution_audit(
        tool_name=report.context.tool_name,
        disposition=report.router_disposition,
        verification_status=report.verification_status,
        audit_ids=list(report.audit_ids),
    )


def _record_router_execution_report(report: MCPExecutionReport) -> None:
    """Persist the last router execution outcome in session state when available."""

    try:
        from fastmcp.server.context import _current_context  # type: ignore

        current_ctx = _current_context.get(None)
    except Exception:
        current_ctx = None

    if current_ctx is None:
        return

    try:
        record_router_execution_outcome(
            current_ctx,
            router_disposition=report.router_disposition,
            error=report.error,
        )
    except Exception:
        try:
            set_session_value(current_ctx, SESSION_LAST_ROUTER_DISPOSITION_KEY, report.router_disposition)
            set_session_value(current_ctx, SESSION_LAST_ROUTER_ERROR_KEY, report.error)
        except Exception:
            return


def _get_active_session_state():
    """Best-effort current MCP session state lookup for execution-policy metadata."""

    try:
        from fastmcp.server.context import _current_context  # type: ignore

        current_ctx = _current_context.get(None)
    except Exception:
        current_ctx = None

    if current_ctx is None:
        return None

    try:
        return get_session_capability_state(current_ctx)
    except Exception:
        return None


def _get_active_context():
    """Best-effort current MCP Context lookup for adapter helpers."""

    try:
        from fastmcp.server.context import _current_context  # type: ignore

        return _current_context.get(None)
    except Exception:
        return None


def _resolve_guided_role_context(tool_name: str, params: Dict[str, Any]) -> tuple[str | None, str | None]:
    """Resolve guided role metadata from explicit params first, then session registry."""

    explicit_role = params.get("guided_role")
    explicit_role_group = params.get("role_group")
    if isinstance(explicit_role, str) and explicit_role.strip():
        session = _get_active_session_state()
        supplied_role_group = explicit_role_group.strip() if isinstance(explicit_role_group, str) else None
        derived_role_group = supplied_role_group
        if session is not None and session.guided_flow_state is not None:
            try:
                domain_profile = str(session.guided_flow_state.get("domain_profile") or "").strip()
                if domain_profile in {"generic", "creature", "building"}:
                    typed_domain_profile = cast(Literal["generic", "creature", "building"], domain_profile)
                    derived_role_group = resolve_guided_role_group_for_domain(
                        typed_domain_profile, explicit_role.strip(), derived_role_group
                    )
            except Exception:
                derived_role_group = None
        return explicit_role.strip(), derived_role_group

    session = _get_active_session_state()
    if session is None or not session.guided_part_registry:
        return None, None

    object_name = params.get("name") or params.get("object_name")
    if not isinstance(object_name, str) or not object_name.strip():
        return None, None

    for item in session.guided_part_registry:
        if not isinstance(item, dict):
            continue
        if item.get("object_name") != object_name:
            continue
        role = item.get("role")
        role_group = item.get("role_group")
        return (
            role.strip() if isinstance(role, str) and role.strip() else None,
            role_group.strip() if isinstance(role_group, str) and role_group.strip() else None,
        )
    return None, None


def _resolve_guided_effective_family(tool_name: str, params: Dict[str, Any]) -> str | None:
    """Resolve the effective family, allowing explicit role-group overrides for role-sensitive tools."""

    base_family = resolve_guided_tool_family(tool_name)
    _role, role_group = _resolve_guided_role_context(tool_name, params)
    if tool_name in _GUIDED_ROLE_REQUIRED_TOOLS and role_group in {
        "spatial_context",
        "reference_context",
        "primary_masses",
        "secondary_parts",
        "attachment_alignment",
        "checkpoint_iterate",
        "inspect_validate",
        "finish",
        "utility",
    }:
        return role_group
    return base_family


def _evaluate_explicit_guided_role_group_policy(
    *,
    flow_state: dict[str, Any],
    tool_name: str,
    params: Dict[str, Any],
    allowed_families: set[str],
    allowed_roles: set[str],
) -> dict[str, Any] | None:
    """Validate caller-supplied role_group against the active domain role map."""

    explicit_role = params.get("guided_role")
    explicit_role_group = params.get("role_group")
    if not isinstance(explicit_role, str) or not explicit_role.strip():
        return None
    if not isinstance(explicit_role_group, str) or not explicit_role_group.strip():
        return None

    domain_profile = str(flow_state.get("domain_profile") or "").strip()
    if domain_profile not in {"generic", "creature", "building"}:
        return None

    typed_domain_profile = cast(Literal["generic", "creature", "building"], domain_profile)
    role = explicit_role.strip()
    supplied_role_group = explicit_role_group.strip()
    try:
        expected_role_group = resolve_guided_role_group_for_domain(
            typed_domain_profile,
            role,
        )
    except ValueError as exc:
        return {
            "status": "blocked",
            "current_step": str(flow_state.get("current_step") or "").strip(),
            "family": resolve_guided_tool_family(tool_name),
            "role": role,
            "role_group": None,
            "tool_name": tool_name,
            "allowed_families": sorted(allowed_families),
            "allowed_roles": sorted(allowed_roles),
            "message": str(exc),
        }

    if supplied_role_group == expected_role_group:
        return None

    return {
        "status": "blocked",
        "current_step": str(flow_state.get("current_step") or "").strip(),
        "family": expected_role_group
        if tool_name in _GUIDED_ROLE_REQUIRED_TOOLS
        else resolve_guided_tool_family(tool_name),
        "role": role,
        "role_group": supplied_role_group,
        "expected_role_group": expected_role_group,
        "tool_name": tool_name,
        "allowed_families": sorted(allowed_families),
        "allowed_roles": sorted(allowed_roles),
        "message": (
            f"Guided execution blocked role_group '{supplied_role_group}' for role '{role}'. "
            f"Expected role_group '{expected_role_group}' for domain profile '{domain_profile}'."
        ),
    }


def _evaluate_guided_execution_policy(
    *,
    surface_profile: str,
    tool_name: str,
    params: Dict[str, Any],
) -> dict[str, Any] | None:
    """Return a typed guided execution-policy decision when one active flow exists."""

    if surface_profile != "llm-guided":
        return None

    session = _get_active_session_state()
    if session is None or not session.guided_flow_state:
        return None

    flow_state = session.guided_flow_state
    current_step = str(flow_state.get("current_step") or "").strip()
    allowed_families = {
        str(family)
        for family in (flow_state.get("allowed_families") or [])
        if isinstance(family, str) and family.strip()
    }
    allowed_roles = {
        str(role) for role in (flow_state.get("allowed_roles") or []) if isinstance(role, str) and role.strip()
    }
    role_group_policy = _evaluate_explicit_guided_role_group_policy(
        flow_state=flow_state,
        tool_name=tool_name,
        params=params,
        allowed_families=allowed_families,
        allowed_roles=allowed_roles,
    )
    if role_group_policy is not None:
        return role_group_policy

    family = _resolve_guided_effective_family(tool_name, params)
    role, role_group = _resolve_guided_role_context(tool_name, params)
    explicit_guided_role = isinstance(params.get("guided_role"), str) and str(params.get("guided_role")).strip()

    if family == "utility":
        return {
            "status": "allowed",
            "current_step": current_step,
            "family": family,
            "role": role,
            "role_group": role_group,
        }

    if family == "spatial_context" and tool_name in _GUIDED_PINNED_SPATIAL_HELPER_TOOLS:
        return {
            "status": "allowed",
            "current_step": current_step,
            "family": family,
            "role": role,
            "role_group": role_group,
        }

    if family is None and allowed_families and _is_unmapped_guided_mutating_tool(tool_name):
        return {
            "status": "blocked",
            "current_step": current_step,
            "family": family,
            "role": role,
            "role_group": role_group,
            "tool_name": tool_name,
            "allowed_families": sorted(allowed_families),
            "allowed_roles": sorted(allowed_roles),
            "message": (
                f"Guided execution blocked unmapped mutating tool '{tool_name}' during step '{current_step}'. "
                "Add it to GUIDED_TOOL_FAMILY_MAP before using it under the guided family contract. "
                f"Allowed families now: {', '.join(sorted(allowed_families)) or 'none'}."
            ),
        }

    if tool_name in _GUIDED_ROLE_REQUIRED_TOOLS and role is None:
        return {
            "status": "blocked",
            "current_step": current_step,
            "family": family,
            "role": role,
            "role_group": role_group,
            "allowed_families": sorted(allowed_families),
            "allowed_roles": sorted(allowed_roles),
            "required_role_groups": list(flow_state.get("required_role_groups") or []),
            "message": (
                f"Guided execution requires an explicit semantic role for '{tool_name}' during step '{current_step}'. "
                "Provide `guided_role=...` on the build tool call or register the object first with "
                "`guided_register_part(object_name=..., role=...)`."
            ),
        }

    if family is not None and allowed_families and family not in allowed_families:
        return {
            "status": "blocked",
            "current_step": current_step,
            "family": family,
            "role": role,
            "role_group": role_group,
            "allowed_families": sorted(allowed_families),
            "allowed_roles": sorted(allowed_roles),
            "message": (
                f"Guided execution blocked tool family '{family}' during step '{current_step}'. "
                f"Allowed families now: {', '.join(sorted(allowed_families)) or 'none'}."
            ),
        }

    if role is not None and allowed_roles and role not in allowed_roles:
        if (
            tool_name == "modeling_transform_object"
            and not explicit_guided_role
            and family in allowed_families
            and role_group == family
        ):
            return {
                "status": "allowed",
                "current_step": current_step,
                "family": family,
                "role": role,
                "role_group": role_group,
            }
        return {
            "status": "blocked",
            "current_step": current_step,
            "family": family,
            "role": role,
            "role_group": role_group,
            "allowed_families": sorted(allowed_families),
            "allowed_roles": sorted(allowed_roles),
            "message": (
                f"Guided execution blocked role '{role}' during step '{current_step}'. "
                f"Allowed roles now: {', '.join(sorted(allowed_roles)) or 'none'}."
            ),
        }

    return {
        "status": "allowed",
        "current_step": current_step,
        "family": family,
        "role": role,
        "role_group": role_group,
    }


def _evaluate_guided_naming_policy(
    *,
    surface_profile: str,
    tool_name: str,
    params: Dict[str, Any],
) -> dict[str, Any] | None:
    """Return a typed guided naming-policy decision for role-sensitive build calls."""

    if surface_profile != "llm-guided":
        return None
    if tool_name not in _GUIDED_ROLE_REQUIRED_TOOLS:
        return None

    explicit_role = params.get("guided_role")
    object_name = params.get("name") or params.get("object_name")
    if not isinstance(explicit_role, str) or not explicit_role.strip():
        return None
    if not isinstance(object_name, str) or not object_name.strip():
        return None

    session = _get_active_session_state()
    if session is None or not session.guided_flow_state:
        return None

    flow_state = session.guided_flow_state
    domain_profile = str(flow_state.get("domain_profile") or "").strip()
    if domain_profile not in {"generic", "creature", "building"}:
        return None
    current_step = str(flow_state.get("current_step") or "").strip() or None

    decision = evaluate_guided_object_name(
        object_name=object_name,
        role=explicit_role.strip(),
        domain_profile=cast(Literal["generic", "creature", "building"], domain_profile),
        current_step=current_step,
    )
    payload = decision.model_dump(mode="json")
    return {
        "status": decision.status,
        "message": decision.message,
        "guided_naming": payload,
    }


def _apply_postcondition_verification(
    audit_events: tuple[CorrectionAuditEventContract, ...],
) -> tuple[tuple[CorrectionAuditEventContract, ...], str]:
    """Evaluate inspection-based verification for registered high-risk correction events."""

    if not audit_events:
        return audit_events, "not_requested"

    registry = get_postcondition_registry()
    scene_handler = get_scene_handler()

    updated_events: list[CorrectionAuditEventContract] = []
    statuses: list[str] = []

    for event in audit_events:
        try:
            category = CorrectionCategory(event.intent.category)
        except ValueError:
            updated_events.append(event)
            continue

        requirement = registry.get(category)
        if requirement is None:
            updated_events.append(event)
            continue

        status = "inconclusive"
        details: dict[str, Any] | None = None

        try:
            if requirement.verification_key == "verify_mode":
                mode_payload = scene_handler.get_mode()
                expected_mode = event.execution.params.get("mode") or event.intent.corrected_params.get("mode")
                actual_mode = mode_payload.get("mode")
                status = "passed" if expected_mode == actual_mode else "failed"
                details = {"expected_mode": expected_mode, "actual_mode": actual_mode}
            elif requirement.verification_key == "verify_selection":
                selection_payload = scene_handler.list_selection()
                selection_count = selection_payload.get("selection_count", 0)
                status = "passed" if selection_count > 0 else "failed"
                details = {"selection_count": selection_count}
            elif requirement.verification_key == "verify_active_object":
                mode_payload = scene_handler.get_mode()
                expected_object = event.execution.params.get("name") or event.intent.corrected_params.get("name")
                actual_object = mode_payload.get("active_object")
                status = "passed" if expected_object == actual_object else "failed"
                details = {"expected_object": expected_object, "actual_object": actual_object}
        except Exception as exc:
            status = "inconclusive"
            details = {"error": str(exc), "verification_key": requirement.verification_key}

        statuses.append(status)
        updated_events.append(
            event.model_copy(
                update={
                    "verification": CorrectionVerificationContract(
                        status=status,
                        details=details,
                    )
                }
            )
        )

    if not statuses:
        return tuple(updated_events), "not_requested"
    if any(status == "failed" for status in statuses):
        overall = "failed"
    elif any(status == "inconclusive" for status in statuses):
        overall = "inconclusive"
    elif all(status == "passed" for status in statuses):
        overall = "passed"
    else:
        overall = "pending"
    return tuple(updated_events), overall


def route_tool_call_report(
    tool_name: str,
    params: Dict[str, Any],
    direct_executor: Callable[[], Any],
    prompt: Optional[str] = None,
) -> MCPExecutionReport:
    """Build a structured execution report for a tool call."""

    context = MCPExecutionContext(tool_name=tool_name, params=params, prompt=prompt)
    surface_profile = _get_active_surface_profile()
    context.surface_profile = surface_profile
    session_state = _get_active_session_state()
    if session_state is not None:
        context.session_phase = session_state.phase.value
    context.guided_tool_family = _resolve_guided_effective_family(tool_name, params)
    context.guided_role, context.guided_role_group = _resolve_guided_role_context(tool_name, params)
    guided_policy = _evaluate_guided_execution_policy(
        surface_profile=surface_profile,
        tool_name=tool_name,
        params=params,
    )
    if guided_policy is not None:
        context.guided_tool_family = guided_policy.get("family")
        context.guided_role = guided_policy.get("role")
        context.guided_role_group = guided_policy.get("role_group")
        if guided_policy.get("status") == "blocked":
            report = MCPExecutionReport(
                context=context,
                router_enabled=is_router_enabled(),
                router_applied=False,
                router_disposition="failed_closed_error",
                error=str(guided_policy.get("message") or "Guided execution blocked."),
                policy_context=guided_policy,
                audit_ids=(),
            )
            _record_router_execution_report(report)
            _log_audit_exposure(report)
            return report
    naming_policy = _evaluate_guided_naming_policy(
        surface_profile=surface_profile,
        tool_name=tool_name,
        params=params,
    )
    if naming_policy is not None and naming_policy.get("status") == "blocked":
        report = MCPExecutionReport(
            context=context,
            router_enabled=is_router_enabled(),
            router_applied=False,
            router_disposition="failed_closed_error",
            error=str(naming_policy.get("message") or "Guided naming blocked."),
            policy_context=naming_policy,
            audit_ids=(),
        )
        _record_router_execution_report(report)
        _log_audit_exposure(report)
        return report

    if not is_router_enabled():
        result = direct_executor()
        report = MCPExecutionReport(
            context=context,
            router_enabled=False,
            router_applied=False,
            router_disposition="bypassed",
            steps=(ExecutionStep(tool_name=tool_name, params=params, result=result),),
            policy_context=naming_policy,
            audit_ids=(),
        )
        _record_router_execution_report(report)
        _log_audit_exposure(report)
        return report

    if _should_bypass_router_for_tool(tool_name):
        result = direct_executor()
        report = MCPExecutionReport(
            context=context,
            router_enabled=True,
            router_applied=False,
            router_disposition="bypassed",
            steps=(ExecutionStep(tool_name=tool_name, params=params, result=result),),
            policy_context=naming_policy,
            audit_ids=(),
        )
        _record_router_execution_report(report)
        _log_audit_exposure(report)
        return report

    router = get_router()
    if router is None:
        if _should_fail_closed_on_router_error(surface_profile):
            report = MCPExecutionReport(
                context=context,
                router_enabled=True,
                router_applied=False,
                router_disposition="failed_closed_error",
                error="Router is enabled but not initialized for this guided surface.",
                audit_ids=(),
            )
            _record_router_execution_report(report)
            _log_audit_exposure(report)
            return report

        result = direct_executor()
        report = MCPExecutionReport(
            context=context,
            router_enabled=True,
            router_applied=False,
            router_disposition="bypassed",
            steps=(ExecutionStep(tool_name=tool_name, params=params, result=result),),
            audit_ids=(),
        )
        _record_router_execution_report(report)
        _log_audit_exposure(report)
        return report

    try:
        corrected_tools = router.process_llm_tool_call(tool_name, params, prompt)
        if corrected_tools:
            final_guided_policy: dict[str, Any] | None = None
            final_naming_policy: dict[str, Any] | None = None
            for index, corrected_tool in enumerate(corrected_tools):
                corrected_tool_name = corrected_tool["tool"]
                corrected_tool_params = corrected_tool["params"]
                step_guided_policy = _evaluate_guided_execution_policy(
                    surface_profile=surface_profile,
                    tool_name=corrected_tool_name,
                    params=corrected_tool_params,
                )
                if step_guided_policy is not None:
                    if index == len(corrected_tools) - 1:
                        final_guided_policy = step_guided_policy
                    if step_guided_policy.get("status") == "blocked":
                        context.guided_tool_family = step_guided_policy.get("family")
                        context.guided_role = step_guided_policy.get("role")
                        context.guided_role_group = step_guided_policy.get("role_group")
                        report = MCPExecutionReport(
                            context=context,
                            router_enabled=True,
                            router_applied=False,
                            router_disposition="failed_closed_error",
                            error=str(step_guided_policy.get("message") or "Guided execution blocked."),
                            policy_context=step_guided_policy,
                            audit_ids=(),
                        )
                        _record_router_execution_report(report)
                        _log_audit_exposure(report)
                        return report
                step_naming_policy = _evaluate_guided_naming_policy(
                    surface_profile=surface_profile,
                    tool_name=corrected_tool_name,
                    params=corrected_tool_params,
                )
                if step_naming_policy is not None:
                    if index == len(corrected_tools) - 1:
                        final_naming_policy = step_naming_policy
                    if step_naming_policy.get("status") == "blocked":
                        context.guided_tool_family = _resolve_guided_effective_family(
                            corrected_tool_name,
                            corrected_tool_params,
                        )
                        context.guided_role, context.guided_role_group = _resolve_guided_role_context(
                            corrected_tool_name,
                            corrected_tool_params,
                        )
                        report = MCPExecutionReport(
                            context=context,
                            router_enabled=True,
                            router_applied=False,
                            router_disposition="failed_closed_error",
                            error=str(step_naming_policy.get("message") or "Guided naming blocked."),
                            policy_context=step_naming_policy,
                            audit_ids=(),
                        )
                        _record_router_execution_report(report)
                        _log_audit_exposure(report)
                        return report

            final_tool = corrected_tools[-1]
            final_tool_name = final_tool["tool"]
            final_tool_params = final_tool["params"]
            context.guided_tool_family = _resolve_guided_effective_family(final_tool_name, final_tool_params)
            context.guided_role, context.guided_role_group = _resolve_guided_role_context(
                final_tool_name,
                final_tool_params,
            )
            if final_guided_policy is not None:
                context.guided_tool_family = final_guided_policy.get("family")
                context.guided_role = final_guided_policy.get("role")
                context.guided_role_group = final_guided_policy.get("role_group")
            naming_policy = final_naming_policy

        if len(corrected_tools) == 1 and corrected_tools[0]["tool"] == tool_name:
            if corrected_tools[0]["params"] == params:
                result = direct_executor()
                report = MCPExecutionReport(
                    context=context,
                    router_enabled=True,
                    router_applied=False,
                    router_disposition="direct",
                    steps=(ExecutionStep(tool_name=tool_name, params=params, result=result),),
                    policy_context=naming_policy,
                    audit_ids=(),
                )
                _record_router_execution_report(report)
                _log_audit_exposure(report)
                return report

        dispatcher = get_dispatcher()
        steps: List[ExecutionStep] = []

        for index, tool in enumerate(corrected_tools):
            tool_to_execute = tool["tool"]
            tool_params = tool["params"]
            dispatch_params = _strip_guided_policy_params_for_dispatch(tool_params)

            logger.debug(
                "Router executing step %s/%s: %s",
                index + 1,
                len(corrected_tools),
                tool_to_execute,
            )

            if tool_to_execute == tool_name and index == len(corrected_tools) - 1:
                result = (
                    direct_executor() if tool_params == params else dispatcher.execute(tool_to_execute, dispatch_params)
                )
            else:
                result = dispatcher.execute(tool_to_execute, dispatch_params)

            steps.append(ExecutionStep(tool_name=tool_to_execute, params=dispatch_params, result=result))

        audit_events = _build_correction_audit_events(
            original_tool_name=tool_name,
            original_params=params,
            corrected_tools=corrected_tools,
            steps=steps,
        )
        audit_events, verification_status = _apply_postcondition_verification(audit_events)

        report = MCPExecutionReport(
            context=context,
            router_enabled=True,
            router_applied=True,
            router_disposition="corrected",
            steps=tuple(steps),
            policy_context=naming_policy,
            audit_events=audit_events,
            audit_ids=_extract_audit_ids(audit_events),
            verification_status=cast(Any, verification_status),
        )
        _record_router_execution_report(report)
        _log_audit_exposure(report)
        return report

    except Exception as e:
        logger.error(f"Router processing failed for {tool_name}: {e}", exc_info=True)
        if _should_fail_closed_on_router_error(surface_profile):
            report = MCPExecutionReport(
                context=context,
                router_enabled=True,
                router_applied=False,
                router_disposition="failed_closed_error",
                error=f"Router processing failed for {tool_name}: {e}",
                audit_ids=(),
            )
            _record_router_execution_report(report)
            _log_audit_exposure(report)
            return report

        fallback_result = direct_executor()
        report = MCPExecutionReport(
            context=context,
            router_enabled=True,
            router_applied=False,
            router_disposition="failed_open_fallback",
            steps=(ExecutionStep(tool_name=tool_name, params=params, result=fallback_result),),
            audit_ids=(),
        )
        _record_router_execution_report(report)
        _log_audit_exposure(report)
        return report


def route_tool_call(
    tool_name: str,
    params: Dict[str, Any],
    direct_executor: Callable[[], Any],
    prompt: Optional[str] = None,
) -> Any:
    """Route a tool call through the Router Supervisor if enabled.

    This function should be called at the beginning of MCP tool functions
    to enable router processing.

    Args:
        tool_name: Name of the tool being called.
        params: Parameters passed to the tool.
        direct_executor: Lambda/function that executes the tool directly.
        prompt: Optional user prompt for better intent classification.

    Returns:
        Result string from tool execution (routed or direct).

    Example:
        def mesh_extrude_region(ctx: Context, depth: float = 1.0) -> str:
            return route_tool_call(
                tool_name="mesh_extrude_region",
                params={"depth": depth},
                direct_executor=lambda: get_mesh_handler().extrude_region(depth=depth),
            )
    """
    report = route_tool_call_report(
        tool_name=tool_name,
        params=params,
        direct_executor=direct_executor,
        prompt=prompt,
    )
    naming_payload = report.policy_context.get("guided_naming") if report.policy_context else None
    if isinstance(naming_payload, dict) and naming_payload.get("status") == "warning":
        current_ctx = _get_active_context()
        if current_ctx is not None and naming_payload.get("message"):
            ctx_warning(current_ctx, str(naming_payload["message"]))
    _maybe_mark_guided_spatial_state_stale_from_report(report)
    _maybe_sync_guided_part_registry_from_report(report)
    if report.error is None and len(report.steps) == 1:
        result = report.steps[0].result
        if not isinstance(result, str):
            return result
    return report.to_legacy_text()


def execute_routed_sequence(tools: List[Dict[str, Any]]) -> str:
    """Execute a sequence of tools from router.

    Args:
        tools: List of tool dicts with 'tool' and 'params' keys.

    Returns:
        Combined result string.
    """
    if not tools:
        return "No operations performed."

    dispatcher = get_dispatcher()
    steps: List[ExecutionStep] = []

    for tool in tools:
        tool_name = tool.get("tool", "")
        params = tool.get("params", {})

        try:
            result = dispatcher.execute(tool_name, params)
            steps.append(ExecutionStep(tool_name=tool_name, params=params, result=result))
        except Exception as e:
            steps.append(
                ExecutionStep(
                    tool_name=tool_name,
                    params=params,
                    result=f"Error executing {tool_name}: {str(e)}",
                    error=str(e),
                )
            )

    report = MCPExecutionReport(
        context=MCPExecutionContext(tool_name="sequence", params={"tools": tools}),
        router_enabled=True,
        router_applied=True,
        router_disposition="corrected",
        steps=tuple(steps),
        audit_ids=(),
    )
    return report.to_legacy_text()


def get_router_status() -> Dict[str, Any]:
    """Get current router status.

    Returns:
        Dictionary with router status info.
    """
    enabled = is_router_enabled()

    if not enabled:
        return {
            "enabled": False,
            "message": "Router Supervisor is disabled. Set ROUTER_ENABLED=true to enable.",
        }

    router = get_router()
    if router is None:
        return {
            "enabled": True,
            "initialized": False,
            "message": "Router enabled but not initialized.",
        }

    return {
        "enabled": True,
        "initialized": True,
        "ready": router.is_ready(),
        "component_status": router.get_component_status(),
        "stats": router.get_stats(),
        "config": str(router.get_config()),
        "assistant_diagnostics": router.get_assistant_diagnostics(),
    }
