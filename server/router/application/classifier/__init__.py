"""
Intent Classifier Module.

Offline intent classification using LaBSE embeddings.
"""

from server.router.application.classifier.intent_classifier import IntentClassifier
from server.router.application.classifier.embedding_cache import EmbeddingCache

__all__ = [
    "IntentClassifier",
    "EmbeddingCache",
]
