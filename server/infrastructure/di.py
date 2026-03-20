from typing import Optional
from server.adapters.rpc.client import RpcClient
from server.application.tool_handlers.scene_handler import SceneToolHandler
from server.application.tool_handlers.modeling_handler import ModelingToolHandler
from server.application.tool_handlers.mesh_handler import MeshToolHandler
from server.application.tool_handlers.collection_handler import CollectionToolHandler
from server.application.tool_handlers.material_handler import MaterialToolHandler
from server.application.tool_handlers.uv_handler import UVToolHandler
from server.application.tool_handlers.curve_handler import CurveToolHandler
from server.application.tool_handlers.system_handler import SystemToolHandler
from server.application.tool_handlers.sculpt_handler import SculptToolHandler
from server.application.tool_handlers.baking_handler import BakingToolHandler
from server.application.tool_handlers.lattice_handler import LatticeToolHandler
from server.application.tool_handlers.router_handler import RouterToolHandler
from server.application.tool_handlers.extraction_handler import ExtractionToolHandler
from server.application.tool_handlers.text_handler import TextToolHandler
from server.application.tool_handlers.armature_handler import ArmatureToolHandler
from server.application.tool_handlers.workflow_catalog_handler import (
    WorkflowCatalogToolHandler,
)
from server.domain.interfaces.rpc import IRpcClient
from server.domain.tools.scene import ISceneTool
from server.domain.tools.modeling import IModelingTool
from server.domain.tools.mesh import IMeshTool
from server.domain.tools.collection import ICollectionTool
from server.domain.tools.material import IMaterialTool
from server.domain.tools.uv import IUVTool
from server.domain.tools.curve import ICurveTool
from server.domain.tools.system import ISystemTool
from server.domain.tools.sculpt import ISculptTool
from server.domain.tools.baking import IBakingTool
from server.domain.tools.lattice import ILatticeTool
from server.domain.tools.router import IRouterTool
from server.domain.tools.extraction import IExtractionTool
from server.domain.tools.text import ITextTool
from server.domain.tools.armature import IArmatureTool
from server.domain.tools.workflow_catalog import IWorkflowCatalogTool
from server.infrastructure.config import get_config
from server.router.infrastructure.workflow_loader import get_workflow_loader

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

def get_sculpt_handler() -> ISculptTool:
    """Provider for ISculptTool. Injects RpcClient."""
    rpc = get_rpc_client()
    return SculptToolHandler(rpc)

def get_baking_handler() -> IBakingTool:
    """Provider for IBakingTool. Injects RpcClient."""
    rpc = get_rpc_client()
    return BakingToolHandler(rpc)

def get_lattice_handler() -> ILatticeTool:
    """Provider for ILatticeTool. Injects RpcClient."""
    rpc = get_rpc_client()
    return LatticeToolHandler(rpc)


def get_extraction_handler() -> IExtractionTool:
    """Provider for IExtractionTool. Injects RpcClient."""
    rpc = get_rpc_client()
    return ExtractionToolHandler(rpc)


def get_text_handler() -> ITextTool:
    """Provider for ITextTool. Injects RpcClient."""
    rpc = get_rpc_client()
    return TextToolHandler(rpc)


def get_armature_handler() -> IArmatureTool:
    """Provider for IArmatureTool. Injects RpcClient."""
    rpc = get_rpc_client()
    return ArmatureToolHandler(rpc)


# --- Router Supervisor ---

# Shared instances for router components (TASK-048)
_labse_model_instance = None
_vector_store_instance = None
_intent_classifier_instance = None
_workflow_classifier_instance = None
_router_instance = None


def get_labse_model():
    """Provider for shared LaBSE model (~1.8GB RAM).

    Singleton - shared between IntentClassifier and WorkflowIntentClassifier.
    """
    global _labse_model_instance
    if _labse_model_instance is None:
        try:
            import os
            from sentence_transformers import SentenceTransformer
            import logging
            running_pytest = os.getenv("PYTEST_CURRENT_TEST") is not None
            if running_pytest:
                logging.info("Skipping LaBSE load under pytest")
                return None

            local_only = os.getenv("HF_HUB_OFFLINE", "").lower() in ("1", "true", "yes")
            logging.info("Loading shared LaBSE model...")
            _labse_model_instance = SentenceTransformer(
                "sentence-transformers/LaBSE",
                local_files_only=local_only,
            )
            logging.info("Shared LaBSE model loaded")
        except ImportError:
            import logging
            logging.warning("sentence-transformers not installed, LaBSE model unavailable")
            return None
        except Exception as e:
            import logging
            logging.warning(f"Failed to load LaBSE model, falling back (reason: {e})")
            return None
    return _labse_model_instance


def get_vector_store():
    """Provider for shared LanceVectorStore.

    Singleton - shared between all classifiers.
    """
    global _vector_store_instance
    if _vector_store_instance is None:
        from server.router.infrastructure.vector_store.lance_store import LanceVectorStore
        _vector_store_instance = LanceVectorStore()
    return _vector_store_instance


