# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Deterministic Set-of-Mark overlay helpers for object-bound visual prompting.

These helpers draw high-contrast numbered marks on a render at the position of
each registered part, so the VLM can refer to parts by a stable mark id instead
of guessing which similar part is meant. Marks are deterministic and computed
server-side from projection diagnostics first, with per-object silhouette masks
as a fallback when projection is unavailable — no GPU overlay code in the addon
and no external segmentation model on the render side.

The marker styling follows BLINK's finding that high-contrast (red), moderately
sized markers are easiest for VLMs to read.
"""

from __future__ import annotations

import base64
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import numpy as np

from .silhouette import _extract_mask_from_image

# (mark_id, x, y) in pixel coordinates of the base image.
NumberedMark = tuple[object, int, int]
MarkAnchorStatus = Literal["projected", "outside_frame", "behind_view", "occluded", "unavailable", "mask_fallback"]
MarkAnchorSource = Literal["deterministic_projection", "mask_centroid_fallback"]

_MARK_RADIUS = 14
_MARK_FILL = (220, 30, 30)
_MARK_OUTLINE = (255, 255, 255)
_MARK_TEXT = (255, 255, 255)


@dataclass(frozen=True, slots=True)
class MarkAnchorResolution:
    """One resolved or rejected mark anchor for overlay metadata."""

    mark_id: int
    object_name: str
    point: tuple[int, int] | None
    anchor_status: MarkAnchorStatus
    source: MarkAnchorSource


def _ordered_mark_pairs(
    object_names: Sequence[str],
    mark_id_map: dict[str, int] | None,
) -> list[tuple[int, str]]:
    ordered_object_names = sorted(dict.fromkeys(str(name).strip() for name in object_names if str(name).strip()))
    if mark_id_map:
        pairs = [
            (mark_id, object_name)
            for object_name, mark_id in sorted(mark_id_map.items(), key=lambda item: (item[1], item[0]))
            if object_name in set(ordered_object_names) and isinstance(mark_id, int) and mark_id > 0
        ]
        if pairs:
            return pairs
    return [(mark_id, object_name) for mark_id, object_name in enumerate(ordered_object_names, start=1)]


def _unit_to_pixel(value: float, *, size: int) -> int:
    return min(size - 1, max(0, int(round(value * max(size - 1, 1)))))


def _numeric_projection_value(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def _projection_point_to_pixel(point: dict[str, Any], *, width: int, height: int) -> tuple[int, int] | None:
    x = _numeric_projection_value(point.get("x"))
    y = _numeric_projection_value(point.get("y"))
    if x is None or y is None:
        return None
    if not 0.0 <= x <= 1.0 or not 0.0 <= y <= 1.0:
        return None
    return _unit_to_pixel(x, size=width), _unit_to_pixel(1.0 - y, size=height)


def _extent_representative_pixel(extent: dict[str, Any], *, width: int, height: int) -> tuple[int, int] | None:
    parsed = [_numeric_projection_value(extent.get(key)) for key in ("min_x", "min_y", "max_x", "max_y")]
    if any(value is None for value in parsed):
        return None
    min_x, min_y, max_x, max_y = parsed
    assert min_x is not None and min_y is not None and max_x is not None and max_y is not None
    clamped_min_x = min(1.0, max(0.0, min_x))
    clamped_max_x = min(1.0, max(0.0, max_x))
    clamped_min_y = min(1.0, max(0.0, min_y))
    clamped_max_y = min(1.0, max(0.0, max_y))
    if clamped_max_x <= clamped_min_x or clamped_max_y <= clamped_min_y:
        return None
    center = {
        "x": (clamped_min_x + clamped_max_x) / 2.0,
        "y": (clamped_min_y + clamped_max_y) / 2.0,
    }
    return _projection_point_to_pixel(center, width=width, height=height)


def _projection_anchor_for_target(
    target: dict[str, Any] | None,
    *,
    width: int,
    height: int,
) -> tuple[tuple[int, int] | None, MarkAnchorStatus]:
    if not isinstance(target, dict):
        return None, "unavailable"
    projection_status = str(target.get("projection_status") or "").strip()
    visibility_verdict = str(target.get("visibility_verdict") or "").strip()
    if projection_status == "behind_view":
        return None, "behind_view"
    if visibility_verdict == "fully_occluded":
        return None, "occluded"
    if projection_status == "outside_frame" or visibility_verdict == "outside_frame":
        return None, "outside_frame"
    projection = target.get("projection")
    if not isinstance(projection, dict):
        return None, "unavailable"
    if projection_status == "unavailable":
        return None, "unavailable"

    center = projection.get("projected_center")
    if isinstance(center, dict):
        center_point = _projection_point_to_pixel(center, width=width, height=height)
        if center_point is not None:
            return center_point, "projected"

    extent = projection.get("projected_extent")
    if isinstance(extent, dict):
        extent_point = _extent_representative_pixel(extent, width=width, height=height)
        if extent_point is not None:
            return extent_point, "projected"

    return None, "outside_frame"


def build_projection_mark_anchors(
    projection_diagnostics: dict[str, Any] | None,
    *,
    object_names: Sequence[str],
    width: int,
    height: int,
    mark_id_map: dict[str, int] | None = None,
) -> list[MarkAnchorResolution]:
    """Resolve mark anchors from view-diagnostics projection payloads.

    Coordinates are converted from normalized Blender camera/view projection
    space into base-image pixel coordinates. Objects with unavailable projection
    data are returned as explicit ``unavailable`` entries so callers can decide
    whether the older mask-centroid fallback is appropriate.
    """

    if not isinstance(projection_diagnostics, dict):
        return [
            MarkAnchorResolution(
                mark_id=mark_id,
                object_name=object_name,
                point=None,
                anchor_status="unavailable",
                source="deterministic_projection",
            )
            for mark_id, object_name in _ordered_mark_pairs(object_names, mark_id_map)
        ]
    targets_by_name: dict[str, dict[str, Any]] = {}
    for item in list(projection_diagnostics.get("targets") or []):
        if not isinstance(item, dict):
            continue
        object_name = str(item.get("object_name") or "").strip()
        if object_name:
            targets_by_name[object_name] = item

    resolutions: list[MarkAnchorResolution] = []
    for mark_id, object_name in _ordered_mark_pairs(object_names, mark_id_map):
        point, anchor_status = _projection_anchor_for_target(
            targets_by_name.get(object_name),
            width=width,
            height=height,
        )
        resolutions.append(
            MarkAnchorResolution(
                mark_id=mark_id,
                object_name=object_name,
                point=point,
                anchor_status=anchor_status,
                source="deterministic_projection",
            )
        )
    return resolutions


def mask_centroid(mask_image_path: str) -> tuple[int, int] | None:
    """Return the integer (x, y) centroid of a silhouette mask image, or None.

    Reuses the same deterministic mask extraction as the silhouette metrics, so a
    mark lands on the same foreground the IoU is computed over.
    """

    mask, _notes = _extract_mask_from_image(mask_image_path)
    if mask is None:
        return None
    ys, xs = np.nonzero(mask)
    if xs.size == 0:
        return None
    return int(round(float(xs.mean()))), int(round(float(ys.mean())))


def overlay_numbered_marks(
    base_image_path: str,
    marks: Sequence[NumberedMark],
    output_path: str,
    *,
    radius: int = _MARK_RADIUS,
) -> str:
    """Draw high-contrast numbered marks on a copy of ``base_image_path``.

    ``marks`` is a sequence of ``(mark_id, x, y)``. Each mark is a filled red
    disc with a white outline and a centered white id. Returns ``output_path``.
    Deterministic and order-stable.
    """

    from PIL import Image, ImageDraw

    with Image.open(base_image_path) as opened:
        image = opened.convert("RGBA")
    draw = ImageDraw.Draw(image)
    for mark_id, x, y in marks:
        bbox = [x - radius, y - radius, x + radius, y + radius]
        draw.ellipse(bbox, fill=_MARK_FILL, outline=_MARK_OUTLINE, width=2)
        draw.text((x, y), str(mark_id), fill=_MARK_TEXT, anchor="mm")
    image.convert("RGB").save(output_path)
    return output_path


def build_marks_from_object_masks(
    object_mask_paths: dict[str, str],
    *,
    mark_id_map: dict[str, int] | None = None,
) -> tuple[list[NumberedMark], dict[int, str]]:
    """Compute numbered marks from per-object mask images.

    Returns ``(marks, mark_id_to_object)`` where mark ids are 1-based and assigned
    from ``mark_id_map`` when supplied, otherwise in sorted object-name order.
    Objects whose mask has no usable foreground are skipped.
    """

    marks: list[NumberedMark] = []
    mark_id_to_object: dict[int, str] = {}
    if mark_id_map:
        ordered_pairs = [
            (mark_id, object_name)
            for object_name, mark_id in sorted(mark_id_map.items(), key=lambda item: (item[1], item[0]))
            if object_name in object_mask_paths and isinstance(mark_id, int) and mark_id > 0
        ]
    else:
        ordered_pairs = [
            (mark_id, object_name) for mark_id, object_name in enumerate(sorted(object_mask_paths), start=1)
        ]
    for mark_id, object_name in ordered_pairs:
        centroid = mask_centroid(object_mask_paths[object_name])
        if centroid is None:
            continue
        x, y = centroid
        marks.append((mark_id, x, y))
        mark_id_to_object[mark_id] = object_name
    return marks, mark_id_to_object


def build_mark_correspondence_table(
    findings: Sequence[dict[str, Any]],
    mark_id_to_object: dict[int, str],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Resolve mark-keyed findings back to scene objects.

    Returns ``(rows, validity_warnings)`` where each row maps a finding's
    ``mark_id`` to the object it labels. A finding whose ``mark_id`` is not in the
    overlay's id->object map is dropped from the table and recorded as a validity
    warning (the VLM-Grounder validity guard against references to non-existent
    marks). Findings without a ``mark_id`` are ignored here (they flow through the
    normal finding channel). Advisory only.
    """

    rows: list[dict[str, Any]] = []
    warnings: list[str] = []
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        mark_id = finding.get("mark_id")
        if not isinstance(mark_id, int) or isinstance(mark_id, bool):
            continue
        object_name = mark_id_to_object.get(mark_id)
        if object_name is None:
            warnings.append(f"Finding referenced mark id {mark_id}, which does not exist on the overlay.")
            continue
        rows.append(
            {
                "mark_id": mark_id,
                "object_name": object_name,
                "finding": str(finding.get("finding") or ""),
                "target_label": finding.get("target_label"),
            }
        )
    return rows, warnings


