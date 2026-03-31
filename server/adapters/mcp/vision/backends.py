# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

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
from .parsing import diagnose_vision_output_text, parse_vision_output_text
from .prompting import (
    build_local_vision_payload_text,
    build_vision_payload_text,
    build_vision_response_json_schema,
    build_vision_system_prompt,
)


def _media_type_for(path: str, fallback: str) -> str:
    guessed, _encoding = mimetypes.guess_type(path)
    return guessed or fallback


def _image_to_data_url(path: str, media_type: str) -> str:
    raw = Path(path).read_bytes()
    encoded = base64.b64encode(raw).decode("ascii")
    return f"data:{media_type};base64,{encoded}"

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


def _extract_gemini_text(payload: dict[str, Any]) -> str:
    candidates = payload.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise VisionBackendUnavailableError("Gemini endpoint returned no candidates.")

    content = candidates[0].get("content")
    if not isinstance(content, dict):
        raise VisionBackendUnavailableError("Gemini endpoint returned no content payload.")

    parts = content.get("parts")
    if not isinstance(parts, list) or not parts:
        raise VisionBackendUnavailableError("Gemini endpoint returned no content parts.")

    chunks: list[str] = []
    for item in parts:
        if isinstance(item, dict):
            text = item.get("text")
            if isinstance(text, str):
                chunks.append(text)
    if chunks:
        return "".join(chunks)
    raise VisionBackendUnavailableError("Gemini endpoint returned no text parts.")


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
        "backend_name": backend_kind,
        "model_name": model_name,
        "goal_summary": str(parsed.get("goal_summary") or ""),
        "reference_match_summary": parsed.get("reference_match_summary"),
        "visible_changes": list(parsed.get("visible_changes") or []),
        "shape_mismatches": list(parsed.get("shape_mismatches") or []),
        "proportion_mismatches": list(parsed.get("proportion_mismatches") or []),
        "correction_focus": list(parsed.get("correction_focus") or []),
        "likely_issues": list(parsed.get("likely_issues") or []),
        "next_corrections": list(parsed.get("next_corrections") or []),
        "recommended_checks": list(parsed.get("recommended_checks") or []),
        "confidence": parsed.get("confidence"),
        "captures_used": list(parsed.get("captures_used") or []),
        "input_summary": _build_input_summary(request),
        "boundary_policy": {
            "interpretation_only": True,
            "not_truth_source": True,
            "not_policy_source": True,
            "requires_deterministic_checks_for_correctness": True,
            "requires_bundle_or_reference_context": True,
            "confidence_is_non_authoritative": True,
        },
    }


def _diagnostics_suffix(diagnostics: dict[str, Any] | None) -> str:
    if not diagnostics:
        return ""
    container_shape = diagnostics.get("container_shape")
    payload_shape = diagnostics.get("payload_shape")
    preview = str(diagnostics.get("raw_preview") or "").strip().replace("\n", " ")
    preview = preview[:160]
    parts = [
        f"container_shape={container_shape}" if container_shape else None,
        f"payload_shape={payload_shape}" if payload_shape else None,
        f"preview={preview}" if preview else None,
    ]
    suffix = ", ".join(part for part in parts if part)
    return f" ({suffix})" if suffix else ""


