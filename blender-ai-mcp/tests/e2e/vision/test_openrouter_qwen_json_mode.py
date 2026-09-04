"""Opt-in live coverage for OpenRouter/Qwen structured-output behavior."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any

import pytest
from PIL import Image
from server.adapters.mcp.vision import (
    OpenAICompatibleVisionBackend,
    VisionImageInput,
    VisionRequest,
    build_vision_runtime_config,
)
from server.infrastructure.config import Config

pytestmark = pytest.mark.e2e


def _base_config(**overrides) -> Config:
    payload: dict[str, Any] = {
        "BLENDER_RPC_HOST": "127.0.0.1",
        "BLENDER_RPC_PORT": 8765,
        "ROUTER_ENABLED": True,
        "ROUTER_LOG_DECISIONS": True,
        "OTEL_ENABLED": False,
        "OTEL_EXPORTER": "none",
        "OTEL_SERVICE_NAME": "blender-ai-mcp",
        "MCP_SURFACE_PROFILE": "llm-guided",
        "MCP_DEFAULT_CONTRACT_LINE": None,
        "MCP_LIST_PAGE_SIZE": 100,
        "MCP_TOOL_TIMEOUT_SECONDS": 30.0,
        "MCP_TASK_TIMEOUT_SECONDS": 300.0,
        "RPC_TIMEOUT_SECONDS": 30.0,
        "ADDON_EXECUTION_TIMEOUT_SECONDS": 30.0,
        "VISION_ENABLED": True,
        "VISION_PROVIDER": "openai_compatible_external",
        "VISION_ALLOW_ON_GUIDED": True,
        "VISION_MAX_IMAGES": 2,
        "VISION_MAX_TOKENS": 500,
        "VISION_TIMEOUT_SECONDS": 120.0,
        "VISION_EXTERNAL_PROVIDER": "openrouter",
        "VISION_OPENROUTER_MODEL": os.getenv("VISION_OPENROUTER_MODEL", "qwen/qwen3-vl-32b-instruct"),
        "VISION_OPENROUTER_API_KEY_ENV": "OPENROUTER_API_KEY",
        "VISION_OPENROUTER_SITE_URL": "https://example.com",
        "VISION_OPENROUTER_SITE_NAME": "blender-ai-mcp-dev",
        "VISION_EXTERNAL_CONTRACT_PROFILE": "generic_full",
        "VISION_OPENROUTER_REQUIRE_PARAMETERS": True,
        "VISION_OPENROUTER_ENABLE_RESPONSE_HEALING": True,
        "VISION_OPENROUTER_PREFER_JSON_OBJECT_FOR_QWEN": True,
    }
    payload.update(overrides)
    return Config(**payload)


def _write_test_image(path: Path) -> None:
    image = Image.new("RGB", (96, 96), (255, 255, 255))
    for x in range(24, 72):
        for y in range(24, 72):
            image.putpixel((x, y), (0, 0, 0))
    image.save(path)


@pytest.mark.slow
def test_live_openrouter_qwen_json_mode_returns_parseable_contract(tmp_path: Path):
    """Opt-in live check that the current OpenRouter/Qwen path returns parseable JSON."""

    if os.getenv("RUN_REAL_OPENROUTER_QWEN_JSON_MODE") != "1":
        pytest.skip("set RUN_REAL_OPENROUTER_QWEN_JSON_MODE=1 to run live OpenRouter/Qwen coverage")
    if not os.getenv("OPENROUTER_API_KEY"):
        pytest.skip("OPENROUTER_API_KEY is required for live OpenRouter/Qwen coverage")

    image_path = tmp_path / "qwen_test.png"
    _write_test_image(image_path)

    runtime = build_vision_runtime_config(_base_config())
    backend = OpenAICompatibleVisionBackend(runtime)
    request = VisionRequest(
        goal="Return a bounded JSON visual comparison payload for this simple black square image.",
        target_object="Square",
        images=(VisionImageInput(path=str(image_path), role="reference", label="square_ref"),),
        prompt_hint="comparison_mode=checkpoint_vs_reference",
    )

    result = asyncio.run(backend.analyze(request))

    assert result["vision_contract_profile"] == "generic_full"
    assert result["goal_summary"]
    assert isinstance(result["visible_changes"], list)
    assert backend.last_output_diagnostics is not None
    assert backend.last_output_diagnostics["payload_shape"] != "no_json"
