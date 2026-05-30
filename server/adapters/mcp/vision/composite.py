# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Optional labelled multi-view grid composite (IG-VLM style).

Tiles several capture views into one labelled montage so a model/budget for which
a single annotated image outperforms many separate images can still receive every
view. Deterministic and order-stable; the per-tile caption is the same symbolic
identity string used elsewhere, so the grid stays consistent with the roster.
"""

from __future__ import annotations

from collections.abc import Sequence

# (label, image_path) for one tile of the grid.
GridTile = tuple[str, str]

_TILE_WIDTH = 512
_TILE_HEIGHT = 384
_LABEL_BAND = 28
_BG = (245, 245, 245)
_LABEL_BG = (30, 30, 30)
_LABEL_FG = (255, 255, 255)


def _grid_dimensions(count: int, columns: int | None) -> tuple[int, int]:
    if count <= 0:
        return 0, 0
    cols = columns if columns and columns > 0 else min(count, 2 if count <= 4 else 3)
    rows = (count + cols - 1) // cols
    return cols, rows


def build_labeled_view_grid(
    tiles: Sequence[GridTile],
    output_path: str,
    *,
    columns: int | None = None,
    tile_width: int = _TILE_WIDTH,
    tile_height: int = _TILE_HEIGHT,
) -> str | None:
    """Composite ``tiles`` into one labelled grid image at ``output_path``.

    Each tile is resized into a fixed cell with a label band naming the view.
    Returns ``output_path``, or ``None`` when there are no tiles. Tiles whose
    image cannot be opened are rendered as an empty labelled cell rather than
    aborting the whole grid.
    """

    from PIL import Image, ImageDraw

    usable = [(str(label), str(path)) for label, path in tiles if str(path).strip()]
    if not usable:
        return None

    cols, rows = _grid_dimensions(len(usable), columns)
    cell_w = tile_width
    cell_h = tile_height + _LABEL_BAND
    canvas = Image.new("RGB", (cols * cell_w, rows * cell_h), _BG)
    draw = ImageDraw.Draw(canvas)

    for index, (label, path) in enumerate(usable):
        col = index % cols
        row = index // cols
        x0 = col * cell_w
        y0 = row * cell_h
        # Label band.
        draw.rectangle([x0, y0, x0 + cell_w, y0 + _LABEL_BAND], fill=_LABEL_BG)
        draw.text((x0 + 6, y0 + _LABEL_BAND // 2), label, fill=_LABEL_FG, anchor="lm")
        # Image cell.
        try:
            with Image.open(path) as opened:
                tile_img = opened.convert("RGB").resize((tile_width, tile_height))
            canvas.paste(tile_img, (x0, y0 + _LABEL_BAND))
        except Exception:
            draw.rectangle(
                [x0, y0 + _LABEL_BAND, x0 + cell_w, y0 + cell_h],
                outline=(200, 200, 200),
                width=1,
            )
    canvas.save(output_path)
    return output_path
