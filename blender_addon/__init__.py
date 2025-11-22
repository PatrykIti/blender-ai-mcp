bl_info = {
    "name": "Blender AI MCP",
    "author": "PC",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),  # Min version, tested on 5.0
    "location": "Background Service",
    "description": "RPC Server for AI MCP Control",
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
except ImportError:
    SceneHandler = None


def register():
    if bpy:
        print("[Blender AI MCP] Registering addon...")
        
        # --- Composition Root (Simple Manual DI) ---
        scene_handler = SceneHandler()

        # --- Register RPC Handlers ---
        rpc_server.register_handler("scene.list_objects", scene_handler.list_objects)
        rpc_server.register_handler("scene.delete_object", scene_handler.delete_object)
        rpc_server.register_handler("scene.clean_scene", scene_handler.clean_scene)
        
        rpc_server.start()
    else:
        print("[Blender AI MCP] Mock registration (bpy not found)")

def unregister():
    if bpy:
        print("[Blender AI MCP] Unregistering addon...")
        rpc_server.stop()

if __name__ == "__main__":
    register()