# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""OpenRouter model-catalog capability lookup helpers."""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from .config import VisionModelCapabilities

logger = logging.getLogger(__name__)

_OPENROUTER_METADATA_TIMEOUT_SECONDS = 5.0


def _unknown_capabilities(model_id: str | None, *, reason: str) -> VisionModelCapabilities:
    normalized_model_id = str(model_id or "").strip() or "unknown-openrouter-model"
    return VisionModelCapabilities(
        model_id=normalized_model_id,
        capability_source="unknown",
        metadata_summary={"lookup_status": reason},
    )


def _as_positive_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int) and value > 0:
        return value
    if isinstance(value, float) and value > 0 and value.is_integer():
        return int(value)
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.isdigit():
            parsed = int(stripped)
            return parsed if parsed > 0 else None
    return None


def _as_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    normalized: list[str] = []
    for item in value:
        text = str(item).strip() if isinstance(item, str) else ""
        if text and text not in normalized:
            normalized.append(text)
    return normalized


def _catalog_url(base_url: str | None) -> str:
    base = str(base_url or "https://openrouter.ai/api/v1").strip().rstrip("/")
    for suffix in ("/chat/completions", "/completions"):
        if base.endswith(suffix):
            base = base[: -len(suffix)].rstrip("/")
    return f"{base}/models"


def normalize_openrouter_model_capabilities(
    *,
    requested_model_id: str | None,
    model_payload: dict[str, Any],
) -> VisionModelCapabilities:
    """Normalize one OpenRouter catalog model object into runtime capabilities."""

    model_id = str(model_payload.get("id") or requested_model_id or "").strip()
    if not model_id:
        return _unknown_capabilities(requested_model_id, reason="missing_model_id")

    architecture = model_payload.get("architecture")
    if not isinstance(architecture, dict):
        architecture = {}
    top_provider = model_payload.get("top_provider")
    if not isinstance(top_provider, dict):
        top_provider = {}

    context_length = _as_positive_int(model_payload.get("context_length")) or _as_positive_int(
        top_provider.get("context_length")
    )
    max_completion_tokens = _as_positive_int(top_provider.get("max_completion_tokens"))
    canonical_slug = str(model_payload.get("canonical_slug") or "").strip() or None

    return VisionModelCapabilities(
        model_id=model_id,
        capability_source="openrouter_api",
        context_length=context_length,
        max_completion_tokens=max_completion_tokens,
        input_modalities=_as_string_list(architecture.get("input_modalities")),
        output_modalities=_as_string_list(architecture.get("output_modalities")),
        supported_parameters=_as_string_list(model_payload.get("supported_parameters")),
        metadata_summary={
            "canonical_slug": canonical_slug,
            "architecture_modality": str(architecture.get("modality") or "").strip() or None,
            "top_provider_context_length": _as_positive_int(top_provider.get("context_length")),
            "top_provider_is_moderated": top_provider.get("is_moderated")
            if isinstance(top_provider.get("is_moderated"), bool)
            else None,
            "has_default_parameters": isinstance(model_payload.get("default_parameters"), dict),
            "has_per_request_limits": isinstance(model_payload.get("per_request_limits"), dict),
        },
    )


def capabilities_from_openrouter_catalog(
    *,
    requested_model_id: str | None,
    catalog_payload: dict[str, Any],
) -> VisionModelCapabilities:
    """Find and normalize one requested model from an OpenRouter catalog payload."""

    requested = str(requested_model_id or "").strip().lower()
    if not requested:
        return _unknown_capabilities(requested_model_id, reason="missing_requested_model_id")

    models = catalog_payload.get("data")
    if not isinstance(models, list):
        return _unknown_capabilities(requested_model_id, reason="malformed_catalog")

    for item in models:
        if not isinstance(item, dict):
            continue
        model_id = str(item.get("id") or "").strip().lower()
        canonical_slug = str(item.get("canonical_slug") or "").strip().lower()
        if requested in {model_id, canonical_slug}:
            return normalize_openrouter_model_capabilities(
                requested_model_id=requested_model_id,
                model_payload=item,
            )

    return _unknown_capabilities(requested_model_id, reason="model_not_found")


async def resolve_openrouter_model_capabilities(
    *,
    base_url: str | None,
    model_id: str | None,
    api_key: str | None = None,
    api_key_env: str | None = None,
    timeout_seconds: float | None = None,
) -> VisionModelCapabilities:
    """Resolve OpenRouter model capabilities from the catalog endpoint.

    The lookup is intentionally lazy and bounded. Failures return an unknown
    capability object so callers can keep a reviewed fallback profile or a
    conservative request policy without crashing normal guided sessions.
    """

    headers: dict[str, str] = {}
    resolved_api_key = api_key or (os.getenv(api_key_env) if api_key_env else None)
    if resolved_api_key:
        headers["Authorization"] = f"Bearer {resolved_api_key}"

    timeout = httpx.Timeout(min(float(timeout_seconds or _OPENROUTER_METADATA_TIMEOUT_SECONDS), 10.0))
    url = _catalog_url(base_url)
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(
                url,
                params={"output_modalities": "all"},
                headers=headers,
            )
            response.raise_for_status()
            payload = response.json()
    except Exception as exc:
        logger.debug("OpenRouter model metadata lookup failed: model_id=%s error=%s", model_id, exc)
        return _unknown_capabilities(model_id, reason="lookup_failed")

    if not isinstance(payload, dict):
        return _unknown_capabilities(model_id, reason="malformed_catalog")
    return capabilities_from_openrouter_catalog(
        requested_model_id=model_id,
        catalog_payload=payload,
    )
