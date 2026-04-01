"""Tests for TASK-121 pluggable vision runtime scaffolding."""

from __future__ import annotations

from typing import Any

import pytest
from server.adapters.mcp.vision import (
    LazyVisionBackendResolver,
    MLXLocalVisionBackend,
    OpenAICompatibleVisionBackend,
    TransformersLocalVisionBackend,
    VisionBackend,
    VisionBackendUnavailableError,
    VisionImageInput,
    VisionRequest,
    build_vision_runtime_config,
)
from server.infrastructure.config import Config


def _base_config(**overrides) -> Config:
    data: dict[str, Any] = {
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
        "VISION_ENABLED": False,
        "VISION_PROVIDER": "transformers_local",
        "VISION_ALLOW_ON_GUIDED": True,
        "VISION_MAX_IMAGES": 6,
        "VISION_MAX_TOKENS": 400,
        "VISION_TIMEOUT_SECONDS": 20.0,
        "VISION_LOCAL_MODEL_ID": None,
        "VISION_LOCAL_MODEL_PATH": None,
        "VISION_LOCAL_DEVICE": "cpu",
        "VISION_LOCAL_DTYPE": "auto",
        "VISION_MLX_MODEL_ID": None,
        "VISION_MLX_MODEL_PATH": None,
        "VISION_EXTERNAL_BASE_URL": None,
        "VISION_EXTERNAL_MODEL": None,
        "VISION_EXTERNAL_API_KEY": None,
        "VISION_EXTERNAL_API_KEY_ENV": None,
        "VISION_EXTERNAL_PROVIDER": "generic",
        "VISION_OPENROUTER_BASE_URL": None,
        "VISION_OPENROUTER_MODEL": None,
        "VISION_OPENROUTER_API_KEY": None,
        "VISION_OPENROUTER_API_KEY_ENV": None,
        "VISION_OPENROUTER_SITE_URL": None,
        "VISION_OPENROUTER_SITE_NAME": None,
        "VISION_GEMINI_BASE_URL": None,
        "VISION_GEMINI_MODEL": None,
        "VISION_GEMINI_API_KEY": None,
        "VISION_GEMINI_API_KEY_ENV": None,
    }
    data.update(overrides)
    return Config(**data)


def test_build_vision_runtime_config_supports_local_transformers_backend():
    config = _base_config(
        VISION_ENABLED=True,
        VISION_PROVIDER="transformers_local",
        VISION_LOCAL_MODEL_ID="Qwen/Qwen3-VL-4B-Instruct",
        VISION_LOCAL_DEVICE="cuda",
        VISION_LOCAL_DTYPE="bfloat16",
    )

    runtime = build_vision_runtime_config(config)

    assert runtime.enabled is True
    assert runtime.provider == "transformers_local"
    assert runtime.active_model_name == "Qwen/Qwen3-VL-4B-Instruct"
    assert runtime.transformers_local is not None
    assert runtime.transformers_local.device == "cuda"


def test_build_vision_runtime_config_supports_external_openai_compatible_backend():
    config = _base_config(
        VISION_ENABLED=True,
        VISION_PROVIDER="openai_compatible_external",
        VISION_EXTERNAL_BASE_URL="http://localhost:8000/v1",
        VISION_EXTERNAL_MODEL="gemma-3-27b-vision",
        VISION_EXTERNAL_API_KEY_ENV="VISION_API_KEY",
    )

    runtime = build_vision_runtime_config(config)

    assert runtime.enabled is True
    assert runtime.provider == "openai_compatible_external"
    assert runtime.active_model_name == "gemma-3-27b-vision"
    assert runtime.openai_compatible_external is not None
    assert runtime.openai_compatible_external.base_url == "http://localhost:8000/v1"


def test_build_vision_runtime_config_supports_openrouter_aliases():
    config = _base_config(
        VISION_ENABLED=True,
        VISION_PROVIDER="openai_compatible_external",
        VISION_EXTERNAL_PROVIDER="openrouter",
        VISION_OPENROUTER_MODEL="google/gemma-3-27b-it:free",
        VISION_OPENROUTER_API_KEY_ENV="OPENROUTER_API_KEY",
        VISION_OPENROUTER_SITE_URL="https://example.com",
        VISION_OPENROUTER_SITE_NAME="blender-ai-mcp-dev",
        VISION_EXTERNAL_BASE_URL=None,
        VISION_EXTERNAL_MODEL=None,
    )

    runtime = build_vision_runtime_config(config)

    assert runtime.enabled is True
    assert runtime.provider == "openai_compatible_external"
    assert runtime.active_model_name == "google/gemma-3-27b-it:free"
    assert runtime.openai_compatible_external is not None
    assert runtime.openai_compatible_external.provider_name == "openrouter"
    assert runtime.openai_compatible_external.base_url == "https://openrouter.ai/api/v1"
    assert runtime.openai_compatible_external.api_key_env == "OPENROUTER_API_KEY"
    assert runtime.openai_compatible_external.site_url == "https://example.com"
    assert runtime.openai_compatible_external.site_name == "blender-ai-mcp-dev"


