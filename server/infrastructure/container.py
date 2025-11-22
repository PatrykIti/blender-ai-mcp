from dataclasses import dataclass
from server.adapters.rpc.client import RpcClient
from server.application.tool_handlers.scene_handler import SceneToolHandler

@dataclass
class Container:
    """Dependency Injection Container"""
    scene_handler: SceneToolHandler

def build_container() -> Container:
    """Constructs the application dependency graph."""
    # 1. Infrastructure / Adapters (Low Level)
    rpc_client = RpcClient()
    
    # 2. Application (High Level)
    scene_handler = SceneToolHandler(rpc_client)
    
    return Container(
        scene_handler=scene_handler
    )

# Global container instance (created once)
_container = build_container()

def get_container() -> Container:
    return _container
