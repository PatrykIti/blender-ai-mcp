"""
Tool Dispatcher for Router Integration.

Maps tool names to their handler methods for router-based execution.
"""

from typing import Dict, Any, Callable, Optional
import logging

from server.infrastructure.di import (
    get_scene_handler,
    get_modeling_handler,
    get_mesh_handler,
    get_collection_handler,
    get_material_handler,
    get_uv_handler,
    get_curve_handler,
    get_system_handler,
    get_sculpt_handler,
    get_baking_handler,
    get_lattice_handler,
    get_extraction_handler,
    get_text_handler,
    get_armature_handler,
)

logger = logging.getLogger(__name__)


class ToolDispatcher:
    """Dispatches tool calls to appropriate handlers.

    Used by Router to execute corrected/expanded tool sequences.
    Maps tool_name -> handler method with parameter translation.
    """

    def __init__(self):
        """Initialize dispatcher with tool mappings."""
        self._tool_map: Dict[str, Callable] = {}
        self._register_tools()

    def _safe_update(self, handler: Any, mappings: Dict[str, str]) -> None:
        """Safely register tool mappings, skipping missing methods.

        Args:
            handler: The handler object.
            mappings: Dict of tool_name -> method_name.
        """
        for tool_name, method_name in mappings.items():
            if hasattr(handler, method_name):
                self._tool_map[tool_name] = getattr(handler, method_name)
            else:
                logger.debug(f"Skipping {tool_name}: {handler.__class__.__name__} has no '{method_name}'")

    def _register_tools(self) -> None:
        """Register all tool mappings.

        Uses _safe_update to skip missing methods gracefully.
        This prevents crashes when handlers don't implement all expected methods.
        """
        # Scene tools
        scene = get_scene_handler()
        self._safe_update(scene, {
            "scene_list_objects": "list_objects",
            "scene_delete_object": "delete_object",
            "scene_clean_scene": "clean_scene",
            "scene_duplicate_object": "duplicate_object",
            "scene_set_active_object": "set_active_object",
            "scene_get_mode": "get_mode",
            "scene_list_selection": "list_selection",
            "scene_inspect_object": "inspect_object",
            "scene_snapshot_state": "snapshot_state",
            # NOTE: scene_compare_snapshot is NOT mapped here because it uses
            # SnapshotDiffService (pure Python, no RPC to Blender needed).
            "scene_inspect_material_slots": "inspect_material_slots",
            "scene_inspect_mesh_topology": "inspect_mesh_topology",
            "scene_inspect_modifiers": "inspect_modifiers",
            "scene_get_constraints": "get_constraints",
            "scene_create_light": "create_light",
            "scene_create_camera": "create_camera",
            "scene_create_empty": "create_empty",
            "scene_rename_object": "rename_object",
            "scene_hide_object": "hide_object",
            "scene_show_all_objects": "show_all_objects",
            "scene_isolate_object": "isolate_object",
            "scene_camera_orbit": "camera_orbit",
            "scene_camera_focus": "camera_focus",
            "scene_get_custom_properties": "get_custom_properties",
            "scene_set_custom_property": "set_custom_property",
            "scene_get_hierarchy": "get_hierarchy",
            "scene_get_bounding_box": "get_bounding_box",
            "scene_get_origin_info": "get_origin_info",
        })

        # System tools
        system = get_system_handler()
        self._safe_update(system, {
            "system_set_mode": "set_mode",
            "system_undo": "undo",
            "system_redo": "redo",
            "system_save_file": "save_file",
            "system_new_file": "new_file",
            "system_snapshot": "snapshot",
            # Export tools
            "export_glb": "export_glb",
            "export_fbx": "export_fbx",
            "export_obj": "export_obj",
            # Import tools
            "import_obj": "import_obj",
            "import_fbx": "import_fbx",
            "import_glb": "import_glb",
            "import_image_as_plane": "import_image_as_plane",
        })

        # Modeling tools
        modeling = get_modeling_handler()
        self._safe_update(modeling, {
            "modeling_create_primitive": "create_primitive",
            "modeling_transform_object": "transform_object",
            "modeling_add_modifier": "add_modifier",
            "modeling_apply_modifier": "apply_modifier",
            "modeling_list_modifiers": "get_modifiers",
            "modeling_get_modifier_data": "get_modifier_data",
            "modeling_convert_to_mesh": "convert_to_mesh",
            "modeling_join_objects": "join_objects",
            "modeling_separate_object": "separate_object",
            "modeling_set_origin": "set_origin",
            # Metaball tools
            "metaball_create": "metaball_create",
            "metaball_add_element": "metaball_add_element",
            "metaball_to_mesh": "metaball_to_mesh",
            # Skin modifier tools
            "skin_create_skeleton": "skin_create_skeleton",
            "skin_set_radius": "skin_set_radius",
        })

        # Mesh tools
        mesh = get_mesh_handler()
        self._safe_update(mesh, {
            "mesh_select_all": "select_all",
            "mesh_select_by_index": "select_by_index",
            "mesh_select_linked": "select_linked",
            "mesh_select_more": "select_more",
            "mesh_select_less": "select_less",
            "mesh_select_boundary": "select_boundary",
            "mesh_select_loop": "select_loop",
            "mesh_select_ring": "select_ring",
            "mesh_select_by_location": "select_by_location",
            "mesh_get_vertex_data": "get_vertex_data",
            "mesh_get_edge_data": "get_edge_data",
            "mesh_get_face_data": "get_face_data",
            "mesh_get_uv_data": "get_uv_data",
            "mesh_get_loop_normals": "get_loop_normals",
            "mesh_get_vertex_group_weights": "get_vertex_group_weights",
            "mesh_get_attributes": "get_attributes",
            "mesh_get_shape_keys": "get_shape_keys",
            "mesh_delete_selected": "delete_selected",
            "mesh_extrude_region": "extrude_region",
            "mesh_fill_holes": "fill_holes",
            "mesh_bevel": "bevel",
            "mesh_loop_cut": "loop_cut",
            "mesh_inset": "inset",
            "mesh_boolean": "boolean",
            "mesh_merge_by_distance": "merge_by_distance",
            "mesh_subdivide": "subdivide",
            "mesh_smooth": "smooth_vertices",
            "mesh_flatten": "flatten_vertices",
            "mesh_randomize": "randomize",
            "mesh_shrink_fatten": "shrink_fatten",
            "mesh_transform_selected": "transform_selected",
            "mesh_bridge_edge_loops": "bridge_edge_loops",
            "mesh_duplicate_selected": "duplicate_selected",
            "mesh_bisect": "bisect",
            "mesh_edge_slide": "edge_slide",
            "mesh_vert_slide": "vert_slide",
            "mesh_triangulate": "triangulate",
            "mesh_remesh_voxel": "remesh_voxel",
            "mesh_spin": "spin",
            "mesh_screw": "screw",
            "mesh_add_vertex": "add_vertex",
            "mesh_add_edge_face": "add_edge_face",
            "mesh_list_groups": "list_groups",
            "mesh_create_vertex_group": "create_vertex_group",
            "mesh_assign_to_group": "assign_to_group",
            "mesh_remove_from_group": "remove_from_group",
            "mesh_edge_crease": "edge_crease",
            "mesh_bevel_weight": "bevel_weight",
            "mesh_mark_sharp": "mark_sharp",
            "mesh_dissolve": "dissolve",
            "mesh_tris_to_quads": "tris_to_quads",
            "mesh_normals_make_consistent": "normals_make_consistent",
            "mesh_decimate": "decimate",
            "mesh_knife_project": "knife_project",
            "mesh_rip": "rip",
            "mesh_split": "split",
            "mesh_edge_split": "edge_split",
            "mesh_set_proportional_edit": "set_proportional_edit",
            "mesh_symmetrize": "symmetrize",
            "mesh_grid_fill": "grid_fill",
            "mesh_poke_faces": "poke_faces",
            "mesh_beautify_fill": "beautify_fill",
            "mesh_mirror": "mirror",
        })

        # Mega-tools compatibility: Router emits these tool names.
        def _mesh_select(
            action: str,
            boundary_mode: str = "EDGE",
        ) -> str:
            if action == "all":
                return mesh.select_all(deselect=False)
            if action == "none":
                return mesh.select_all(deselect=True)
            if action == "linked":
                return mesh.select_linked()
            if action == "more":
                return mesh.select_more()
            if action == "less":
                return mesh.select_less()
            if action == "boundary":
                return mesh.select_boundary(mode=boundary_mode)
            return f"Error: Unknown action '{action}'."

        def _mesh_select_targeted(
            action: str,
            indices: Optional[list[int]] = None,
            element_type: str = "VERT",
            selection_mode: str = "SET",
            edge_index: Optional[int] = None,
            axis: Optional[str] = None,
            min_coord: Optional[float] = None,
            max_coord: Optional[float] = None,
        ) -> str:
            if action == "by_index":
                if indices is None:
                    return "Error: 'by_index' action requires 'indices'."
                return mesh.select_by_index(indices, element_type, selection_mode)
            if action == "loop":
                if edge_index is None:
                    return "Error: 'loop' action requires 'edge_index'."
                return mesh.select_loop(edge_index)
            if action == "ring":
                if edge_index is None:
                    return "Error: 'ring' action requires 'edge_index'."
                return mesh.select_ring(edge_index)
            if action == "by_location":
                if axis is None or min_coord is None or max_coord is None:
                    return "Error: 'by_location' action requires 'axis', 'min_coord', and 'max_coord'."
                return mesh.select_by_location(axis, min_coord, max_coord, mode=element_type)
            return f"Error: Unknown action '{action}'."

        self._tool_map["mesh_select"] = _mesh_select
        self._tool_map["mesh_select_targeted"] = _mesh_select_targeted

        # Material tools
        material = get_material_handler()
        self._safe_update(material, {
            "material_list": "list_materials",
            "material_list_by_object": "list_by_object",
            "material_create": "create_material",
            "material_assign": "assign_material",
            "material_set_params": "set_material_params",
            "material_set_texture": "set_material_texture",
            "material_inspect_nodes": "inspect_nodes",
        })

        # UV tools
        uv = get_uv_handler()
        self._safe_update(uv, {
            "uv_list_maps": "list_maps",
            "uv_unwrap": "unwrap",
            "uv_pack_islands": "pack_islands",
            "uv_create_seam": "create_seam",
        })

        # Collection tools
        collection = get_collection_handler()
        self._safe_update(collection, {
            "collection_list": "list_collections",
            "collection_list_objects": "list_objects",
            "collection_manage": "manage_collection",
        })

        # Curve tools
        curve = get_curve_handler()
        self._safe_update(curve, {
            "curve_create": "create",
            "curve_to_mesh": "to_mesh",
        })

        # Sculpt tools
        sculpt = get_sculpt_handler()
        self._safe_update(sculpt, {
            "sculpt_auto": "auto_sculpt",
            "sculpt_brush_smooth": "brush_smooth",
            "sculpt_brush_grab": "brush_grab",
            "sculpt_brush_crease": "brush_crease",
            "sculpt_brush_clay": "brush_clay",
            "sculpt_brush_inflate": "brush_inflate",
            "sculpt_brush_blob": "brush_blob",
            "sculpt_brush_snake_hook": "brush_snake_hook",
            "sculpt_brush_draw": "brush_draw",
            "sculpt_brush_pinch": "brush_pinch",
            "sculpt_enable_dyntopo": "enable_dyntopo",
            "sculpt_disable_dyntopo": "disable_dyntopo",
            "sculpt_dyntopo_flood_fill": "dyntopo_flood_fill",
        })

        # Baking tools
        baking = get_baking_handler()
        self._safe_update(baking, {
            "bake_normal_map": "bake_normal_map",
            "bake_ao": "bake_ao",
            "bake_combined": "bake_combined",
            "bake_diffuse": "bake_diffuse",
        })

        # Lattice tools
        lattice = get_lattice_handler()
        self._safe_update(lattice, {
            "lattice_create": "create",
            "lattice_bind": "bind",
            "lattice_edit_point": "edit_point",
        })

        # Extraction tools
        extraction = get_extraction_handler()
        self._safe_update(extraction, {
            "extraction_deep_topology": "deep_topology",
            "extraction_component_separate": "component_separate",
            "extraction_detect_symmetry": "detect_symmetry",
            "extraction_edge_loop_analysis": "edge_loop_analysis",
            "extraction_face_group_analysis": "face_group_analysis",
            "extraction_render_angles": "render_angles",
        })

        # Text tools
        text = get_text_handler()
        self._safe_update(text, {
            "text_create": "create",
            "text_edit": "edit",
            "text_to_mesh": "to_mesh",
        })

        # Armature tools
        armature = get_armature_handler()
        self._safe_update(armature, {
            "armature_create": "create",
            "armature_add_bone": "add_bone",
            "armature_bind": "bind",
            "armature_pose_bone": "pose_bone",
            "armature_weight_paint_assign": "weight_paint_assign",
        })

    def execute(self, tool_name: str, params: Dict[str, Any]) -> str:
        """Execute a tool by name with given parameters.

        Args:
            tool_name: Name of the tool to execute.
            params: Parameters to pass to the tool.

        Returns:
            Result string from tool execution.
        """
        handler = self._tool_map.get(tool_name)

        if handler is None:
            logger.warning(f"Tool not found in dispatcher: {tool_name}")
            return f"Error: Tool '{tool_name}' not found in dispatcher."

        try:
            # Filter params to only include non-None values
            filtered_params = {k: v for k, v in params.items() if v is not None}
            return handler(**filtered_params)
        except TypeError as e:
            logger.error(f"Parameter error for {tool_name}: {e}")
            return f"Error executing {tool_name}: {str(e)}"
        except Exception as e:
            logger.error(f"Tool execution failed for {tool_name}: {e}")
            return f"Error executing {tool_name}: {str(e)}"

    def has_tool(self, tool_name: str) -> bool:
        """Check if a tool is registered.

        Args:
            tool_name: Name of the tool.

        Returns:
            True if tool is registered.
        """
        return tool_name in self._tool_map

    def list_tools(self) -> list:
        """List all registered tool names.

        Returns:
            List of tool names.
        """
        return list(self._tool_map.keys())


# Singleton instance
_dispatcher_instance: Optional[ToolDispatcher] = None


def get_dispatcher() -> ToolDispatcher:
    """Get singleton ToolDispatcher instance."""
    global _dispatcher_instance
    if _dispatcher_instance is None:
        _dispatcher_instance = ToolDispatcher()
    return _dispatcher_instance
