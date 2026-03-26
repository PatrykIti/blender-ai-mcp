# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Stub backend implementations for the pluggable vision runtime."""

from __future__ import annotations

from .backend import VisionBackend, VisionBackendUnavailableError, VisionRequest
from .config import VisionRuntimeConfig


class TransformersLocalVisionBackend(VisionBackend):
    """Lazy local backend stub for Hugging Face/Transformers VLMs."""

    def __init__(self, runtime_config: VisionRuntimeConfig) -> None:
        if runtime_config.transformers_local is None:
            raise VisionBackendUnavailableError("transformers_local backend is not configured.")
        self._runtime_config = runtime_config
        self._local_config = runtime_config.transformers_local

    @property
    def backend_kind(self):
        return "transformers_local"

    @property
    def model_name(self) -> str:
        return self._local_config.model_id or self._local_config.model_path or "unknown-local-model"

    async def analyze(self, request: VisionRequest) -> dict[str, object]:
        raise VisionBackendUnavailableError(
            "transformers_local vision backend wiring exists, but inference is not implemented yet."
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

    async def analyze(self, request: VisionRequest) -> dict[str, object]:
        raise VisionBackendUnavailableError(
            "openai_compatible_external vision backend wiring exists, but inference is not implemented yet."
        )


def create_vision_backend(runtime_config: VisionRuntimeConfig) -> VisionBackend:
    """Create one backend instance for the selected provider without loading a model at import time."""

    if runtime_config.provider == "transformers_local":
        return TransformersLocalVisionBackend(runtime_config)
    if runtime_config.provider == "openai_compatible_external":
        return OpenAICompatibleVisionBackend(runtime_config)
    raise VisionBackendUnavailableError(f"Unsupported vision backend provider '{runtime_config.provider}'.")
