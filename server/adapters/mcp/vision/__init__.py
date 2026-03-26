# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Pluggable vision runtime scaffolding for TASK-121."""

from .backend import VisionBackend, VisionBackendUnavailableError, VisionImageInput, VisionRequest
from .backends import (
    MLXLocalVisionBackend,
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
    CAPTURE_PRESET_PROFILES,
    COMPACT_CAPTURE_PRESET_SPECS,
    DEFAULT_CAPTURE_PRESET_SPECS,
    RICH_CAPTURE_PRESET_SPECS,
    CapturePresetSpec,
    build_capture_bundle,
    capture_scene_state,
    capture_stage_images,
    resolve_capture_preset_specs,
    restore_scene_state,
)
from .config import (
    VisionBackendKind,
    VisionMLXLocalConfig,
    VisionOpenAICompatibleConfig,
    VisionRuntimeConfig,
    VisionTransformersLocalConfig,
)
from .policy import choose_capture_preset_profile, choose_reference_target_view, infer_capture_preset_profile
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
    "MLXLocalVisionBackend",
    "VisionMLXLocalConfig",
    "OpenAICompatibleVisionBackend",
    "TransformersLocalVisionBackend",
    "VisionOpenAICompatibleConfig",
    "VisionRequest",
    "VisionRuntimeConfig",
    "VisionTransformersLocalConfig",
    "VISION_ASSIST_POLICY",
    "CapturePresetSpec",
    "CAPTURE_PRESET_PROFILES",
    "COMPACT_CAPTURE_PRESET_SPECS",
    "DEFAULT_CAPTURE_PRESET_SPECS",
    "RICH_CAPTURE_PRESET_SPECS",
    "attach_vision_artifacts",
    "choose_capture_preset_profile",
    "choose_reference_target_view",
    "build_reference_capture_images",
    "build_capture_bundle",
    "capture_scene_state",
    "capture_stage_images",
    "resolve_capture_preset_specs",
    "build_vision_request_from_capture_bundle",
    "infer_capture_preset_profile",
    "select_reference_records_for_target",
    "build_vision_runtime_config",
    "create_vision_backend",
    "restore_scene_state",
    "run_vision_assist",
]
