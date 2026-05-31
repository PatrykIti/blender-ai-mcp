# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Deterministic Set-of-Mark overlay helpers for object-bound visual prompting.

These helpers draw high-contrast numbered marks on a render at the position of
each registered part, so the VLM can refer to parts by a stable mark id instead
of guessing which similar part is meant. Marks are deterministic and computed
server-side from per-object silhouette masks (e.g. isolated renders) — no GPU
overlay code in the addon and no external segmentation model on the render side.

The marker styling follows BLINK's finding that high-contrast (red), moderately
sized markers are easiest for VLMs to read.
"""

from __future__ import annotations

import base64
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import numpy as np

from .silhouette import _extract_mask_from_image

# (mark_id, x, y) in pixel coordinates of the base image.
NumberedMark = tuple[object, int, int]

_MARK_RADIUS = 14
_MARK_FILL = (220, 30, 30)
_MARK_OUTLINE = (255, 255, 255)
_MARK_TEXT = (255, 255, 255)


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
    """Build a numbered-mark overlay of the base capture for the given objects.

    Renders per-object isolated masks from the same view, assigns stable marks,
    and overlays them on ``base_image_path``. Returns
    ``(overlay_path_or_None, mark_id_to_object)``; the overlay path is None when no
    object mask was usable.
    """

    object_masks = render_object_masks(
        scene_handler,
        object_names,
        output_dir=output_dir,
        view_name=view_name,
        width=width,
        height=height,
    )
    marks, mark_id_to_object = build_marks_from_object_masks(object_masks, mark_id_map=mark_id_map)
    if not marks:
        return None, {}
    overlay_numbered_marks(base_image_path, marks, output_path)
    return output_path, mark_id_to_object
