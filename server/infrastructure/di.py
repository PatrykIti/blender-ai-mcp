from server.adapters.rpc.client import RpcClient
from server.application.tool_handlers.scene_handler import SceneToolHandler
from server.application.tool_handlers.modeling_handler import ModelingToolHandler
from server.application.tool_handlers.mesh_handler import MeshToolHandler
from server.application.tool_handlers.collection_handler import CollectionToolHandler
from server.application.tool_handlers.material_handler import MaterialToolHandler
from server.application.tool_handlers.uv_handler import UVToolHandler
from server.application.tool_handlers.curve_handler import CurveToolHandler
from server.application.tool_handlers.system_handler import SystemToolHandler
from server.application.tool_handlers.export_handler import ExportToolHandler
from server.application.tool_handlers.import_handler import ImportToolHandler
from server.application.tool_handlers.sculpt_handler import SculptToolHandler
from server.application.tool_handlers.baking_handler import BakingToolHandler
from server.domain.interfaces.rpc import IRpcClient
from server.domain.tools.scene import ISceneTool
from server.domain.tools.modeling import IModelingTool
from server.domain.tools.mesh import IMeshTool
from server.domain.tools.collection import ICollectionTool
from server.domain.tools.material import IMaterialTool
from server.domain.tools.uv import IUVTool
from server.domain.tools.curve import ICurveTool
from server.domain.tools.system import ISystemTool
from server.domain.tools.export import IExportTool
from server.domain.tools.import_tool import IImportTool
from server.domain.tools.sculpt import ISculptTool
from server.domain.tools.baking import IBakingTool
from server.infrastructure.config import get_config

# --- Providers (Factory Functions) ---
# Wzorzec "Singleton" realizowany przez zmienne modułu (lub lru_cache)

_rpc_client_instance = None

def get_rpc_client() -> IRpcClient:
    """Provider for IRpcClient. Acts as a Singleton."""
    global _rpc_client_instance
    if _rpc_client_instance is None:
        config = get_config()
        _rpc_client_instance = RpcClient(host=config.BLENDER_RPC_HOST, port=config.BLENDER_RPC_PORT)
    return _rpc_client_instance

def get_scene_handler() -> ISceneTool:
    """Provider for ISceneTool. Injects RpcClient."""
    rpc = get_rpc_client()
    return SceneToolHandler(rpc)

def get_modeling_handler() -> IModelingTool:
    """Provider for IModelingTool. Injects RpcClient."""
    rpc = get_rpc_client()
    return ModelingToolHandler(rpc)

def get_mesh_handler() -> IMeshTool:
    """Provider for IMeshTool. Injects RpcClient."""
    rpc = get_rpc_client()
    return MeshToolHandler(rpc)

def get_collection_handler() -> ICollectionTool:
    """Provider for ICollectionTool. Injects RpcClient."""
    rpc = get_rpc_client()
    return CollectionToolHandler(rpc)

def get_material_handler() -> IMaterialTool:
    """Provider for IMaterialTool. Injects RpcClient."""
    rpc = get_rpc_client()
    return MaterialToolHandler(rpc)

def get_uv_handler() -> IUVTool:
    """Provider for IUVTool. Injects RpcClient."""
    rpc = get_rpc_client()
    return UVToolHandler(rpc)


def get_curve_handler() -> ICurveTool:
    """Provider for ICurveTool. Injects RpcClient."""
    rpc = get_rpc_client()
    return CurveToolHandler(rpc)


def get_system_handler() -> ISystemTool:
    """Provider for ISystemTool. Injects RpcClient."""
    rpc = get_rpc_client()
    return SystemToolHandler(rpc)


def get_export_handler() -> IExportTool:
    """Provider for IExportTool. Injects RpcClient."""
    rpc = get_rpc_client()
    return ExportToolHandler(rpc)


def get_sculpt_handler() -> ISculptTool:
    """Provider for ISculptTool. Injects RpcClient."""
    rpc = get_rpc_client()
    return SculptToolHandler(rpc)


def get_baking_handler() -> IBakingTool:
    """Provider for IBakingTool. Injects RpcClient."""
    rpc = get_rpc_client()
    return BakingToolHandler(rpc)


def get_import_handler() -> IImportTool:
    """Provider for IImportTool. Injects RpcClient."""
    rpc = get_rpc_client()
    return ImportToolHandler(rpc)
