"""Tests for OpenRouter model-catalog capability normalization."""

from __future__ import annotations

import asyncio

import httpx
from server.adapters.mcp.vision.openrouter_models import (
    capabilities_from_openrouter_catalog,
    normalize_openrouter_model_capabilities,
    resolve_openrouter_model_capabilities,
)


def test_openrouter_model_payload_normalizes_capability_fields():
    capabilities = normalize_openrouter_model_capabilities(
        requested_model_id="openai/gpt-5.4-nano",
        model_payload={
            "id": "openai/gpt-5.4-nano",
            "canonical_slug": "openai/gpt-5.4-nano",
            "context_length": 400_000,
            "architecture": {
                "modality": "text+image->text",
                "input_modalities": ["text", "image"],
                "output_modalities": ["text"],
            },
            "top_provider": {
                "context_length": 400_000,
                "max_completion_tokens": 128_000,
                "is_moderated": True,
            },
            "supported_parameters": ["max_tokens", "response_format", "structured_outputs"],
            "default_parameters": {"temperature": 0.0},
            "per_request_limits": {"prompt_tokens": 400_000},
        },
    )

    assert capabilities.capability_source == "openrouter_api"
    assert capabilities.model_id == "openai/gpt-5.4-nano"
    assert capabilities.context_length == 400_000
    assert capabilities.max_completion_tokens == 128_000
    assert capabilities.input_modalities == ["text", "image"]
    assert capabilities.output_modalities == ["text"]
    assert capabilities.supported_parameters == ["max_tokens", "response_format", "structured_outputs"]
    assert capabilities.metadata_summary["canonical_slug"] == "openai/gpt-5.4-nano"
    assert capabilities.metadata_summary["top_provider_is_moderated"] is True
    assert capabilities.metadata_summary["has_default_parameters"] is True
    assert capabilities.metadata_summary["has_per_request_limits"] is True


def test_openrouter_catalog_missing_model_degrades_to_unknown_capabilities():
    capabilities = capabilities_from_openrouter_catalog(
        requested_model_id="missing/model",
        catalog_payload={"data": [{"id": "openai/gpt-5.4-nano"}]},
    )

    assert capabilities.capability_source == "unknown"
    assert capabilities.model_id == "missing/model"
    assert capabilities.metadata_summary == {"lookup_status": "model_not_found"}


def test_openrouter_catalog_malformed_payload_degrades_to_unknown_capabilities():
    capabilities = capabilities_from_openrouter_catalog(
        requested_model_id="openai/gpt-5.4-nano",
        catalog_payload={"data": "not-a-list"},
    )

    assert capabilities.capability_source == "unknown"
    assert capabilities.metadata_summary == {"lookup_status": "malformed_catalog"}


def test_openrouter_metadata_lookup_is_bounded_and_secretless_on_failure(monkeypatch):
    captured: dict = {}

    class _FailingAsyncClient:
        def __init__(self, *, timeout):
            captured["timeout"] = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, params=None, headers=None):
            captured["url"] = url
            captured["params"] = params
            captured["headers"] = headers
            raise httpx.TimeoutException("timeout")

    monkeypatch.setenv("OPENROUTER_API_KEY", "secret-value")
    monkeypatch.setattr(httpx, "AsyncClient", lambda timeout=None: _FailingAsyncClient(timeout=timeout))

    capabilities = asyncio.run(
        resolve_openrouter_model_capabilities(
            base_url="https://openrouter.ai/api/v1/chat/completions",
            model_id="openai/gpt-5.4-nano",
            api_key_env="OPENROUTER_API_KEY",
            timeout_seconds=20.0,
        )
    )

    assert capabilities.capability_source == "unknown"
    assert capabilities.metadata_summary == {"lookup_status": "lookup_failed"}
    assert captured["url"] == "https://openrouter.ai/api/v1/models"
    assert captured["params"] == {"output_modalities": "all"}
    assert captured["headers"] == {"Authorization": "Bearer secret-value"}
    assert captured["timeout"].connect == 10.0
