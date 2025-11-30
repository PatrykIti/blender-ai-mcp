from typing import List, Optional, Union
from fastmcp import Context
from server.adapters.mcp.instance import mcp
from server.adapters.mcp.utils import parse_coordinate
from server.infrastructure.di import get_lattice_handler


@mcp.tool()
def lattice_create(
    ctx: Context,
    name: str = "Lattice",
    target_object: Optional[str] = None,
    location: Union[str, List[float], None] = None,
    points_u: int = 2,
    points_v: int = 2,
    points_w: int = 2,
    interpolation: str = "KEY_LINEAR",
) -> str:
    """
    [OBJECT MODE][SCENE] Creates a lattice object for non-destructive deformation.

    Lattices provide a cage of control points around an object. Moving these points
    deforms the object smoothly. Perfect for: tapering towers, bending shapes,
    organic deformations.

    If target_object is provided, the lattice is automatically sized and positioned
    to encompass the target's bounding box with a small margin.

    Interpolation types:
        - KEY_LINEAR: Sharp, direct interpolation (default)
        - KEY_CARDINAL: Smooth curves
        - KEY_CATMULL_ROM: Very smooth curves
        - KEY_BSPLINE: Smoothest, most rounded curves

    Workflow: AFTER → lattice_bind(target_object, lattice_name) | lattice_edit_point

    Args:
        name: Name for the lattice object (default "Lattice")
        target_object: If provided, fit lattice to this object's bounds
        location: World position [x, y, z] (ignored if target_object is set)
        points_u: Resolution along U (width) axis, 2-64 (default 2)
        points_v: Resolution along V (depth) axis, 2-64 (default 2)
        points_w: Resolution along W (height) axis, 2-64 (default 2)
        interpolation: KEY_LINEAR, KEY_CARDINAL, KEY_CATMULL_ROM, KEY_BSPLINE

    Examples:
        lattice_create(name="TowerLattice", target_object="Tower", points_w=4)
        lattice_create(name="BendLattice", points_u=2, points_v=2, points_w=6)
    """
    handler = get_lattice_handler()
    try:
        parsed_location = parse_coordinate(location)
        return handler.lattice_create(
            name=name,
            target_object=target_object,
            location=parsed_location,
            points_u=points_u,
            points_v=points_v,
            points_w=points_w,
            interpolation=interpolation,
        )
    except RuntimeError as e:
        return str(e)


@mcp.tool()
def lattice_bind(
    ctx: Context,
    object_name: str,
    lattice_name: str,
    vertex_group: Optional[str] = None,
) -> str:
    """
    [OBJECT MODE][NON-DESTRUCTIVE] Binds an object to a lattice deformer.

    Adds a Lattice modifier to the target object. Moving the lattice's control
    points will deform the bound object. This is non-destructive - removing
    the modifier restores the original shape.

    Use vertex_group to limit which vertices are affected by the deformation.

    Workflow: BEFORE → lattice_create | AFTER → lattice_edit_point (deform)

    Args:
        object_name: Name of the mesh object to deform
        lattice_name: Name of the lattice object to bind to
        vertex_group: Optional vertex group to limit deformation

    Examples:
        lattice_bind(object_name="Tower", lattice_name="TowerLattice")
        lattice_bind(object_name="Character", lattice_name="BendLattice", vertex_group="Torso")
    """
    handler = get_lattice_handler()
    try:
        return handler.lattice_bind(
            object_name=object_name,
            lattice_name=lattice_name,
            vertex_group=vertex_group,
        )
    except RuntimeError as e:
        return str(e)


@mcp.tool()
def lattice_edit_point(
    ctx: Context,
    lattice_name: str,
    point_index: Union[int, List[int]],
    offset: Union[str, List[float]],
    relative: bool = True,
) -> str:
    """
    [OBJECT MODE] Moves lattice control points to deform bound objects.

    Lattice points are indexed in U → V → W order (fastest to slowest varying).
    For a 2x2x4 lattice (16 points), bottom layer is 0-3, top layer is 12-15.

    Point index calculation: index = u + (v * points_u) + (w * points_u * points_v)

    Use case - Taper a tower:
        1. Create 2x2x4 lattice around tower
        2. Move top 4 points inward: lattice_edit_point(name, [12,13,14,15], [-0.3,-0.3,0])

    Workflow: BEFORE → lattice_create, lattice_bind | RESULT → object deformation

    Args:
        lattice_name: Name of the lattice object
        point_index: Single index or list of indices (0-based)
        offset: [x, y, z] offset (if relative=True) or absolute position (if relative=False)
        relative: True = offset from current position, False = set absolute position

    Examples:
        lattice_edit_point("TowerLattice", point_index=[12,13,14,15], offset=[-0.3,-0.3,0])
        lattice_edit_point("BendLattice", point_index=7, offset=[0,0,0.5])
    """
    handler = get_lattice_handler()
    try:
        parsed_offset = parse_coordinate(offset)
        return handler.lattice_edit_point(
            lattice_name=lattice_name,
            point_index=point_index,
            offset=parsed_offset,
            relative=relative,
        )
    except RuntimeError as e:
        return str(e)
