"""Temporary path utilities for viewport and other file outputs.

This module centralizes logic for resolving internal (container) and external
(host-visible) temp directories, so adapters can map files written inside a
Docker container to paths that make sense on the host.

Environment Variables:
    BLENDER_AI_TMP_INTERNAL_DIR: Optional. Base internal temp dir. If unset,
        defaults to tempfile.gettempdir().
    BLENDER_AI_TMP_EXTERNAL_DIR: Optional. Host-visible base dir corresponding
        to the internal temp dir. If unset, falls back to BLENDER_AI_TMP_INTERNAL_DIR.
"""

from pathlib import Path
from typing import Tuple
import os
import tempfile


def get_viewport_output_paths(filename: str, latest_name: str = "viewport_latest.jpg") -> Tuple[Path, Path, str, str]:
    """Return internal and external paths for viewport image files.

    The function always creates (if needed) an internal temp subdirectory
    `blender-ai-mcp` under the chosen temp base directory. External paths
    are **not** created; they are only returned as strings for display to
    the user/LLM.

    Args:
        filename: Name of the timestamped image file (e.g. "viewport_...jpg").
        latest_name: Name for the rolling "latest" image file.

    Returns:
        A tuple of:
            - internal_timestamped: Path to the timestamped image inside container.
            - internal_latest: Path to the "latest" image inside container.
            - external_timestamped: Host-visible path for the timestamped image.
            - external_latest: Host-visible path for the "latest" image.
    """
    internal_base_str = os.getenv("BLENDER_AI_TMP_INTERNAL_DIR") or tempfile.gettempdir()
    external_base_str = os.getenv("BLENDER_AI_TMP_EXTERNAL_DIR") or internal_base_str

    internal_base = Path(internal_base_str)
    external_base = Path(external_base_str)

    internal_dir = internal_base / "blender-ai-mcp"
    internal_dir.mkdir(parents=True, exist_ok=True)

    external_dir = external_base / "blender-ai-mcp"

    internal_timestamped = internal_dir / filename
    internal_latest = internal_dir / latest_name

    external_timestamped = str(external_dir / filename)
    external_latest = str(external_dir / latest_name)

    return internal_timestamped, internal_latest, external_timestamped, external_latest
