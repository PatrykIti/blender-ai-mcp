# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Deterministic visibility policy for FastMCP surface profiles and phases."""

from __future__ import annotations

import re
from typing import Any

from server.adapters.mcp.contracts.guided_flow import GuidedFlowFamilyLiteral
from server.adapters.mcp.session_phase import SessionPhase, coerce_session_phase
from server.adapters.mcp.settings import SurfaceProfileSettings

GUIDED_ENTRY_TOOLS: tuple[str, ...] = (
    "router_set_goal",
    "router_get_status",
    "workflow_catalog",
    "browse_workflows",
    "reference_images",
)

GUIDED_UTILITY_TOOLS: tuple[str, ...] = (
    "scene_clean_scene",
    "scene_get_viewport",
)

GUIDED_DISCOVERY_TOOLS: tuple[str, ...] = (
    "search_tools",
    "call_tool",
)

GUIDED_SPATIAL_GRAPH_TOOLS: tuple[str, ...] = (
    "scene_scope_graph",
    "scene_relation_graph",
)

GUIDED_VIEW_DIAGNOSTIC_TOOLS: tuple[str, ...] = ("scene_view_diagnostics",)
GUIDED_SPATIAL_SUPPORT_TOOLS: tuple[str, ...] = (
    *GUIDED_SPATIAL_GRAPH_TOOLS,
    *GUIDED_VIEW_DIAGNOSTIC_TOOLS,
)
GUIDED_SPATIAL_CONTEXT_DIRECT_TOOLS: tuple[str, ...] = (
    *GUIDED_SPATIAL_SUPPORT_TOOLS,
    "check_scene",
    "inspect_scene",
    "scene_clean_scene",
    "scene_get_viewport",
    "reference_images",
    "reference_compare_checkpoint",
    "reference_compare_current_view",
    "reference_compare_stage_checkpoint",
    "reference_iterate_stage_checkpoint",
    "router_get_status",
)

GUIDED_MANUAL_BUILD_HANDOFF_TOOLS: tuple[str, ...] = (
    "scene_create",
    "check_scene",
    "inspect_scene",
    "macro_relative_layout",
    "macro_attach_part_to_surface",
    "macro_align_part_with_contact",
    "macro_place_symmetry_pair",
    "macro_place_supported_pair",
    "macro_cleanup_part_intersections",
    "macro_adjust_relative_proportion",
    "macro_adjust_segment_chain_arc",
    "macro_cutout_recess",
    "macro_finish_form",
)

GUIDED_MANUAL_BUILD_SUPPORTING_TOOLS: tuple[str, ...] = (
    "reference_images",
    "guided_register_part",
    "scene_clean_scene",
    "reference_compare_checkpoint",
    "reference_compare_current_view",
    "reference_compare_stage_checkpoint",
    "reference_iterate_stage_checkpoint",
    "router_get_status",
    *GUIDED_SPATIAL_SUPPORT_TOOLS,
)

CREATURE_LOW_POLY_BLOCKOUT_DIRECT_TOOLS: tuple[str, ...] = (
    "check_scene",
    "inspect_scene",
    "collection_manage",
    "scene_set_active_object",
    "scene_set_mode",
    "scene_get_viewport",
    "scene_measure_dimensions",
    "scene_assert_proportion",
    "modeling_create_primitive",
    "modeling_transform_object",
    "mesh_select",
    "mesh_select_targeted",
    "mesh_extrude_region",
    "mesh_loop_cut",
    "mesh_bevel",
    "mesh_symmetrize",
    "mesh_merge_by_distance",
    "mesh_dissolve",
    "macro_adjust_relative_proportion",
    "macro_adjust_segment_chain_arc",
    "macro_align_part_with_contact",
    "macro_cleanup_part_intersections",
)

CREATURE_LOW_POLY_BLOCKOUT_SUPPORTING_TOOLS: tuple[str, ...] = (
    "reference_images",
    "guided_register_part",
    "scene_clean_scene",
    "reference_compare_checkpoint",
    "reference_compare_current_view",
    "reference_compare_stage_checkpoint",
    "reference_iterate_stage_checkpoint",
    "router_get_status",
    *GUIDED_SPATIAL_SUPPORT_TOOLS,
)

