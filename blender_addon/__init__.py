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

from .rpc_server import rpc_server
# Import API handlers
try:
    from .api import scene
except ImportError:
    scene = None


def register():
    if bpy:
        print("[Blender AI MCP] Registering addon...")
        
        # Register RPC Handlers
        if scene:
            rpc_server.register_handler("scene.list_objects", scene.list_objects)
            rpc_server.register_handler("scene.delete_object", scene.delete_object)
            rpc_server.register_handler("scene.clean_scene", scene.clean_scene)
        
        rpc_server.start()
    else:
        print("[Blender AI MCP] Mock registration (bpy not found)")

def unregister():
    if bpy:
        print("[Blender AI MCP] Unregistering addon...")
        rpc_server.stop()

if __name__ == "__main__":
    register()
