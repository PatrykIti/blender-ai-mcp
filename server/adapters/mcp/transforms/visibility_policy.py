# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Deterministic visibility policy for FastMCP surface profiles and phases."""

from __future__ import annotations

from typing import Any

from server.adapters.mcp.session_phase import SessionPhase, coerce_session_phase
from server.adapters.mcp.settings import SurfaceProfileSettings
from server.adapters.mcp.visibility.tags import phase_tag

GUIDED_ENTRY_TOOLS: tuple[str, ...] = (
    "router_set_goal",
    "router_get_status",
    "workflow_catalog",
    "browse_workflows",
)

GUIDED_BUILD_ESCAPE_HATCH_TOOLS: tuple[str, ...] = (
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
    "macro_cutout_recess",
    "modeling_create_primitive",
    "modeling_transform_object",
    "modeling_add_modifier",
    "modeling_apply_modifier",
    "modeling_list_modifiers",
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
    "mesh_inspect",
    "material_list",
    "material_list_by_object",
    "material_inspect_nodes",
    "uv_list_maps",
    "collection_list",
    "collection_list_objects",
    "extraction_render_angles",
)


def build_visibility_rules(
    surface_profile: SurfaceProfileSettings | str,
    phase: SessionPhase | str = SessionPhase.BOOTSTRAP,
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
                    "workflow_router_first",
                    "manual_tools_no_router",
                    "recommended_prompts",
                },
            },
        ]

    if resolved_surface != "llm-guided":
        raise ValueError(f"Unknown visibility surface profile '{resolved_surface}'")

    rules: list[dict[str, Any]] = [
        {"enabled": False, "components": {"tool"}, "match_all": True},
        {"enabled": True, "components": {"tool"}, "names": set(GUIDED_ENTRY_TOOLS)},
        {"enabled": True, "components": {"tool"}, "names": {"list_prompts", "get_prompt"}},
        {
            "enabled": True,
            "components": {"prompt"},
            "names": {
                "getting_started",
                "workflow_router_first",
                "manual_tools_no_router",
                "demo_low_poly_medieval_well",
                "demo_generic_modeling",
                "recommended_prompts",
            },
        },
    ]

    if resolved_phase == SessionPhase.BUILD:
        rules.append({"enabled": True, "components": {"tool"}, "names": set(GUIDED_BUILD_ESCAPE_HATCH_TOOLS)})
    elif resolved_phase == SessionPhase.INSPECT_VALIDATE:
        rules.append({"enabled": True, "components": {"tool"}, "names": set(GUIDED_INSPECT_ESCAPE_HATCH_TOOLS)})

    return rules
