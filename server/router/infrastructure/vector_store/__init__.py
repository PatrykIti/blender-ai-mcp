"""
Vector Store Infrastructure.

LanceDB-based vector storage for semantic search.

TASK-047
"""

from server.router.infrastructure.vector_store.lance_store import LanceVectorStore
from server.router.infrastructure.vector_store.migrations import (
    PickleToLanceMigration,
    auto_migrate_if_needed,
)

__all__ = [
    "LanceVectorStore",
    "PickleToLanceMigration",
    "auto_migrate_if_needed",
]