GUIDED_UTILITY_HANDOFF_TOOLS: tuple[str, ...] = (
    "scene_clean_scene",
    "scene_get_viewport",
)

GUIDED_UTILITY_SUPPORTING_TOOLS: tuple[str, ...] = ("router_get_status",)

GUIDED_TOOL_FAMILY_MAP: dict[str, GuidedFlowFamilyLiteral] = {
    "scene_scope_graph": "spatial_context",
    "scene_relation_graph": "spatial_context",
    "scene_view_diagnostics": "spatial_context",
    "reference_images": "reference_context",
    "reference_compare_checkpoint": "checkpoint_iterate",
    "reference_compare_current_view": "checkpoint_iterate",
    "reference_compare_stage_checkpoint": "checkpoint_iterate",
    "reference_iterate_stage_checkpoint": "checkpoint_iterate",
    "modeling_create_primitive": "primary_masses",
    "modeling_transform_object": "primary_masses",
    "collection_manage": "utility",
    "scene_create": "primary_masses",
    "macro_relative_layout": "secondary_parts",
    "macro_place_symmetry_pair": "secondary_parts",
    "macro_place_supported_pair": "secondary_parts",
    "macro_adjust_relative_proportion": "secondary_parts",
    "macro_adjust_segment_chain_arc": "secondary_parts",
    "macro_attach_part_to_surface": "attachment_alignment",
    "macro_align_part_with_contact": "attachment_alignment",
    "macro_cleanup_part_intersections": "attachment_alignment",
    "inspect_scene": "inspect_validate",
    "check_scene": "inspect_validate",
    "scene_measure_dimensions": "inspect_validate",
    "scene_measure_distance": "inspect_validate",
    "scene_measure_gap": "inspect_validate",
    "scene_measure_alignment": "inspect_validate",
    "scene_measure_overlap": "inspect_validate",
    "scene_assert_contact": "inspect_validate",
    "scene_assert_dimensions": "inspect_validate",
    "scene_assert_containment": "inspect_validate",
    "scene_assert_symmetry": "inspect_validate",
    "scene_assert_proportion": "inspect_validate",
    "macro_finish_form": "finish",
    "scene_clean_scene": "utility",
    "scene_get_viewport": "utility",
}

GUIDED_OVERLAY_FAMILY_ORDER: dict[str, tuple[GuidedFlowFamilyLiteral, ...]] = {
    "generic": (
        "spatial_context",
        "reference_context",
        "primary_masses",
        "secondary_parts",
        "checkpoint_iterate",
        "inspect_validate",
        "finish",
    ),
    "creature": (
        "spatial_context",
        "reference_context",
        "primary_masses",
        "secondary_parts",
        "attachment_alignment",
        "checkpoint_iterate",
        "inspect_validate",
        "finish",
    ),
    "building": (
        "spatial_context",
        "reference_context",
        "primary_masses",
        "secondary_parts",
        "checkpoint_iterate",
        "inspect_validate",
        "finish",
    ),
}

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
_LOW_POLY_GOAL_HINTS: tuple[str, ...] = ("blockout", "low poly", "low-poly")