def get_router_config():
    """Provider for RouterConfig."""
    from server.router.infrastructure.config import RouterConfig
    config = get_config()
    return RouterConfig(log_decisions=config.ROUTER_LOG_DECISIONS)


def get_intent_classifier():
    """Provider for IntentClassifier (tool classification).

    Singleton - uses shared LaBSE model and vector store.
    """
    global _intent_classifier_instance
    if _intent_classifier_instance is None:
        from server.router.application.classifier.intent_classifier import IntentClassifier
        _intent_classifier_instance = IntentClassifier(
            config=get_router_config(),
            vector_store=get_vector_store(),
            model=get_labse_model(),
        )
    return _intent_classifier_instance


def get_workflow_classifier():
    """Provider for WorkflowIntentClassifier (workflow classification).

    Singleton - uses shared LaBSE model and vector store.
    """
    global _workflow_classifier_instance
    if _workflow_classifier_instance is None:
        from server.router.application.classifier.workflow_intent_classifier import (
            WorkflowIntentClassifier,
        )
        _workflow_classifier_instance = WorkflowIntentClassifier(
            config=get_router_config(),
            vector_store=get_vector_store(),
            model=get_labse_model(),
        )
    return _workflow_classifier_instance


def get_router():
    """Provider for SupervisorRouter. Singleton with lazy initialization.

    Returns None if router is disabled in config.
    Uses shared classifiers via DI (TASK-048).
    """
    global _router_instance
    config = get_config()

    if not config.ROUTER_ENABLED:
        return None

    if _router_instance is None:
        from server.router.application.router import SupervisorRouter
        from server.router.infrastructure.metadata_loader import MetadataLoader

        _router_instance = SupervisorRouter(
            config=get_router_config(),
            rpc_client=get_rpc_client(),
            classifier=get_intent_classifier(),
            workflow_classifier=get_workflow_classifier(),
        )

        # Load tool metadata for intent classification
        try:
            loader = MetadataLoader()
            metadata = loader.load_all()
            # Convert ToolMetadata objects to dicts for classifier
            metadata_dicts = {
                name: tool.to_dict() for name, tool in metadata.items()
            }
            _router_instance.load_tool_metadata(metadata_dicts)
        except Exception as e:
            import logging
            logging.warning(f"Failed to load tool metadata for router: {e}")

    return _router_instance


def is_router_enabled() -> bool:
    """Check if router is enabled in config."""
    config = get_config()
    return config.ROUTER_ENABLED


# --- Parameter Resolution (TASK-055) ---

_parameter_store_instance = None
_parameter_resolver_instance = None


def get_parameter_store():
    """Provider for ParameterStore.

    Singleton - uses shared LanceDB vector store for learned mappings.
    """
    global _parameter_store_instance
    if _parameter_store_instance is None:
        from server.router.application.resolver.parameter_store import ParameterStore
        _parameter_store_instance = ParameterStore(
            vector_store=get_vector_store(),
            classifier=get_workflow_classifier(),
        )
    return _parameter_store_instance


def get_parameter_resolver():
    """Provider for ParameterResolver.

    Singleton - uses shared classifier and store.
    """
    global _parameter_resolver_instance
    if _parameter_resolver_instance is None:
        from server.router.application.resolver.parameter_resolver import ParameterResolver
        _parameter_resolver_instance = ParameterResolver(
            classifier=get_workflow_classifier(),
            store=get_parameter_store(),
        )
    return _parameter_resolver_instance


# --- Router Handler ---

_router_handler_instance = None


def get_router_handler() -> IRouterTool:
    """Provider for IRouterTool. Singleton with lazy initialization.

    Returns:
        RouterToolHandler instance.

    Clean Architecture: All dependencies injected via DI.
    Router, parameter resolver, and workflow loader are lazily initialized
    on first access through their respective get_* functions.
    """
    global _router_handler_instance
    if _router_handler_instance is None:
        config = get_config()
        _router_handler_instance = RouterToolHandler(
            router=get_router() if config.ROUTER_ENABLED else None,
            enabled=config.ROUTER_ENABLED,
            parameter_resolver=get_parameter_resolver() if config.ROUTER_ENABLED else None,
            workflow_loader=get_workflow_loader() if config.ROUTER_ENABLED else None,
        )
    return _router_handler_instance


# --- Workflow Catalog Handler (read-only workflow introspection) ---

_workflow_catalog_handler_instance = None


def get_workflow_catalog_handler() -> IWorkflowCatalogTool:
    """Provider for IWorkflowCatalogTool. Singleton with lazy initialization."""
    global _workflow_catalog_handler_instance
    if _workflow_catalog_handler_instance is None:
        _workflow_catalog_handler_instance = WorkflowCatalogToolHandler(
            workflow_loader=get_workflow_loader(),
            workflow_classifier=get_workflow_classifier(),
            vector_store=get_vector_store(),
        )
    return _workflow_catalog_handler_instance
