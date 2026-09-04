# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Registry helpers for reviewed model-capability fallback profiles."""

from __future__ import annotations

from .openrouter_openai import OPENROUTER_OPENAI_PROFILES
from .types import ModelCapabilityProfile, VisionModelProviderName

_ALL_PROFILES: tuple[ModelCapabilityProfile, ...] = (*OPENROUTER_OPENAI_PROFILES,)
_PROFILE_BY_PROVIDER_AND_MODEL = {(profile.provider, profile.model_id.lower()): profile for profile in _ALL_PROFILES}


def resolve_model_profile(
    *,
    provider: VisionModelProviderName,
    model_id: str | None,
) -> ModelCapabilityProfile | None:
    """Return one reviewed fallback profile for a provider/model id."""

    normalized_model_id = str(model_id or "").strip().lower()
    if not normalized_model_id:
        return None
    return _PROFILE_BY_PROVIDER_AND_MODEL.get((provider, normalized_model_id))


def resolve_fallback_model_capabilities(
    *,
    provider: VisionModelProviderName,
    model_id: str | None,
):
    """Return runtime capability metadata for a provider/model id."""

    profile = resolve_model_profile(provider=provider, model_id=model_id)
    if profile is None:
        return None
    return profile.to_runtime_capabilities()
