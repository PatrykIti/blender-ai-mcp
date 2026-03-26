# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Backend implementations for the pluggable vision runtime."""

from __future__ import annotations

import base64
import importlib
import json
import mimetypes
import os
from pathlib import Path
from typing import Any

import httpx

from .backend import VisionBackend, VisionBackendUnavailableError, VisionRequest
from .config import VisionRuntimeConfig

_VISION_SYSTEM_PROMPT = """You are a bounded vision assistant for Blender modeling.

You are not the truth source. Use images only to interpret visible change and
compare against the goal/reference. Do not claim geometric correctness from
images alone. Recommend deterministic follow-up checks when correctness matters.

Return only one JSON object with keys:
- goal_summary: string
- reference_match_summary: string or null
- visible_changes: string[]
- likely_issues: [{category: string, summary: string, severity: "high"|"medium"|"low"}]
- recommended_checks: [{tool_name: string, reason: string, priority: "high"|"normal"}]
- confidence: number or null
- captures_used: string[]
"""


def _media_type_for(path: str, fallback: str) -> str:
    guessed, _encoding = mimetypes.guess_type(path)
    return guessed or fallback


def _image_to_data_url(path: str, media_type: str) -> str:
    raw = Path(path).read_bytes()
    encoded = base64.b64encode(raw).decode("ascii")
    return f"data:{media_type};base64,{encoded}"


