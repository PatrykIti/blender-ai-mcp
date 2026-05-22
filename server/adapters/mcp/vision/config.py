# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Configuration models for the pluggable vision-assist runtime."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

VisionBackendKind = Literal["transformers_local", "mlx_local", "openai_compatible_external"]
VisionExternalProviderName = Literal["generic", "openrouter", "google_ai_studio"]
VisionContractProfile = Literal["generic_full", "google_family_compare"]
VisionReferenceClassifierProviderName = Literal["generic_sidecar", "generic", "openrouter", "google_ai_studio"]
VisionSegmentationProviderName = Literal["generic_sidecar"]
VisionLocalizationProviderName = Literal["generic_sidecar"]
VisionOptionalCapabilityName = Literal[
    "external_model_capabilities",
    "reference_classifier",
    "part_segmentation",
    "part_localization",
]
VisionOptionalCapabilityStatus = Literal["available", "disabled", "unavailable", "planned"]
VisionOptionalCapabilityActivationScope = Literal["vision_request", "reference_understanding", "compare_packet"]
VisionOptionalCapabilityLifecycleClass = Literal["request_scoped_only", "external_runtime", "sidecar_process"]
VisionModelCapabilitySource = Literal["fallback_registry", "openrouter_api", "env_override", "unknown"]
VISION_FAIL_SAFE_MAX_IMAGES = 12
VISION_FAIL_SAFE_MAX_INPUT_CHARS = 48_000
VISION_FAIL_SAFE_MAX_TOKENS = 8_192