class TransformersLocalVisionBackend(VisionBackend):
    """Lazy local backend stub for Hugging Face/Transformers VLMs."""

    def __init__(self, runtime_config: VisionRuntimeConfig) -> None:
        if runtime_config.transformers_local is None:
            raise VisionBackendUnavailableError("transformers_local backend is not configured.")
        self._runtime_config = runtime_config
        self._local_config = runtime_config.transformers_local
        self._runtime_modules: tuple[Any, Any] | None = None
        self._processor: Any | None = None
        self._model: Any | None = None
        self._last_output_diagnostics: dict[str, Any] | None = None

    @property
    def backend_kind(self):
        return "transformers_local"

    @property
    def model_name(self) -> str:
        return self._local_config.model_id or self._local_config.model_path or "unknown-local-model"

    @property
    def last_output_diagnostics(self) -> dict[str, Any] | None:
        return self._last_output_diagnostics

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

    def _resolve_model_source(self) -> str:
        return self._local_config.model_id or self._local_config.model_path or self.model_name

    def _resolve_torch_dtype(self, torch_module: Any):
        dtype_name = str(self._local_config.dtype or "auto").lower()
        if dtype_name == "auto":
            return None
        mapping = {
            "float32": getattr(torch_module, "float32", None),
            "float16": getattr(torch_module, "float16", None),
            "bfloat16": getattr(torch_module, "bfloat16", None),
        }
        resolved = mapping.get(dtype_name)
        if resolved is None:
            raise VisionBackendUnavailableError(f"Unsupported local vision dtype '{self._local_config.dtype}'")
        return resolved

    def _ensure_local_components(self) -> tuple[Any, Any, Any]:
        transformers, torch_module = self._ensure_runtime_modules()
        if self._processor is not None and self._model is not None:
            return transformers, torch_module, self._processor

        processor_cls = getattr(transformers, "AutoProcessor", None)
        model_cls = getattr(transformers, "AutoModelForImageTextToText", None)
        if processor_cls is None or model_cls is None:
            raise VisionBackendUnavailableError(
                "transformers_local backend requires AutoProcessor and AutoModelForImageTextToText support"
            )

        model_source = self._resolve_model_source()
        load_kwargs: dict[str, Any] = {}
        torch_dtype = self._resolve_torch_dtype(torch_module)
        if torch_dtype is not None:
            load_kwargs["torch_dtype"] = torch_dtype

        try:
            self._processor = processor_cls.from_pretrained(model_source)
            self._model = model_cls.from_pretrained(model_source, **load_kwargs)
            if self._local_config.device != "auto" and hasattr(self._model, "to"):
                self._model = self._model.to(self._local_config.device)
        except Exception as exc:
            raise VisionBackendUnavailableError(f"Failed to load local vision runtime: {exc}") from exc

        return transformers, torch_module, self._processor

    def _build_local_messages(self, request: VisionRequest) -> list[dict[str, Any]]:
        image_items = [{"type": "image", "path": image.path} for image in request.images]
        return [
            {
                "role": "system",
                "content": [{"type": "text", "text": build_vision_system_prompt(backend_kind=self.backend_kind)}],
            },
            {
                "role": "user",
                "content": [
                    *image_items,
                    {"type": "text", "text": build_local_vision_payload_text(request)},
                ],
            },
        ]

    def _move_inputs_to_device(self, inputs: Any, device: Any) -> Any:
        if hasattr(inputs, "to"):
            return inputs.to(device)
        if isinstance(inputs, dict):
            moved: dict[str, Any] = {}
            for key, value in inputs.items():
                moved[key] = value.to(device) if hasattr(value, "to") else value
            return moved
        return inputs

    async def analyze(self, request: VisionRequest) -> dict[str, object]:
        _transformers, _torch_module, processor = self._ensure_local_components()
        model = self._model
        if model is None:
            raise VisionBackendUnavailableError("Local vision model failed to initialize.")
        if not hasattr(processor, "apply_chat_template") or not hasattr(processor, "batch_decode"):
            raise VisionBackendUnavailableError("Local vision processor does not expose the required chat/decode methods.")

        messages = self._build_local_messages(request)

        try:
            inputs = processor.apply_chat_template(
                messages,
                tokenize=True,
                return_dict=True,
                return_tensors="pt",
                add_generation_prompt=True,
            )
            model_device = getattr(model, "device", self._local_config.device)
            inputs = self._move_inputs_to_device(inputs, model_device)
            output_ids = model.generate(**inputs, max_new_tokens=self._runtime_config.max_tokens)
            input_ids = getattr(inputs, "input_ids", None)
            if input_ids is None and isinstance(inputs, dict):
                input_ids = inputs.get("input_ids")
            if input_ids is None:
                raise VisionBackendUnavailableError("Local vision inputs did not expose input_ids for decoding.")
            generated_ids = [output[len(prompt_ids) :] for prompt_ids, output in zip(input_ids, output_ids)]
            output_text = processor.batch_decode(
                generated_ids,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True,
            )
            if not output_text:
                raise VisionBackendUnavailableError("Local vision runtime returned no decoded text.")
            raw_text = str(output_text[0])
            self._last_output_diagnostics = diagnose_vision_output_text(raw_text)
            parsed_content = parse_vision_output_text(raw_text, request)
        except VisionBackendUnavailableError:
            raise
        except (json.JSONDecodeError, ValueError) as exc:
            raise VisionBackendUnavailableError("Local vision runtime did not return valid JSON content.") from exc
        except Exception as exc:
            raise VisionBackendUnavailableError(f"Local vision inference failed: {exc}") from exc

        return _normalize_assist_payload(
            backend_kind=self.backend_kind,
            model_name=self.model_name,
            request=request,
            parsed=parsed_content,
        )