def _unwrap_json_text(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```") and stripped.endswith("```"):
        lines = stripped.splitlines()
        if len(lines) >= 3:
            return "\n".join(lines[1:-1]).strip()
    return stripped


def _extract_message_text(payload: dict[str, Any]) -> str:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise VisionBackendUnavailableError("Vision endpoint returned no choices.")

    message = choices[0].get("message")
    if not isinstance(message, dict):
        raise VisionBackendUnavailableError("Vision endpoint returned no message payload.")

    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        chunks: list[str] = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    chunks.append(text)
        if chunks:
            return "".join(chunks)
    raise VisionBackendUnavailableError("Vision endpoint returned an unsupported message content shape.")


def _build_input_summary(request: VisionRequest) -> dict[str, Any]:
    before = sum(1 for image in request.images if image.role == "before")
    after = sum(1 for image in request.images if image.role == "after")
    reference = sum(1 for image in request.images if image.role == "reference")
    return {
        "before_image_count": before,
        "after_image_count": after,
        "reference_image_count": reference,
        "target_object": request.target_object,
    }


def _normalize_assist_payload(
    *,
    backend_kind: str,
    model_name: str,
    request: VisionRequest,
    parsed: dict[str, Any],
) -> dict[str, Any]:
    return {
        "backend_kind": backend_kind,
        "model_name": model_name,
        "goal_summary": str(parsed.get("goal_summary") or ""),
        "reference_match_summary": parsed.get("reference_match_summary"),
        "visible_changes": list(parsed.get("visible_changes") or []),
        "likely_issues": list(parsed.get("likely_issues") or []),
        "recommended_checks": list(parsed.get("recommended_checks") or []),
        "confidence": parsed.get("confidence"),
        "captures_used": list(parsed.get("captures_used") or []),
        "input_summary": _build_input_summary(request),
    }


class TransformersLocalVisionBackend(VisionBackend):
    """Lazy local backend stub for Hugging Face/Transformers VLMs."""

    def __init__(self, runtime_config: VisionRuntimeConfig) -> None:
        if runtime_config.transformers_local is None:
            raise VisionBackendUnavailableError("transformers_local backend is not configured.")
        self._runtime_config = runtime_config
        self._local_config = runtime_config.transformers_local
        self._runtime_modules: tuple[Any, Any] | None = None

    @property
    def backend_kind(self):
        return "transformers_local"

    @property
    def model_name(self) -> str:
        return self._local_config.model_id or self._local_config.model_path or "unknown-local-model"

    def _ensure_runtime_modules(self) -> tuple[Any, Any]:
        if self._runtime_modules is not None:
            return self._runtime_modules

        try:
            transformers = importlib.import_module("transformers")
            torch = importlib.import_module("torch")
        except ModuleNotFoundError as exc:
            raise VisionBackendUnavailableError(
                "transformers_local backend requires optional runtime dependencies: transformers and torch"
            ) from exc

        self._runtime_modules = (transformers, torch)
        return self._runtime_modules

    async def analyze(self, request: VisionRequest) -> dict[str, object]:
        self._ensure_runtime_modules()
        raise VisionBackendUnavailableError(
            "transformers_local backend resolved its optional runtime dependencies, but inference is not implemented yet."
        )


class OpenAICompatibleVisionBackend(VisionBackend):
    """Lazy external backend stub for OpenAI-compatible vision endpoints."""

    def __init__(self, runtime_config: VisionRuntimeConfig) -> None:
        if runtime_config.openai_compatible_external is None:
            raise VisionBackendUnavailableError("openai_compatible_external backend is not configured.")
        self._runtime_config = runtime_config
        self._external_config = runtime_config.openai_compatible_external

    @property
    def backend_kind(self):
        return "openai_compatible_external"

    @property
    def model_name(self) -> str:
        return self._external_config.model or "unknown-external-model"

    def _endpoint_url(self) -> str:
        base_url = (self._external_config.base_url or "").rstrip("/")
        if base_url.endswith("/chat/completions"):
            return base_url
        return f"{base_url}/chat/completions"

    def _resolved_api_key(self) -> str | None:
        if self._external_config.api_key:
            return self._external_config.api_key
        if self._external_config.api_key_env:
            return os.getenv(self._external_config.api_key_env) or None
        return None

    def _build_request_payload(self, request: VisionRequest) -> dict[str, Any]:
        content: list[dict[str, Any]] = [
            {
                "type": "text",
                "text": json.dumps(
                    {
                        "goal": request.goal,
                        "target_object": request.target_object,
                        "prompt_hint": request.prompt_hint,
                        "truth_summary": request.truth_summary,
                        "metadata": request.metadata,
                        "images": [
                            {
                                "role": image.role,
                                "label": image.label,
                            }
                            for image in request.images
                        ],
                    },
                    ensure_ascii=True,
                    sort_keys=True,
                    indent=2,
                ),
            }
        ]

        for image in request.images:
            media_type = _media_type_for(image.path, image.media_type)
            content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": _image_to_data_url(image.path, media_type),
                    },
                }
            )

        return {
            "model": self.model_name,
            "temperature": 0.0,
            "max_tokens": self._runtime_config.max_tokens,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": _VISION_SYSTEM_PROMPT},
                {"role": "user", "content": content},
            ],
        }

    async def analyze(self, request: VisionRequest) -> dict[str, object]:
        headers = {"Content-Type": "application/json"}
        api_key = self._resolved_api_key()
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        timeout = httpx.Timeout(self._runtime_config.timeout_seconds)
        payload = self._build_request_payload(request)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    self._endpoint_url(),
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                parsed_response = response.json()
        except httpx.HTTPError as exc:
            raise VisionBackendUnavailableError(f"Vision endpoint request failed: {exc}") from exc
        except Exception as exc:  # pragma: no cover - defensive normalization
            raise VisionBackendUnavailableError(f"Vision endpoint execution failed: {exc}") from exc

        content = _extract_message_text(parsed_response)
        try:
            parsed_content = json.loads(_unwrap_json_text(content))
        except json.JSONDecodeError as exc:
            raise VisionBackendUnavailableError("Vision endpoint did not return valid JSON content.") from exc

        return _normalize_assist_payload(
            backend_kind=self.backend_kind,
            model_name=self.model_name,
            request=request,
            parsed=parsed_content,
        )


def create_vision_backend(runtime_config: VisionRuntimeConfig) -> VisionBackend:
    """Create one backend instance for the selected provider without loading a model at import time."""

    if runtime_config.provider == "transformers_local":
        return TransformersLocalVisionBackend(runtime_config)
    if runtime_config.provider == "openai_compatible_external":
        return OpenAICompatibleVisionBackend(runtime_config)
    raise VisionBackendUnavailableError(f"Unsupported vision backend provider '{runtime_config.provider}'.")