class VisionModelCapabilities(BaseModel):
    """Bounded model capability metadata used for request policy decisions."""

    model_config = ConfigDict(extra="forbid")

    model_id: str
    capability_source: VisionModelCapabilitySource = "unknown"
    context_length: int | None = None
    max_completion_tokens: int | None = None
    input_modalities: list[str] = []
    output_modalities: list[str] = []
    supported_parameters: list[str] = []
    metadata_summary: dict[str, Any] = Field(default_factory=dict)


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

    provider_name: VisionExternalProviderName = "generic"
    vision_contract_profile: VisionContractProfile = "generic_full"
    base_url: str | None = None
    model: str | None = None
    api_key: str | None = None
    api_key_env: str | None = None
    site_url: str | None = None
    site_name: str | None = None
    require_parameters: bool = False
    enable_response_healing: bool = True
    prefer_json_object_for_qwen: bool = True
    model_capabilities: VisionModelCapabilities | None = None

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
    max_images: int = Field(default=8, ge=1)
    max_input_chars: int = Field(default=12000, ge=1)
    max_tokens: int = Field(default=400, ge=1)
    timeout_seconds: float = Field(default=20.0, gt=0)
    transformers_local: VisionTransformersLocalConfig | None = None
    mlx_local: VisionMLXLocalConfig | None = None
    openai_compatible_external: VisionOpenAICompatibleConfig | None = None
    reference_classifier: "VisionReferenceClassifierConfig | None" = None
    segmentation_sidecar: "VisionSegmentationSidecarConfig | None" = None
    localization_config: "VisionLocalizationConfig | None" = None

    @property
    def effective_max_images(self) -> int:
        """Return the image cap after fail-safe clipping."""

        return min(self.max_images, VISION_FAIL_SAFE_MAX_IMAGES)

    @property
    def effective_max_input_chars(self) -> int:
        """Return the input-character cap after fail-safe clipping."""

        return min(self.max_input_chars, VISION_FAIL_SAFE_MAX_INPUT_CHARS)

    @property
    def effective_max_tokens(self) -> int:
        """Return the output-token cap after model-capability and fail-safe policy."""

        model_capabilities = (
            self.openai_compatible_external.model_capabilities if self.openai_compatible_external is not None else None
        )
        model_cap = model_capabilities.max_completion_tokens if model_capabilities is not None else None
        if model_cap is None:
            return min(self.max_tokens, VISION_FAIL_SAFE_MAX_TOKENS)
        profile = self.active_vision_contract_profile
        profile_floor = 4096 if profile == "google_family_compare" else 2048
        return min(max(self.max_tokens, profile_floor), model_cap, VISION_FAIL_SAFE_MAX_TOKENS)

    @property
    def budget_clip_fields(self) -> list[str]:
        """Return budget names where configured values were clipped before execution."""

        clipped_fields: list[str] = []
        if self.effective_max_images < self.max_images:
            clipped_fields.append("max_images")
        if self.effective_max_input_chars < self.max_input_chars:
            clipped_fields.append("max_input_chars")
        if self.effective_max_tokens < self.max_tokens:
            clipped_fields.append("max_output_tokens")
        return clipped_fields

    @model_validator(mode="after")
    def validate_provider_config(self) -> "VisionRuntimeConfig":
        """Require configuration for the selected provider when enabled."""

        if not self.enabled:
            return self

        if self.provider == "transformers_local" and self.transformers_local is None:
            raise ValueError(
                "enabled vision runtime with provider=transformers_local requires transformers_local config"
            )

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

    @property
    def active_vision_contract_profile(self) -> VisionContractProfile | None:
        """Return the resolved external vision contract profile for diagnostics."""

        if self.provider != "openai_compatible_external" or self.openai_compatible_external is None:
            return None
        return self.openai_compatible_external.vision_contract_profile

    @property
    def active_reference_classifier(self) -> "VisionReferenceClassifierConfig | None":
        """Return the optional reference-classifier config when enabled."""

        return self.reference_classifier

    @property
    def active_segmentation_sidecar(self) -> "VisionSegmentationSidecarConfig | None":
        """Return the optional segmentation sidecar config when enabled."""

        return self.segmentation_sidecar

    @property
    def active_localization_config(self) -> "VisionLocalizationConfig | None":
        """Return the optional compare-time localization config when enabled."""

        return self.localization_config

    @property
    def optional_capability_inventory(self) -> "VisionOptionalCapabilityInventory":
        """Return one typed internal inventory for optional vision support branches."""

        capabilities: list[VisionOptionalCapabilityState] = []
        external_config = self.openai_compatible_external
        external_provider_name = external_config.provider_name if external_config is not None else None
        external_model_id = external_config.model if external_config is not None else None
        if self.provider == "openai_compatible_external" and external_config is not None:
            external_prerequisite_summary = (
                "External runtime capability metadata is available for bounded request policy."
                if external_config.model_capabilities is not None
                else "External runtime is configured, but capability metadata is not currently attached."
            )
            capabilities.append(
                VisionOptionalCapabilityState(
                    capability_name="external_model_capabilities",
                    status="available",
                    provider_name=external_provider_name,
                    model_id=external_model_id,
                    prerequisite_summary=external_prerequisite_summary,
                    activation_scope="vision_request",
                    lifecycle_class="external_runtime",
                )
            )
        else:
            capabilities.append(
                VisionOptionalCapabilityState(
                    capability_name="external_model_capabilities",
                    status="disabled",
                    provider_name=external_provider_name,
                    model_id=external_model_id,
                    prerequisite_summary="External model capability metadata is inactive on the current runtime.",
                    activation_scope="vision_request",
                    lifecycle_class="external_runtime",
                )
            )

        reference_classifier = self.active_reference_classifier
        capabilities.append(
            VisionOptionalCapabilityState(
                capability_name="reference_classifier",
                status="available" if reference_classifier is not None else "disabled",
                provider_name=reference_classifier.provider_name if reference_classifier is not None else None,
                model_id=reference_classifier.model if reference_classifier is not None else None,
                prerequisite_summary=(
                    "Optional reference classifier is configured for advisory-only RU support."
                    if reference_classifier is not None
                    else "Optional reference classifier is disabled by default."
                ),
                activation_scope="reference_understanding",
                lifecycle_class="sidecar_process",
            )
        )

        segmentation_sidecar = self.active_segmentation_sidecar
        capabilities.append(
            VisionOptionalCapabilityState(
                capability_name="part_segmentation",
                status="available" if segmentation_sidecar is not None else "disabled",
                provider_name=segmentation_sidecar.provider_name if segmentation_sidecar is not None else None,
                model_id=segmentation_sidecar.model if segmentation_sidecar is not None else None,
                prerequisite_summary=(
                    "Optional packet-local segmentation is configured for bounded compare-time support."
                    if segmentation_sidecar is not None
                    else "Optional packet-local segmentation is disabled by default."
                ),
                activation_scope="compare_packet",
                lifecycle_class="sidecar_process",
            )
        )

        localization_config = self.active_localization_config
        capabilities.append(
            VisionOptionalCapabilityState(
                capability_name="part_localization",
                status="available" if localization_config is not None else "disabled",
                provider_name=localization_config.provider_name if localization_config is not None else None,
                model_id=localization_config.model if localization_config is not None else None,
                prerequisite_summary=(
                    "Optional packet-local localization is configured for bounded compare-time support."
                    if localization_config is not None
                    else "Optional packet-local localization is disabled by default."
                ),
                activation_scope="compare_packet",
                lifecycle_class="sidecar_process" if localization_config is not None else "request_scoped_only",
            )
        )

        return VisionOptionalCapabilityInventory(capabilities=capabilities)