class MLXLocalVisionBackend(VisionBackend):
    """Lazy local backend for Apple Silicon MLX vision runtimes."""

    def __init__(self, runtime_config: VisionRuntimeConfig) -> None:
        if runtime_config.mlx_local is None:
            raise VisionBackendUnavailableError("mlx_local backend is not configured.")
        self._runtime_config = runtime_config
        self._mlx_config = runtime_config.mlx_local
        self._runtime_modules: tuple[Any, Any, Any] | None = None
        self._model: Any | None = None
        self._processor: Any | None = None
        self._model_config: Any | None = None
        self._last_output_diagnostics: dict[str, Any] | None = None

    @property
    def backend_kind(self):
        return "mlx_local"

    @property
    def model_name(self) -> str:
        return self._mlx_config.model_id or self._mlx_config.model_path or "unknown-mlx-model"

    @property
    def last_output_diagnostics(self) -> dict[str, Any] | None:
        return self._last_output_diagnostics

    def _resolve_model_source(self) -> str:
        return self._mlx_config.model_id or self._mlx_config.model_path or self.model_name

    def _ensure_runtime_modules(self) -> tuple[Any, Any, Any]:
        if self._runtime_modules is not None:
            return self._runtime_modules

        try:
            mlx_vlm = importlib.import_module("mlx_vlm")
            prompt_utils = importlib.import_module("mlx_vlm.prompt_utils")
            utils = importlib.import_module("mlx_vlm.utils")
        except ModuleNotFoundError as exc:
            raise VisionBackendUnavailableError(
                "mlx_local backend requires optional runtime dependency: mlx-vlm"
            ) from exc

        self._runtime_modules = (mlx_vlm, prompt_utils, utils)
        return self._runtime_modules

    def _ensure_local_components(self) -> tuple[Any, Any, Any]:
        mlx_vlm, prompt_utils, utils = self._ensure_runtime_modules()
        if self._model is not None and self._processor is not None and self._model_config is not None:
            return mlx_vlm, prompt_utils, utils

        model_source = self._resolve_model_source()
        try:
            self._model, self._processor = mlx_vlm.load(model_source)
            self._model_config = utils.load_config(model_source)
        except Exception as exc:
            raise VisionBackendUnavailableError(f"Failed to load MLX vision runtime: {exc}") from exc

        return mlx_vlm, prompt_utils, utils

    def _build_prompt_payload(self, request: VisionRequest) -> str:
        return build_local_vision_payload_text(request)

    async def analyze(self, request: VisionRequest) -> dict[str, object]:
        mlx_vlm, prompt_utils, _utils = self._ensure_local_components()
        if self._model is None or self._processor is None or self._model_config is None:
            raise VisionBackendUnavailableError("MLX local vision runtime failed to initialize.")

        image_paths = [image.path for image in request.images]
        prompt_payload = self._build_prompt_payload(request)

        try:
            formatted_prompt = prompt_utils.apply_chat_template(
                self._processor,
                self._model_config,
                prompt_payload,
                num_images=len(image_paths),
            )

            try:
                output = mlx_vlm.generate(
                    self._model,
                    self._processor,
                    formatted_prompt,
                    image_paths,
                    verbose=False,
                    max_tokens=self._runtime_config.max_tokens,
                )
            except TypeError:
                output = mlx_vlm.generate(
                    self._model,
                    self._processor,
                    prompt=formatted_prompt,
                    image=image_paths,
                    verbose=False,
                    max_tokens=self._runtime_config.max_tokens,
                )

            output_text = getattr(output, "text", output)
            if not output_text:
                raise VisionBackendUnavailableError("MLX local vision runtime returned no output.")
            raw_text = str(output_text)
            self._last_output_diagnostics = diagnose_vision_output_text(raw_text)
            parsed_content = parse_vision_output_text(raw_text, request)
        except VisionBackendUnavailableError:
            raise
        except (json.JSONDecodeError, ValueError) as exc:
            raise VisionBackendUnavailableError("MLX local vision runtime did not return valid JSON content.") from exc
        except Exception as exc:
            raise VisionBackendUnavailableError(f"MLX local vision inference failed: {exc}") from exc

        return _normalize_assist_payload(
            backend_kind=self.backend_kind,
            model_name=self.model_name,
            request=request,
            parsed=parsed_content,
        )