GUIDED_BUILD_ESCAPE_HATCH_TOOLS: tuple[str, ...] = (
    "guided_register_part",
    "scene_clean_scene",
    "scene_context",
    "check_scene",
    "scene_inspect",
    "inspect_scene",
    "scene_configure",
    "configure_scene",
    "scene_create",
    "scene_list_objects",
    "scene_duplicate_object",
    "scene_set_active_object",
    "scene_set_mode",
    "scene_rename_object",
    "scene_hide_object",
    "scene_show_all_objects",
    "scene_isolate_object",
    "scene_camera_orbit",
    "scene_camera_focus",
    "scene_snapshot_state",
    "scene_compare_snapshot",
    "scene_get_custom_properties",
    "scene_set_custom_property",
    "scene_get_hierarchy",
    "scene_get_bounding_box",
    "scene_get_origin_info",
    "scene_view_diagnostics",
    "scene_get_viewport",
    "scene_measure_distance",
    "scene_measure_dimensions",
    "scene_measure_gap",
    "scene_measure_alignment",
    "scene_measure_overlap",
    "scene_assert_contact",
    "scene_assert_dimensions",
    "scene_assert_containment",
    "scene_assert_symmetry",
    "scene_assert_proportion",
    "reference_compare_checkpoint",
    "reference_compare_current_view",
    "reference_compare_stage_checkpoint",
    "reference_iterate_stage_checkpoint",
    "macro_relative_layout",
    "macro_attach_part_to_surface",
    "macro_align_part_with_contact",
    "macro_place_symmetry_pair",
    "macro_place_supported_pair",
    "macro_cleanup_part_intersections",
    "macro_adjust_relative_proportion",
    "macro_adjust_segment_chain_arc",
    "macro_cutout_recess",
    "macro_finish_form",
    "modeling_create_primitive",
    "modeling_transform_object",
    "modeling_convert_to_mesh",
    "modeling_join_objects",
    "modeling_separate_object",
    "modeling_set_origin",
    "mesh_select",
    "mesh_select_targeted",
    "mesh_delete_selected",
    "mesh_extrude_region",
    "mesh_fill_holes",
    "mesh_bevel",
    "mesh_loop_cut",
    "mesh_inset",
    "mesh_boolean",
    "mesh_merge_by_distance",
    "mesh_subdivide",
    "mesh_smooth",
    "mesh_flatten",
    "mesh_randomize",
    "mesh_shrink_fatten",
    "mesh_transform_selected",
    "mesh_bridge_edge_loops",
    "mesh_duplicate_selected",
    "mesh_bisect",
    "mesh_edge_slide",
    "mesh_vert_slide",
    "mesh_triangulate",
    "mesh_remesh_voxel",
    "mesh_spin",
    "mesh_screw",
    "mesh_add_vertex",
    "mesh_add_edge_face",
    "mesh_list_groups",
    "mesh_create_vertex_group",
    "mesh_assign_to_group",
    "mesh_remove_from_group",
    "mesh_edge_crease",
    "mesh_bevel_weight",
    "mesh_mark_sharp",
    "mesh_dissolve",
    "mesh_tris_to_quads",
    "mesh_normals_make_consistent",
    "mesh_decimate",
    "mesh_knife_project",
    "mesh_rip",
    "mesh_split",
    "mesh_edge_split",
    "mesh_set_proportional_edit",
    "mesh_symmetrize",
    "mesh_grid_fill",
    "mesh_poke_faces",
    "mesh_beautify_fill",
    "mesh_mirror",
    "mesh_inspect",
    "material_list",
    "material_list_by_object",
    "material_create",
    "material_assign",
    "material_set_params",
    "material_set_texture",
    "material_inspect_nodes",
    "uv_list_maps",
    "uv_unwrap",
    "uv_pack_islands",
    "uv_create_seam",
    "collection_list",
    "collection_list_objects",
    "collection_manage",
)

GUIDED_INSPECT_ESCAPE_HATCH_TOOLS: tuple[str, ...] = (
    "scene_context",
    "check_scene",
    "scene_inspect",
    "inspect_scene",
    "scene_configure",
    "configure_scene",
    "scene_list_objects",
    "scene_snapshot_state",
    "scene_compare_snapshot",
    "scene_get_custom_properties",
    "scene_get_hierarchy",
    "scene_get_bounding_box",
    "scene_get_origin_info",
    "scene_scope_graph",
    "scene_relation_graph",
    "scene_view_diagnostics",
    "scene_get_viewport",
    "scene_hide_object",
    "scene_show_all_objects",
    "scene_isolate_object",
    "scene_camera_orbit",
    "scene_camera_focus",
    "scene_measure_distance",
    "scene_measure_dimensions",
    "scene_measure_gap",
    "scene_measure_alignment",
    "scene_measure_overlap",
    "scene_assert_contact",
    "scene_assert_dimensions",
    "scene_assert_containment",
    "scene_assert_symmetry",
    "scene_assert_proportion",
    "reference_compare_checkpoint",
    "reference_compare_current_view",
    "reference_compare_stage_checkpoint",
    "reference_iterate_stage_checkpoint",
    "mesh_inspect",
    "material_list",
    "material_list_by_object",
    "material_inspect_nodes",
    "uv_list_maps",
    "collection_list",
    "collection_list_objects",
    "extraction_render_angles",
)


