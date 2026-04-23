# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Deterministic silhouette-analysis helpers for staged reference comparison."""

from __future__ import annotations

from collections import deque
from typing import Any

import numpy as np

_NORMALIZED_MASK_SIZE = 128
_BORDER_RATIO_THRESHOLD = 0.35


def _metric_severity(delta: float, *, high: float, medium: float) -> str:
    absolute = abs(delta)
    if absolute >= high:
        return "high"
    if absolute >= medium:
        return "medium"
    return "low"


def _largest_component(mask: np.ndarray) -> np.ndarray:
    if mask.ndim != 2 or not bool(mask.any()):
        return np.zeros_like(mask, dtype=bool)

    visited = np.zeros(mask.shape, dtype=bool)
    best_coords: list[tuple[int, int]] = []

    height, width = mask.shape
    active_pixels = np.argwhere(mask)
    for y, x in active_pixels:
        if visited[y, x]:
            continue
        queue: deque[tuple[int, int]] = deque([(int(y), int(x))])
        visited[y, x] = True
        coords: list[tuple[int, int]] = []
        while queue:
            current_y, current_x = queue.popleft()
            coords.append((current_y, current_x))
            for delta_y, delta_x in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                next_y = current_y + delta_y
                next_x = current_x + delta_x
                if next_y < 0 or next_y >= height or next_x < 0 or next_x >= width:
                    continue
                if visited[next_y, next_x] or not bool(mask[next_y, next_x]):
                    continue
                visited[next_y, next_x] = True
                queue.append((next_y, next_x))

        if len(coords) > len(best_coords):
            best_coords = coords

    component = np.zeros_like(mask, dtype=bool)
    if not best_coords:
        return component
    ys, xs = zip(*best_coords)
    component[np.array(ys), np.array(xs)] = True
    return component


def _otsu_threshold(values: np.ndarray) -> int:
    histogram = np.bincount(values.ravel(), minlength=256).astype(np.float64)
    total = float(values.size)
    if total <= 0:
        return 127
    if int(np.count_nonzero(histogram)) <= 1:
        return 127

    cumulative = np.cumsum(histogram)
    cumulative_mean = np.cumsum(histogram * np.arange(256, dtype=np.float64))
    global_mean = cumulative_mean[-1]

    denominator = cumulative * (total - cumulative)
    denominator[denominator == 0.0] = np.nan
    between_class_variance = ((global_mean * cumulative - cumulative_mean) ** 2) / denominator
    if not bool(np.isfinite(between_class_variance).any()):
        return 127
    threshold = int(np.nanargmax(between_class_variance))
    return max(1, min(254, threshold))


def _candidate_score(mask: np.ndarray) -> float:
    if not bool(mask.any()):
        return float("-inf")

    component = _largest_component(mask)
    if not bool(component.any()):
        return float("-inf")

    border = np.concatenate(
        (
            component[0, :],
            component[-1, :],
            component[:, 0],
            component[:, -1],
        )
    )
    border_ratio = float(border.mean()) if border.size else 0.0
    area_ratio = float(component.mean())
    centered_area_bonus = 1.0 - abs(area_ratio - 0.25)
    return centered_area_bonus - (border_ratio * 2.0)


def _extract_mask_from_image(image_path: str) -> tuple[np.ndarray | None, list[str]]:
    notes: list[str] = []

    try:
        from PIL import Image
    except ImportError:
        return None, ["Pillow is not installed; deterministic silhouette analysis is unavailable."]

    try:
        with Image.open(image_path) as image:
            rgba_image = image.convert("RGBA")
            rgba = np.asarray(rgba_image)
    except Exception:
        return None, [f"Image '{image_path}' could not be decoded for deterministic silhouette analysis."]

    alpha = rgba[:, :, 3]
    if np.any(alpha < 250):
        component = _largest_component(alpha > 32)
        if bool(component.any()):
            return component, notes
        notes.append("Alpha channel was present, but no stable foreground component was found.")

    grayscale = np.dot(rgba[:, :, :3], np.array([0.299, 0.587, 0.114], dtype=np.float64)).astype(np.uint8)
    if int(grayscale.min()) == int(grayscale.max()):
        notes.append("Image luminance was uniform; Otsu thresholding could not isolate a silhouette mask.")
        return None, notes
    threshold = _otsu_threshold(grayscale)
    candidates = (
        _largest_component(grayscale <= threshold),
        _largest_component(grayscale >= threshold),
    )
    best_candidate = max(candidates, key=_candidate_score)
    if not bool(best_candidate.any()):
        notes.append("Otsu thresholding did not isolate a stable silhouette mask.")
        return None, notes

    border = np.concatenate(
        (
            best_candidate[0, :],
            best_candidate[-1, :],
            best_candidate[:, 0],
            best_candidate[:, -1],
        )
    )
    if float(border.mean()) > _BORDER_RATIO_THRESHOLD:
        notes.append("Foreground touched most borders; silhouette mask is low confidence.")

    return best_candidate, notes


def _crop_bbox(mask: np.ndarray) -> tuple[np.ndarray, tuple[int, int]]:
    positions = np.argwhere(mask)
    if positions.size == 0:
        return mask, (0, 0)

    y_min, x_min = positions.min(axis=0)
    y_max, x_max = positions.max(axis=0)
    cropped = mask[y_min : y_max + 1, x_min : x_max + 1]
    return cropped, (int(cropped.shape[1]), int(cropped.shape[0]))