class VisionReferenceClassifierConfig(BaseModel):
    """Configuration for the optional reference-classifier sidecar."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = False
    provider_name: VisionReferenceClassifierProviderName = "generic_sidecar"
    endpoint: str | None = None
    model: str | None = None
    api_key: str | None = None
    api_key_env: str | None = None
    timeout_seconds: float = Field(default=15.0, gt=0)
    max_labels: int = Field(default=5, ge=1, le=5)

    @model_validator(mode="after")
    def validate_endpoint(self) -> "VisionReferenceClassifierConfig":
        """Require an explicit endpoint only when the classifier is enabled."""

        if self.enabled and not self.endpoint:
            raise ValueError("enabled reference_classifier requires endpoint")
        return self


class VisionSegmentationSidecarConfig(BaseModel):
    """Configuration for the optional part-segmentation sidecar."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = False
    provider_name: VisionSegmentationProviderName = "generic_sidecar"
    endpoint: str | None = None
    model: str | None = None
    api_key: str | None = None
    api_key_env: str | None = None
    timeout_seconds: float = Field(default=15.0, gt=0)
    max_parts: int = Field(default=16, ge=1, le=64)

    @model_validator(mode="after")
    def validate_endpoint(self) -> "VisionSegmentationSidecarConfig":
        """Require an explicit endpoint only when the sidecar is enabled."""

        if self.enabled and not self.endpoint:
            raise ValueError("enabled segmentation_sidecar requires endpoint")
        return self


class VisionLocalizationConfig(BaseModel):
    """Configuration for the optional compare-time localization sidecar."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = False
    provider_name: VisionLocalizationProviderName = "generic_sidecar"
    endpoint: str | None = None
    model: str | None = None
    api_key: str | None = None
    api_key_env: str | None = None
    timeout_seconds: float = Field(default=15.0, gt=0)
    max_candidates: int = Field(default=8, ge=1, le=32)

    @model_validator(mode="after")
    def validate_endpoint(self) -> "VisionLocalizationConfig":
        """Require an explicit endpoint only when localization is enabled."""

        if self.enabled and not self.endpoint:
            raise ValueError("enabled localization_config requires endpoint")
        return self


class VisionLocalizationCandidate(BaseModel):
    """One provider-neutral internal packet-local localization candidate."""

    model_config = ConfigDict(extra="forbid")

    packet_id: str
    query_label: str
    reference_id: str | None = None
    capture_label: str | None = None
    target_view: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    box_xyxy: tuple[float, float, float, float]
    crop_path: str | None = None


class VisionOptionalCapabilityState(BaseModel):
    """One internal optional capability state used for additive diagnostics."""

    model_config = ConfigDict(extra="forbid")

    capability_name: VisionOptionalCapabilityName
    status: VisionOptionalCapabilityStatus
    provider_name: str | None = None
    model_id: str | None = None
    prerequisite_summary: str | None = None
    activation_scope: VisionOptionalCapabilityActivationScope
    lifecycle_class: VisionOptionalCapabilityLifecycleClass
    advisory_only: bool = True


class VisionOptionalCapabilityInventory(BaseModel):
    """Canonical typed internal inventory for optional vision capabilities."""

    model_config = ConfigDict(extra="forbid")

    capabilities: list[VisionOptionalCapabilityState] = Field(default_factory=list)

    def get(self, capability_name: VisionOptionalCapabilityName) -> VisionOptionalCapabilityState | None:
        """Return one capability state by name when present."""

        for item in self.capabilities:
            if item.capability_name == capability_name:
                return item
        return None
