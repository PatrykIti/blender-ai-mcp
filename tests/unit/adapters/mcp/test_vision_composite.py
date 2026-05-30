"""Tests for the optional labelled multi-view grid composite."""

from __future__ import annotations

from pathlib import Path

from server.adapters.mcp.vision.composite import build_labeled_view_grid


def _write_img(path: Path, color: tuple[int, int, int]) -> None:
    from PIL import Image

    Image.new("RGB", (100, 80), color).save(path)


def test_build_labeled_view_grid_tiles_views(tmp_path: Path):
    from PIL import Image

    front = tmp_path / "front.png"
    side = tmp_path / "side.png"
    _write_img(front, (10, 20, 30))
    _write_img(side, (40, 50, 60))
    out = tmp_path / "grid.png"

    result = build_labeled_view_grid(
        [("front", str(front)), ("side", str(side))],
        str(out),
        tile_width=120,
        tile_height=90,
    )
    assert result == str(out)
    with Image.open(out) as grid:
        # Two tiles, default 2 columns -> 1 row; width = 2*120, height = 90 + label band.
        assert grid.size[0] == 2 * 120
        assert grid.size[1] == 90 + 28


def test_build_labeled_view_grid_returns_none_for_no_tiles(tmp_path: Path):
    assert build_labeled_view_grid([], str(tmp_path / "x.png")) is None
    assert build_labeled_view_grid([("front", "  ")], str(tmp_path / "x.png")) is None


def test_build_labeled_view_grid_survives_unreadable_tile(tmp_path: Path):
    from PIL import Image

    good = tmp_path / "good.png"
    _write_img(good, (0, 0, 0))
    out = tmp_path / "grid.png"
    # A missing path renders an empty cell instead of aborting.
    result = build_labeled_view_grid(
        [("front", str(good)), ("side", str(tmp_path / "missing.png"))],
        str(out),
        tile_width=100,
        tile_height=80,
    )
    assert result == str(out)
    with Image.open(out) as grid:
        assert grid.size[0] == 2 * 100
