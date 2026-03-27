"""Tests for the bounded vision runtime runner."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from server.adapters.mcp.vision import (
    LazyVisionBackendResolver,
    VisionBackend,
    VisionBackendUnavailableError,
    VisionImageInput,
    VisionRequest,
    build_vision_runtime_config,
    run_vision_assist,
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
        "VISION_MAX_IMAGES": 2,
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


@dataclass
class _Ctx:
    request_id: str = "req_vision"
    is_background_task: bool = False
    task_id: str | None = None


class _SuccessBackend(VisionBackend):
    def __init__(self, backend_kind: str, model_name: str) -> None:
        self._backend_kind = backend_kind
        self._model_name = model_name

    @property
    def backend_kind(self):
        return self._backend_kind

    @property
    def model_name(self) -> str:
        return self._model_name

    async def analyze(self, request: VisionRequest) -> dict[str, object]:
        return {
            "backend_kind": self.backend_kind,
            "model_name": self.model_name,
            "goal_summary": "Looks closer to the goal.",
            "reference_match_summary": None,
            "visible_changes": ["Front profile changed."],
            "likely_issues": [],
            "recommended_checks": [],
            "confidence": 0.55,
            "captures_used": [image.label or image.role for image in request.images],
        }


def _request(image_count: int = 1) -> VisionRequest:
    images = tuple(
        VisionImageInput(path=f"/tmp/image_{idx}.png", role="before", label=f"before_{idx}")
        for idx in range(image_count)
    )
    return VisionRequest(goal="Make the housing closer to the reference.", images=images)


def test_runner_rejects_background_task_context():
    runtime = build_vision_runtime_config(_config())
    resolver = LazyVisionBackendResolver(runtime)
    ctx = _Ctx(is_background_task=True, task_id="task_1")

    result = asyncio.run(run_vision_assist(ctx, request=_request(), resolver=resolver))

    assert result.status == "rejected_by_policy"
    assert result.rejection_reason == "background_request_forbidden"


def test_runner_rejects_image_budget_overflow():
    runtime = build_vision_runtime_config(_config(VISION_MAX_IMAGES=1))
    resolver = LazyVisionBackendResolver(runtime)

    result = asyncio.run(run_vision_assist(_Ctx(), request=_request(image_count=2), resolver=resolver))

    assert result.status == "rejected_by_policy"
    assert result.rejection_reason == "image_budget_exceeded"


def test_runner_returns_unavailable_when_backend_is_disabled():
    runtime = build_vision_runtime_config(_config(VISION_ENABLED=False))
    resolver = LazyVisionBackendResolver(runtime)

    result = asyncio.run(run_vision_assist(_Ctx(), request=_request(), resolver=resolver))

    assert result.status == "unavailable"
    assert result.capability_source == "unavailable"


def test_runner_returns_success_for_local_backend(monkeypatch):
    runtime = build_vision_runtime_config(_config())
    resolver = LazyVisionBackendResolver(runtime)
    monkeypatch.setattr(
        resolver,
        "resolve_default",
        lambda: _SuccessBackend("transformers_local", "Qwen/Qwen3-VL-4B-Instruct"),
    )

    result = asyncio.run(run_vision_assist(_Ctx(), request=_request(), resolver=resolver))

    assert result.status == "success"
    assert result.capability_source == "local_runtime"
    assert result.result is not None
    assert result.result.backend_kind == "transformers_local"


def test_runner_returns_success_for_external_backend(monkeypatch):
    runtime = build_vision_runtime_config(
        _config(
            VISION_PROVIDER="openai_compatible_external",
            VISION_EXTERNAL_BASE_URL="http://localhost:8000/v1",
            VISION_EXTERNAL_MODEL="gemma-3-27b-vision",
            VISION_LOCAL_MODEL_ID=None,
        )
    )
    resolver = LazyVisionBackendResolver(runtime)
    monkeypatch.setattr(
        resolver,
        "resolve_default",
        lambda: _SuccessBackend("openai_compatible_external", "gemma-3-27b-vision"),
    )

    result = asyncio.run(run_vision_assist(_Ctx(), request=_request(), resolver=resolver))

    assert result.status == "success"
    assert result.capability_source == "external_runtime"
    assert result.result is not None
    assert result.result.backend_kind == "openai_compatible_external"


def test_runner_returns_success_for_mlx_local_backend(monkeypatch):
    runtime = build_vision_runtime_config(
        _config(
            VISION_PROVIDER="mlx_local",
            VISION_LOCAL_MODEL_ID=None,
            VISION_MLX_MODEL_ID="mlx-community/Qwen3-VL-4B-Instruct-4bit",
        )
    )
    resolver = LazyVisionBackendResolver(runtime)
    monkeypatch.setattr(
        resolver,
        "resolve_default",
        lambda: _SuccessBackend("mlx_local", "mlx-community/Qwen3-VL-4B-Instruct-4bit"),
    )

    result = asyncio.run(run_vision_assist(_Ctx(), request=_request(), resolver=resolver))

    assert result.status == "success"
    assert result.capability_source == "local_runtime"
    assert result.result is not None
    assert result.result.model_name == "mlx-community/Qwen3-VL-4B-Instruct-4bit"


def test_runner_normalizes_backend_unavailable_errors(monkeypatch):
    runtime = build_vision_runtime_config(_config())
    resolver = LazyVisionBackendResolver(runtime)

    async def _raise(_request: VisionRequest) -> dict[str, object]:
        raise VisionBackendUnavailableError("runtime missing")

    backend = _SuccessBackend("transformers_local", "Qwen/Qwen3-VL-4B-Instruct")
    monkeypatch.setattr(backend, "analyze", _raise)
    monkeypatch.setattr(resolver, "resolve_default", lambda: backend)

    result = asyncio.run(run_vision_assist(_Ctx(), request=_request(), resolver=resolver))

    assert result.status == "unavailable"
    assert result.capability_source == "local_runtime"
