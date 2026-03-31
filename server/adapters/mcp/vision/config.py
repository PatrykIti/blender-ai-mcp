# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Configuration models for the pluggable vision-assist runtime."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

VisionBackendKind = Literal["transformers_local", "mlx_local", "openai_compatible_external"]


class VisionTransformersLocalConfig(BaseModel):
    """Configuration for local Hugging Face/Transformers vision runtimes."""

    model_config = ConfigDict(extra="forbid")

    model_id: str | None = None
    model_path: str | None = None
    device: str = "cpu"
    dtype: str = "auto"

    @model_validator(mode="after")
    def validate_source(self) -> "VisionTransformersLocalConfig":
        """Require one explicit model source for local runtimes."""

        if not self.model_id and not self.model_path:
            raise ValueError("transformers_local backend requires model_id or model_path")
        return self


class VisionOpenAICompatibleConfig(BaseModel):
    """Configuration for external OpenAI-compatible vision endpoints."""

    model_config = ConfigDict(extra="forbid")

    provider_name: Literal["generic", "openrouter", "google_ai_studio"] = "generic"
    base_url: str | None = None
    model: str | None = None
    api_key: str | None = None
    api_key_env: str | None = None
    site_url: str | None = None
    site_name: str | None = None

    @model_validator(mode="after")
    def validate_endpoint(self) -> "VisionOpenAICompatibleConfig":
        """Require one explicit endpoint target for external runtimes."""

        if not self.base_url:
            raise ValueError("openai_compatible_external backend requires base_url")
        if not self.model:
            raise ValueError("openai_compatible_external backend requires model")
        return self


class VisionMLXLocalConfig(BaseModel):
    """Configuration for local Apple Silicon MLX vision runtimes."""

    model_config = ConfigDict(extra="forbid")

    model_id: str | None = None
    model_path: str | None = None

    @model_validator(mode="after")
    def validate_source(self) -> "VisionMLXLocalConfig":
        """Require one explicit model source for MLX runtimes."""

        if not self.model_id and not self.model_path:
            raise ValueError("mlx_local backend requires model_id or model_path")
        return self


class VisionRuntimeConfig(BaseModel):
    """Top-level runtime configuration for bounded vision assistance."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = False
    provider: VisionBackendKind = "transformers_local"
    allow_on_guided: bool = True
    max_images: int = Field(default=8, ge=1, le=12)
    max_tokens: int = Field(default=400, ge=1)
    timeout_seconds: float = Field(default=20.0, gt=0)
    transformers_local: VisionTransformersLocalConfig | None = None
    mlx_local: VisionMLXLocalConfig | None = None
    openai_compatible_external: VisionOpenAICompatibleConfig | None = None

    @model_validator(mode="after")
    def validate_provider_config(self) -> "VisionRuntimeConfig":
        """Require configuration for the selected provider when enabled."""

        if not self.enabled:
            return self

        if self.provider == "transformers_local" and self.transformers_local is None:
            raise ValueError("enabled vision runtime with provider=transformers_local requires transformers_local config")

        if self.provider == "mlx_local" and self.mlx_local is None:
            raise ValueError("enabled vision runtime with provider=mlx_local requires mlx_local config")

        if self.provider == "openai_compatible_external" and self.openai_compatible_external is None:
            raise ValueError(
                "enabled vision runtime with provider=openai_compatible_external requires openai_compatible_external config"
            )
        return self

    @property
    def active_backend_config(
        self,
    ) -> VisionTransformersLocalConfig | VisionMLXLocalConfig | VisionOpenAICompatibleConfig | None:
        """Return the config block for the selected backend."""

        if self.provider == "transformers_local":
            return self.transformers_local
        if self.provider == "mlx_local":
            return self.mlx_local
        return self.openai_compatible_external

    @property
    def active_model_name(self) -> str | None:
        """Return a human-readable model name for diagnostics."""

        active = self.active_backend_config
        if active is None:
            return None
        if isinstance(active, VisionTransformersLocalConfig):
            return active.model_id or active.model_path
        if isinstance(active, VisionMLXLocalConfig):
            return active.model_id or active.model_path
        return active.model