def build_guided_handoff_payload(
    continuation_mode: str,
    *,
    surface_profile: SurfaceProfileSettings | str,
    phase: SessionPhase | str,
    goal: str | None = None,
) -> dict[str, Any] | None:
    """Build the explicit guided continuation contract for bounded no-match paths."""

    resolved_surface = (
        surface_profile.name if isinstance(surface_profile, SurfaceProfileSettings) else str(surface_profile)
    )
    resolved_phase = coerce_session_phase(phase)
    if resolved_surface != "llm-guided":
        return None

    if continuation_mode == "guided_manual_build":
        normalized_goal = str(goal or "").strip().lower()
        is_creature_goal = any(
            re.search(rf"(?<![a-z0-9]){re.escape(token)}(?![a-z0-9])", normalized_goal)
            for token in _CREATURE_GOAL_HINTS
        )
        is_low_poly_goal = any(
            re.search(rf"(?<![a-z0-9]){re.escape(token)}(?![a-z0-9])", normalized_goal)
            for token in _LOW_POLY_GOAL_HINTS
        )
        target_phase: SessionPhase = resolved_phase if resolved_phase == SessionPhase.BUILD else SessionPhase.BUILD
        if is_creature_goal and is_low_poly_goal:
            return {
                "kind": "guided_manual_build",
                "recipe_id": "low_poly_creature_blockout",
                "target_phase": target_phase.value,
                "surface_profile": resolved_surface,
                "direct_tools": list(CREATURE_LOW_POLY_BLOCKOUT_DIRECT_TOOLS),
                "supporting_tools": list(CREATURE_LOW_POLY_BLOCKOUT_SUPPORTING_TOOLS),
                "discovery_tools": list(GUIDED_DISCOVERY_TOOLS),
                "workflow_import_recommended": False,
                "message": (
                    "Continue on the guided creature blockout surface. "
                    "Start with modeling/mesh blockout tools, use reference iterate/measure tools between stages, "
                    "and keep sculpt or finish-heavy tools for later refinement only."
                ),
            }
        return {
            "kind": "guided_manual_build",
            "recipe_id": None,
            "target_phase": target_phase.value,
            "surface_profile": resolved_surface,
            "direct_tools": list(GUIDED_MANUAL_BUILD_HANDOFF_TOOLS),
            "supporting_tools": list(GUIDED_MANUAL_BUILD_SUPPORTING_TOOLS),
            "discovery_tools": list(GUIDED_DISCOVERY_TOOLS),
            "workflow_import_recommended": False,
            "message": (
                "Continue manual modeling on the guided build surface. "
                "Use directly visible build tools/macros first, and only use discovery when needed."
            ),
        }

    if continuation_mode == "guided_utility":
        utility_target_phase: SessionPhase = (
            resolved_phase if resolved_phase == SessionPhase.PLANNING else SessionPhase.PLANNING
        )
        return {
            "kind": "guided_utility",
            "recipe_id": None,
            "target_phase": utility_target_phase.value,
            "surface_profile": resolved_surface,
            "direct_tools": list(GUIDED_UTILITY_HANDOFF_TOOLS),
            "supporting_tools": list(GUIDED_UTILITY_SUPPORTING_TOOLS),
            "discovery_tools": list(GUIDED_DISCOVERY_TOOLS),
            "workflow_import_recommended": False,
            "message": (
                "Continue on the guided utility path. "
                "Use direct utility tools first, and only use discovery when needed."
            ),
        }

    return None


def _is_creature_blockout_handoff(guided_handoff: dict[str, Any] | None) -> bool:
    return (
        isinstance(guided_handoff, dict)
        and guided_handoff.get("kind") == "guided_manual_build"
        and guided_handoff.get("recipe_id") == "low_poly_creature_blockout"
    )


def _guided_handoff_visible_tools(guided_handoff: dict[str, Any] | None) -> set[str]:
    if not isinstance(guided_handoff, dict):
        return set()
    return {
        *[str(name) for name in guided_handoff.get("direct_tools") or [] if str(name).strip()],
        *[str(name) for name in guided_handoff.get("supporting_tools") or [] if str(name).strip()],
    }


