"""Tests for the OpenAI-compatible vision backend."""

from __future__ import annotations

import asyncio
import json
from typing import Any

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
        "VISION_EXTERNAL_PROVIDER": "generic",
        "VISION_EXTERNAL_CONTRACT_PROFILE": None,
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
    payload.update(overrides)
    return Config(**payload)


class _FakeResponse:
    def __init__(self, payload: dict, status_code: int = 200, headers: dict[str, str] | None = None) -> None:
        self._payload = payload
        self.status_code = status_code
        self._headers = headers or {}

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "boom",
                request=httpx.Request("POST", "http://localhost"),
                response=httpx.Response(
                    self.status_code,
                    headers=self._headers,
                    json=self._payload,
                    request=httpx.Request("POST", "http://localhost"),
                ),
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
                            "likely_issues": [
                                {"category": "front_profile", "summary": "Top edge still looks too flat."}
                            ],
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
    assert result["vision_contract_profile"] == "google_family_compare"
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


def test_external_backend_supports_openrouter_headers_and_default_endpoint(monkeypatch, tmp_path):
    image_path = tmp_path / "after.png"
    image_path.write_bytes(b"fake-png")

    runtime = build_vision_runtime_config(
        _config(
            VISION_EXTERNAL_PROVIDER="openrouter",
            VISION_EXTERNAL_BASE_URL=None,
            VISION_EXTERNAL_MODEL=None,
            VISION_EXTERNAL_API_KEY=None,
            VISION_EXTERNAL_API_KEY_ENV=None,
            VISION_OPENROUTER_MODEL="google/gemma-3-27b-it:free",
            VISION_OPENROUTER_API_KEY="openrouter-secret",
            VISION_OPENROUTER_SITE_URL="https://example.com",
            VISION_OPENROUTER_SITE_NAME="blender-ai-mcp-dev",
            VISION_OPENROUTER_REQUIRE_PARAMETERS=True,
        )
    )
    backend = OpenAICompatibleVisionBackend(runtime)
    request = VisionRequest(goal="goal", images=(VisionImageInput(path=str(image_path), role="after"),))

    captured: dict = {}
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

    assert captured["url"] == "https://openrouter.ai/api/v1/chat/completions"
    assert captured["headers"]["Authorization"] == "Bearer openrouter-secret"
    assert captured["headers"]["HTTP-Referer"] == "https://example.com"
    assert captured["headers"]["X-Title"] == "blender-ai-mcp-dev"
    assert captured["json"]["provider"] == {"require_parameters": True}
    assert captured["json"]["plugins"] == [{"id": "response-healing"}]
    assert captured["json"]["response_format"]["type"] == "json_schema"
    assert captured["json"]["response_format"]["json_schema"]["name"] == "vision_assist"
    assert captured["json"]["response_format"]["json_schema"]["strict"] is True
    assert "visible_changes" in captured["json"]["response_format"]["json_schema"]["schema"]["properties"]


def test_external_backend_defaults_openrouter_require_parameters_to_false(monkeypatch, tmp_path):
    image_path = tmp_path / "after.png"
    image_path.write_bytes(b"fake-png")

    runtime = build_vision_runtime_config(
        _config(
            VISION_EXTERNAL_PROVIDER="openrouter",
            VISION_EXTERNAL_BASE_URL=None,
            VISION_EXTERNAL_MODEL=None,
            VISION_EXTERNAL_API_KEY=None,
            VISION_EXTERNAL_API_KEY_ENV=None,
            VISION_OPENROUTER_MODEL="google/gemma-3-27b-it:free",
            VISION_OPENROUTER_API_KEY="openrouter-secret",
        )
    )
    backend = OpenAICompatibleVisionBackend(runtime)
    request = VisionRequest(goal="goal", images=(VisionImageInput(path=str(image_path), role="after"),))

    captured: dict = {}
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

    assert captured["json"]["provider"] == {"require_parameters": False}


