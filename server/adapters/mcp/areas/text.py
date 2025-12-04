from typing import List, Literal, Optional
from fastmcp import Context
from server.adapters.mcp.instance import mcp
from server.adapters.mcp.router_helper import route_tool_call
from server.infrastructure.di import get_text_handler


# ==============================================================================
# TASK-034: Text & Annotations
# ==============================================================================

@mcp.tool()
def text_create(
    ctx: Context,
    text: str = "Text",
    name: str = "Text",
    location: Optional[List[float]] = None,
    font: Optional[str] = None,
    size: float = 1.0,
    extrude: float = 0.0,
    bevel_depth: float = 0.0,
    bevel_resolution: int = 0,
    align_x: Literal["LEFT", "CENTER", "RIGHT", "JUSTIFY", "FLUSH"] = "LEFT",
    align_y: Literal["TOP", "TOP_BASELINE", "MIDDLE", "BOTTOM_BASELINE", "BOTTOM"] = "BOTTOM_BASELINE",
) -> str:
    """
    [OBJECT MODE][SCENE] Creates a 3D text object.

    Text objects are curve-based and support extrusion, beveling, and font customization.
    Can be converted to mesh for game export or boolean operations.

    Workflow: AFTER -> text_to_mesh (for game export) | modeling_add_modifier

    Args:
        text: The text content to display (default "Text")
        name: Name for the text object (default "Text")
        location: Optional [x, y, z] position. Default is [0, 0, 0].
        font: Path to .ttf/.otf font file (None uses Blender's default font)
        size: Text size in Blender units (default 1.0)
        extrude: Depth/extrusion amount for 3D effect (default 0.0 = flat)
        bevel_depth: Bevel depth for rounded edges (default 0.0)
        bevel_resolution: Bevel resolution/segments (default 0)
        align_x: Horizontal alignment (LEFT, CENTER, RIGHT, JUSTIFY, FLUSH)
        align_y: Vertical alignment (TOP, TOP_BASELINE, MIDDLE, BOTTOM_BASELINE, BOTTOM)

    Examples:
        text_create(text="Hello World") -> Creates flat text at origin
        text_create(text="3D", extrude=0.2, bevel_depth=0.02) -> 3D extruded text with bevel
        text_create(text="EXIT", size=2.0, align_x="CENTER") -> Centered sign text
    """
    def execute():
        handler = get_text_handler()
        try:
            return handler.create(
                text=text,
                name=name,
                location=location,
                font=font,
                size=size,
                extrude=extrude,
                bevel_depth=bevel_depth,
                bevel_resolution=bevel_resolution,
                align_x=align_x,
                align_y=align_y,
            )
        except RuntimeError as e:
            return str(e)

    return route_tool_call(
        tool_name="text_create",
        params={
            "text": text,
            "name": name,
            "location": location,
            "font": font,
            "size": size,
            "extrude": extrude,
            "bevel_depth": bevel_depth,
            "bevel_resolution": bevel_resolution,
            "align_x": align_x,
            "align_y": align_y,
        },
        direct_executor=execute
    )


@mcp.tool()
def text_edit(
    ctx: Context,
    object_name: str,
    text: Optional[str] = None,
    size: Optional[float] = None,
    extrude: Optional[float] = None,
    bevel_depth: Optional[float] = None,
    bevel_resolution: Optional[int] = None,
    align_x: Optional[Literal["LEFT", "CENTER", "RIGHT", "JUSTIFY", "FLUSH"]] = None,
    align_y: Optional[Literal["TOP", "TOP_BASELINE", "MIDDLE", "BOTTOM_BASELINE", "BOTTOM"]] = None,
) -> str:
    """
    [OBJECT MODE][NON-DESTRUCTIVE] Edits an existing text object's properties.

    Only provided parameters are modified; others remain unchanged.
    Object must be of type 'FONT' (text object).

    Workflow: BEFORE -> text_create | AFTER -> text_to_mesh

    Args:
        object_name: Name of the text object to edit
        text: New text content (None = keep current)
        size: New text size (None = keep current)
        extrude: New extrusion depth (None = keep current)
        bevel_depth: New bevel depth (None = keep current)
        bevel_resolution: New bevel resolution (None = keep current)
        align_x: New horizontal alignment (None = keep current)
        align_y: New vertical alignment (None = keep current)

    Examples:
        text_edit(object_name="Text", text="New Content") -> Changes text content
        text_edit(object_name="Sign", extrude=0.5, bevel_depth=0.05) -> Adds 3D depth
        text_edit(object_name="Label", align_x="CENTER") -> Centers text
    """
    def execute():
        handler = get_text_handler()
        try:
            return handler.edit(
                object_name=object_name,
                text=text,
                size=size,
                extrude=extrude,
                bevel_depth=bevel_depth,
                bevel_resolution=bevel_resolution,
                align_x=align_x,
                align_y=align_y,
            )
        except RuntimeError as e:
            return str(e)

    return route_tool_call(
        tool_name="text_edit",
        params={
            "object_name": object_name,
            "text": text,
            "size": size,
            "extrude": extrude,
            "bevel_depth": bevel_depth,
            "bevel_resolution": bevel_resolution,
            "align_x": align_x,
            "align_y": align_y,
        },
        direct_executor=execute
    )


@mcp.tool()
def text_to_mesh(
    ctx: Context,
    object_name: str,
    keep_original: bool = False,
) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Converts a text object to mesh geometry.

    Required for:
    - Game engine export (text objects don't export directly)
    - Mesh editing operations (extrude, bevel individual letters)
    - Boolean operations with other meshes

    Note: Also available via modeling_convert_to_mesh which handles all curve types.

    Workflow: BEFORE -> text_create | AFTER -> mesh_* tools, export_*

    Args:
        object_name: Name of the text object to convert
        keep_original: If True, duplicates before converting (keeps original text object)

    Examples:
        text_to_mesh(object_name="Logo") -> Converts text to mesh (destroys original)
        text_to_mesh(object_name="Sign", keep_original=True) -> Keeps text, creates mesh copy
    """
    def execute():
        handler = get_text_handler()
        try:
            return handler.to_mesh(
                object_name=object_name,
                keep_original=keep_original,
            )
        except RuntimeError as e:
            return str(e)

    return route_tool_call(
        tool_name="text_to_mesh",
        params={
            "object_name": object_name,
            "keep_original": keep_original,
        },
        direct_executor=execute
    )
