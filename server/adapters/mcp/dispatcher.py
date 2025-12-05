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

    def _register_tools(self) -> None:
        """Register all tool mappings."""
        # Scene tools
        scene = get_scene_handler()
        self._tool_map.update({
            "scene_list_objects": scene.list_objects,
            "scene_delete_object": scene.delete_object,
            "scene_clean_scene": scene.clean_scene,
            "scene_duplicate_object": scene.duplicate_object,
            "scene_set_active_object": scene.set_active_object,
            "scene_get_mode": scene.get_mode,
            "scene_list_selection": scene.list_selection,
            "scene_inspect_object": scene.inspect_object,
            "scene_snapshot_state": scene.snapshot_state,
            "scene_compare_snapshot": scene.compare_snapshot,
            "scene_inspect_material_slots": scene.inspect_material_slots,
            "scene_inspect_mesh_topology": scene.inspect_mesh_topology,
            "scene_inspect_modifiers": scene.inspect_modifiers,
            "scene_create_light": scene.create_light,
            "scene_create_camera": scene.create_camera,
            "scene_create_empty": scene.create_empty,
            "scene_rename_object": scene.rename_object,
            "scene_hide_object": scene.hide_object,
            "scene_show_all_objects": scene.show_all_objects,
            "scene_isolate_object": scene.isolate_object,
            "scene_camera_orbit": scene.camera_orbit,
            "scene_camera_focus": scene.camera_focus,
            # TASK-045: Object Inspection Tools
            "scene_get_custom_properties": scene.get_custom_properties,
            "scene_set_custom_property": scene.set_custom_property,
            "scene_get_hierarchy": scene.get_hierarchy,
            "scene_get_bounding_box": scene.get_bounding_box,
            "scene_get_origin_info": scene.get_origin_info,
        })

        # System tools
        system = get_system_handler()
        self._tool_map.update({
            "system_set_mode": system.set_mode,
            "system_undo": system.undo,
            "system_redo": system.redo,
            "system_save_file": system.save_file,
            "system_new_file": system.new_file,
            "system_snapshot": system.snapshot,
        })

        # Modeling tools
        modeling = get_modeling_handler()
        self._tool_map.update({
            "modeling_create_primitive": modeling.create_primitive,
            "modeling_transform_object": modeling.transform_object,
            "modeling_add_modifier": modeling.add_modifier,
            "modeling_apply_modifier": modeling.apply_modifier,
            "modeling_list_modifiers": modeling.list_modifiers,
            "modeling_convert_to_mesh": modeling.convert_to_mesh,
            "modeling_join_objects": modeling.join_objects,
            "modeling_separate_object": modeling.separate_object,
            "modeling_set_origin": modeling.set_origin,
        })

        # Mesh tools
        mesh = get_mesh_handler()
        self._tool_map.update({
            "mesh_select_all": mesh.select_all,
            "mesh_select_by_index": mesh.select_by_index,
            "mesh_select_linked": mesh.select_linked,
            "mesh_select_more": mesh.select_more,
            "mesh_select_less": mesh.select_less,
            "mesh_select_boundary": mesh.select_boundary,
            "mesh_select_loop": mesh.select_loop,
            "mesh_select_ring": mesh.select_ring,
            "mesh_select_by_location": mesh.select_by_location,
            "mesh_get_vertex_data": mesh.get_vertex_data,
            "mesh_delete_selected": mesh.delete_selected,
            "mesh_extrude_region": mesh.extrude_region,
            "mesh_fill_holes": mesh.fill_holes,
            "mesh_bevel": mesh.bevel,
            "mesh_loop_cut": mesh.loop_cut,
            "mesh_inset": mesh.inset,
            "mesh_boolean": mesh.boolean_operation,
            "mesh_merge_by_distance": mesh.merge_by_distance,
            "mesh_subdivide": mesh.subdivide,
            "mesh_smooth": mesh.smooth,
            "mesh_flatten": mesh.flatten,
            "mesh_randomize": mesh.randomize,
            "mesh_shrink_fatten": mesh.shrink_fatten,
            "mesh_transform_selected": mesh.transform_selected,
            "mesh_bridge_edge_loops": mesh.bridge_edge_loops,
            "mesh_duplicate_selected": mesh.duplicate_selected,
            "mesh_bisect": mesh.bisect,
            "mesh_edge_slide": mesh.edge_slide,
            "mesh_vert_slide": mesh.vert_slide,
            "mesh_triangulate": mesh.triangulate,
            "mesh_remesh_voxel": mesh.remesh_voxel,
            "mesh_spin": mesh.spin,
            "mesh_screw": mesh.screw,
            "mesh_add_vertex": mesh.add_vertex,
            "mesh_add_edge_face": mesh.add_edge_face,
            "mesh_list_groups": mesh.list_groups,
            "mesh_create_vertex_group": mesh.create_vertex_group,
            "mesh_assign_to_group": mesh.assign_to_group,
            "mesh_remove_from_group": mesh.remove_from_group,
            "mesh_edge_crease": mesh.edge_crease,
            "mesh_bevel_weight": mesh.bevel_weight,
            "mesh_mark_sharp": mesh.mark_sharp,
            "mesh_dissolve": mesh.dissolve,
            "mesh_tris_to_quads": mesh.tris_to_quads,
            "mesh_normals_make_consistent": mesh.normals_make_consistent,
            "mesh_decimate": mesh.decimate,
            "mesh_knife_project": mesh.knife_project,
            "mesh_rip": mesh.rip,
            "mesh_split": mesh.split,
            "mesh_edge_split": mesh.edge_split,
            "mesh_set_proportional_edit": mesh.set_proportional_edit,
            # TASK-036: Symmetry & Advanced Fill
            "mesh_symmetrize": mesh.symmetrize,
            "mesh_grid_fill": mesh.grid_fill,
            "mesh_poke_faces": mesh.poke_faces,
            "mesh_beautify_fill": mesh.beautify_fill,
            "mesh_mirror": mesh.mirror,
        })

        # Material tools
        material = get_material_handler()
        self._tool_map.update({
            "material_list": material.list_materials,
            "material_list_by_object": material.list_by_object,
            "material_create": material.create_material,
            "material_assign": material.assign_material,
            "material_set_params": material.set_material_params,
            "material_set_texture": material.set_material_texture,
            # TASK-045-6: material_inspect_nodes
            "material_inspect_nodes": material.inspect_nodes,
        })

        # UV tools
        uv = get_uv_handler()
        self._tool_map.update({
            "uv_list_maps": uv.list_maps,
            "uv_unwrap": uv.unwrap,
            "uv_pack_islands": uv.pack_islands,
            "uv_create_seam": uv.create_seam,
        })

        # Collection tools
        collection = get_collection_handler()
        self._tool_map.update({
            "collection_list": collection.list_collections,
            "collection_list_objects": collection.list_objects,
            "collection_create": collection.create,
            "collection_delete": collection.delete,
            "collection_rename": collection.rename,
            "collection_move_object": collection.move_object,
        })

        # Curve tools
        curve = get_curve_handler()
        self._tool_map.update({
            "curve_create": curve.create,
            "curve_to_mesh": curve.to_mesh,
        })

        # Sculpt tools
        sculpt = get_sculpt_handler()
        self._tool_map.update({
            "sculpt_auto": sculpt.auto_sculpt,
            "sculpt_brush_smooth": sculpt.brush_smooth,
            "sculpt_brush_grab": sculpt.brush_grab,
            "sculpt_brush_crease": sculpt.brush_crease,
            "sculpt_brush_clay": sculpt.brush_clay,
            "sculpt_brush_inflate": sculpt.brush_inflate,
            "sculpt_brush_blob": sculpt.brush_blob,
            "sculpt_brush_snake_hook": sculpt.brush_snake_hook,
            "sculpt_brush_draw": sculpt.brush_draw,
            "sculpt_brush_pinch": sculpt.brush_pinch,
            "sculpt_enable_dyntopo": sculpt.enable_dyntopo,
            "sculpt_disable_dyntopo": sculpt.disable_dyntopo,
            "sculpt_dyntopo_flood_fill": sculpt.dyntopo_flood_fill,
        })

        # Baking tools
        baking = get_baking_handler()
        self._tool_map.update({
            "bake_normal_map": baking.bake_normal_map,
            "bake_ao": baking.bake_ao,
            "bake_combined": baking.bake_combined,
            "bake_diffuse": baking.bake_diffuse,
        })

        # Lattice tools
        lattice = get_lattice_handler()
        self._tool_map.update({
            "lattice_create": lattice.create,
            "lattice_bind": lattice.bind,
            "lattice_edit_point": lattice.edit_point,
        })

        # Extraction tools
        extraction = get_extraction_handler()
        self._tool_map.update({
            "extraction_deep_topology": extraction.deep_topology,
            "extraction_component_separate": extraction.component_separate,
            "extraction_detect_symmetry": extraction.detect_symmetry,
            "extraction_edge_loop_analysis": extraction.edge_loop_analysis,
            "extraction_face_group_analysis": extraction.face_group_analysis,
            "extraction_render_angles": extraction.render_angles,
        })

        # Text tools
        text = get_text_handler()
        self._tool_map.update({
            "text_create": text.create,
            "text_edit": text.edit,
            "text_to_mesh": text.to_mesh,
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
