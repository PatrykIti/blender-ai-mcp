# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Structured contracts for TASK-121 vision/capture inputs."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from .base import MCPContract
from .scene import SceneAssembledTargetScopeContract


class VisionObjectIdCaptureArtifactContract(MCPContract):
    """Internal object-ID sidecar for deterministic per-object silhouette evidence."""

    image_path: str | None = Field(
        default=None,
        description="Local PNG path for the object-ID pass when capture succeeded.",
    )
    host_visible_path: str | None = Field(
        default=None,
        description="Host-visible PNG path for debugging the object-ID pass.",
    )
    media_type: str = Field(default="image/png", description="Media type for the object-ID pass artifact.")
    index_map: dict[int, str] = Field(
        default_factory=dict,
        description="Object-ID pass index map keyed by pass-index band.",
    )
    missing_objects: list[str] = Field(
        default_factory=list,
        description="Requested objects that were absent when the pass was rendered.",
    )
    capture_ok: bool = Field(
        default=True,
        description="False when the object-ID pass failed but the primary viewport capture still succeeded.",
    )
    capture_warning: str | None = Field(
        default=None,
        description="Short warning explaining why the object-ID sidecar is unavailable.",
    )


class VisionOverlayMarkContract(MCPContract):
    """One deterministic Set-of-Mark marker drawn on an overlay capture."""

    mark_id: int = Field(description="Stable numbered mark id; visible on the overlay only when status is placed.")
    object_name: str = Field(description="Scene object represented by this mark.")
    status: Literal["placed", "unmarked"] = Field(
        default="placed",
        description="Whether the mark was placed on the overlay or the object could not be marked.",
    )
    source: Literal["deterministic_projection", "grounded_sam_sidecar"] = Field(
        default="deterministic_projection",
        description="Whether this mark came from deterministic render projection or optional reference grounding.",
    )
    image_side: Literal["render", "reference"] = Field(
        default="render",
        description="Which side of the compare pair the mark labels.",
    )


class VisionCaptureImageContract(MCPContract):
    """One deterministic image artifact used in a capture bundle."""

    label: str
    image_path: str
    host_visible_path: str | None = None
    preset_name: str | None = None
    media_type: str = "image/png"
    view_kind: Literal[
        "wide",
        "focus",
        "top",
        "oblique",
        "overlay",
        "reference",
        "grid",
        "depth",
        "normal",
        "object_id",
    ] = "wide"
    projection: Literal["orthographic", "perspective"] | None = Field(
        default=None,
        description=(
            "Symbolic camera projection hint for the capture. Used to distinguish "
            "orthographic top/standard views from perspective oblique/detail views."
        ),
    )
    capture_ok: bool = True
    """Advisory reliability flag: ``False`` when a camera/view op for this preset
    returned a known failure marker, so the framed view may not match its label.
    Defaults to ``True`` so existing serialized payloads stay valid."""
    capture_warning: str | None = None
    """Short advisory note naming which view op failed and the preset it was
    meant to produce; ``None`` on a clean capture."""
    object_id_artifact: VisionObjectIdCaptureArtifactContract | None = None
    """Optional internal object-ID sidecar used for deterministic per-object
    silhouette evidence. It is not transmitted as a VLM image by default."""
    overlay_marks: list[VisionOverlayMarkContract] = Field(default_factory=list)
    """Set-of-Mark ids visible on this overlay capture, mapped back to scene objects."""


class VisionCaptureBundleContract(MCPContract):
    """One before/after capture bundle prepared for bounded visual comparison."""

    bundle_id: str
    goal_id: str | None = None
    target_object: str | None = None
    assembled_target_scope: SceneAssembledTargetScopeContract | None = None
    preset_names: list[str]
    captures_before: list[VisionCaptureImageContract]
    captures_after: list[VisionCaptureImageContract]
    truth_summary: dict[str, Any] | None = None
    capture_warnings: list[str] = []
    """Advisory bundle-level summary of per-image capture failures across both
    stages; empty when every capture in the bundle framed cleanly."""
