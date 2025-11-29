bl_info = {
    "name": "Blender AI MCP",
    "author": "Patryk Ciechański",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),  # Min version, tested on 5.0
    "location": "Background Service",
    "description": "RPC Server for AI MCP Control. GitHub: https://github.com/PatrykIti/blender-ai-mcp",
    "category": "System",
}

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
except ImportError:
    SceneHandler = None
    ModelingHandler = None
    MeshHandler = None
    CollectionHandler = None
    MaterialHandler = None
    UVHandler = None


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

        # Material
        rpc_server.register_handler("material.list", material_handler.list_materials)
        rpc_server.register_handler("material.list_by_object", material_handler.list_by_object)

        # UV
        rpc_server.register_handler("uv.list_maps", uv_handler.list_maps)

        rpc_server.start()
    else:
        print("[Blender AI MCP] Mock registration (bpy not found)")

def unregister():
    if bpy:
        print("[Blender AI MCP] Unregistering addon...")
        rpc_server.stop()

if __name__ == "__main__":
    register()
