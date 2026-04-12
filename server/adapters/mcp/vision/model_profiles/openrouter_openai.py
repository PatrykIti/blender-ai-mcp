# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Reviewed OpenRouter OpenAI-family fallback profiles."""

from __future__ import annotations

from .types import ModelCapabilityProfile

OPENROUTER_OPENAI_PROFILES: tuple[ModelCapabilityProfile, ...] = (
    ModelCapabilityProfile(
        model_id="openai/gpt-5.4-nano",
        provider="openrouter",
        family="openai_gpt_5_4",
        context_length=400_000,
        max_completion_tokens=128_000,
        input_modalities=("text", "image"),
        output_modalities=("text",),
        supported_parameters=("response_format", "structured_outputs"),
        preferred_contract_profile="google_family_compare",
        preferred_stage_max_tokens=4096,
        docs_url="https://openrouter.ai/openai/gpt-5.4-nano",
        last_reviewed="2026-04-12",
        notes=(
            "Operator-reviewed OpenRouter profile. Use the narrower checkpoint compare contract by default; "
            "the full generic envelope can be too large for bounded stage compare responses."
        ),
    ),
)
