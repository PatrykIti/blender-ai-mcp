import sys
from unittest.mock import MagicMock

from blender_addon.application.handlers.scene import SceneHandler


class TestSceneGetConstraints:
    def setup_method(self):
        self.handler = SceneHandler()
        self.mock_bpy = sys.modules["bpy"]

    def test_get_constraints_object_only(self):
        target = MagicMock()
        target.name = "Empty"

        prop_target = MagicMock()
        prop_target.identifier = "target"
        prop_target.type = "POINTER"

        prop_influence = MagicMock()
        prop_influence.identifier = "influence"
        prop_influence.type = "FLOAT"

        constraint = MagicMock()
        constraint.name = "Track"
        constraint.type = "TRACK_TO"
        constraint.target = target
        constraint.influence = 0.5
        constraint.bl_rna.properties = [prop_target, prop_influence]

        obj = MagicMock()
        obj.name = "Rig"
        obj.type = "EMPTY"
        obj.constraints = [constraint]

        self.mock_bpy.data.objects = {"Rig": obj}

        result = self.handler.get_constraints("Rig")

        assert result["constraint_count"] == 1
        assert result["constraints"][0]["properties"]["target"] == "Empty"
        assert result["constraints"][0]["properties"]["influence"] == 0.5
        assert result["bone_constraints"] == []

    def test_get_constraints_includes_bones(self):
        prop_influence = MagicMock()
        prop_influence.identifier = "influence"
        prop_influence.type = "FLOAT"

        bone_constraint = MagicMock()
        bone_constraint.name = "CopyRot"
        bone_constraint.type = "COPY_ROTATION"
        bone_constraint.influence = 1.0
        bone_constraint.bl_rna.properties = [prop_influence]

        bone = MagicMock()
        bone.name = "Bone"
        bone.constraints = [bone_constraint]

        pose = MagicMock()
        pose.bones = [bone]

        obj = MagicMock()
        obj.name = "Armature"
        obj.type = "ARMATURE"
        obj.constraints = []
        obj.pose = pose

        self.mock_bpy.data.objects = {"Armature": obj}

        result = self.handler.get_constraints("Armature", include_bones=True)

        assert result["constraint_count"] == 0
        assert result["bone_constraints"][0]["bone_name"] == "Bone"
        assert result["bone_constraints"][0]["constraints"][0]["name"] == "CopyRot"

