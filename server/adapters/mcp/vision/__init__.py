# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Pluggable vision runtime scaffolding for TASK-121."""

from .backend import VisionBackend, VisionBackendUnavailableError, VisionImageInput, VisionRequest
from .backends import (
    OpenAICompatibleVisionBackend,
    TransformersLocalVisionBackend,
    create_vision_backend,
)
from .capture import (
    build_reference_capture_images,
    build_vision_request_from_capture_bundle,
    select_reference_records_for_target,
)
from .capture_runtime import (
    DEFAULT_CAPTURE_PRESET_SPECS,
    CapturePresetSpec,
    build_capture_bundle,
    capture_stage_images,
)
from .config import (
    VisionBackendKind,
    VisionOpenAICompatibleConfig,
    VisionRuntimeConfig,
    VisionTransformersLocalConfig,
)
from .reporting import attach_vision_artifacts
from .runtime import LazyVisionBackendResolver, build_vision_runtime_config

_RUNNER_EXPORTS = {
    "VISION_ASSIST_POLICY",
    "run_vision_assist",
}


def __getattr__(name: str):
    """Resolve runner exports lazily to avoid package-level cycles."""

    if name not in _RUNNER_EXPORTS:
        raise AttributeError(name)

    from server.adapters.mcp.vision import runner

    return getattr(runner, name)

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
    "VISION_ASSIST_POLICY",
    "CapturePresetSpec",
    "DEFAULT_CAPTURE_PRESET_SPECS",
    "attach_vision_artifacts",
    "build_reference_capture_images",
    "build_capture_bundle",
    "capture_stage_images",
    "build_vision_request_from_capture_bundle",
    "select_reference_records_for_target",
    "build_vision_runtime_config",
    "create_vision_backend",
    "run_vision_assist",
]
