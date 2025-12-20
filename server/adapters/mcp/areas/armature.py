"""
MCP Adapter for Armature Tools.

TASK-037: Armature & Rigging
Exposes armature tools via FastMCP.
"""

from typing import Literal
from mcp.server.fastmcp import Context

from server.adapters.mcp.registry import mcp
from server.adapters.mcp.router_helper import route_tool_call
from server.infrastructure.di import get_armature_handler


def get_handler():
    """Get armature handler instance."""
    return get_armature_handler()


@mcp.tool()
def armature_create(
    ctx: Context,
    name: str = "Armature",
    location: list[float] | None = None,
    bone_name: str = "Bone",
    bone_length: float = 1.0
) -> str:
    """[OBJECT MODE][SCENE] Creates armature with initial bone.

    Armature is a skeleton structure for deforming meshes.
    Essential for character animation, mechanical rigs, and procedural motion.

    After creation, add more bones with armature_add_bone, then bind mesh
    with armature_bind.

    Workflow: AFTER -> armature_add_bone | armature_bind

    Args:
        name: Name for the armature object (default "Armature")
        location: World position [x, y, z] (default origin)
        bone_name: Name for the initial bone (default "Bone")
        bone_length: Length of the initial bone in Blender units (default 1.0)

    Examples:
        armature_create(name="CharacterRig") -> Simple rig at origin
        armature_create(name="Spine", bone_name="Root", bone_length=0.5) -> Custom bone
    """
    handler = get_handler()
    return handler.create(
        name=name,
        location=location,
        bone_name=bone_name,
        bone_length=bone_length
    )


@mcp.tool()
def armature_add_bone(
    ctx: Context,
    armature_name: str,
    bone_name: str,
    head: list[float],
    tail: list[float],
    parent_bone: str | None = None,
    use_connect: bool = False
) -> str:
    """[EDIT MODE on armature] Adds bone to armature.

    Bones can be parented to create hierarchy:
    - Spine -> Chest -> Neck -> Head
    - Shoulder -> Upper Arm -> Forearm -> Hand -> Fingers

    Connected bones (use_connect=True) share position with parent tail.

    Workflow: BEFORE -> armature_create or existing armature

    Args:
        armature_name: Name of the armature object
        bone_name: Name for the new bone
        head: Start position [x, y, z] in armature local space
        tail: End position [x, y, z] in armature local space
        parent_bone: Optional parent bone name for hierarchy
        use_connect: If True, bone head connects to parent tail (no gap)

    Examples:
        armature_add_bone("Rig", "Spine", [0,0,0], [0,0,0.5]) -> Root bone
        armature_add_bone("Rig", "Chest", [0,0,0.5], [0,0,1], parent_bone="Spine", use_connect=True)
    """
    handler = get_handler()
    return handler.add_bone(
        armature_name=armature_name,
        bone_name=bone_name,
        head=head,
        tail=tail,
        parent_bone=parent_bone,
        use_connect=use_connect
    )


@mcp.tool()
def armature_bind(
    ctx: Context,
    mesh_name: str,
    armature_name: str,
    bind_type: Literal["AUTO", "ENVELOPE", "EMPTY"] = "AUTO"
) -> str:
    """[OBJECT MODE] Binds mesh to armature with automatic weights.

    Creates Armature modifier and vertex groups for each bone.
    The mesh will deform when bones are posed.

    Bind types:
    - AUTO: Automatic weight calculation based on bone proximity (best for organic)
    - ENVELOPE: Use bone envelope volumes for weights (good for simple meshes)
    - EMPTY: Create modifier without weights (for manual weight painting)

    Workflow: BEFORE -> Mesh and armature positioned correctly
              AFTER -> armature_pose_bone or animation

    Args:
        mesh_name: Name of the mesh object to bind
        armature_name: Name of the armature to bind to
        bind_type: Weight calculation method (AUTO, ENVELOPE, EMPTY)

    Examples:
        armature_bind("Character", "CharacterRig") -> Auto weights
        armature_bind("Robot", "RobotArm", bind_type="EMPTY") -> Manual weights
    """
    handler = get_handler()
    return handler.bind(
        mesh_name=mesh_name,
        armature_name=armature_name,
        bind_type=bind_type
    )


