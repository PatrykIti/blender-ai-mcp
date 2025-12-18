"""
Intent Classifier Module.

Offline intent classification using LaBSE embeddings.
Supports both tool and workflow classification.

TASK-047: Migrated to LanceDB vector store.
Legacy EmbeddingCache kept for backward compatibility during transition.
"""

from server.router.application.classifier.intent_classifier import IntentClassifier
from server.router.application.classifier.workflow_intent_classifier import (
    WorkflowIntentClassifier,
)

# Legacy imports - kept for backward compatibility
try:
    from server.router.application.classifier.embedding_cache import EmbeddingCache
except ImportError:
    EmbeddingCache = None  # type: ignore

__all__ = [
    "IntentClassifier",
    "WorkflowIntentClassifier",
]

# Add EmbeddingCache to exports if available
if EmbeddingCache is not None:
    __all__.append("EmbeddingCache")