def test_openrouter_openai_family_uses_capability_aware_output_cap(monkeypatch, tmp_path):
    image_path = tmp_path / "after.png"
    image_path.write_bytes(b"fake-png")

    runtime = build_vision_runtime_config(
        _config(
            VISION_EXTERNAL_PROVIDER="openrouter",
            VISION_OPENROUTER_MODEL="openai/gpt-5.4-nano",
            VISION_OPENROUTER_API_KEY="openrouter-secret",
            VISION_MAX_TOKENS=600,
        )
    )
    backend = OpenAICompatibleVisionBackend(runtime)
    request = VisionRequest(
        goal="low poly squirrel",
        images=(VisionImageInput(path=str(image_path), role="after"),),
        prompt_hint="comparison_mode=stage_checkpoint_vs_reference",
    )

    captured: dict = {}
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda timeout=None: _FakeAsyncClient(
            response=_FakeResponse(
                {
                    "choices": [
                        {
                            "message": {
                                "content": '{"goal_summary":"ok","shape_mismatches":[],"proportion_mismatches":[],"correction_focus":[],"next_corrections":[]}'
                            }
                        }
                    ]
                }
            ),
            captured=captured,
        ),
    )

    result = asyncio.run(backend.analyze(request))

    assert result["vision_contract_profile"] == "google_family_compare"
    assert captured["json"]["max_tokens"] == 4096


def test_external_backend_uses_json_object_for_qwen_family_on_openrouter(monkeypatch, tmp_path):
    image_path = tmp_path / "after.png"
    image_path.write_bytes(b"fake-png")

    runtime = build_vision_runtime_config(
        _config(
            VISION_EXTERNAL_PROVIDER="openrouter",
            VISION_OPENROUTER_MODEL="qwen/qwen3-vl-32b-instruct",
            VISION_OPENROUTER_API_KEY="openrouter-secret",
        )
    )
    backend = OpenAICompatibleVisionBackend(runtime)
    request = VisionRequest(goal="goal", images=(VisionImageInput(path=str(image_path), role="after"),))

    captured: dict = {}
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

    assert captured["json"]["provider"] == {"require_parameters": False}
    assert captured["json"]["plugins"] == [{"id": "response-healing"}]
    assert captured["json"]["response_format"] == {"type": "json_object"}


def test_external_backend_supports_google_ai_studio_generate_content(monkeypatch, tmp_path):
    image_path = tmp_path / "reference.png"
    image_path.write_bytes(b"fake-png")

    runtime = build_vision_runtime_config(
        _config(
            VISION_EXTERNAL_PROVIDER="google_ai_studio",
            VISION_EXTERNAL_BASE_URL=None,
            VISION_EXTERNAL_MODEL=None,
            VISION_GEMINI_MODEL="gemini-2.5-flash",
            VISION_GEMINI_API_KEY="gemini-secret",
        )
    )
    backend = OpenAICompatibleVisionBackend(runtime)
    request = VisionRequest(goal="goal", images=(VisionImageInput(path=str(image_path), role="reference"),))

    captured: dict = {}
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda timeout=None: _FakeAsyncClient(
            response=_FakeResponse(
                {
                    "candidates": [
                        {
                            "content": {
                                "parts": [
                                    {
                                        "text": '{"goal_summary":"ok","visible_changes":[],"shape_mismatches":[],"proportion_mismatches":[],"correction_focus":[],"likely_issues":[],"next_corrections":[],"recommended_checks":[]}'
                                    }
                                ]
                            }
                        }
                    ]
                }
            ),
            captured=captured,
        ),
    )

    result = asyncio.run(backend.analyze(request))

    assert result["backend_kind"] == "openai_compatible_external"
    assert result["vision_contract_profile"] == "google_family_compare"
    assert captured["url"] == "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    assert captured["headers"]["x-goog-api-key"] == "gemini-secret"
    assert captured["json"]["generationConfig"]["responseMimeType"] == "application/json"
    assert "responseJsonSchema" in captured["json"]["generationConfig"]
    assert "contents" in captured["json"]