def render_object_masks(
    scene_handler: Any,
    object_names: Sequence[str],
    *,
    output_dir: str,
    view_name: str | None = None,
    width: int = 1280,
    height: int = 960,
) -> dict[str, str]:
    """Render each object isolated from a shared view to produce per-object masks.

    Reuses the existing addon ``isolate_object`` / ``set_standard_view`` /
    ``get_viewport`` so no new addon render code is required. Every object is
    rendered from the same view and resolution so the resulting centroids align
    with a base capture taken from that same view. Returns
    ``{object_name: mask_image_path}``; objects whose render fails are skipped.
    """

    masks: dict[str, str] = {}
    for index, object_name in enumerate(object_names):
        try:
            if hasattr(scene_handler, "isolate_object"):
                scene_handler.isolate_object([object_name])
            if view_name and hasattr(scene_handler, "set_standard_view"):
                scene_handler.set_standard_view(view_name)
            encoded = scene_handler.get_viewport(width=width, height=height, shading="SOLID", focus_target=None)
        except Exception:
            continue
        if not isinstance(encoded, str) or not encoded:
            continue
        mask_path = Path(output_dir) / f"objmask_{index}.png"
        try:
            mask_path.write_bytes(base64.b64decode(encoded))
        except Exception:
            continue
        masks[object_name] = str(mask_path)
    return masks


