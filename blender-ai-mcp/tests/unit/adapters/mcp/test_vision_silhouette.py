"""Focused regression tests for deterministic silhouette analysis."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from server.adapters.mcp.vision.silhouette import build_silhouette_analysis


def _metric(payload: dict[str, Any], metric_id: str) -> dict[str, Any]:
    for metric in payload["metrics"]:
        if metric["metric_id"] == metric_id:
            return metric
    raise AssertionError(f"Metric {metric_id!r} not found in silhouette payload.")


def _write_offset_rectangle(path: Path, *, box: tuple[int, int, int, int]) -> None:
    from PIL import Image, ImageDraw

    image = Image.new("RGBA", (200, 200), (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle(box, fill=(0, 0, 0, 255))
    image.save(path)


def test_silhouette_analysis_bbox_normalizes_shifted_matching_shapes(tmp_path: Path):
    reference_path = tmp_path / "reference.png"
    capture_path = tmp_path / "capture.png"
    _write_offset_rectangle(reference_path, box=(35, 45, 95, 165))
    _write_offset_rectangle(capture_path, box=(95, 20, 155, 140))

    payload = build_silhouette_analysis(
        reference_path=str(reference_path),
        capture_path=str(capture_path),
        reference_label="reference",
        capture_label="capture",
        target_view="front",
    )

    assert payload["status"] == "available"
    assert payload["alignment_mode"] == "bbox_normalized"
    assert _metric(payload, "mask_iou")["observed_value"] > 0.98
    assert _metric(payload, "contour_drift")["observed_value"] < 0.02


def test_silhouette_analysis_returns_unavailable_for_uniform_opaque_images(tmp_path: Path):
    from PIL import Image

    reference_path = tmp_path / "solid_reference.png"
    capture_path = tmp_path / "solid_capture.png"
    Image.new("RGBA", (64, 64), (255, 255, 255, 255)).save(reference_path)
    Image.new("RGBA", (64, 64), (0, 0, 0, 255)).save(capture_path)

    payload = build_silhouette_analysis(
        reference_path=str(reference_path),
        capture_path=str(capture_path),
    )

    assert payload["status"] == "unavailable"
    assert payload["metrics"] == []
    assert any("uniform" in note for note in payload["notes"])