def test_openrouter_google_family_compare_flow_uses_narrow_schema_and_prompt(monkeypatch, tmp_path):
    image_path = tmp_path / "reference.png"
    image_path.write_bytes(b"fake-png")

    runtime = build_vision_runtime_config(
        _config(
            VISION_EXTERNAL_PROVIDER="openrouter",
            VISION_EXTERNAL_BASE_URL=None,
            VISION_EXTERNAL_MODEL=None,
            VISION_OPENROUTER_MODEL="google/gemma-3-27b-it:free",
            VISION_OPENROUTER_API_KEY="openrouter-secret",
        )
    )
    backend = OpenAICompatibleVisionBackend(runtime)
    request = VisionRequest(
        goal="low poly squirrel",
        target_object="Squirrel",
        images=(VisionImageInput(path=str(image_path), role="reference", label="ref_front"),),
        prompt_hint="comparison_mode=stage_checkpoint_vs_reference",
    )

    captured: dict = {}
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda timeout=None: _FakeAsyncClient(
            response=_FakeResponse(
                {
                    "choices": [
                        {
                            "message": {
                                "content": json.dumps(
                                    {
                                        "goal_summary": "Closer overall.",
                                        "reference_match_summary": "Head shape is closer.",
                                        "shape_mismatches": ["Head silhouette is still too spherical."],
                                        "proportion_mismatches": ["Tail still reads too small."],
                                        "correction_focus": ["Head silhouette"],
                                        "next_corrections": ["Flatten the head silhouette slightly."],
                                    }
                                )
                            }
                        }
                    ]
                }
            ),
            captured=captured,
        ),
    )

    result = asyncio.run(backend.analyze(request))

    schema = captured["json"]["response_format"]["json_schema"]["schema"]
    system_text = captured["json"]["messages"][0]["content"]
    payload_text = captured["json"]["messages"][1]["content"][0]["text"]

    assert result["goal_summary"] == "Closer overall."
    assert result["visible_changes"] == []
    assert result["vision_contract_profile"] == "google_family_compare"
    assert captured["url"] == "https://openrouter.ai/api/v1/chat/completions"
    assert set(schema["properties"]) == {
        "goal_summary",
        "reference_match_summary",
        "shape_mismatches",
        "proportion_mismatches",
        "correction_focus",
        "next_corrections",
    }
    assert (
        "Do not return visible_changes, likely_issues, recommended_checks, confidence, or captures_used." in system_text
    )
    assert "OUTPUT_TEMPLATE:" in payload_text
    assert '"shape_mismatches"' in payload_text


def test_google_ai_studio_compare_flow_uses_narrow_schema_and_prompt(monkeypatch, tmp_path):
    image_path = tmp_path / "reference.png"
    image_path.write_bytes(b"fake-png")

    runtime = build_vision_runtime_config(
        _config(
            VISION_EXTERNAL_PROVIDER="google_ai_studio",
            VISION_EXTERNAL_BASE_URL=None,
            VISION_EXTERNAL_MODEL=None,
            VISION_GEMINI_MODEL="gemini-2.5-flash",
            VISION_GEMINI_API_KEY="gemini-secret",
        )
    )
    backend = OpenAICompatibleVisionBackend(runtime)
    request = VisionRequest(
        goal="low poly squirrel",
        target_object="Squirrel",
        images=(VisionImageInput(path=str(image_path), role="reference", label="ref_front"),),
        prompt_hint="comparison_mode=stage_checkpoint_vs_reference",
    )

    captured: dict = {}
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda timeout=None: _FakeAsyncClient(
            response=_FakeResponse(
                {
                    "candidates": [
                        {
                            "content": {
                                "parts": [
                                    {
                                        "text": json.dumps(
                                            {
                                                "goal_summary": "Closer overall.",
                                                "reference_match_summary": "Head shape is closer.",
                                                "shape_mismatches": ["Head silhouette is still too spherical."],
                                                "proportion_mismatches": ["Tail still reads too small."],
                                                "correction_focus": ["Head silhouette"],
                                                "next_corrections": ["Flatten the head silhouette slightly."],
                                            }
                                        )
                                    }
                                ]
                            }
                        }
                    ]
                }
            ),
            captured=captured,
        ),
    )

    result = asyncio.run(backend.analyze(request))

    schema = captured["json"]["generationConfig"]["responseJsonSchema"]
    system_text = captured["json"]["systemInstruction"]["parts"][0]["text"]
    payload_text = captured["json"]["contents"][0]["parts"][0]["text"]

    assert result["goal_summary"] == "Closer overall."
    assert result["visible_changes"] == []
    assert result["vision_contract_profile"] == "google_family_compare"
    assert set(schema["properties"]) == {
        "goal_summary",
        "reference_match_summary",
        "shape_mismatches",
        "proportion_mismatches",
        "correction_focus",
        "next_corrections",
    }
    assert (
        "Do not return visible_changes, likely_issues, recommended_checks, confidence, or captures_used." in system_text
    )
    assert "OUTPUT_TEMPLATE:" in payload_text
    assert '"shape_mismatches"' in payload_text