def _anchor_metadata(
    resolutions: Sequence[MarkAnchorResolution],
) -> dict[int, dict[str, Any]]:
    return {
        item.mark_id: {
            "object_name": item.object_name,
            "status": "placed" if item.point is not None else "unmarked",
            "anchor_status": item.anchor_status,
            "source": item.source,
        }
        for item in resolutions
    }


def build_object_mark_overlay_with_metadata(
    scene_handler: Any,
    *,
    object_names: Sequence[str],
    base_image_path: str,
    output_path: str,
    output_dir: str,
    view_name: str | None = None,
    width: int = 1280,
    height: int = 960,
    mark_id_map: dict[str, int] | None = None,
    projection_diagnostics: dict[str, Any] | None = None,
) -> tuple[str | None, dict[int, str], dict[int, dict[str, Any]]]:
    """Build a numbered-mark overlay of the base capture for the given objects.

    Uses projection diagnostics first when available, falling back to per-object
    mask centroids only when projection data is unavailable. Returns
    ``(overlay_path_or_None, mark_id_to_object, mark_metadata_by_id)``; the
    overlay path is None when no usable anchor was available.
    """

    projection_resolutions = build_projection_mark_anchors(
        projection_diagnostics,
        object_names=object_names,
        width=width,
        height=height,
        mark_id_map=mark_id_map,
    )
    resolutions_by_object = {item.object_name: item for item in projection_resolutions}
    fallback_object_names = [
        item.object_name
        for item in projection_resolutions
        if item.point is None and item.anchor_status == "unavailable"
    ]
    fallback_resolutions: list[MarkAnchorResolution] = []
    if fallback_object_names:
        fallback_mark_map = {
            item.object_name: item.mark_id
            for item in projection_resolutions
            if item.object_name in fallback_object_names
        }
        object_masks = render_object_masks(
            scene_handler,
            fallback_object_names,
            output_dir=output_dir,
            view_name=view_name,
            width=width,
            height=height,
        )
        fallback_marks, _fallback_mark_id_to_object = build_marks_from_object_masks(
            object_masks,
            mark_id_map=fallback_mark_map,
        )
        fallback_points = {
            mark_id: (int(x), int(y))
            for mark_id, x, y in fallback_marks
            if isinstance(mark_id, int) and not isinstance(mark_id, bool)
        }
        fallback_object_by_id = {mark_id: object_name for object_name, mark_id in fallback_mark_map.items()}
        for mark_id, point in sorted(fallback_points.items()):
            object_name = fallback_object_by_id.get(mark_id)
            if object_name is None:
                continue
            fallback_resolutions.append(
                MarkAnchorResolution(
                    mark_id=mark_id,
                    object_name=object_name,
                    point=point,
                    anchor_status="mask_fallback",
                    source="mask_centroid_fallback",
                )
            )
            resolutions_by_object[object_name] = fallback_resolutions[-1]

    ordered_resolutions = [
        resolutions_by_object[object_name]
        for _mark_id, object_name in _ordered_mark_pairs(object_names, mark_id_map)
        if object_name in resolutions_by_object
    ]
    marks: list[NumberedMark] = [
        (item.mark_id, item.point[0], item.point[1]) for item in ordered_resolutions if item.point is not None
    ]
    mark_id_to_object = {item.mark_id: item.object_name for item in ordered_resolutions if item.point is not None}
    mark_metadata_by_id = _anchor_metadata(ordered_resolutions)
    if not marks:
        return None, {}, mark_metadata_by_id
    overlay_numbered_marks(base_image_path, marks, output_path)
    return output_path, mark_id_to_object, mark_metadata_by_id


def build_object_mark_overlay(
    scene_handler: Any,
    *,
    object_names: Sequence[str],
    base_image_path: str,
    output_path: str,
    output_dir: str,
    view_name: str | None = None,
    width: int = 1280,
    height: int = 960,
    mark_id_map: dict[str, int] | None = None,
) -> tuple[str | None, dict[int, str]]:
    """Backward-compatible wrapper for callers that do not need anchor metadata."""

    overlay_path, mark_id_to_object, _metadata = build_object_mark_overlay_with_metadata(
        scene_handler,
        object_names=object_names,
        base_image_path=base_image_path,
        output_path=output_path,
        output_dir=output_dir,
        view_name=view_name,
        width=width,
        height=height,
        mark_id_map=mark_id_map,
    )
    return overlay_path, mark_id_to_object
