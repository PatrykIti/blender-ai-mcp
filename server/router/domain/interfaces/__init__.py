"""
Router Domain Interfaces.

Abstract interfaces for all router components.
"""

from server.router.domain.interfaces.i_interceptor import IToolInterceptor
from server.router.domain.interfaces.i_scene_analyzer import ISceneAnalyzer
from server.router.domain.interfaces.i_pattern_detector import IPatternDetector
from server.router.domain.interfaces.i_correction_engine import ICorrectionEngine
from server.router.domain.interfaces.i_override_engine import IOverrideEngine
from server.router.domain.interfaces.i_expansion_engine import IExpansionEngine
from server.router.domain.interfaces.i_firewall import IFirewall
from server.router.domain.interfaces.i_intent_classifier import IIntentClassifier
from server.router.domain.interfaces.i_vector_store import (
    IVectorStore,
    VectorNamespace,
    VectorRecord,
    SearchResult,
)
from server.router.domain.interfaces.i_workflow_intent_classifier import (
    IWorkflowIntentClassifier,
)
from server.router.domain.interfaces.matcher import (
    IMatcher,
    IModifierExtractor,
)
from server.router.domain.interfaces.i_parameter_resolver import (
    IParameterStore,
    IParameterResolver,
)

__all__ = [
    "IToolInterceptor",
    "ISceneAnalyzer",
    "IPatternDetector",
    "ICorrectionEngine",
    "IOverrideEngine",
    "IExpansionEngine",
    "IFirewall",
    "IIntentClassifier",
    # Vector Store (TASK-047)
    "IVectorStore",
    "VectorNamespace",
    "VectorRecord",
    "SearchResult",
    # Workflow Intent Classifier (TASK-047)
    "IWorkflowIntentClassifier",
    # Ensemble Matcher (TASK-053)
    "IMatcher",
    "IModifierExtractor",
    # Parameter Resolution (TASK-055)
    "IParameterStore",
    "IParameterResolver",
]
