# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Runtime configuration bridge for bounded vision assistance.

This module intentionally stops at typed configuration and lazy backend
resolution scaffolding. It does not load a heavyweight local VLM during the
core MCP server bootstrap path.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal, cast

from server.infrastructure.config import Config

from .backend import VisionBackend, VisionBackendUnavailableError
from .backends import create_vision_backend
from .config import (
    VisionBackendKind,
    VisionMLXLocalConfig,
    VisionOpenAICompatibleConfig,
    VisionRuntimeConfig,
    VisionTransformersLocalConfig,
)

_OPENROUTER_DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
_GOOGLE_AI_STUDIO_DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"


def build_vision_runtime_config(config: Config) -> VisionRuntimeConfig:
    """Build typed vision runtime config from flat application settings."""

    local_config = None
    if config.VISION_LOCAL_MODEL_ID or config.VISION_LOCAL_MODEL_PATH:
        local_config = VisionTransformersLocalConfig(
            model_id=config.VISION_LOCAL_MODEL_ID,
            model_path=config.VISION_LOCAL_MODEL_PATH,
            device=config.VISION_LOCAL_DEVICE,
            dtype=config.VISION_LOCAL_DTYPE,
        )

    mlx_local_config = None
    if config.VISION_MLX_MODEL_ID or config.VISION_MLX_MODEL_PATH:
        mlx_local_config = VisionMLXLocalConfig(
            model_id=config.VISION_MLX_MODEL_ID,
            model_path=config.VISION_MLX_MODEL_PATH,
        )

    external_config = None
    explicit_external_provider = config.VISION_EXTERNAL_PROVIDER
    if explicit_external_provider == "openrouter":
        use_openrouter_profile = True
        use_google_ai_studio_profile = False
    elif explicit_external_provider == "google_ai_studio":
        use_openrouter_profile = False
        use_google_ai_studio_profile = True
    else:
        if config.VISION_OPENROUTER_MODEL and config.VISION_GEMINI_MODEL:
            raise ValueError(
                "VISION_OPENROUTER_MODEL and VISION_GEMINI_MODEL are both set while VISION_EXTERNAL_PROVIDER=generic. "
                "Choose one provider explicitly."
            )
        use_openrouter_profile = bool(config.VISION_OPENROUTER_MODEL)
        use_google_ai_studio_profile = bool(config.VISION_GEMINI_MODEL)

    if use_openrouter_profile:
        should_build_external_config = bool(config.VISION_OPENROUTER_MODEL or config.VISION_EXTERNAL_MODEL)
    elif use_google_ai_studio_profile:
        should_build_external_config = bool(config.VISION_GEMINI_MODEL or config.VISION_EXTERNAL_MODEL)
    else:
        should_build_external_config = bool(config.VISION_EXTERNAL_BASE_URL and config.VISION_EXTERNAL_MODEL)

    if should_build_external_config:
        external_provider_name: Literal["generic", "openrouter", "google_ai_studio"]
        external_base_url: str | None
        external_model: str | None
        external_api_key: str | None
        external_api_key_env: str | None
        site_url: str | None
        site_name: str | None

        if use_openrouter_profile:
            external_provider_name = "openrouter"
            external_base_url = config.VISION_OPENROUTER_BASE_URL or _OPENROUTER_DEFAULT_BASE_URL
            external_model = config.VISION_OPENROUTER_MODEL or config.VISION_EXTERNAL_MODEL
            external_api_key = config.VISION_OPENROUTER_API_KEY or config.VISION_EXTERNAL_API_KEY
            external_api_key_env = config.VISION_OPENROUTER_API_KEY_ENV or config.VISION_EXTERNAL_API_KEY_ENV
            site_url = config.VISION_OPENROUTER_SITE_URL
            site_name = config.VISION_OPENROUTER_SITE_NAME
        elif use_google_ai_studio_profile:
            external_provider_name = "google_ai_studio"
            external_base_url = config.VISION_GEMINI_BASE_URL or _GOOGLE_AI_STUDIO_DEFAULT_BASE_URL
            external_model = config.VISION_GEMINI_MODEL or config.VISION_EXTERNAL_MODEL
            external_api_key = config.VISION_GEMINI_API_KEY or config.VISION_EXTERNAL_API_KEY
            external_api_key_env = (
                config.VISION_GEMINI_API_KEY_ENV or config.VISION_EXTERNAL_API_KEY_ENV or "GEMINI_API_KEY"
            )
            site_url = None
            site_name = None
        else:
            external_provider_name = "generic"
            external_base_url = config.VISION_EXTERNAL_BASE_URL
            external_model = config.VISION_EXTERNAL_MODEL
            external_api_key = config.VISION_EXTERNAL_API_KEY
            external_api_key_env = config.VISION_EXTERNAL_API_KEY_ENV
            site_url = None
            site_name = None

        external_config = VisionOpenAICompatibleConfig(
            provider_name=external_provider_name,
            base_url=external_base_url,
            model=external_model,
            api_key=external_api_key,
            api_key_env=external_api_key_env,
            site_url=site_url,
            site_name=site_name,
        )

    return VisionRuntimeConfig(
        enabled=config.VISION_ENABLED,
        provider=cast(VisionBackendKind, config.VISION_PROVIDER),
        allow_on_guided=config.VISION_ALLOW_ON_GUIDED,
        max_images=config.VISION_MAX_IMAGES,
        max_tokens=config.VISION_MAX_TOKENS,
        timeout_seconds=config.VISION_TIMEOUT_SECONDS,
        transformers_local=local_config,
        mlx_local=mlx_local_config,
        openai_compatible_external=external_config,
    )


class LazyVisionBackendResolver:
    """Lazy, failure-tolerant resolver for optional vision backends.

    The concrete backend factory is intentionally injected so the main MCP server
    can start without importing or loading heavyweight vision runtimes.
    """

    def __init__(self, runtime_config: VisionRuntimeConfig) -> None:
        self._runtime_config = runtime_config

    @property
    def runtime_config(self) -> VisionRuntimeConfig:
        """Expose the typed runtime configuration for diagnostics."""

        return self._runtime_config

    def resolve(self, factory: Callable[[VisionRuntimeConfig], VisionBackend | None]) -> VisionBackend:
        """Resolve one backend lazily using an injected factory.

        The factory should accept a ``VisionRuntimeConfig`` and either return a
        concrete ``VisionBackend`` or raise an exception that will be normalized
        into ``VisionBackendUnavailableError``.
        """

        if not self._runtime_config.enabled:
            raise VisionBackendUnavailableError("Vision runtime is disabled.")

        try:
            backend = factory(self._runtime_config)
        except VisionBackendUnavailableError:
            raise
        except Exception as exc:  # pragma: no cover - defensive normalization
            raise VisionBackendUnavailableError(str(exc)) from exc

        if backend is None:
            raise VisionBackendUnavailableError("Vision backend factory returned no backend.")
        return backend

    def resolve_default(self) -> VisionBackend:
        """Resolve the default backend implementation for the selected provider."""

        return self.resolve(create_vision_backend)