def test_build_vision_runtime_config_supports_google_ai_studio_aliases():
    config = _base_config(
        VISION_ENABLED=True,
        VISION_PROVIDER="openai_compatible_external",
        VISION_EXTERNAL_PROVIDER="google_ai_studio",
        VISION_GEMINI_MODEL="gemini-2.5-flash",
        VISION_GEMINI_API_KEY_ENV="GEMINI_API_KEY",
        VISION_EXTERNAL_BASE_URL=None,
        VISION_EXTERNAL_MODEL=None,
    )

    runtime = build_vision_runtime_config(config)

    assert runtime.enabled is True
    assert runtime.provider == "openai_compatible_external"
    assert runtime.active_model_name == "gemini-2.5-flash"
    assert runtime.openai_compatible_external is not None
    assert runtime.openai_compatible_external.provider_name == "google_ai_studio"
    assert runtime.openai_compatible_external.base_url == "https://generativelanguage.googleapis.com/v1beta"
    assert runtime.openai_compatible_external.api_key_env == "GEMINI_API_KEY"


def test_explicit_google_provider_wins_even_if_openrouter_model_env_is_present():
    config = _base_config(
        VISION_ENABLED=True,
        VISION_PROVIDER="openai_compatible_external",
        VISION_EXTERNAL_PROVIDER="google_ai_studio",
        VISION_GEMINI_MODEL="gemini-2.5-flash",
        VISION_OPENROUTER_MODEL="google/gemma-3-27b-it:free",
    )

    runtime = build_vision_runtime_config(config)

    assert runtime.openai_compatible_external is not None
    assert runtime.openai_compatible_external.provider_name == "google_ai_studio"
    assert runtime.active_model_name == "gemini-2.5-flash"


def test_disabled_runtime_does_not_build_external_profile_from_provider_name_alone():
    config = _base_config(
        VISION_ENABLED=False,
        VISION_PROVIDER="openai_compatible_external",
        VISION_EXTERNAL_PROVIDER="openrouter",
        VISION_OPENROUTER_MODEL=None,
        VISION_EXTERNAL_BASE_URL=None,
        VISION_EXTERNAL_MODEL=None,
    )

    runtime = build_vision_runtime_config(config)

    assert runtime.enabled is False
    assert runtime.openai_compatible_external is None


def test_generic_external_provider_rejects_conflicting_openrouter_and_gemini_models():
    config = _base_config(
        VISION_ENABLED=True,
        VISION_PROVIDER="openai_compatible_external",
        VISION_EXTERNAL_PROVIDER="generic",
        VISION_OPENROUTER_MODEL="google/gemma-3-27b-it:free",
        VISION_GEMINI_MODEL="gemini-2.5-flash",
    )

    with pytest.raises(ValueError, match="both set while VISION_EXTERNAL_PROVIDER=generic"):
        build_vision_runtime_config(config)


def test_build_vision_runtime_config_supports_mlx_local_backend():
    config = _base_config(
        VISION_ENABLED=True,
        VISION_PROVIDER="mlx_local",
        VISION_MLX_MODEL_ID="mlx-community/Qwen3-VL-4B-Instruct-4bit",
    )

    runtime = build_vision_runtime_config(config)

    assert runtime.enabled is True
    assert runtime.provider == "mlx_local"
    assert runtime.active_model_name == "mlx-community/Qwen3-VL-4B-Instruct-4bit"
    assert runtime.mlx_local is not None


def test_enabled_local_runtime_requires_model_source():
    config = _base_config(
        VISION_ENABLED=True,
        VISION_PROVIDER="transformers_local",
    )

    with pytest.raises(ValueError, match="requires transformers_local config"):
        build_vision_runtime_config(config)


def test_enabled_external_runtime_requires_endpoint_target():
    config = _base_config(
        VISION_ENABLED=True,
        VISION_PROVIDER="openai_compatible_external",
    )

    with pytest.raises(ValueError, match="requires openai_compatible_external config"):
        build_vision_runtime_config(config)


def test_config_rejects_unknown_external_provider():
    with pytest.raises(ValueError, match="VISION_EXTERNAL_PROVIDER must be one of"):
        _base_config(VISION_EXTERNAL_PROVIDER="mystery")


