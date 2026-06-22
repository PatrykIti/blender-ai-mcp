"""Tests for deterministic Set-of-Mark overlay helpers."""

from __future__ import annotations

from pathlib import Path

from server.adapters.mcp.vision.marks import (
    build_marks_from_object_masks,
    build_projection_mark_anchors,
    mask_centroid,
    overlay_numbered_marks,
)


def _rgb_at(image, x: int, y: int) -> tuple[int, int, int]:
    pixel = image.getpixel((x, y))
    assert isinstance(pixel, tuple)
    return int(pixel[0]), int(pixel[1]), int(pixel[2])


def _write_filled_rect(path: Path, *, box: tuple[int, int, int, int]) -> None:
    from PIL import Image, ImageDraw

    image = Image.new("RGBA", (200, 200), (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle(box, fill=(0, 0, 0, 255))
    image.save(path)


def _write_blank(path: Path) -> None:
    from PIL import Image

    Image.new("RGBA", (200, 200), (255, 255, 255, 255)).save(path)


def test_mask_centroid_of_centered_rectangle(tmp_path: Path):
    path = tmp_path / "mask.png"
    _write_filled_rect(path, box=(60, 80, 140, 120))  # center ~ (100, 100)
    centroid = mask_centroid(str(path))
    assert centroid is not None
    x, y = centroid
    assert abs(x - 100) <= 2
    assert abs(y - 100) <= 2


def test_mask_centroid_none_for_blank(tmp_path: Path):
    path = tmp_path / "blank.png"
    _write_blank(path)
    assert mask_centroid(str(path)) is None


def test_overlay_numbered_marks_draws_red_marks(tmp_path: Path):
    from PIL import Image

    base = tmp_path / "base.png"
    Image.new("RGB", (200, 200), (255, 255, 255)).save(base)
    out = tmp_path / "out.png"
    overlay_numbered_marks(str(base), [(1, 50, 50), (2, 150, 150)], str(out))

    with Image.open(out) as result:
        rgb = result.convert("RGB")
        # The disc fill is red off-center (the exact center holds the white id).
        for cx, cy in ((50, 50), (150, 150)):
            r, g, b = _rgb_at(rgb, cx + 8, cy)
            assert r > 150 and g < 120 and b < 120, f"expected a red mark near ({cx},{cy}), got {(r, g, b)}"
        # A far corner stays white (marks are local).
        assert _rgb_at(rgb, 5, 5) == (255, 255, 255)


def test_build_marks_from_object_masks_assigns_stable_sorted_ids(tmp_path: Path):
    body = tmp_path / "body.png"
    head = tmp_path / "head.png"
    empty = tmp_path / "empty.png"
    _write_filled_rect(body, box=(20, 20, 80, 80))
    _write_filled_rect(head, box=(120, 120, 180, 180))
    _write_blank(empty)

    marks, mapping = build_marks_from_object_masks({"Head": str(head), "Body": str(body), "Tail": str(empty)})
    # 1-based ids in sorted object-name order; the empty-mask object is skipped.
    assert mapping == {1: "Body", 2: "Head"}
    assert [mark_id for mark_id, _x, _y in marks] == [1, 2]
    # Body mark sits in the Body mask region (top-left), Head in bottom-right.
    body_mark = next(m for m in marks if m[0] == 1)
    head_mark = next(m for m in marks if m[0] == 2)
    assert body_mark[1] < head_mark[1] and body_mark[2] < head_mark[2]


def test_build_marks_from_object_masks_preserves_ids_for_unmarked_objects(tmp_path: Path):
    body = tmp_path / "body.png"
    head = tmp_path / "head.png"
    _write_blank(body)
    _write_filled_rect(head, box=(120, 120, 180, 180))

    marks, mapping = build_marks_from_object_masks({"Head": str(head), "Body": str(body)})

    assert mapping == {2: "Head"}
    assert [mark_id for mark_id, _x, _y in marks] == [2]


def test_build_projection_mark_anchors_prefers_center_and_visible_extent():
    anchors = build_projection_mark_anchors(
        {
            "targets": [
                {
                    "object_name": "Body",
                    "visibility_verdict": "visible",
                    "projection_status": "projected",
                    "projection": {"projected_center": {"x": 0.25, "y": 0.75}},
                },
                {
                    "object_name": "Head",
                    "visibility_verdict": "partially_visible",
                    "projection_status": "projected",
                    "projection": {
                        "projected_center": {"x": 1.4, "y": 0.2},
                        "projected_extent": {"min_x": 0.6, "min_y": 0.2, "max_x": 0.8, "max_y": 0.4},
                    },
                },
            ]
        },
        object_names=["Head", "Body"],
        width=200,
        height=100,
        mark_id_map={"Body": 4, "Head": 9},
    )

    assert [(item.mark_id, item.object_name, item.point, item.anchor_status) for item in anchors] == [
        (4, "Body", (50, 25), "projected"),
        (9, "Head", (139, 69), "projected"),
    ]


def test_build_projection_mark_anchors_reports_non_projectable_states():
    anchors = build_projection_mark_anchors(
        {
            "targets": [
                {"object_name": "Body", "visibility_verdict": "outside_frame", "projection_status": "outside_frame"},
                {"object_name": "Head", "visibility_verdict": "outside_frame", "projection_status": "behind_view"},
                {"object_name": "Tail", "visibility_verdict": "fully_occluded", "projection_status": "projected"},
            ]
        },
        object_names=["Body", "Head", "Tail", "Ear"],
        width=200,
        height=100,
    )

    status_by_object = {item.object_name: item.anchor_status for item in anchors}
    assert status_by_object == {
        "Body": "outside_frame",
        "Ear": "unavailable",
        "Head": "behind_view",
        "Tail": "occluded",
    }
    assert all(item.point is None for item in anchors)


class _MaskHandler:
    """Mock scene handler whose isolated render places the object's silhouette at a
    distinct position, so per-object centroids differ."""

    def __init__(self) -> None:
        self.isolated: str | None = None
        self.view_calls: list[str] = []
        self._boxes = {"Body": (20, 20, 80, 80), "Head": (120, 120, 180, 180)}

    def isolate_object(self, names):
        self.isolated = names[0]

    def set_standard_view(self, view_name):
        self.view_calls.append(view_name)

    def get_viewport(self, width=1280, height=960, shading="SOLID", camera_name=None, focus_target=None):
        import base64
        import io

        from PIL import Image, ImageDraw

        img = Image.new("RGBA", (200, 200), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.rectangle(self._boxes.get(self.isolated, (90, 90, 110, 110)), fill=(0, 0, 0, 255))
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("ascii")


def test_build_object_mark_overlay_orchestrates_isolated_renders(tmp_path: Path):
    from PIL import Image
    from server.adapters.mcp.vision.marks import build_object_mark_overlay

    base = tmp_path / "base.png"
    Image.new("RGB", (200, 200), (255, 255, 255)).save(base)
    out = tmp_path / "overlay.png"
    handler = _MaskHandler()

    overlay_path, mapping = build_object_mark_overlay(
        handler,
        object_names=["Head", "Body"],
        base_image_path=str(base),
        output_path=str(out),
        output_dir=str(tmp_path),
        view_name="FRONT",
    )

    assert overlay_path == str(out)
    # Stable 1-based ids in sorted object order.
    assert mapping == {1: "Body", 2: "Head"}
    # Each object was isolated and rendered from the requested shared view.
    assert handler.view_calls == ["FRONT", "FRONT"]
    # A red mark exists in each object's region of the overlay.
    with Image.open(out) as result:
        rgb = result.convert("RGB")
        # Body centroid ~ (50,50), Head centroid ~ (150,150); check near them.
        for cx, cy in ((50, 50), (150, 150)):
            assert any(_rgb_at(rgb, cx + dx, cy)[0] > 150 and _rgb_at(rgb, cx + dx, cy)[1] < 120 for dx in (-8, 8))


def test_build_object_mark_overlay_returns_none_when_no_masks(tmp_path: Path):
    from PIL import Image
    from server.adapters.mcp.vision.marks import build_object_mark_overlay

    base = tmp_path / "base.png"
    Image.new("RGB", (200, 200), (255, 255, 255)).save(base)

    class _EmptyHandler(_MaskHandler):
        def get_viewport(self, width=1280, height=960, shading="SOLID", camera_name=None, focus_target=None):
            import base64
            import io

            from PIL import Image as _Image

            buffer = io.BytesIO()
            _Image.new("RGBA", (200, 200), (255, 255, 255, 255)).save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue()).decode("ascii")

    overlay_path, mapping = build_object_mark_overlay(
        _EmptyHandler(),
        object_names=["Head", "Body"],
        base_image_path=str(base),
        output_path=str(tmp_path / "overlay.png"),
        output_dir=str(tmp_path),
    )
    assert overlay_path is None
    assert mapping == {}


def test_build_mark_correspondence_table_resolves_and_guards():
    from server.adapters.mcp.vision.marks import build_mark_correspondence_table

    mark_id_to_object = {1: "Body", 2: "Head"}
    findings = [
        {"finding": "head too wide", "mark_id": 2, "target_label": "head"},
        {"finding": "body too narrow", "mark_id": 1},
        {"finding": "ghost", "mark_id": 9},  # non-existent mark -> validity warning
        {"finding": "no mark here"},  # no mark_id -> ignored by the table
    ]
    rows, warnings = build_mark_correspondence_table(findings, mark_id_to_object)

    assert [(r["mark_id"], r["object_name"]) for r in rows] == [(2, "Head"), (1, "Body")]
    assert any("mark id 9" in w for w in warnings)
    assert len(warnings) == 1
