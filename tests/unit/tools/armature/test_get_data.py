from unittest.mock import MagicMock

import bpy

from blender_addon.application.handlers.armature import ArmatureHandler


def test_armature_get_data_with_pose():
    handler = ArmatureHandler()

    bone_root = MagicMock()
    bone_root.name = "Root"
    bone_root.head_local = [0.0, 0.0, 0.0]
    bone_root.tail_local = [0.0, 0.0, 1.0]
    bone_root.roll = 0.0
    bone_root.parent = None
    bone_root.use_connect = False
    bone_root.use_deform = True
    bone_root.inherit_scale = "FULL"

    bone_child = MagicMock()
    bone_child.name = "Child"
    bone_child.head_local = [0.0, 0.0, 1.0]
    bone_child.tail_local = [0.0, 0.0, 2.0]
    bone_child.roll = 0.1
    bone_child.parent = bone_root
    bone_child.use_connect = True
    bone_child.use_deform = True
    bone_child.inherit_scale = "FULL"

    armature_data = MagicMock()
    armature_data.bones = [bone_root, bone_child]

    pose_bone = MagicMock()
    pose_bone.name = "Root"
    pose_bone.location = [0.0, 0.0, 0.0]
    pose_bone.scale = [1.0, 1.0, 1.0]
    pose_bone.rotation_mode = "XYZ"
    pose_bone.rotation_euler = [0.1, 0.2, 0.3]

    pose = MagicMock()
    pose.bones = [pose_bone]

    armature_obj = MagicMock()
    armature_obj.name = "Armature"
    armature_obj.type = "ARMATURE"
    armature_obj.data = armature_data
    armature_obj.pose = pose

    bpy.data.objects = {"Armature": armature_obj}

    result = handler.get_data("Armature", include_pose=True)

    assert result["bone_count"] == 2
    assert result["bones"][1]["parent"] == "Root"
    assert result["pose"][0]["rotation_mode"] == "XYZ"