def test_enabled_mlx_runtime_requires_model_source():
    config = _base_config(
        VISION_ENABLED=True,
        VISION_PROVIDER="mlx_local",
    )

    with pytest.raises(ValueError, match="requires mlx_local config"):
        build_vision_runtime_config(config)


def test_vision_request_carries_before_after_and_reference_images():
    request = VisionRequest(
        goal="make the housing closer to the reference",
        target_object="Housing",
        images=(
            VisionImageInput(path="/tmp/before_front.png", role="before", label="front_before"),
            VisionImageInput(path="/tmp/after_front.png", role="after", label="front_after"),
            VisionImageInput(path="/tmp/reference.png", role="reference", label="reference_main"),
        ),
        truth_summary={"dimensions": [0.2, 0.1, 0.05]},
    )

    assert request.images[0].role == "before"
    assert request.images[1].role == "after"
    assert request.images[2].role == "reference"
    assert request.truth_summary == {"dimensions": [0.2, 0.1, 0.05]}


def test_lazy_resolver_does_not_require_backend_when_disabled():
    runtime = build_vision_runtime_config(_base_config())
    resolver = LazyVisionBackendResolver(runtime)

    with pytest.raises(VisionBackendUnavailableError, match="disabled"):
        resolver.resolve(lambda cfg: None)


def test_lazy_resolver_normalizes_backend_factory_failures():
    runtime = build_vision_runtime_config(
        _base_config(
            VISION_ENABLED=True,
            VISION_PROVIDER="transformers_local",
            VISION_LOCAL_MODEL_ID="Qwen/Qwen3-VL-4B-Instruct",
        )
    )
    resolver = LazyVisionBackendResolver(runtime)

    with pytest.raises(VisionBackendUnavailableError, match="boom"):
        resolver.resolve(lambda cfg: (_ for _ in ()).throw(RuntimeError("boom")))


def test_lazy_resolver_returns_backend_instance_only_on_explicit_resolve():
    class DummyBackend(VisionBackend):
        @property
        def backend_kind(self):
            return "transformers_local"

        @property
        def model_name(self) -> str:
            return "Qwen/Qwen3-VL-4B-Instruct"

        async def analyze(self, request: VisionRequest) -> dict[str, object]:
            return {"status": "success"}

    runtime = build_vision_runtime_config(
        _base_config(
            VISION_ENABLED=True,
            VISION_PROVIDER="transformers_local",
            VISION_LOCAL_MODEL_ID="Qwen/Qwen3-VL-4B-Instruct",
        )
    )
    resolver = LazyVisionBackendResolver(runtime)

    backend = resolver.resolve(lambda cfg: DummyBackend())

    assert backend.backend_kind == "transformers_local"
    assert backend.model_name == "Qwen/Qwen3-VL-4B-Instruct"


def test_default_resolver_returns_transformers_stub_backend():
    runtime = build_vision_runtime_config(
        _base_config(
            VISION_ENABLED=True,
            VISION_PROVIDER="transformers_local",
            VISION_LOCAL_MODEL_ID="Qwen/Qwen3-VL-4B-Instruct",
        )
    )

    backend = LazyVisionBackendResolver(runtime).resolve_default()

    assert isinstance(backend, TransformersLocalVisionBackend)
    assert backend.model_name == "Qwen/Qwen3-VL-4B-Instruct"


def test_default_resolver_returns_external_stub_backend():
    runtime = build_vision_runtime_config(
        _base_config(
            VISION_ENABLED=True,
            VISION_PROVIDER="openai_compatible_external",
            VISION_EXTERNAL_BASE_URL="http://localhost:8000/v1",
            VISION_EXTERNAL_MODEL="gemma-3-27b-vision",
        )
    )

    backend = LazyVisionBackendResolver(runtime).resolve_default()

    assert isinstance(backend, OpenAICompatibleVisionBackend)
    assert backend.model_name == "gemma-3-27b-vision"


def test_default_resolver_returns_mlx_stub_backend():
    runtime = build_vision_runtime_config(
        _base_config(
            VISION_ENABLED=True,
            VISION_PROVIDER="mlx_local",
            VISION_MLX_MODEL_ID="mlx-community/Qwen3-VL-4B-Instruct-4bit",
            VISION_LOCAL_MODEL_ID=None,
        )
    )

    backend = LazyVisionBackendResolver(runtime).resolve_default()

    assert isinstance(backend, MLXLocalVisionBackend)
    assert backend.model_name == "mlx-community/Qwen3-VL-4B-Instruct-4bit"