def test_external_backend_invalid_json_error_includes_diagnostics(monkeypatch, tmp_path):
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

    with pytest.raises(VisionBackendUnavailableError, match="container_shape=prose"):
        asyncio.run(backend.analyze(request))


def test_external_backend_invalid_json_error_includes_contract_profile(monkeypatch, tmp_path):
    image_path = tmp_path / "reference.png"
    image_path.write_bytes(b"fake-png")

    runtime = build_vision_runtime_config(
        _config(
            VISION_EXTERNAL_PROVIDER="openrouter",
            VISION_EXTERNAL_BASE_URL=None,
            VISION_EXTERNAL_MODEL=None,
            VISION_OPENROUTER_MODEL="google/gemma-3-27b-it:free",
            VISION_OPENROUTER_API_KEY="openrouter-secret",
        )
    )
    backend = OpenAICompatibleVisionBackend(runtime)
    request = VisionRequest(
        goal="goal",
        images=(VisionImageInput(path=str(image_path), role="reference"),),
        prompt_hint="comparison_mode=stage_checkpoint_vs_reference",
    )

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda timeout=None: _FakeAsyncClient(
            response=_FakeResponse({"choices": [{"message": {"content": "not-json"}}]}),
            captured={},
        ),
    )

    with pytest.raises(VisionBackendUnavailableError, match="vision_contract_profile=google_family_compare"):
        asyncio.run(backend.analyze(request))


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


def test_openrouter_http_error_logs_payload_summary_and_response_preview(monkeypatch, tmp_path, caplog):
    image_path = tmp_path / "reference.png"
    image_path.write_bytes(b"fake-png")

    runtime = build_vision_runtime_config(
        _config(
            VISION_EXTERNAL_PROVIDER="openrouter",
            VISION_EXTERNAL_BASE_URL=None,
            VISION_EXTERNAL_MODEL=None,
            VISION_OPENROUTER_MODEL="google/gemma-4-31b-it",
            VISION_OPENROUTER_API_KEY="openrouter-secret",
        )
    )
    backend = OpenAICompatibleVisionBackend(runtime)
    request = VisionRequest(
        goal="low poly squirrel",
        target_object="Head",
        images=(VisionImageInput(path=str(image_path), role="reference", label="front_ref"),),
        prompt_hint="comparison_mode=stage_checkpoint_vs_reference",
    )

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda timeout=None: _FakeAsyncClient(
            response=_FakeResponse(
                {"error": {"message": "Provider rejected json_schema for this model."}},
                status_code=400,
                headers={"x-request-id": "req_123", "content-type": "application/json"},
            ),
            captured={},
        ),
    )

    with caplog.at_level("ERROR"):
        with pytest.raises(VisionBackendUnavailableError, match="Provider rejected json_schema"):
            asyncio.run(backend.analyze(request))

    log_text = "\n".join(caplog.messages)
    assert "External vision request failed with HTTP status." in log_text
    assert "google/gemma-4-31b-it" in log_text
    assert "google_family_compare" in log_text
    assert "https://openrouter.ai/api/v1/chat/completions" in log_text
    assert "json_schema" in log_text
    assert "Provider rejected json_schema for this model." in log_text
