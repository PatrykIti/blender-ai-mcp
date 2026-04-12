# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Reviewed fallback model-capability profiles for vision runtimes."""

from .registry import resolve_fallback_model_capabilities
from .types import ModelCapabilityProfile

__all__ = ["ModelCapabilityProfile", "resolve_fallback_model_capabilities"]
