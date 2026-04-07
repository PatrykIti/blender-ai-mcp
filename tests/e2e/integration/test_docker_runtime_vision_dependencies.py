"""Opt-in smoke coverage for Docker runtime vision dependencies."""

from __future__ import annotations

import os
import subprocess

import pytest

pytestmark = pytest.mark.e2e


@pytest.mark.slow
def test_docker_runtime_has_pillow_and_silhouette_imports():
    """Opt-in smoke test for the built Docker image used by guided vision flows."""

    if os.getenv("RUN_DOCKER_RUNTIME_VISION_SMOKE") != "1":
        pytest.skip("set RUN_DOCKER_RUNTIME_VISION_SMOKE=1 to run Docker runtime smoke coverage")

    image = os.getenv("BLENDER_AI_MCP_DOCKER_IMAGE", "blender-ai-mcp:local")
    command = [
        "docker",
        "run",
        "--rm",
        image,
        "python",
        "-c",
        (
            "from PIL import Image; "
            "from server.adapters.mcp.vision.silhouette import build_silhouette_analysis; "
            "print(Image.__name__); "
            "print(build_silhouette_analysis is not None)"
        ),
    ]

    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "docker runtime smoke failed")

    assert "Image" in completed.stdout
    assert "True" in completed.stdout
