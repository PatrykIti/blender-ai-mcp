# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Typed declarations for reviewed model-capability fallback profiles."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from server.adapters.mcp.vision.config import VisionContractProfile, VisionModelCapabilities

VisionModelProviderName = Literal["openrouter"]


class ModelCapabilityProfile(BaseModel):
    """One reviewed fallback profile for a concrete provider/model id."""

    model_config = ConfigDict(extra="forbid")

    model_id: str
    provider: VisionModelProviderName
    family: str
    context_length: int | None = None
    max_completion_tokens: int | None = None
    input_modalities: tuple[str, ...] = ()
    output_modalities: tuple[str, ...] = ()
    supported_parameters: tuple[str, ...] = ()
    preferred_contract_profile: VisionContractProfile | None = None
    preferred_stage_max_tokens: int | None = None
    docs_url: str | None = None
    last_reviewed: str
    notes: str | None = None

    def to_runtime_capabilities(self) -> VisionModelCapabilities:
        """Convert the reviewed profile into runtime capability metadata."""

        return VisionModelCapabilities(
            model_id=self.model_id,
            capability_source="fallback_registry",
            context_length=self.context_length,
            max_completion_tokens=self.max_completion_tokens,
            input_modalities=list(self.input_modalities),
            output_modalities=list(self.output_modalities),
            supported_parameters=list(self.supported_parameters),
        )
