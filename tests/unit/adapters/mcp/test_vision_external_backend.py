"""Tests for the OpenAI-compatible vision backend."""

from __future__ import annotations

import asyncio
import json

import httpx
import pytest

from server.adapters.mcp.vision import (
    OpenAICompatibleVisionBackend,
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
        "VISION_PROVIDER": "openai_compatible_external",
        "VISION_ALLOW_ON_GUIDED": True,
        "VISION_MAX_IMAGES": 6,
        "VISION_MAX_TOKENS": 400,
        "VISION_TIMEOUT_SECONDS": 20.0,
        "VISION_LOCAL_MODEL_ID": None,
        "VISION_LOCAL_MODEL_PATH": None,
        "VISION_LOCAL_DEVICE": "cpu",
        "VISION_LOCAL_DTYPE": "auto",
        "VISION_EXTERNAL_BASE_URL": "http://localhost:8000/v1",
        "VISION_EXTERNAL_MODEL": "gemma-3-27b-vision",
        "VISION_EXTERNAL_API_KEY": None,
        "VISION_EXTERNAL_API_KEY_ENV": None,
    }
    payload.update(overrides)
    return Config(**payload)


class _FakeResponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "boom",
                request=httpx.Request("POST", "http://localhost"),
                response=httpx.Response(self.status_code),
            )

    def json(self) -> dict:
        return self._payload


class _FakeAsyncClient:
    def __init__(self, *, response: _FakeResponse, captured: dict) -> None:
        self._response = response
        self._captured = captured

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, json=None, headers=None):
        self._captured["url"] = url
        self._captured["json"] = json
        self._captured["headers"] = headers
        return self._response


def test_external_backend_analyze_returns_structured_payload(monkeypatch, tmp_path):
    image_path = tmp_path / "before.png"
    image_path.write_bytes(b"fake-png")

    request = VisionRequest(
        goal="Make the housing closer to the reference.",
        target_object="Housing",
        images=(VisionImageInput(path=str(image_path), role="before", label="front_before"),),
        truth_summary={"dimensions": [0.2, 0.1, 0.05]},
    )
    runtime = build_vision_runtime_config(_config(VISION_EXTERNAL_API_KEY="secret"))
    backend = OpenAICompatibleVisionBackend(runtime)

    captured: dict = {}
    payload = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "goal_summary": "Closer to the intended rounded housing shape.",
                            "reference_match_summary": "Front silhouette is somewhat closer to reference.",
                            "visible_changes": ["The visible front edges appear softer."],
                            "likely_issues": [{"category": "front_profile", "summary": "Top edge still looks too flat."}],
                            "recommended_checks": [
                                {"tool_name": "scene_measure_dimensions", "reason": "Check overall size drift"}
                            ],
                            "confidence": 0.63,
                            "captures_used": ["front_before"],
                        }
                    )
                }
            }
        ]
    }
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda timeout=None: _FakeAsyncClient(response=_FakeResponse(payload), captured=captured),
    )

    result = asyncio.run(backend.analyze(request))

    assert result["backend_kind"] == "openai_compatible_external"
    assert result["model_name"] == "gemma-3-27b-vision"
    assert result["goal_summary"] == "Closer to the intended rounded housing shape."
    assert result["input_summary"]["before_image_count"] == 1
    assert captured["url"] == "http://localhost:8000/v1/chat/completions"
    assert captured["headers"]["Authorization"] == "Bearer secret"
    assert captured["json"]["response_format"] == {"type": "json_object"}


def test_external_backend_uses_api_key_env_when_inline_key_missing(monkeypatch, tmp_path):
    image_path = tmp_path / "after.png"
    image_path.write_bytes(b"fake-png")

    runtime = build_vision_runtime_config(
        _config(
            VISION_EXTERNAL_API_KEY=None,
            VISION_EXTERNAL_API_KEY_ENV="VISION_API_KEY",
        )
    )
    backend = OpenAICompatibleVisionBackend(runtime)
    request = VisionRequest(goal="goal", images=(VisionImageInput(path=str(image_path), role="after"),))

    captured: dict = {}
    monkeypatch.setenv("VISION_API_KEY", "env-secret")
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda timeout=None: _FakeAsyncClient(
            response=_FakeResponse(
                {"choices": [{"message": {"content": '{"goal_summary":"ok","visible_changes":[]}'}}]}
            ),
            captured=captured,
        ),
    )

    asyncio.run(backend.analyze(request))

    assert captured["headers"]["Authorization"] == "Bearer env-secret"


def test_external_backend_rejects_invalid_json_content(monkeypatch, tmp_path):
    image_path = tmp_path / "reference.png"
    image_path.write_bytes(b"fake-png")

    runtime = build_vision_runtime_config(_config())
    backend = OpenAICompatibleVisionBackend(runtime)
    request = VisionRequest(goal="goal", images=(VisionImageInput(path=str(image_path), role="reference"),))

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda timeout=None: _FakeAsyncClient(
            response=_FakeResponse({"choices": [{"message": {"content": "not-json"}}]}),
            captured={},
        ),
    )

    with pytest.raises(VisionBackendUnavailableError, match="valid JSON"):
        asyncio.run(backend.analyze(request))
