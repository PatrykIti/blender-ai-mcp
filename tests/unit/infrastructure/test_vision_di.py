"""Tests for lazy vision runtime DI providers."""

from __future__ import annotations

from typing import Any

import server.infrastructure.di as di
from server.adapters.mcp.vision import LazyVisionBackendResolver
from server.infrastructure.config import Config


def _config(**overrides) -> Config:
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
        "VISION_PROVIDER": "transformers_local",
        "VISION_ALLOW_ON_GUIDED": True,
        "VISION_MAX_IMAGES": 6,
        "VISION_MAX_TOKENS": 400,
        "VISION_TIMEOUT_SECONDS": 20.0,
        "VISION_LOCAL_MODEL_ID": "Qwen/Qwen3-VL-4B-Instruct",
        "VISION_LOCAL_MODEL_PATH": None,
        "VISION_LOCAL_DEVICE": "cpu",
        "VISION_LOCAL_DTYPE": "auto",
        "VISION_MLX_MODEL_ID": None,
        "VISION_MLX_MODEL_PATH": None,
        "VISION_EXTERNAL_BASE_URL": None,
        "VISION_EXTERNAL_MODEL": None,
        "VISION_EXTERNAL_API_KEY": None,
        "VISION_EXTERNAL_API_KEY_ENV": None,
    }
    payload.update(overrides)
    return Config(**payload)


def test_di_provides_lazy_vision_runtime_without_loading_model(monkeypatch):
    monkeypatch.setattr(di, "get_config", lambda: _config())
    di._vision_runtime_config_instance = None
    di._vision_backend_resolver_instance = None

    runtime = di.get_vision_runtime_config()
    resolver = di.get_vision_backend_resolver()

    assert runtime.enabled is True
    assert runtime.active_model_name == "Qwen/Qwen3-VL-4B-Instruct"
    assert isinstance(resolver, LazyVisionBackendResolver)
    assert resolver.runtime_config is runtime
