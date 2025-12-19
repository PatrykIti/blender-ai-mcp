# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

bl_info = {
    "name": "Blender AI MCP",
    "author": "Patryk Ciechański",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),  # Min version, tested on 5.0
    "location": "Background Service",
    "description": "RPC Server for AI MCP Control. GitHub: https://github.com/PatrykIti/blender-ai-mcp",
    "category": "System",
}

__author__ = bl_info["author"]

try:
    import bpy
except ImportError:
    bpy = None

from .infrastructure.rpc_server import rpc_server
# Import Application Handlers
try:
    from .application.handlers.scene import SceneHandler
    from .application.handlers.modeling import ModelingHandler
    from .application.handlers.mesh import MeshHandler
    from .application.handlers.collection import CollectionHandler
    from .application.handlers.material import MaterialHandler
    from .application.handlers.uv import UVHandler
    from .application.handlers.curve import CurveHandler
    from .application.handlers.system import SystemHandler
    from .application.handlers.sculpt import SculptHandler
    from .application.handlers.baking import BakingHandler
    from .application.handlers.lattice import LatticeHandler
    from .application.handlers.extraction import ExtractionHandler
    from .application.handlers.text import TextHandler
    from .application.handlers.armature import ArmatureHandler
except ImportError:
    SceneHandler = None
    ModelingHandler = None
    MeshHandler = None
    CollectionHandler = None
    MaterialHandler = None
    UVHandler = None
    CurveHandler = None
    SystemHandler = None
    SculptHandler = None
    BakingHandler = None
    LatticeHandler = None
    ExtractionHandler = None
    TextHandler = None
    ArmatureHandler = None