@mcp.tool()
def armature_pose_bone(
    ctx: Context,
    armature_name: str,
    bone_name: str,
    rotation: list[float] | None = None,
    location: list[float] | None = None,
    scale: list[float] | None = None
) -> str:
    """[POSE MODE] Poses armature bone.

    Sets the current pose without keyframing. Bound meshes will deform
    according to bone weights.

    For animation, combine with keyframe tools (future).

    Workflow: BEFORE -> armature_bind (mesh must be bound)

    Args:
        armature_name: Name of the armature
        bone_name: Name of the bone to pose
        rotation: Euler rotation in degrees [x, y, z] (optional)
        location: Local position offset [x, y, z] (optional)
        scale: Scale factors [x, y, z] (optional)

    Examples:
        armature_pose_bone("Rig", "UpperArm", rotation=[0, 0, 45]) -> Rotate 45 deg on Z
        armature_pose_bone("Rig", "Spine", rotation=[10, 0, 0]) -> Bend forward
    """
    handler = get_handler()
    return handler.pose_bone(
        armature_name=armature_name,
        bone_name=bone_name,
        rotation=rotation,
        location=location,
        scale=scale
    )


@mcp.tool()
def armature_weight_paint_assign(
    ctx: Context,
    object_name: str,
    vertex_group: str,
    weight: float = 1.0,
    mode: Literal["REPLACE", "ADD", "SUBTRACT"] = "REPLACE"
) -> str:
    """[WEIGHT PAINT/EDIT MODE][SELECTION-BASED] Assigns weights to selected vertices.

    For precise control over bone deformation influence.
    Use after armature_bind with EMPTY weights, or to refine AUTO weights.

    Weight values: 0.0 = no influence, 1.0 = full influence from bone.

    Modes:
    - REPLACE: Set weight to specified value
    - ADD: Add to existing weight
    - SUBTRACT: Subtract from existing weight

    Workflow: BEFORE -> Select vertices in Edit Mode, or paint in Weight Paint Mode
              AFTER -> Test pose with armature_pose_bone

    Args:
        object_name: Name of the mesh object
        vertex_group: Name of the vertex group (matches bone name)
        weight: Weight value 0.0-1.0 (default 1.0)
        mode: Assignment mode (REPLACE, ADD, SUBTRACT)

    Examples:
        armature_weight_paint_assign("Character", "Hand.L", weight=1.0) -> Full weight
        armature_weight_paint_assign("Character", "Forearm.L", weight=0.5) -> Half weight
    """
    handler = get_handler()
    return handler.weight_paint_assign(
        object_name=object_name,
        vertex_group=vertex_group,
        weight=weight,
        mode=mode
    )


@mcp.tool()
def armature_get_data(
    ctx: Context,
    object_name: str,
    include_pose: bool = False
) -> str:
    """
    [OBJECT MODE][READ-ONLY][SAFE] Returns armature bones and hierarchy.

    Workflow: READ-ONLY | USE → rig reconstruction in workflows

    Args:
        object_name: Name of the armature object to inspect
        include_pose: Include pose transforms (location/rotation/scale)

    Returns:
        JSON string with bone hierarchy and optional pose data.
    """
    def execute():
        handler = get_handler()
        try:
            import json
            data = handler.get_data(object_name, include_pose)
            return json.dumps(data, indent=2)
        except RuntimeError as e:
            return str(e)

    return route_tool_call(
        tool_name="armature_get_data",
        params={"object_name": object_name, "include_pose": include_pose},
        direct_executor=execute
    )
