"""
Embedding Cache Implementation.

Manages caching of tool embeddings for fast intent classification.
"""

import hashlib
import pickle
from pathlib import Path
from typing import Dict, Any, Optional
import logging

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


logger = logging.getLogger(__name__)


class EmbeddingCache:
    """Cache for tool embeddings.

    Stores pre-computed embeddings to avoid recomputation on startup.
    Validates cache against metadata hash to detect changes.
    """

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize embedding cache.

        Args:
            cache_dir: Directory for cache files. Uses temp dir if None.
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".cache" / "blender-ai-mcp" / "router"
        self._cache_dir = Path(cache_dir)
        self._cache_file = self._cache_dir / "tool_embeddings.pkl"
        self._hash_file = self._cache_dir / "metadata_hash.txt"
        self._ensure_cache_dir()

    def _ensure_cache_dir(self) -> None:
        """Ensure cache directory exists."""
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        embeddings: Dict[str, Any],
        metadata_hash: str,
    ) -> bool:
        """Save embeddings to cache.

        Args:
            embeddings: Dictionary of tool_name -> embedding vector.
            metadata_hash: Hash of source metadata for validation.

        Returns:
            True if saved successfully.
        """
        if not NUMPY_AVAILABLE:
            logger.warning("NumPy not available, cannot save embeddings")
            return False

        try:
            # Save embeddings
            with open(self._cache_file, "wb") as f:
                pickle.dump(embeddings, f)

            # Save hash
            with open(self._hash_file, "w") as f:
                f.write(metadata_hash)

            logger.info(f"Saved {len(embeddings)} tool embeddings to cache")
            return True

        except Exception as e:
            logger.error(f"Failed to save embeddings cache: {e}")
            return False

    def load(self) -> Optional[Dict[str, Any]]:
        """Load embeddings from cache.

        Returns:
            Dictionary of tool_name -> embedding vector, or None if not cached.
        """
        if not NUMPY_AVAILABLE:
            return None

        if not self._cache_file.exists():
            return None

        try:
            with open(self._cache_file, "rb") as f:
                embeddings = pickle.load(f)

            logger.info(f"Loaded {len(embeddings)} tool embeddings from cache")
            return embeddings

        except Exception as e:
            logger.error(f"Failed to load embeddings cache: {e}")
            return None

    def is_valid(self, metadata_hash: str) -> bool:
        """Check if cache is valid for given metadata.

        Args:
            metadata_hash: Hash of current metadata.

        Returns:
            True if cache exists and matches metadata hash.
        """
        if not self._cache_file.exists():
            return False

        if not self._hash_file.exists():
            return False

        try:
            with open(self._hash_file, "r") as f:
                cached_hash = f.read().strip()

            return cached_hash == metadata_hash

        except Exception:
            return False

    def clear(self) -> bool:
        """Clear the cache.

        Returns:
            True if cleared successfully.
        """
        try:
            if self._cache_file.exists():
                self._cache_file.unlink()
            if self._hash_file.exists():
                self._hash_file.unlink()
            logger.info("Cleared embeddings cache")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False

    def get_cache_path(self) -> Path:
        """Get the cache directory path.

        Returns:
            Path to cache directory.
        """
        return self._cache_dir

    def get_cache_size(self) -> int:
        """Get cache file size in bytes.

        Returns:
            Size in bytes, or 0 if no cache.
        """
        if self._cache_file.exists():
            return self._cache_file.stat().st_size
        return 0

    @staticmethod
    def compute_metadata_hash(metadata: Dict[str, Any]) -> str:
        """Compute hash of metadata for cache validation.

        Args:
            metadata: Tool metadata dictionary.

        Returns:
            SHA256 hash string.
        """
        # Sort keys for consistent hashing
        content = str(sorted(metadata.items()))
        return hashlib.sha256(content.encode()).hexdigest()[:16]
