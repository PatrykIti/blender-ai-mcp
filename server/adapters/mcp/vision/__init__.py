# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Pluggable vision runtime scaffolding for TASK-121."""

from .backend import VisionBackend, VisionBackendUnavailableError, VisionImageInput, VisionRequest
from .backends import (
    OpenAICompatibleVisionBackend,
    TransformersLocalVisionBackend,
    create_vision_backend,
)
from .config import (
    VisionBackendKind,
    VisionOpenAICompatibleConfig,
    VisionRuntimeConfig,
    VisionTransformersLocalConfig,
)
from .runtime import LazyVisionBackendResolver, build_vision_runtime_config

__all__ = [
    "VisionBackend",
    "VisionBackendKind",
    "VisionBackendUnavailableError",
    "VisionImageInput",
    "LazyVisionBackendResolver",
    "OpenAICompatibleVisionBackend",
    "TransformersLocalVisionBackend",
    "VisionOpenAICompatibleConfig",
    "VisionRequest",
    "VisionRuntimeConfig",
    "VisionTransformersLocalConfig",
    "build_vision_runtime_config",
    "create_vision_backend",
]
