# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Runtime configuration bridge for bounded vision assistance.

This module intentionally stops at typed configuration and lazy backend
resolution scaffolding. It does not load a heavyweight local VLM during the
core MCP server bootstrap path.
"""

from __future__ import annotations

from collections.abc import Callable

from server.infrastructure.config import Config

from .backend import VisionBackend, VisionBackendUnavailableError
from .backends import create_vision_backend
from .config import (
    VisionMLXLocalConfig,
    VisionOpenAICompatibleConfig,
    VisionRuntimeConfig,
    VisionTransformersLocalConfig,
)

_OPENROUTER_DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"


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
    use_openrouter_profile = bool(config.VISION_OPENROUTER_MODEL) or config.VISION_EXTERNAL_PROVIDER == "openrouter"
    if use_openrouter_profile or config.VISION_EXTERNAL_BASE_URL or config.VISION_EXTERNAL_MODEL:
        external_base_url = (
            config.VISION_OPENROUTER_BASE_URL or _OPENROUTER_DEFAULT_BASE_URL
            if use_openrouter_profile
            else config.VISION_EXTERNAL_BASE_URL
        )
        external_config = VisionOpenAICompatibleConfig(
            provider_name="openrouter" if use_openrouter_profile else "generic",
            base_url=external_base_url,
            model=config.VISION_OPENROUTER_MODEL or config.VISION_EXTERNAL_MODEL,
            api_key=config.VISION_OPENROUTER_API_KEY or config.VISION_EXTERNAL_API_KEY,
            api_key_env=config.VISION_OPENROUTER_API_KEY_ENV or config.VISION_EXTERNAL_API_KEY_ENV,
            site_url=config.VISION_OPENROUTER_SITE_URL,
            site_name=config.VISION_OPENROUTER_SITE_NAME,
        )

    return VisionRuntimeConfig(
        enabled=config.VISION_ENABLED,
        provider=config.VISION_PROVIDER,
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
