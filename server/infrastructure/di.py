from server.adapters.rpc.client import RpcClient
from server.application.tool_handlers.scene_handler import SceneToolHandler
from server.application.tool_handlers.modeling_handler import ModelingToolHandler
from server.domain.interfaces.rpc import IRpcClient
from server.domain.tools.scene import ISceneTool
from server.domain.tools.modeling import IModelingTool

# --- Providers (Factory Functions) ---
# Wzorzec "Singleton" realizowany przez zmienne modułu (lub lru_cache)

_rpc_client_instance = None

def get_rpc_client() -> IRpcClient:
    """Provider for IRpcClient. Acts as a Singleton."""
    global _rpc_client_instance
    if _rpc_client_instance is None:
        _rpc_client_instance = RpcClient()
    return _rpc_client_instance

def get_scene_handler() -> ISceneTool:
    """Provider for ISceneTool. Injects RpcClient."""
    rpc = get_rpc_client()
    return SceneToolHandler(rpc)

def get_modeling_handler() -> IModelingTool:
    """Provider for IModelingTool. Injects RpcClient."""
    rpc = get_rpc_client()
    return ModelingToolHandler(rpc)
