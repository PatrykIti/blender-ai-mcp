"""Tests for the lazy local transformers vision backend scaffold."""

from __future__ import annotations

import asyncio
import importlib

import pytest

from server.adapters.mcp.vision import (
    TransformersLocalVisionBackend,
    VisionBackendUnavailableError,
    VisionImageInput,
    VisionRequest,
    build_vision_runtime_config,
)
from server.infrastructure.config import Config


def _config(**overrides) -> Config:
    payload = {
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
        "VISION_PROVIDER": "transformers_local",
        "VISION_ALLOW_ON_GUIDED": True,
        "VISION_MAX_IMAGES": 6,
        "VISION_MAX_TOKENS": 400,
        "VISION_TIMEOUT_SECONDS": 20.0,
        "VISION_LOCAL_MODEL_ID": "Qwen/Qwen3-VL-4B-Instruct",
        "VISION_LOCAL_MODEL_PATH": None,
        "VISION_LOCAL_DEVICE": "cpu",
        "VISION_LOCAL_DTYPE": "auto",
        "VISION_EXTERNAL_BASE_URL": None,
        "VISION_EXTERNAL_MODEL": None,
        "VISION_EXTERNAL_API_KEY": None,
        "VISION_EXTERNAL_API_KEY_ENV": None,
    }
    payload.update(overrides)
    return Config(**payload)


def test_local_backend_init_does_not_import_heavy_runtime(monkeypatch):
    calls: list[str] = []

    def _fake_import(name: str):
        calls.append(name)
        raise AssertionError("init should not import runtime modules")

    monkeypatch.setattr(importlib, "import_module", _fake_import)

    runtime = build_vision_runtime_config(_config())
    backend = TransformersLocalVisionBackend(runtime)

    assert backend.model_name == "Qwen/Qwen3-VL-4B-Instruct"
    assert calls == []


def test_local_backend_analyze_imports_runtime_lazily_and_fails_cleanly(monkeypatch, tmp_path):
    image_path = tmp_path / "before.png"
    image_path.write_bytes(b"fake-png")
    request = VisionRequest(goal="goal", images=(VisionImageInput(path=str(image_path), role="before"),))

    calls: list[str] = []

    def _fake_import(name: str):
        calls.append(name)
        if name == "transformers":
            return object()
        if name == "torch":
            return object()
        raise ModuleNotFoundError(name)

    monkeypatch.setattr(importlib, "import_module", _fake_import)

    backend = TransformersLocalVisionBackend(build_vision_runtime_config(_config()))

    with pytest.raises(VisionBackendUnavailableError, match="inference is not implemented yet"):
        asyncio.run(backend.analyze(request))

    assert calls == ["transformers", "torch"]


def test_local_backend_reports_missing_optional_dependencies(monkeypatch, tmp_path):
    image_path = tmp_path / "after.png"
    image_path.write_bytes(b"fake-png")
    request = VisionRequest(goal="goal", images=(VisionImageInput(path=str(image_path), role="after"),))

    def _missing_import(name: str):
        raise ModuleNotFoundError(name)

    monkeypatch.setattr(importlib, "import_module", _missing_import)

    backend = TransformersLocalVisionBackend(build_vision_runtime_config(_config()))

    with pytest.raises(VisionBackendUnavailableError, match="optional runtime dependencies"):
        asyncio.run(backend.analyze(request))
