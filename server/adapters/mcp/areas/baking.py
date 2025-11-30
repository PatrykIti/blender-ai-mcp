"""
Adapter Layer: Baking MCP Tools

Exposes texture baking operations as MCP tools for AI models.
"""

from typing import Optional
from fastmcp import Context

from server.adapters.mcp.instance import mcp
from server.infrastructure.di import get_baking_handler


@mcp.tool()
def bake_normal_map(
    ctx: Context,
    object_name: str,
    output_path: str,
    resolution: int = 1024,
    high_poly_source: Optional[str] = None,
    cage_extrusion: float = 0.1,
    margin: int = 16,
    normal_space: str = "TANGENT"
) -> str:
    """
    [OBJECT MODE][REQUIRES UV][CYCLES] Bakes normal map to texture file.

    Normal maps encode surface detail as RGB values, allowing low-poly meshes
    to appear detailed without extra geometry. Essential for game assets.

    Baking Modes:
    - Self-bake (high_poly_source=None): Bakes from object's own geometry
    - High-to-low (high_poly_source set): Transfers detail from high-poly source

    Args:
        object_name: Target low-poly object to bake onto (must have UV map)
        output_path: File path to save the baked image (PNG/EXR supported)
        resolution: Image resolution in pixels (default 1024x1024)
        high_poly_source: Optional high-poly object name for detail transfer
        cage_extrusion: Ray distance for high-to-low baking (default 0.1)
        margin: Pixel margin for UV island bleeding (default 16)
        normal_space: "TANGENT" (most common) or "OBJECT" space

    Requirements:
    - Object must have UV map (use uv_unwrap first)
    - Cycles renderer will be temporarily enabled
    - Material with image texture node auto-created if missing

    Workflow: BEFORE → uv_unwrap | AFTER → material_set_texture(input_name="Normal")

    Example:
    - Self-bake: bake_normal_map("LowPoly_Mesh", "/tmp/normal.png")
    - High-to-low: bake_normal_map("LowPoly", "/tmp/normal.png", high_poly_source="HighPoly_Sculpt")
    """
    handler = get_baking_handler()
    return handler.bake_normal_map(
        object_name=object_name,
        output_path=output_path,
        resolution=resolution,
        high_poly_source=high_poly_source,
        cage_extrusion=cage_extrusion,
        margin=margin,
        normal_space=normal_space
    )


@mcp.tool()
def bake_ao(
    ctx: Context,
    object_name: str,
    output_path: str,
    resolution: int = 1024,
    samples: int = 128,
    distance: float = 1.0,
    margin: int = 16
) -> str:
    """
    [OBJECT MODE][REQUIRES UV][CYCLES] Bakes ambient occlusion map to texture file.

    AO maps capture how much ambient light reaches each surface point.
    Dark areas indicate crevices/corners where light is occluded.
    Essential for adding depth and realism without runtime cost.

    Args:
        object_name: Target object to bake (must have UV map)
        output_path: File path to save the baked image (PNG recommended)
        resolution: Image resolution in pixels (default 1024x1024)
        samples: Number of samples for quality (higher = better but slower)
        distance: Maximum ray distance for occlusion calculation
        margin: Pixel margin for UV island bleeding (default 16)

    Use Cases:
    - Game assets (multiply with diffuse texture)
    - Architectural visualization
    - Detail enhancement for stylized art

    Workflow: BEFORE → uv_unwrap | AFTER → Use in game engine as AO multiply

    Tip: For clean AO, ensure mesh has no overlapping geometry.
    """
    handler = get_baking_handler()
    return handler.bake_ao(
        object_name=object_name,
        output_path=output_path,
        resolution=resolution,
        samples=samples,
        distance=distance,
        margin=margin
    )


@mcp.tool()
def bake_combined(
    ctx: Context,
    object_name: str,
    output_path: str,
    resolution: int = 1024,
    samples: int = 128,
    margin: int = 16,
    use_pass_direct: bool = True,
    use_pass_indirect: bool = True,
    use_pass_color: bool = True
) -> str:
    """
    [OBJECT MODE][REQUIRES UV][CYCLES] Bakes combined render to texture file.

    Captures the full rendered appearance including materials and lighting
    into a single texture. Useful for lightmaps and pre-baked effects.

    Args:
        object_name: Target object to bake (must have UV map)
        output_path: File path to save the baked image
        resolution: Image resolution in pixels (default 1024x1024)
        samples: Number of render samples (higher = less noise)
        margin: Pixel margin for UV island bleeding (default 16)
        use_pass_direct: Include direct lighting contribution
        use_pass_indirect: Include indirect/bounced lighting
        use_pass_color: Include diffuse color from materials

    Use Cases:
    - Lightmaps for static lighting in games
    - Mobile game optimization (pre-baked lighting)
    - Texture atlases with baked effects

    Note: Ensure scene has proper lighting setup before baking.
    """
    handler = get_baking_handler()
    return handler.bake_combined(
        object_name=object_name,
        output_path=output_path,
        resolution=resolution,
        samples=samples,
        margin=margin,
        use_pass_direct=use_pass_direct,
        use_pass_indirect=use_pass_indirect,
        use_pass_color=use_pass_color
    )


@mcp.tool()
def bake_diffuse(
    ctx: Context,
    object_name: str,
    output_path: str,
    resolution: int = 1024,
    margin: int = 16
) -> str:
    """
    [OBJECT MODE][REQUIRES UV][CYCLES] Bakes diffuse/albedo color to texture file.

    Captures only the base color from materials without any lighting.
    Useful for converting procedural materials to static textures.

    Args:
        object_name: Target object to bake (must have UV map)
        output_path: File path to save the baked image
        resolution: Image resolution in pixels (default 1024x1024)
        margin: Pixel margin for UV island bleeding (default 16)

    Use Cases:
    - Converting procedural Blender materials to game-ready textures
    - Creating texture atlases
    - Exporting materials for other software

    Note: Only captures color, not lighting. For full appearance use bake_combined.
    """
    handler = get_baking_handler()
    return handler.bake_diffuse(
        object_name=object_name,
        output_path=output_path,
        resolution=resolution,
        margin=margin
    )
