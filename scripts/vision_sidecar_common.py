#!/usr/bin/env python3
"""Shared helpers for local optional vision sidecar scripts."""

from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import numpy as np


@dataclass(frozen=True)
class PayloadImageRef:
    """One reference or capture image extracted from a sidecar payload."""

    source_kind: Literal["capture", "reference"]
    image_path: str
    reference_id: str | None = None
    capture_label: str | None = None
    target_view: str | None = None
    media_type: str | None = None


def resolve_device_name(requested: str) -> str:
    """Resolve one concrete torch device name from an operator-facing value."""

    normalized = str(requested or "auto").strip().lower()
    if normalized != "auto":
        return normalized

    try:
        import torch
    except Exception:
        return "cpu"

    if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda:0"
    return "cpu"


def resolve_model_alias(model_name: str, aliases: dict[str, str]) -> str:
    """Expand one user-facing alias into the real model identifier."""

    requested = str(model_name or "").strip()
    if not requested:
        raise ValueError("A model name or alias is required.")
    return aliases.get(requested, requested)


def iter_payload_images(payload: dict[str, Any]) -> list[PayloadImageRef]:
    """Return captures first, then references, preserving only usable paths."""

    images: list[PayloadImageRef] = []

    captures = payload.get("captures")
    if isinstance(captures, list):
        for item in captures:
            if not isinstance(item, dict):
                continue
            image_path = str(item.get("image_path") or "").strip()
            if not image_path:
                continue
            images.append(
                PayloadImageRef(
                    source_kind="capture",
                    image_path=image_path,
                    capture_label=str(item.get("label") or "").strip() or None,
                    target_view=str(item.get("target_view") or item.get("view_kind") or "").strip() or None,
                    media_type=str(item.get("media_type") or "").strip() or None,
                )
            )

    references = payload.get("references")
    if isinstance(references, list):
        for item in references:
            if not isinstance(item, dict):
                continue
            image_path = str(item.get("image_path") or item.get("stored_path") or "").strip()
            if not image_path:
                continue
            images.append(
                PayloadImageRef(
                    source_kind="reference",
                    image_path=image_path,
                    reference_id=str(item.get("reference_id") or "").strip() or None,
                    target_view=str(item.get("target_view") or "").strip() or None,
                    media_type=str(item.get("media_type") or "").strip() or None,
                )
            )

    return images


def humanize_query_label(query_label: str) -> str:
    """Turn an internal query label into a detector-friendly text prompt."""

    return " ".join(part for part in str(query_label or "").replace("-", "_").split("_") if part).strip()


def clamp_box_to_image(
    box_xyxy: tuple[float, float, float, float],
    *,
    width: int,
    height: int,
) -> tuple[int, int, int, int]:
    """Clamp one XYXY box into the current image bounds."""

    x1, y1, x2, y2 = box_xyxy
    clipped = (
        max(0, min(int(round(x1)), width)),
        max(0, min(int(round(y1)), height)),
        max(0, min(int(round(x2)), width)),
        max(0, min(int(round(y2)), height)),
    )
    if clipped[2] <= clipped[0]:
        clipped = (clipped[0], clipped[1], min(width, clipped[0] + 1), clipped[3])
    if clipped[3] <= clipped[1]:
        clipped = (clipped[0], clipped[1], clipped[2], min(height, clipped[1] + 1))
    return clipped


def write_temp_image(image: Any, *, prefix: str, suffix: str) -> str:
    """Persist one PIL image to a temp file and return its path."""

    with tempfile.NamedTemporaryFile(prefix=prefix, suffix=suffix, delete=False) as handle:
        output_path = Path(handle.name)
    image.save(output_path)
    return str(output_path)


def write_mask_image(mask: np.ndarray, *, prefix: str) -> str:
    """Persist one boolean/float mask as a grayscale PNG."""

    from PIL import Image

    normalized = np.asarray(mask)
    if normalized.dtype != np.uint8:
        normalized = normalized.astype(np.uint8)
    if normalized.max(initial=0) <= 1:
        normalized = normalized * 255
    return write_temp_image(Image.fromarray(normalized, mode="L"), prefix=prefix, suffix=".png")


def mask_bbox(mask: np.ndarray) -> tuple[int, int, int, int] | None:
    """Return one XYXY bbox for a boolean mask when any foreground exists."""

    normalized = np.asarray(mask).astype(bool)
    points = np.argwhere(normalized)
    if points.size == 0:
        return None
    y1, x1 = points.min(axis=0)
    y2, x2 = points.max(axis=0)
    return int(x1), int(y1), int(x2) + 1, int(y2) + 1
