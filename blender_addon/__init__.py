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
except ImportError:
    SceneHandler = None
    ModelingHandler = None
    MeshHandler = None


def register():
    if bpy:
        print("[Blender AI MCP] Registering addon...")
        
        # --- Composition Root (Simple Manual DI) ---
        scene_handler = SceneHandler()
        modeling_handler = ModelingHandler()
        mesh_handler = MeshHandler()

        # --- Register RPC Handlers ---
        # Scene
        rpc_server.register_handler("scene.list_objects", scene_handler.list_objects)
        rpc_server.register_handler("scene.delete_object", scene_handler.delete_object)
        rpc_server.register_handler("scene.clean_scene", scene_handler.clean_scene)
        rpc_server.register_handler("scene.duplicate_object", scene_handler.duplicate_object)
        rpc_server.register_handler("scene.set_active_object", scene_handler.set_active_object)
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
        
        rpc_server.start()
    else:
        print("[Blender AI MCP] Mock registration (bpy not found)")

def unregister():
    if bpy:
        print("[Blender AI MCP] Unregistering addon...")
        rpc_server.stop()

if __name__ == "__main__":
    register()