def register():
    if bpy:
        print("[Blender AI MCP] Registering addon...")

        # --- Composition Root (Simple Manual DI) ---
        scene_handler = SceneHandler()
        modeling_handler = ModelingHandler()
        mesh_handler = MeshHandler()
        collection_handler = CollectionHandler()
        material_handler = MaterialHandler()
        uv_handler = UVHandler()
        curve_handler = CurveHandler()
        system_handler = SystemHandler()
        sculpt_handler = SculptHandler()
        baking_handler = BakingHandler()
        lattice_handler = LatticeHandler()
        extraction_handler = ExtractionHandler()
        text_handler = TextHandler()
        armature_handler = ArmatureHandler()

        # --- Register RPC Handlers ---
        # Scene
        rpc_server.register_handler("scene.list_objects", scene_handler.list_objects)
        rpc_server.register_handler("scene.delete_object", scene_handler.delete_object)
        rpc_server.register_handler("scene.clean_scene", scene_handler.clean_scene)
        rpc_server.register_handler("scene.duplicate_object", scene_handler.duplicate_object)
        rpc_server.register_handler("scene.set_active_object", scene_handler.set_active_object)
        rpc_server.register_handler("scene.get_mode", scene_handler.get_mode)
        rpc_server.register_handler("scene.list_selection", scene_handler.list_selection)
        rpc_server.register_handler("scene.inspect_object", scene_handler.inspect_object)
        rpc_server.register_handler("scene.snapshot_state", scene_handler.snapshot_state)
        rpc_server.register_handler("scene.inspect_material_slots", scene_handler.inspect_material_slots)
        rpc_server.register_handler("scene.inspect_mesh_topology", scene_handler.inspect_mesh_topology)
        rpc_server.register_handler("scene.inspect_modifiers", scene_handler.inspect_modifiers)
        rpc_server.register_handler("scene.get_viewport", scene_handler.get_viewport)
        rpc_server.register_handler("scene.create_light", scene_handler.create_light)
        rpc_server.register_handler("scene.create_camera", scene_handler.create_camera)
        rpc_server.register_handler("scene.create_empty", scene_handler.create_empty)
        rpc_server.register_handler("scene.set_mode", scene_handler.set_mode)
        # TASK-043: Scene Utility Tools
        rpc_server.register_handler("scene.rename_object", scene_handler.rename_object)
        rpc_server.register_handler("scene.hide_object", scene_handler.hide_object)
        rpc_server.register_handler("scene.show_all_objects", scene_handler.show_all_objects)
        rpc_server.register_handler("scene.isolate_object", scene_handler.isolate_object)
        rpc_server.register_handler("scene.camera_orbit", scene_handler.camera_orbit)
        rpc_server.register_handler("scene.camera_focus", scene_handler.camera_focus)
        # TASK-045: Object Inspection Tools
        rpc_server.register_handler("scene.get_custom_properties", scene_handler.get_custom_properties)
        rpc_server.register_handler("scene.set_custom_property", scene_handler.set_custom_property)
        rpc_server.register_handler("scene.get_hierarchy", scene_handler.get_hierarchy)
        rpc_server.register_handler("scene.get_bounding_box", scene_handler.get_bounding_box)
        rpc_server.register_handler("scene.get_origin_info", scene_handler.get_origin_info)

        # Modeling
        rpc_server.register_handler("modeling.create_primitive", modeling_handler.create_primitive)
        rpc_server.register_handler("modeling.transform_object", modeling_handler.transform_object)
        rpc_server.register_handler("modeling.add_modifier", modeling_handler.add_modifier)
        rpc_server.register_handler("modeling.apply_modifier", modeling_handler.apply_modifier)
        rpc_server.register_handler("modeling.convert_to_mesh", modeling_handler.convert_to_mesh)
        rpc_server.register_handler("modeling.join_objects", modeling_handler.join_objects)
        rpc_server.register_handler("modeling.separate_object", modeling_handler.separate_object)
        rpc_server.register_handler("modeling.set_origin", modeling_handler.set_origin)
        rpc_server.register_handler("modeling.get_modifiers", modeling_handler.get_modifiers)

        # Mesh (Edit Mode)
        rpc_server.register_handler("mesh.select_all", mesh_handler.select_all)
        rpc_server.register_handler("mesh.delete_selected", mesh_handler.delete_selected)
        rpc_server.register_handler("mesh.select_by_index", mesh_handler.select_by_index)
        rpc_server.register_handler("mesh.extrude_region", mesh_handler.extrude_region)
        rpc_server.register_handler("mesh.fill_holes", mesh_handler.fill_holes)
        rpc_server.register_handler("mesh.bevel", mesh_handler.bevel)
        rpc_server.register_handler("mesh.loop_cut", mesh_handler.loop_cut)
        rpc_server.register_handler("mesh.inset", mesh_handler.inset)
        rpc_server.register_handler("mesh.boolean", mesh_handler.boolean)
        rpc_server.register_handler("mesh.merge_by_distance", mesh_handler.merge_by_distance)
        rpc_server.register_handler("mesh.subdivide", mesh_handler.subdivide)
        rpc_server.register_handler("mesh.smooth_vertices", mesh_handler.smooth_vertices)
        rpc_server.register_handler("mesh.flatten_vertices", mesh_handler.flatten_vertices)
        rpc_server.register_handler("mesh.list_groups", mesh_handler.list_groups)
        rpc_server.register_handler("mesh.select_loop", mesh_handler.select_loop)
        rpc_server.register_handler("mesh.select_ring", mesh_handler.select_ring)
        rpc_server.register_handler("mesh.select_linked", mesh_handler.select_linked)
        rpc_server.register_handler("mesh.select_more", mesh_handler.select_more)
        rpc_server.register_handler("mesh.select_less", mesh_handler.select_less)
        rpc_server.register_handler("mesh.get_vertex_data", mesh_handler.get_vertex_data)
        rpc_server.register_handler("mesh.get_edge_data", mesh_handler.get_edge_data)
        rpc_server.register_handler("mesh.get_face_data", mesh_handler.get_face_data)
        rpc_server.register_handler("mesh.get_uv_data", mesh_handler.get_uv_data)
        rpc_server.register_handler("mesh.select_by_location", mesh_handler.select_by_location)
        rpc_server.register_handler("mesh.select_boundary", mesh_handler.select_boundary)
        # TASK-016: Organic & Deform Tools
        rpc_server.register_handler("mesh.randomize", mesh_handler.randomize)
        rpc_server.register_handler("mesh.shrink_fatten", mesh_handler.shrink_fatten)
        # TASK-017: Vertex Group Tools
        rpc_server.register_handler("mesh.create_vertex_group", mesh_handler.create_vertex_group)
        rpc_server.register_handler("mesh.assign_to_group", mesh_handler.assign_to_group)
        rpc_server.register_handler("mesh.remove_from_group", mesh_handler.remove_from_group)
        # TASK-018: Phase 2.5 - Advanced Precision Tools
        rpc_server.register_handler("mesh.bisect", mesh_handler.bisect)
        rpc_server.register_handler("mesh.edge_slide", mesh_handler.edge_slide)
        rpc_server.register_handler("mesh.vert_slide", mesh_handler.vert_slide)
        rpc_server.register_handler("mesh.triangulate", mesh_handler.triangulate)
        rpc_server.register_handler("mesh.remesh_voxel", mesh_handler.remesh_voxel)

        # Collection
        rpc_server.register_handler("collection.list", collection_handler.list_collections)
        rpc_server.register_handler("collection.list_objects", collection_handler.list_objects)
        rpc_server.register_handler("collection.manage", collection_handler.manage_collection)

        # Material
        rpc_server.register_handler("material.list", material_handler.list_materials)
        rpc_server.register_handler("material.list_by_object", material_handler.list_by_object)
        # TASK-023: Material Tools
        rpc_server.register_handler("material.create", material_handler.create_material)
        rpc_server.register_handler("material.assign", material_handler.assign_material)
        rpc_server.register_handler("material.set_params", material_handler.set_material_params)
        rpc_server.register_handler("material.set_texture", material_handler.set_material_texture)
        # TASK-045-6: material_inspect_nodes
        rpc_server.register_handler("material.inspect_nodes", material_handler.inspect_nodes)

        # UV
        rpc_server.register_handler("uv.list_maps", uv_handler.list_maps)
        # TASK-024: UV Tools
        rpc_server.register_handler("uv.unwrap", uv_handler.unwrap)
        rpc_server.register_handler("uv.pack_islands", uv_handler.pack_islands)
        rpc_server.register_handler("uv.create_seam", uv_handler.create_seam)

        # TASK-019: Phase 2.4 - Core Transform & Geometry
        rpc_server.register_handler("mesh.transform_selected", mesh_handler.transform_selected)
        rpc_server.register_handler("mesh.bridge_edge_loops", mesh_handler.bridge_edge_loops)
        rpc_server.register_handler("mesh.duplicate_selected", mesh_handler.duplicate_selected)

        # TASK-021: Phase 2.6 - Curves & Procedural
        rpc_server.register_handler("curve.create_curve", curve_handler.create_curve)
        rpc_server.register_handler("curve.curve_to_mesh", curve_handler.curve_to_mesh)
        rpc_server.register_handler("mesh.spin", mesh_handler.spin)
        rpc_server.register_handler("mesh.screw", mesh_handler.screw)
        rpc_server.register_handler("mesh.add_vertex", mesh_handler.add_vertex)
        rpc_server.register_handler("mesh.add_edge_face", mesh_handler.add_edge_face)

        # Export Tools (consolidated into system_handler)
        rpc_server.register_handler("export.glb", system_handler.export_glb)
        rpc_server.register_handler("export.fbx", system_handler.export_fbx)
        rpc_server.register_handler("export.obj", system_handler.export_obj)

        # TASK-025: System Tools
        rpc_server.register_handler("system.set_mode", system_handler.set_mode)
        rpc_server.register_handler("system.undo", system_handler.undo)
        rpc_server.register_handler("system.redo", system_handler.redo)
        rpc_server.register_handler("system.save_file", system_handler.save_file)
        rpc_server.register_handler("system.new_file", system_handler.new_file)
        rpc_server.register_handler("system.snapshot", system_handler.snapshot)
        rpc_server.register_handler("system.purge_orphans", system_handler.purge_orphans)

        # TASK-027: Sculpting Tools
        rpc_server.register_handler("sculpt.auto", sculpt_handler.auto_sculpt)
        rpc_server.register_handler("sculpt.brush_smooth", sculpt_handler.brush_smooth)
        rpc_server.register_handler("sculpt.brush_grab", sculpt_handler.brush_grab)
        rpc_server.register_handler("sculpt.brush_crease", sculpt_handler.brush_crease)

        # TASK-038: Organic Modeling Tools
        # Metaball tools
        rpc_server.register_handler("modeling.metaball_create", modeling_handler.metaball_create)
        rpc_server.register_handler("modeling.metaball_add_element", modeling_handler.metaball_add_element)
        rpc_server.register_handler("modeling.metaball_to_mesh", modeling_handler.metaball_to_mesh)
        # Skin modifier tools
        rpc_server.register_handler("modeling.skin_create_skeleton", modeling_handler.skin_create_skeleton)
        rpc_server.register_handler("modeling.skin_set_radius", modeling_handler.skin_set_radius)
        # Sculpt brushes
        rpc_server.register_handler("sculpt.brush_clay", sculpt_handler.brush_clay)
        rpc_server.register_handler("sculpt.brush_inflate", sculpt_handler.brush_inflate)
        rpc_server.register_handler("sculpt.brush_blob", sculpt_handler.brush_blob)
        rpc_server.register_handler("sculpt.brush_snake_hook", sculpt_handler.brush_snake_hook)
        rpc_server.register_handler("sculpt.brush_draw", sculpt_handler.brush_draw)
        rpc_server.register_handler("sculpt.brush_pinch", sculpt_handler.brush_pinch)
        # Dyntopo tools
        rpc_server.register_handler("sculpt.enable_dyntopo", sculpt_handler.enable_dyntopo)
        rpc_server.register_handler("sculpt.disable_dyntopo", sculpt_handler.disable_dyntopo)
        rpc_server.register_handler("sculpt.dyntopo_flood_fill", sculpt_handler.dyntopo_flood_fill)
        # Proportional editing
        rpc_server.register_handler("mesh.set_proportional_edit", mesh_handler.set_proportional_edit)

        # TASK-029: Edge Weights & Creases (Subdivision Control)
        rpc_server.register_handler("mesh.edge_crease", mesh_handler.edge_crease)
        rpc_server.register_handler("mesh.bevel_weight", mesh_handler.bevel_weight)
        rpc_server.register_handler("mesh.mark_sharp", mesh_handler.mark_sharp)

        # TASK-030: Mesh Cleanup & Optimization
        rpc_server.register_handler("mesh.dissolve", mesh_handler.dissolve)
        rpc_server.register_handler("mesh.tris_to_quads", mesh_handler.tris_to_quads)
        rpc_server.register_handler("mesh.normals_make_consistent", mesh_handler.normals_make_consistent)
        rpc_server.register_handler("mesh.decimate", mesh_handler.decimate)

        # TASK-032: Knife & Cut Tools
        rpc_server.register_handler("mesh.knife_project", mesh_handler.knife_project)
        rpc_server.register_handler("mesh.rip", mesh_handler.rip)
        rpc_server.register_handler("mesh.split", mesh_handler.split)
        rpc_server.register_handler("mesh.edge_split", mesh_handler.edge_split)

        # TASK-036: Symmetry & Advanced Fill
        rpc_server.register_handler("mesh.symmetrize", mesh_handler.symmetrize)
        rpc_server.register_handler("mesh.grid_fill", mesh_handler.grid_fill)
        rpc_server.register_handler("mesh.poke_faces", mesh_handler.poke_faces)
        rpc_server.register_handler("mesh.beautify_fill", mesh_handler.beautify_fill)
        rpc_server.register_handler("mesh.mirror", mesh_handler.mirror)

        # TASK-031: Baking Tools
        rpc_server.register_handler("baking.normal_map", baking_handler.bake_normal_map)
        rpc_server.register_handler("baking.ao", baking_handler.bake_ao)
        rpc_server.register_handler("baking.combined", baking_handler.bake_combined)
        rpc_server.register_handler("baking.diffuse", baking_handler.bake_diffuse)

        # Import Tools (consolidated into system_handler)
        rpc_server.register_handler("import.obj", system_handler.import_obj)
        rpc_server.register_handler("import.fbx", system_handler.import_fbx)
        rpc_server.register_handler("import.glb", system_handler.import_glb)
        rpc_server.register_handler("import.image_as_plane", system_handler.import_image_as_plane)

        # TASK-033: Lattice Deformation Tools
        rpc_server.register_handler("lattice.create", lattice_handler.lattice_create)
        rpc_server.register_handler("lattice.bind", lattice_handler.lattice_bind)
        rpc_server.register_handler("lattice.edit_point", lattice_handler.lattice_edit_point)

        # TASK-044: Extraction Analysis Tools
        rpc_server.register_handler("extraction.deep_topology", extraction_handler.deep_topology)
        rpc_server.register_handler("extraction.component_separate", extraction_handler.component_separate)
        rpc_server.register_handler("extraction.detect_symmetry", extraction_handler.detect_symmetry)
        rpc_server.register_handler("extraction.edge_loop_analysis", extraction_handler.edge_loop_analysis)
        rpc_server.register_handler("extraction.face_group_analysis", extraction_handler.face_group_analysis)
        rpc_server.register_handler("extraction.render_angles", extraction_handler.render_angles)

        # TASK-034: Text & Annotations
        rpc_server.register_handler("text.create", text_handler.create)
        rpc_server.register_handler("text.edit", text_handler.edit)
        rpc_server.register_handler("text.to_mesh", text_handler.to_mesh)

        # TASK-037: Armature & Rigging
        rpc_server.register_handler("armature.create", armature_handler.create)
        rpc_server.register_handler("armature.add_bone", armature_handler.add_bone)
        rpc_server.register_handler("armature.bind", armature_handler.bind)
        rpc_server.register_handler("armature.pose_bone", armature_handler.pose_bone)
        rpc_server.register_handler("armature.weight_paint_assign", armature_handler.weight_paint_assign)

        rpc_server.start()
    else:
        print("[Blender AI MCP] Mock registration (bpy not found)")

def unregister():
    if bpy:
        print("[Blender AI MCP] Unregistering addon...")
        rpc_server.stop()

if __name__ == "__main__":
    register()
