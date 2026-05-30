"""Focused regression tests for deterministic silhouette analysis."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from server.adapters.mcp.areas.reference_silhouette import (
    build_action_hints_from_silhouette,
    build_compare_support_evidence,
)
from server.adapters.mcp.contracts.reference import ReferenceSilhouetteAnalysisContract
from server.adapters.mcp.vision.silhouette import build_silhouette_analysis, compute_silhouette_iou


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


def test_compare_support_evidence_projects_metric_and_hint_summaries(tmp_path: Path):
    reference_path = tmp_path / "reference.png"
    capture_path = tmp_path / "capture.png"
    _write_offset_rectangle(reference_path, box=(35, 45, 95, 165))
    _write_offset_rectangle(capture_path, box=(35, 45, 70, 165))

    payload = build_silhouette_analysis(
        reference_path=str(reference_path),
        capture_path=str(capture_path),
        reference_label="reference",
        capture_label="capture",
        target_view="front",
    )
    analysis = ReferenceSilhouetteAnalysisContract.model_validate(payload)
    hints = build_action_hints_from_silhouette(analysis, target_object="Creature")
    evidence = build_compare_support_evidence(analysis, action_hints=hints)

    assert evidence
    assert any(
        item.evidence_kind == "silhouette_metric" and ("Silhouette overlap" in item.summary or "delta" in item.summary)
        for item in evidence
    )
    assert any(item.evidence_kind == "action_hint" for item in evidence)


def _write_triangle(path: Path, *, points) -> None:
    from PIL import Image, ImageDraw

    image = Image.new("RGBA", (200, 200), (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.polygon(points, fill=(0, 0, 0, 255))
    image.save(path)


def test_compute_silhouette_iou_identical_masks_is_one(tmp_path: Path):
    a = tmp_path / "a.png"
    b = tmp_path / "b.png"
    _write_offset_rectangle(a, box=(35, 45, 95, 165))
    # Same shape, different position/size -> bbox-normalized IoU is 1.0.
    _write_offset_rectangle(b, box=(100, 20, 180, 180))
    iou = compute_silhouette_iou(str(a), str(b))
    assert iou is not None
    assert iou > 0.98


def test_compute_silhouette_iou_box_vs_triangle_is_partial(tmp_path: Path):
    box = tmp_path / "box.png"
    tri = tmp_path / "tri.png"
    _write_offset_rectangle(box, box=(40, 40, 160, 160))
    _write_triangle(tri, points=[(40, 160), (160, 160), (100, 40)])
    iou = compute_silhouette_iou(str(box), str(tri))
    assert iou is not None
    # A triangle fills roughly half its bbox, so IoU against a full box is partial.
    assert 0.3 < iou < 0.8


def test_compute_silhouette_iou_returns_none_for_blank_image(tmp_path: Path):
    from PIL import Image

    blank = tmp_path / "blank.png"
    Image.new("RGBA", (200, 200), (255, 255, 255, 255)).save(blank)
    box = tmp_path / "box.png"
    _write_offset_rectangle(box, box=(40, 40, 160, 160))
    # A uniform image yields no usable foreground mask.
    assert compute_silhouette_iou(str(blank), str(box)) is None