class OpenAICompatibleVisionBackend(VisionBackend):
    """Lazy external backend stub for OpenAI-compatible vision endpoints."""

    def __init__(self, runtime_config: VisionRuntimeConfig) -> None:
        if runtime_config.openai_compatible_external is None:
            raise VisionBackendUnavailableError("openai_compatible_external backend is not configured.")
        self._runtime_config = runtime_config
        self._external_config = runtime_config.openai_compatible_external
        self._last_output_diagnostics: dict[str, Any] | None = None

    @property
    def backend_kind(self):
        return "openai_compatible_external"

    @property
    def model_name(self) -> str:
        return self._external_config.model or "unknown-external-model"

    @property
    def last_output_diagnostics(self) -> dict[str, Any] | None:
        return self._last_output_diagnostics

    def _endpoint_url(self) -> str:
        base_url = (self._external_config.base_url or "").rstrip("/")
        if self._external_config.provider_name == "google_ai_studio":
            model_name = self.model_name
            if model_name.startswith("models/"):
                return f"{base_url}/{model_name}:generateContent"
            return f"{base_url}/models/{model_name}:generateContent"
        if base_url.endswith("/chat/completions"):
            return base_url
        return f"{base_url}/chat/completions"

    def _resolved_api_key(self) -> str | None:
        if self._external_config.api_key:
            return self._external_config.api_key
        if self._external_config.api_key_env:
            return os.getenv(self._external_config.api_key_env) or None
        if self._external_config.provider_name == "google_ai_studio":
            return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or None
        return None

    def _provider_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self._external_config.provider_name == "openrouter":
            if self._external_config.site_url:
                headers["HTTP-Referer"] = self._external_config.site_url
            if self._external_config.site_name:
                headers["X-Title"] = self._external_config.site_name
        return headers

    def _build_request_payload(self, request: VisionRequest) -> dict[str, Any]:
        if self._external_config.provider_name == "google_ai_studio":
            parts: list[dict[str, Any]] = [{"text": build_vision_payload_text(request)}]
            for image in request.images:
                media_type = _media_type_for(image.path, image.media_type)
                encoded = base64.b64encode(Path(image.path).read_bytes()).decode("ascii")
                parts.append(
                    {
                        "inline_data": {
                            "mime_type": media_type,
                            "data": encoded,
                        }
                    }
                )

            return {
                "systemInstruction": {
                    "parts": [
                        {
                            "text": build_vision_system_prompt(backend_kind=self.backend_kind),
                        }
                    ]
                },
                "contents": [{"parts": parts}],
                "generationConfig": {
                    "temperature": 0.0,
                    "maxOutputTokens": self._runtime_config.max_tokens,
                    "responseMimeType": "application/json",
                    "responseJsonSchema": build_vision_response_json_schema(),
                },
            }

        content: list[dict[str, Any]] = [
            {
                "type": "text",
                "text": build_vision_payload_text(request),
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

        response_format: dict[str, Any]
        if self._external_config.provider_name == "openrouter":
            response_format = {
                "type": "json_schema",
                "json_schema": {
                    "name": "vision_assist",
                    "strict": True,
                    "schema": build_vision_response_json_schema(),
                },
            }
        else:
            response_format = {"type": "json_object"}

        return {
            "model": self.model_name,
            "temperature": 0.0,
            "max_tokens": self._runtime_config.max_tokens,
            "response_format": response_format,
            "messages": [
                {"role": "system", "content": build_vision_system_prompt(backend_kind=self.backend_kind)},
                {"role": "user", "content": content},
            ],
        }

    async def analyze(self, request: VisionRequest) -> dict[str, object]:
        headers = {"Content-Type": "application/json"}
        headers.update(self._provider_headers())
        api_key = self._resolved_api_key()
        if api_key and self._external_config.provider_name == "google_ai_studio":
            headers["x-goog-api-key"] = api_key
        elif api_key:
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

        if self._external_config.provider_name == "google_ai_studio":
            content = _extract_gemini_text(parsed_response)
        else:
            content = _extract_message_text(parsed_response)
        try:
            self._last_output_diagnostics = diagnose_vision_output_text(content)
            parsed_content = parse_vision_output_text(content, request)
        except (json.JSONDecodeError, ValueError) as exc:
            raise VisionBackendUnavailableError(
                "Vision endpoint did not return valid JSON content."
                f"{_diagnostics_suffix(self._last_output_diagnostics)}"
            ) from exc

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
    if runtime_config.provider == "mlx_local":
        return MLXLocalVisionBackend(runtime_config)
    if runtime_config.provider == "openai_compatible_external":
        return OpenAICompatibleVisionBackend(runtime_config)
    raise VisionBackendUnavailableError(f"Unsupported vision backend provider '{runtime_config.provider}'.")