def _normalize_mask(mask: np.ndarray) -> np.ndarray:
    try:
        from PIL import Image
    except ImportError as exc:  # pragma: no cover - handled by caller notes
        raise RuntimeError("Pillow is required for deterministic silhouette normalization.") from exc

    image = Image.fromarray((mask.astype(np.uint8) * 255), mode="L")
    normalized = image.resize((_NORMALIZED_MASK_SIZE, _NORMALIZED_MASK_SIZE), resample=Image.Resampling.NEAREST)
    return np.asarray(normalized) > 0


def _band_mean(profile: np.ndarray, start: float, end: float) -> float:
    if profile.size == 0:
        return 0.0
    start_index = max(0, int(round(profile.size * start)))
    end_index = min(profile.size, int(round(profile.size * end)))
    if end_index <= start_index:
        return 0.0
    return float(np.mean(profile[start_index:end_index]))


def build_silhouette_analysis(
    *,
    reference_path: str,
    capture_path: str,
    reference_label: str | None = None,
    capture_label: str | None = None,
    target_view: str | None = None,
) -> dict[str, Any]:
    """Build deterministic silhouette metrics from one reference/capture pair."""

    reference_mask, reference_notes = _extract_mask_from_image(reference_path)
    capture_mask, capture_notes = _extract_mask_from_image(capture_path)
    notes = [*reference_notes, *capture_notes]
    if reference_mask is None or capture_mask is None:
        return {
            "status": "unavailable",
            "reference_label": reference_label,
            "capture_label": capture_label,
            "target_view": target_view,
            "mask_extraction_mode": "unavailable",
            "alignment_mode": "unavailable",
            "metrics": [],
            "notes": notes or ["Silhouette extraction was unavailable for the provided images."],
        }

    reference_crop, reference_bbox = _crop_bbox(reference_mask)
    capture_crop, capture_bbox = _crop_bbox(capture_mask)

    if reference_bbox == (0, 0) or capture_bbox == (0, 0):
        return {
            "status": "unavailable",
            "reference_label": reference_label,
            "capture_label": capture_label,
            "target_view": target_view,
            "mask_extraction_mode": "unavailable",
            "alignment_mode": "unavailable",
            "metrics": [],
            "notes": notes or ["Silhouette masks did not contain a usable foreground bbox."],
        }

    normalized_reference = _normalize_mask(reference_crop)
    normalized_capture = _normalize_mask(capture_crop)

    intersection = float(np.logical_and(normalized_reference, normalized_capture).sum())
    union = float(np.logical_or(normalized_reference, normalized_capture).sum()) or 1.0
    reference_row_profile = normalized_reference.mean(axis=1)
    capture_row_profile = normalized_capture.mean(axis=1)
    reference_column_profile = normalized_reference.mean(axis=0)
    capture_column_profile = normalized_capture.mean(axis=0)

    contour_drift = float(
        (
            np.mean(np.abs(reference_row_profile - capture_row_profile))
            + np.mean(np.abs(reference_column_profile - capture_column_profile))
        )
        / 2.0
    )
    reference_aspect_ratio = float(reference_bbox[1] / max(reference_bbox[0], 1))
    capture_aspect_ratio = float(capture_bbox[1] / max(capture_bbox[0], 1))

    metrics = [
        {
            "metric_id": "mask_iou",
            "reference_value": 1.0,
            "observed_value": intersection / union,
            "delta": (intersection / union) - 1.0,
            "severity": _metric_severity((intersection / union) - 1.0, high=0.35, medium=0.18),
        },
        {
            "metric_id": "contour_drift",
            "reference_value": 0.0,
            "observed_value": contour_drift,
            "delta": contour_drift,
            "severity": _metric_severity(contour_drift, high=0.18, medium=0.09),
        },
        {
            "metric_id": "aspect_ratio_delta",
            "reference_value": reference_aspect_ratio,
            "observed_value": capture_aspect_ratio,
            "delta": capture_aspect_ratio - reference_aspect_ratio,
            "severity": _metric_severity(capture_aspect_ratio - reference_aspect_ratio, high=0.35, medium=0.18),
        },
    ]

    for metric_id, start, end in (
        ("upper_band_width_delta", 0.0, 0.2),
        ("mid_band_width_delta", 0.35, 0.65),
        ("lower_band_width_delta", 0.75, 1.0),
        ("left_projection_delta", 0.0, 0.2),
        ("right_projection_delta", 0.8, 1.0),
    ):
        reference_profile = reference_row_profile
        capture_profile = capture_row_profile
        if metric_id.endswith("projection_delta"):
            reference_profile = reference_column_profile
            capture_profile = capture_column_profile
        reference_value = _band_mean(reference_profile, start, end)
        observed_value = _band_mean(capture_profile, start, end)
        delta = observed_value - reference_value
        metrics.append(
            {
                "metric_id": metric_id,
                "reference_value": reference_value,
                "observed_value": observed_value,
                "delta": delta,
                "severity": _metric_severity(delta, high=0.18, medium=0.09),
            }
        )

    return {
        "status": "available",
        "reference_label": reference_label,
        "capture_label": capture_label,
        "target_view": target_view,
        "mask_extraction_mode": "alpha_or_otsu_largest_component",
        "alignment_mode": "bbox_normalized",
        "metrics": metrics,
        "notes": notes,
    }
