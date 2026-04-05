"""Targeted end-to-end coverage for external vision contract-profile compare routing."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass

import httpx
import pytest
from server.adapters.mcp.vision import (
    LazyVisionBackendResolver,
    VisionImageInput,
    VisionRequest,
    build_vision_runtime_config,
)
from server.adapters.mcp.vision.runner import run_vision_assist
from server.infrastructure.config import Config

pytestmark = pytest.mark.e2e


@dataclass
class FakeContext:
    request_id: str | None = "req_contract_profile"
    is_background_task: bool = False


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


def test_openrouter_google_family_compare_profile_reaches_final_contract(monkeypatch, tmp_path):
    after_path = tmp_path / "after.png"
    reference_path = tmp_path / "reference.png"
    after_path.write_bytes(b"fake-png")
    reference_path.write_bytes(b"fake-png")

    runtime = build_vision_runtime_config(
        Config(
            VISION_ENABLED=True,
            VISION_PROVIDER="openai_compatible_external",
            VISION_EXTERNAL_PROVIDER="openrouter",
            VISION_OPENROUTER_MODEL="google/gemma-3-27b-it:free",
            VISION_OPENROUTER_API_KEY="openrouter-secret",
        )
    )
    resolver = LazyVisionBackendResolver(runtime)
    request = VisionRequest(
        goal="low poly squirrel",
        target_object="Squirrel",
        images=(
            VisionImageInput(path=str(after_path), role="after", label="stage_after"),
            VisionImageInput(path=str(reference_path), role="reference", label="ref_front"),
        ),
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

    outcome = asyncio.run(run_vision_assist(FakeContext(), request=request, resolver=resolver))

    assert outcome.status == "success"
    assert outcome.result is not None
    assert runtime.active_vision_contract_profile == "google_family_compare"
    assert outcome.result.vision_contract_profile == "google_family_compare"
    assert outcome.result.visible_changes == []
    assert outcome.result.shape_mismatches == ["Head silhouette is still too spherical."]
    assert captured["url"] == "https://openrouter.ai/api/v1/chat/completions"
    schema = captured["json"]["response_format"]["json_schema"]["schema"]
    assert "visible_changes" not in schema["properties"]