def resolve_guided_tool_family(tool_name: str) -> GuidedFlowFamilyLiteral | None:
    """Return the shared guided family for one tool name when defined."""

    return GUIDED_TOOL_FAMILY_MAP.get(tool_name)


def get_guided_overlay_family_order(domain_profile: str) -> tuple[GuidedFlowFamilyLiteral, ...]:
    """Return the canonical family order for one guided overlay."""

    return GUIDED_OVERLAY_FAMILY_ORDER.get(domain_profile, GUIDED_OVERLAY_FAMILY_ORDER["generic"])


def build_visibility_rules(
    surface_profile: SurfaceProfileSettings | str,
    phase: SessionPhase | str = SessionPhase.BOOTSTRAP,
    guided_handoff: dict[str, Any] | None = None,
    guided_flow_state: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Build deterministic visibility rules for a profile/phase combination."""

    if isinstance(surface_profile, SurfaceProfileSettings):
        resolved_surface = surface_profile.name
        code_mode_allowed_tools = set(surface_profile.code_mode_allowed_tools)
    else:
        resolved_surface = str(surface_profile)
        code_mode_allowed_tools = set()

    resolved_phase = coerce_session_phase(phase)

    if resolved_surface in {"legacy-manual", "legacy-flat", "internal-debug"}:
        return []

    if resolved_surface == "code-mode-pilot":
        if not code_mode_allowed_tools:
            return []
        return [
            {"enabled": False, "components": {"tool"}, "match_all": True},
            {"enabled": True, "components": {"tool"}, "names": code_mode_allowed_tools},
            {
                "enabled": True,
                "components": {"prompt"},
                "names": {
                    "getting_started",
                    "guided_session_start",
                    "workflow_router_first",
                    "manual_tools_no_router",
                    "reference_guided_creature_build",
                    "recommended_prompts",
                },
            },
        ]

    if resolved_surface != "llm-guided":
        raise ValueError(f"Unknown visibility surface profile '{resolved_surface}'")

    rules: list[dict[str, Any]] = [
        {"enabled": False, "components": {"tool"}, "match_all": True},
        {"enabled": True, "components": {"tool"}, "names": set(GUIDED_ENTRY_TOOLS)},
        {"enabled": True, "components": {"tool"}, "names": set(GUIDED_DISCOVERY_TOOLS)},
        {"enabled": True, "components": {"tool"}, "names": set(GUIDED_SPATIAL_SUPPORT_TOOLS)},
    ]
    if resolved_phase in {SessionPhase.BOOTSTRAP, SessionPhase.PLANNING}:
        rules.append(
            {
                "enabled": True,
                "components": {"tool"},
                "names": set(GUIDED_UTILITY_TOOLS),
            }
        )
    rules.extend(
        [
            {"enabled": True, "components": {"tool"}, "names": {"list_prompts", "get_prompt"}},
            {
                "enabled": True,
                "components": {"prompt"},
                "names": {
                    "getting_started",
                    "guided_session_start",
                    "workflow_router_first",
                    "manual_tools_no_router",
                    "demo_low_poly_medieval_well",
                    "demo_generic_modeling",
                    "reference_guided_creature_build",
                    "recommended_prompts",
                },
            },
        ]
    )

    current_flow_step = str((guided_flow_state or {}).get("current_step") or "").strip().lower()
    spatial_refresh_required = bool((guided_flow_state or {}).get("spatial_refresh_required"))

    if resolved_phase == SessionPhase.BUILD:
        if current_flow_step == "establish_spatial_context" or spatial_refresh_required:
            build_tools = set(GUIDED_SPATIAL_CONTEXT_DIRECT_TOOLS)
        else:
            build_tools = (
                _guided_handoff_visible_tools(guided_handoff)
                if _is_creature_blockout_handoff(guided_handoff)
                else set(GUIDED_BUILD_ESCAPE_HATCH_TOOLS)
            )
        rules.append({"enabled": True, "components": {"tool"}, "names": build_tools})
    elif resolved_phase == SessionPhase.INSPECT_VALIDATE:
        rules.append({"enabled": True, "components": {"tool"}, "names": set(GUIDED_INSPECT_ESCAPE_HATCH_TOOLS)})

    return rules
