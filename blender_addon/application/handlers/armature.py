"""
Blender Addon Handler for Armature Tools.

TASK-037: Armature & Rigging
Direct Blender API implementation.
"""

import bpy
import math
from typing import Optional, List


class ArmatureHandler:
    """Handler for armature/rigging operations in Blender."""

    def create(
        self,
        name: str = "Armature",
        location: Optional[List[float]] = None,
        bone_name: str = "Bone",
        bone_length: float = 1.0
    ) -> str:
        """
        [OBJECT MODE][SCENE] Creates armature with initial bone.

        Args:
            name: Name for the armature object.
            location: World position [x, y, z].
            bone_name: Name for the initial bone.
            bone_length: Length of the initial bone.

        Returns:
            Success message with armature details.
        """
        # Ensure Object Mode
        if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # Parse location
        loc = tuple(location) if location else (0, 0, 0)

        # Create armature
        bpy.ops.object.armature_add(location=loc)
        armature = bpy.context.active_object
        armature.name = name
        armature.data.name = name

        # Rename the initial bone
        bpy.ops.object.mode_set(mode='EDIT')
        edit_bone = armature.data.edit_bones[0]
        edit_bone.name = bone_name

        # Set bone length (tail position relative to head)
        edit_bone.tail = (edit_bone.head[0], edit_bone.head[1], edit_bone.head[2] + bone_length)

        bpy.ops.object.mode_set(mode='OBJECT')

        return f"Created armature '{name}' at {loc} with bone '{bone_name}' (length={bone_length})"

    def add_bone(
        self,
        armature_name: str,
        bone_name: str,
        head: List[float],
        tail: List[float],
        parent_bone: Optional[str] = None,
        use_connect: bool = False
    ) -> str:
        """
        [EDIT MODE on armature] Adds bone to armature.

        Args:
            armature_name: Name of the armature object.
            bone_name: Name for the new bone.
            head: Start position [x, y, z].
            tail: End position [x, y, z].
            parent_bone: Optional parent bone name.
            use_connect: Connect to parent (no gap).

        Returns:
            Success message with bone details.
        """
        # Find armature
        if armature_name not in bpy.data.objects:
            raise ValueError(f"Armature '{armature_name}' not found")

        armature = bpy.data.objects[armature_name]
        if armature.type != 'ARMATURE':
            raise ValueError(f"Object '{armature_name}' is not an armature (type: {armature.type})")

        # Set as active and enter Edit Mode
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='EDIT')

        # Create new bone
        edit_bone = armature.data.edit_bones.new(bone_name)
        edit_bone.head = tuple(head)
        edit_bone.tail = tuple(tail)

        # Set parent if specified
        if parent_bone:
            if parent_bone not in armature.data.edit_bones:
                bpy.ops.object.mode_set(mode='OBJECT')
                raise ValueError(f"Parent bone '{parent_bone}' not found in armature '{armature_name}'")
            edit_bone.parent = armature.data.edit_bones[parent_bone]
            edit_bone.use_connect = use_connect

        bpy.ops.object.mode_set(mode='OBJECT')

        parent_info = f", parent='{parent_bone}'" if parent_bone else ""
        connect_info = ", connected" if use_connect else ""
        return f"Added bone '{bone_name}' to '{armature_name}' (head={head}, tail={tail}{parent_info}{connect_info})"

    def bind(
        self,
        mesh_name: str,
        armature_name: str,
        bind_type: str = "AUTO"
    ) -> str:
        """
        [OBJECT MODE] Binds mesh to armature with automatic weights.

        Args:
            mesh_name: Name of the mesh to bind.
            armature_name: Name of the armature.
            bind_type: Binding type (AUTO, ENVELOPE, EMPTY).

        Returns:
            Success message with binding details.
        """
        # Validate inputs
        if mesh_name not in bpy.data.objects:
            raise ValueError(f"Mesh '{mesh_name}' not found")
        if armature_name not in bpy.data.objects:
            raise ValueError(f"Armature '{armature_name}' not found")

        mesh = bpy.data.objects[mesh_name]
        armature = bpy.data.objects[armature_name]

        if mesh.type != 'MESH':
            raise ValueError(f"Object '{mesh_name}' is not a mesh (type: {mesh.type})")
        if armature.type != 'ARMATURE':
            raise ValueError(f"Object '{armature_name}' is not an armature (type: {armature.type})")

        # Validate bind_type
        valid_types = ["AUTO", "ENVELOPE", "EMPTY"]
        bind_type = bind_type.upper()
        if bind_type not in valid_types:
            raise ValueError(f"Invalid bind_type '{bind_type}'. Must be one of: {valid_types}")

        # Ensure Object Mode
        if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # Deselect all, then select mesh and armature
        bpy.ops.object.select_all(action='DESELECT')
        mesh.select_set(True)
        armature.select_set(True)
        bpy.context.view_layer.objects.active = armature

        # Parent with appropriate method
        try:
            if bind_type == "AUTO":
                bpy.ops.object.parent_set(type='ARMATURE_AUTO')
            elif bind_type == "ENVELOPE":
                bpy.ops.object.parent_set(type='ARMATURE_ENVELOPE')
            else:  # EMPTY
                bpy.ops.object.parent_set(type='ARMATURE')
        except RuntimeError as e:
            raise RuntimeError(f"Binding failed: {e}")

        # Count vertex groups created
        bone_count = len(armature.data.bones)

        return f"Bound mesh '{mesh_name}' to armature '{armature_name}' (bind_type={bind_type}, bones={bone_count})"

    def pose_bone(
        self,
        armature_name: str,
        bone_name: str,
        rotation: Optional[List[float]] = None,
        location: Optional[List[float]] = None,
        scale: Optional[List[float]] = None
    ) -> str:
        """
        [POSE MODE] Poses armature bone.

        Args:
            armature_name: Name of the armature.
            bone_name: Name of the bone to pose.
            rotation: Euler rotation in degrees [x, y, z].
            location: Local position offset [x, y, z].
            scale: Scale factors [x, y, z].

        Returns:
            Success message with pose details.
        """
        # Find armature
        if armature_name not in bpy.data.objects:
            raise ValueError(f"Armature '{armature_name}' not found")

        armature = bpy.data.objects[armature_name]
        if armature.type != 'ARMATURE':
            raise ValueError(f"Object '{armature_name}' is not an armature (type: {armature.type})")

        # Enter Pose Mode
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')

        # Find pose bone
        if bone_name not in armature.pose.bones:
            bpy.ops.object.mode_set(mode='OBJECT')
            raise ValueError(f"Bone '{bone_name}' not found in armature '{armature_name}'")

        bone = armature.pose.bones[bone_name]

        # Apply transforms
        changes = []
        if rotation is not None:
            # Convert degrees to radians
            bone.rotation_mode = 'XYZ'
            bone.rotation_euler = [math.radians(r) for r in rotation]
            changes.append(f"rotation={rotation}")

        if location is not None:
            bone.location = tuple(location)
            changes.append(f"location={location}")

        if scale is not None:
            bone.scale = tuple(scale)
            changes.append(f"scale={scale}")

        if not changes:
            bpy.ops.object.mode_set(mode='OBJECT')
            return f"No changes applied to bone '{bone_name}'"

        bpy.ops.object.mode_set(mode='OBJECT')

        return f"Posed bone '{bone_name}' in '{armature_name}': {', '.join(changes)}"

    def weight_paint_assign(
        self,
        object_name: str,
        vertex_group: str,
        weight: float = 1.0,
        mode: str = "REPLACE"
    ) -> str:
        """
        [WEIGHT PAINT/EDIT MODE][SELECTION-BASED] Assigns weights to selected vertices.

        Args:
            object_name: Name of the mesh object.
            vertex_group: Name of the vertex group.
            weight: Weight value (0.0-1.0).
            mode: Assignment mode (REPLACE, ADD, SUBTRACT).

        Returns:
            Success message with weight details.
        """
        # Find object
        if object_name not in bpy.data.objects:
            raise ValueError(f"Object '{object_name}' not found")

        obj = bpy.data.objects[object_name]
        if obj.type != 'MESH':
            raise ValueError(f"Object '{object_name}' is not a mesh (type: {obj.type})")

        # Validate mode
        valid_modes = ["REPLACE", "ADD", "SUBTRACT"]
        mode = mode.upper()
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode '{mode}'. Must be one of: {valid_modes}")

        # Clamp weight
        weight = max(0.0, min(1.0, weight))

        # Find or create vertex group
        if vertex_group not in obj.vertex_groups:
            obj.vertex_groups.new(name=vertex_group)

        vg = obj.vertex_groups[vertex_group]

        # Set as active
        bpy.context.view_layer.objects.active = obj

        # Store current mode and switch to Edit Mode to get selection
        previous_mode = obj.mode
        if previous_mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

        # Get selected vertices
        bpy.ops.object.mode_set(mode='OBJECT')  # Need object mode to read selection
        selected_verts = [v.index for v in obj.data.vertices if v.select]

        if not selected_verts:
            if previous_mode != 'OBJECT':
                bpy.ops.object.mode_set(mode=previous_mode)
            raise ValueError("No vertices selected. Select vertices in Edit Mode first.")

        # Assign weights
        if mode == "REPLACE":
            vg.add(selected_verts, weight, 'REPLACE')
        elif mode == "ADD":
            vg.add(selected_verts, weight, 'ADD')
        else:  # SUBTRACT
            vg.add(selected_verts, weight, 'SUBTRACT')

        # Restore mode
        if previous_mode != 'OBJECT':
            bpy.ops.object.mode_set(mode=previous_mode)

        return f"Assigned weight {weight} to {len(selected_verts)} vertices in group '{vertex_group}' (mode={mode})"
