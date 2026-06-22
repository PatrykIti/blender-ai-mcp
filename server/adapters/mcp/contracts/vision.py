# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Structured contracts for TASK-121 vision/capture inputs."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from .base import MCPContract
from .scene import SceneAssembledTargetScopeContract


class VisionObjectIdCaptureArtifactContract(MCPContract):
    """Internal Object Index sidecar for deterministic object-level silhouette evidence."""

    image_path: str | None = Field(
        default=None,
        description="Local PNG path for the Object Index / pass_index pass when capture succeeded.",
    )
    host_visible_path: str | None = Field(
        default=None,
        description="Host-visible PNG path for debugging the Object Index / pass_index pass.",
    )
    media_type: str = Field(default="image/png", description="Media type for the Object Index pass artifact.")
    evidence_scope: Literal["object_level_visible_surface"] = Field(
        default="object_level_visible_surface",
        description=(
            "Evidence scope: rendered visible surface for whole scene objects only. "
            "This is whole-object evidence only and does not identify sub-object regions."
        ),
    )
    object_index_source: Literal["object_index_pass_index"] = Field(
        default="object_index_pass_index",
        description="Blender Object Index / object.pass_index value used as the object-level identifier.",
    )
    encoding: Literal["object_index_grayscale_band"] = Field(
        default="object_index_grayscale_band",
        description="8-bit grayscale band encoding derived from pass-index/object-count ordering.",
    )
    cryptomatte_status: Literal["deferred"] = Field(
        default="deferred",
        description="Cryptomatte is intentionally deferred for this artifact path.",
    )
    object_count: int = Field(
        default=0,
        ge=0,
        description="Highest pass-index/object-count value used for grayscale band decoding when known.",
    )
    grayscale_band_count: int = Field(
        default=255,
        ge=1,
        description="Maximum non-background grayscale bands available in the current 8-bit PNG sidecar.",
    )
    high_count_quantization_risk: bool = Field(
        default=False,
        description="True when the object count makes adjacent grayscale bands too close for robust decoding.",
    )
    index_map: dict[int, str] = Field(
        default_factory=dict,
        description="Object Index pass map keyed by positive Blender pass_index value.",
    )
    missing_objects: list[str] = Field(
        default_factory=list,
        description="Requested objects that were absent when the pass was rendered.",
    )
    capture_ok: bool = Field(
        default=True,
        description="False when the Object Index pass failed but the primary viewport capture still succeeded.",
    )
    capture_warning: str | None = Field(
        default=None,
        description="Short warning explaining why the Object Index sidecar is unavailable.",
    )
    notes: list[str] = Field(
        default_factory=list,
        description="Decode caveats such as grayscale-band quantization risk.",
    )


class VisionOverlayMarkContract(MCPContract):
    """One deterministic Set-of-Mark marker drawn on an overlay capture."""

    mark_id: int = Field(description="Stable numbered mark id; visible on the overlay only when status is placed.")
    object_name: str = Field(description="Scene object represented by this mark.")
    status: Literal["placed", "unmarked"] = Field(
        default="placed",
        description="Whether the mark was placed on the overlay or the object could not be marked.",
    )
    source: Literal["deterministic_projection", "mask_centroid_fallback", "grounded_sam_sidecar"] = Field(
        default="deterministic_projection",
        description="Whether this mark came from deterministic render projection or optional reference grounding.",
    )
    image_side: Literal["render", "reference"] = Field(
        default="render",
        description="Which side of the compare pair the mark labels.",
    )
    anchor_status: (
        Literal[
            "projected",
            "outside_frame",
            "behind_view",
            "occluded",
            "unavailable",
            "mask_fallback",
        ]
        | None
    ) = Field(
        default=None,
        description="Projection/placement status for the visual anchor used to place or skip this mark.",
    )
    anchor_source: Literal["projection_diagnostics", "mask_centroid_fallback", "grounded_sam_sidecar"] | None = Field(
        default=None,
        description="Deterministic source used for the rendered anchor location or reference-side mark.",
    )
    anchor_x: int | None = Field(
        default=None,
        description="Pixel x-coordinate of the rendered mark anchor when status is placed.",
    )
    anchor_y: int | None = Field(
        default=None,
        description="Pixel y-coordinate of the rendered mark anchor when status is placed.",
    )
    anchor_reason: str | None = Field(
        default=None,
        description="Bounded diagnostic for unavailable, off-frame, occluded, or fallback anchors.",
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
    """Optional internal Object Index sidecar used for deterministic object-level
    visible-surface silhouette evidence. It is not transmitted as a VLM image by default."""
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
