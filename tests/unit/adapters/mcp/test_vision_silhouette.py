"""Focused regression tests for deterministic silhouette analysis."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from server.adapters.mcp.areas.reference_silhouette import (
    build_action_hints_from_silhouette,
    build_compare_support_evidence,
    build_silhouette_analysis_payload,
)
from server.adapters.mcp.contracts.reference import (
    ReferenceImageRecordContract,
    ReferencePerObjectSilhouetteMetricContract,
    ReferenceSilhouetteAnalysisContract,
)
from server.adapters.mcp.contracts.vision import VisionCaptureImageContract, VisionObjectIdCaptureArtifactContract
from server.adapters.mcp.vision.silhouette import (
    build_silhouette_analysis,
    compute_iou_convergence,
    compute_per_object_iou,
    compute_silhouette_iou,
)


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


def _write_object_id_rectangles(path: Path) -> None:
    from PIL import Image, ImageDraw

    image = Image.new("L", (200, 200), 0)
    draw = ImageDraw.Draw(image)
    draw.rectangle((30, 40, 90, 160), fill=128)
    draw.rectangle((120, 40, 180, 160), fill=255)
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


def test_compute_per_object_iou_decodes_object_id_band(tmp_path: Path):
    reference = tmp_path / "reference.png"
    object_id = tmp_path / "object_id.png"
    _write_offset_rectangle(reference, box=(35, 45, 95, 165))
    _write_object_id_rectangles(object_id)

    result = compute_per_object_iou(
        reference_path=str(reference),
        object_id_path=str(object_id),
        index_map={1: "Head", 2: "Body"},
        object_name="Head",
    )

    assert result["status"] == "available"
    assert result["object_index"] == 1
    assert result["mask_iou"] is not None
    assert result["mask_iou"] > 0.98
    assert result["severity"] == "low"


def test_compute_per_object_iou_reports_missing_index_map_entry(tmp_path: Path):
    reference = tmp_path / "reference.png"
    object_id = tmp_path / "object_id.png"
    _write_offset_rectangle(reference, box=(35, 45, 95, 165))
    _write_object_id_rectangles(object_id)

    result = compute_per_object_iou(
        reference_path=str(reference),
        object_id_path=str(object_id),
        index_map={"1": "Head"},
        object_name="Tail",
    )

    assert result["status"] == "unavailable"
    assert result["mask_iou"] is None
    assert any("Tail" in note for note in result["notes"])


def test_silhouette_payload_populates_per_object_metrics_from_capture_side_object_id(tmp_path: Path):
    reference = tmp_path / "reference.png"
    capture = tmp_path / "capture.png"
    object_id = tmp_path / "object_id.png"
    _write_offset_rectangle(reference, box=(35, 45, 95, 165))
    _write_offset_rectangle(capture, box=(35, 45, 95, 165))
    _write_object_id_rectangles(object_id)

    payload = build_silhouette_analysis_payload(
        selected_reference_records=[
            ReferenceImageRecordContract(
                reference_id="ref_front",
                goal="match head",
                media_type="image/png",
                original_path=str(reference),
                stored_path=str(reference),
                added_at="2026-03-26T00:00:00Z",
                label="reference_front",
            )
        ],
        captures=[
            VisionCaptureImageContract(
                label="target_front_after",
                image_path=str(capture),
                preset_name="target_front",
                view_kind="focus",
                object_id_artifact=VisionObjectIdCaptureArtifactContract(
                    image_path=str(object_id),
                    index_map={1: "Head", 2: "Body"},
                ),
            )
        ],
        target_view="front",
        target_objects=["Head", "Tail"],
    )

    assert payload is not None
    metrics = {metric.object_name: metric for metric in payload.per_object_metrics}
    assert metrics["Head"].status == "available"
    assert metrics["Head"].mask_iou is not None
    assert metrics["Head"].mask_iou > 0.98
    assert metrics["Tail"].status == "unavailable"
    assert any("capture-side object-ID mask" in note for note in metrics["Head"].notes)


def test_silhouette_payload_keeps_unavailable_per_object_metric_for_failed_object_id(tmp_path: Path):
    reference = tmp_path / "reference.png"
    capture = tmp_path / "capture.png"
    _write_offset_rectangle(reference, box=(35, 45, 95, 165))
    _write_offset_rectangle(capture, box=(35, 45, 95, 165))

    payload = build_silhouette_analysis_payload(
        selected_reference_records=[
            ReferenceImageRecordContract(
                reference_id="ref_front",
                goal="match head",
                media_type="image/png",
                original_path=str(reference),
                stored_path=str(reference),
                added_at="2026-03-26T00:00:00Z",
            )
        ],
        captures=[
            VisionCaptureImageContract(
                label="target_front_after",
                image_path=str(capture),
                preset_name="target_front",
                view_kind="focus",
                object_id_artifact=VisionObjectIdCaptureArtifactContract(
                    capture_ok=False,
                    capture_warning="No camera available for object-ID pass.",
                ),
            )
        ],
        target_view="front",
        target_objects=["Head"],
    )

    assert payload is not None
    assert len(payload.per_object_metrics) == 1
    metric = payload.per_object_metrics[0]
    assert metric.object_name == "Head"
    assert metric.status == "unavailable"
    assert metric.mask_iou is None
    assert any("No camera available" in note for note in metric.notes)


def test_compare_support_evidence_projects_per_object_iou():
    analysis = ReferenceSilhouetteAnalysisContract(
        status="available",
        reference_label="reference",
        capture_label="capture",
        target_view="front",
        per_object_metrics=[
            ReferencePerObjectSilhouetteMetricContract(
                object_name="Head",
                object_index=1,
                status="available",
                mask_iou=0.42,
                severity="high",
            )
        ],
    )

    evidence = build_compare_support_evidence(analysis)

    assert any(
        item.evidence_kind == "per_object_iou"
        and item.part_label == "Head"
        and item.observed_value == 0.42
        and "Capture-side Object-ID IoU" in item.summary
        for item in evidence
    )


def test_compute_iou_convergence_classifies_direction():
    assert compute_iou_convergence(0.5, 0.7)["verdict"] == "improved"
    assert compute_iou_convergence(0.7, 0.5)["verdict"] == "regressed"
    assert compute_iou_convergence(0.50, 0.505)["verdict"] == "stalled"
    improved = compute_iou_convergence(0.5, 0.7)
    assert improved["status"] == "ok"
    assert abs(improved["delta"] - 0.2) < 1e-9


def test_compute_iou_convergence_unavailable_for_missing_values():
    out = compute_iou_convergence(None, 0.7)
    assert out["status"] == "unavailable"
    assert out["verdict"] == "unknown"
    assert out["delta"] is None


def test_silhouette_analysis_drops_dead_band_metrics(tmp_path: Path):
    reference_path = tmp_path / "reference.png"
    capture_path = tmp_path / "capture.png"
    _write_offset_rectangle(reference_path, box=(35, 45, 95, 165))
    _write_offset_rectangle(capture_path, box=(95, 20, 155, 140))
    payload = build_silhouette_analysis(reference_path=str(reference_path), capture_path=str(capture_path))
    metric_ids = {metric["metric_id"] for metric in payload["metrics"]}
    # The unconsumed band metrics are no longer emitted; the consumed ones remain.
    assert "mid_band_width_delta" not in metric_ids
    assert "lower_band_width_delta" not in metric_ids
    assert {"mask_iou", "upper_band_width_delta", "left_projection_delta", "right_projection_delta"} <= metric_ids


def test_aspect_ratio_delta_is_normalized_relative_fraction(tmp_path: Path):
    reference_path = tmp_path / "reference.png"
    capture_path = tmp_path / "capture.png"
    # Reference is square-ish (ar ~1.0); capture is twice as tall (ar ~2.0).
    _write_offset_rectangle(reference_path, box=(60, 60, 140, 140))
    _write_offset_rectangle(capture_path, box=(80, 20, 120, 180))
    payload = build_silhouette_analysis(reference_path=str(reference_path), capture_path=str(capture_path))
    aspect = _metric(payload, "aspect_ratio_delta")
    # Normalized relative fraction ~ +1.0 (100% taller), bounded near the [0,1] band scale.
    assert aspect["delta"] > 0.5
    assert aspect["severity"] == "high"
