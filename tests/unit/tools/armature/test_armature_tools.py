"""
Tests for TASK-037 (Armature & Rigging) armature tools.
Pure pytest style - uses conftest.py fixtures.
"""
import pytest
from unittest.mock import MagicMock, patch

import bpy

from blender_addon.application.handlers.armature import ArmatureHandler


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def armature_handler():
    """Provides a fresh ArmatureHandler instance."""
    return ArmatureHandler()


@pytest.fixture
def mock_armature_object():
    """Sets up mock armature object."""
    mock_obj = MagicMock()
    mock_obj.name = 'Armature'
    mock_obj.type = 'ARMATURE'
    mock_obj.mode = 'OBJECT'
    mock_obj.data = MagicMock()
    mock_obj.data.name = 'Armature'
    mock_obj.data.edit_bones = MagicMock()
    mock_obj.data.bones = MagicMock()
    mock_obj.pose = MagicMock()
    mock_obj.pose.bones = {}

    # Edit bone mock
    mock_edit_bone = MagicMock()
    mock_edit_bone.name = 'Bone'
    mock_edit_bone.head = [0, 0, 0]
    mock_edit_bone.tail = [0, 0, 1]
    mock_edit_bone.parent = None
    mock_edit_bone.use_connect = False

    mock_obj.data.edit_bones.__getitem__ = MagicMock(return_value=mock_edit_bone)
    mock_obj.data.edit_bones.__contains__ = MagicMock(return_value=True)
    mock_obj.data.edit_bones.new = MagicMock(return_value=mock_edit_bone)

    bpy.context.active_object = mock_obj
    return mock_obj


@pytest.fixture
def mock_mesh_object():
    """Sets up mock mesh object."""
    mock_obj = MagicMock()
    mock_obj.name = 'Mesh'
    mock_obj.type = 'MESH'
    mock_obj.mode = 'OBJECT'
    mock_obj.data = MagicMock()
    mock_obj.data.vertices = [MagicMock(index=i, select=False) for i in range(8)]
    mock_obj.vertex_groups = {}
    return mock_obj


@pytest.fixture
def mock_pose_bone():
    """Sets up mock pose bone."""
    mock_bone = MagicMock()
    mock_bone.name = 'Bone'
    mock_bone.rotation_mode = 'XYZ'
    mock_bone.rotation_euler = [0, 0, 0]
    mock_bone.location = [0, 0, 0]
    mock_bone.scale = [1, 1, 1]
    return mock_bone


# =============================================================================
# TASK-037-1: armature_create tests
# =============================================================================

class TestArmatureCreate:
    """Tests for armature_create tool."""

    def test_create_default_armature(self, armature_handler, mock_armature_object):
        """Should create armature at origin with default bone."""
        bpy.ops.object.armature_add = MagicMock()
        bpy.ops.object.mode_set = MagicMock()

        result = armature_handler.create()

        bpy.ops.object.armature_add.assert_called_with(location=(0, 0, 0))
        assert "Created armature" in result
        assert "Armature" in result

    def test_create_armature_with_name(self, armature_handler, mock_armature_object):
        """Should create armature with specified name."""
        bpy.ops.object.armature_add = MagicMock()
        bpy.ops.object.mode_set = MagicMock()

        result = armature_handler.create(name="CharacterRig")

        assert mock_armature_object.name == "CharacterRig"
        assert "CharacterRig" in result

    def test_create_armature_with_location(self, armature_handler, mock_armature_object):
        """Should create armature at specified location."""
        bpy.ops.object.armature_add = MagicMock()
        bpy.ops.object.mode_set = MagicMock()

        result = armature_handler.create(location=[1, 2, 3])

        bpy.ops.object.armature_add.assert_called_with(location=(1, 2, 3))
        assert "(1, 2, 3)" in result

    def test_create_armature_with_bone_name(self, armature_handler, mock_armature_object):
        """Should create armature with named initial bone."""
        bpy.ops.object.armature_add = MagicMock()
        bpy.ops.object.mode_set = MagicMock()

        mock_edit_bone = mock_armature_object.data.edit_bones[0]
        result = armature_handler.create(bone_name="Root")

        assert mock_edit_bone.name == "Root"
        assert "Root" in result

    def test_create_armature_with_bone_length(self, armature_handler, mock_armature_object):
        """Should create armature with specified bone length."""
        bpy.ops.object.armature_add = MagicMock()
        bpy.ops.object.mode_set = MagicMock()

        mock_edit_bone = mock_armature_object.data.edit_bones[0]
        mock_edit_bone.head = [0, 0, 0]

        result = armature_handler.create(bone_length=2.0)

        assert "length=2.0" in result


# =============================================================================
# TASK-037-2: armature_add_bone tests
# =============================================================================

class TestArmatureAddBone:
    """Tests for armature_add_bone tool."""

    def test_add_bone_to_armature(self, armature_handler, mock_armature_object):
        """Should add bone to existing armature."""
        bpy.data.objects = {'Armature': mock_armature_object}
        bpy.context.view_layer = MagicMock()
        bpy.ops.object.mode_set = MagicMock()

        result = armature_handler.add_bone(
            armature_name='Armature',
            bone_name='Spine',
            head=[0, 0, 0],
            tail=[0, 0, 0.5]
        )

        mock_armature_object.data.edit_bones.new.assert_called_with('Spine')
        assert "Added bone 'Spine'" in result

    def test_add_bone_with_parent(self, armature_handler, mock_armature_object):
        """Should add bone with parent relationship."""
        bpy.data.objects = {'Armature': mock_armature_object}
        bpy.context.view_layer = MagicMock()
        bpy.ops.object.mode_set = MagicMock()

        result = armature_handler.add_bone(
            armature_name='Armature',
            bone_name='Chest',
            head=[0, 0, 0.5],
            tail=[0, 0, 1],
            parent_bone='Bone'
        )

        assert "parent='Bone'" in result

    def test_add_bone_connected(self, armature_handler, mock_armature_object):
        """Should add connected bone to parent."""
        bpy.data.objects = {'Armature': mock_armature_object}
        bpy.context.view_layer = MagicMock()
        bpy.ops.object.mode_set = MagicMock()

        result = armature_handler.add_bone(
            armature_name='Armature',
            bone_name='Neck',
            head=[0, 0, 1],
            tail=[0, 0, 1.3],
            parent_bone='Bone',
            use_connect=True
        )

        assert "connected" in result

    def test_add_bone_armature_not_found_raises(self, armature_handler):
        """Should raise ValueError when armature not found."""
        bpy.data.objects = {}

        with pytest.raises(ValueError, match="not found"):
            armature_handler.add_bone(
                armature_name='NonExistent',
                bone_name='Bone',
                head=[0, 0, 0],
                tail=[0, 0, 1]
            )

    def test_add_bone_wrong_type_raises(self, armature_handler, mock_mesh_object):
        """Should raise ValueError when object is not armature."""
        bpy.data.objects = {'Mesh': mock_mesh_object}

        with pytest.raises(ValueError, match="not an armature"):
            armature_handler.add_bone(
                armature_name='Mesh',
                bone_name='Bone',
                head=[0, 0, 0],
                tail=[0, 0, 1]
            )

    def test_add_bone_parent_not_found_raises(self, armature_handler, mock_armature_object):
        """Should raise ValueError when parent bone not found."""
        bpy.data.objects = {'Armature': mock_armature_object}
        bpy.context.view_layer = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        mock_armature_object.data.edit_bones.__contains__ = MagicMock(return_value=False)

        with pytest.raises(ValueError, match="Parent bone"):
            armature_handler.add_bone(
                armature_name='Armature',
                bone_name='Child',
                head=[0, 0, 0],
                tail=[0, 0, 1],
                parent_bone='NonExistent'
            )


# =============================================================================
# TASK-037-3: armature_bind tests
# =============================================================================

class TestArmatureBind:
    """Tests for armature_bind tool."""

    def test_bind_mesh_to_armature_auto(self, armature_handler, mock_armature_object, mock_mesh_object):
        """Should bind mesh to armature with auto weights."""
        bpy.data.objects = {
            'Armature': mock_armature_object,
            'Mesh': mock_mesh_object
        }
        mock_armature_object.data.bones = [MagicMock(), MagicMock()]  # 2 bones
        bpy.context.view_layer = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.object.select_all = MagicMock()
        bpy.ops.object.parent_set = MagicMock()

        result = armature_handler.bind(
            mesh_name='Mesh',
            armature_name='Armature'
        )

        bpy.ops.object.parent_set.assert_called_with(type='ARMATURE_AUTO')
        assert "Bound mesh 'Mesh'" in result
        assert "bind_type=AUTO" in result

    def test_bind_mesh_envelope(self, armature_handler, mock_armature_object, mock_mesh_object):
        """Should bind mesh with envelope weights."""
        bpy.data.objects = {
            'Armature': mock_armature_object,
            'Mesh': mock_mesh_object
        }
        mock_armature_object.data.bones = [MagicMock()]
        bpy.context.view_layer = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.object.select_all = MagicMock()
        bpy.ops.object.parent_set = MagicMock()

        result = armature_handler.bind(
            mesh_name='Mesh',
            armature_name='Armature',
            bind_type='ENVELOPE'
        )

        bpy.ops.object.parent_set.assert_called_with(type='ARMATURE_ENVELOPE')
        assert "bind_type=ENVELOPE" in result

    def test_bind_mesh_empty(self, armature_handler, mock_armature_object, mock_mesh_object):
        """Should bind mesh without automatic weights."""
        bpy.data.objects = {
            'Armature': mock_armature_object,
            'Mesh': mock_mesh_object
        }
        mock_armature_object.data.bones = [MagicMock()]
        bpy.context.view_layer = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.object.select_all = MagicMock()
        bpy.ops.object.parent_set = MagicMock()

        result = armature_handler.bind(
            mesh_name='Mesh',
            armature_name='Armature',
            bind_type='EMPTY'
        )

        bpy.ops.object.parent_set.assert_called_with(type='ARMATURE')
        assert "bind_type=EMPTY" in result

    def test_bind_mesh_not_found_raises(self, armature_handler, mock_armature_object):
        """Should raise ValueError when mesh not found."""
        bpy.data.objects = {'Armature': mock_armature_object}

        with pytest.raises(ValueError, match="Mesh.*not found"):
            armature_handler.bind(
                mesh_name='NonExistent',
                armature_name='Armature'
            )

    def test_bind_armature_not_found_raises(self, armature_handler, mock_mesh_object):
        """Should raise ValueError when armature not found."""
        bpy.data.objects = {'Mesh': mock_mesh_object}

        with pytest.raises(ValueError, match="Armature.*not found"):
            armature_handler.bind(
                mesh_name='Mesh',
                armature_name='NonExistent'
            )

    def test_bind_invalid_type_raises(self, armature_handler, mock_armature_object, mock_mesh_object):
        """Should raise ValueError for invalid bind type."""
        bpy.data.objects = {
            'Armature': mock_armature_object,
            'Mesh': mock_mesh_object
        }
        bpy.context.view_layer = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.object.select_all = MagicMock()

        with pytest.raises(ValueError, match="Invalid bind_type"):
            armature_handler.bind(
                mesh_name='Mesh',
                armature_name='Armature',
                bind_type='INVALID'
            )


# =============================================================================
# TASK-037-4: armature_pose_bone tests
# =============================================================================

class TestArmaturePoseBone:
    """Tests for armature_pose_bone tool."""

    def test_pose_bone_rotation(self, armature_handler, mock_armature_object, mock_pose_bone):
        """Should pose bone with rotation."""
        bpy.data.objects = {'Armature': mock_armature_object}
        mock_armature_object.pose.bones = {'Bone': mock_pose_bone}
        bpy.context.view_layer = MagicMock()
        bpy.ops.object.mode_set = MagicMock()

        result = armature_handler.pose_bone(
            armature_name='Armature',
            bone_name='Bone',
            rotation=[45, 0, 0]
        )

        assert "rotation=[45, 0, 0]" in result
        assert "Posed bone 'Bone'" in result

    def test_pose_bone_location(self, armature_handler, mock_armature_object, mock_pose_bone):
        """Should pose bone with location."""
        bpy.data.objects = {'Armature': mock_armature_object}
        mock_armature_object.pose.bones = {'Bone': mock_pose_bone}
        bpy.context.view_layer = MagicMock()
        bpy.ops.object.mode_set = MagicMock()

        result = armature_handler.pose_bone(
            armature_name='Armature',
            bone_name='Bone',
            location=[0.1, 0, 0]
        )

        assert "location=[0.1, 0, 0]" in result

    def test_pose_bone_scale(self, armature_handler, mock_armature_object, mock_pose_bone):
        """Should pose bone with scale."""
        bpy.data.objects = {'Armature': mock_armature_object}
        mock_armature_object.pose.bones = {'Bone': mock_pose_bone}
        bpy.context.view_layer = MagicMock()
        bpy.ops.object.mode_set = MagicMock()

        result = armature_handler.pose_bone(
            armature_name='Armature',
            bone_name='Bone',
            scale=[1.5, 1.5, 1.5]
        )

        assert "scale=[1.5, 1.5, 1.5]" in result

    def test_pose_bone_multiple_transforms(self, armature_handler, mock_armature_object, mock_pose_bone):
        """Should pose bone with multiple transforms."""
        bpy.data.objects = {'Armature': mock_armature_object}
        mock_armature_object.pose.bones = {'Bone': mock_pose_bone}
        bpy.context.view_layer = MagicMock()
        bpy.ops.object.mode_set = MagicMock()

        result = armature_handler.pose_bone(
            armature_name='Armature',
            bone_name='Bone',
            rotation=[30, 0, 15],
            location=[0, 0.1, 0]
        )

        assert "rotation=" in result
        assert "location=" in result

    def test_pose_bone_no_changes(self, armature_handler, mock_armature_object, mock_pose_bone):
        """Should report no changes when no transforms provided."""
        bpy.data.objects = {'Armature': mock_armature_object}
        mock_armature_object.pose.bones = {'Bone': mock_pose_bone}
        bpy.context.view_layer = MagicMock()
        bpy.ops.object.mode_set = MagicMock()

        result = armature_handler.pose_bone(
            armature_name='Armature',
            bone_name='Bone'
        )

        assert "No changes" in result

    def test_pose_bone_not_found_raises(self, armature_handler, mock_armature_object):
        """Should raise ValueError when bone not found."""
        bpy.data.objects = {'Armature': mock_armature_object}
        mock_armature_object.pose.bones = {}
        bpy.context.view_layer = MagicMock()
        bpy.ops.object.mode_set = MagicMock()

        with pytest.raises(ValueError, match="Bone.*not found"):
            armature_handler.pose_bone(
                armature_name='Armature',
                bone_name='NonExistent'
            )

    def test_pose_armature_not_found_raises(self, armature_handler):
        """Should raise ValueError when armature not found."""
        bpy.data.objects = {}

        with pytest.raises(ValueError, match="Armature.*not found"):
            armature_handler.pose_bone(
                armature_name='NonExistent',
                bone_name='Bone'
            )


# =============================================================================
# TASK-037-5: armature_weight_paint_assign tests
# =============================================================================

class TestArmatureWeightPaintAssign:
    """Tests for armature_weight_paint_assign tool."""

    def test_assign_weight_to_vertices(self, armature_handler, mock_mesh_object):
        """Should assign weight to selected vertices."""
        # Set up selected vertices
        mock_mesh_object.data.vertices[0].select = True
        mock_mesh_object.data.vertices[1].select = True
        mock_vg = MagicMock()
        mock_mesh_object.vertex_groups = {'Hand': mock_vg}

        bpy.data.objects = {'Mesh': mock_mesh_object}
        bpy.context.view_layer = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        mock_mesh_object.mode = 'EDIT'

        result = armature_handler.weight_paint_assign(
            object_name='Mesh',
            vertex_group='Hand',
            weight=1.0
        )

        mock_vg.add.assert_called_once()
        assert "Assigned weight 1.0" in result
        assert "2 vertices" in result

    def test_assign_weight_replace_mode(self, armature_handler, mock_mesh_object):
        """Should assign weight with REPLACE mode."""
        mock_mesh_object.data.vertices[0].select = True
        mock_vg = MagicMock()
        mock_mesh_object.vertex_groups = {'Arm': mock_vg}

        bpy.data.objects = {'Mesh': mock_mesh_object}
        bpy.context.view_layer = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        mock_mesh_object.mode = 'EDIT'

        result = armature_handler.weight_paint_assign(
            object_name='Mesh',
            vertex_group='Arm',
            weight=0.5,
            mode='REPLACE'
        )

        mock_vg.add.assert_called_with([0], 0.5, 'REPLACE')
        assert "mode=REPLACE" in result

    def test_assign_weight_add_mode(self, armature_handler, mock_mesh_object):
        """Should assign weight with ADD mode."""
        mock_mesh_object.data.vertices[0].select = True
        mock_vg = MagicMock()
        mock_mesh_object.vertex_groups = {'Leg': mock_vg}

        bpy.data.objects = {'Mesh': mock_mesh_object}
        bpy.context.view_layer = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        mock_mesh_object.mode = 'EDIT'

        result = armature_handler.weight_paint_assign(
            object_name='Mesh',
            vertex_group='Leg',
            weight=0.3,
            mode='ADD'
        )

        mock_vg.add.assert_called_with([0], 0.3, 'ADD')
        assert "mode=ADD" in result

    def test_assign_weight_subtract_mode(self, armature_handler, mock_mesh_object):
        """Should assign weight with SUBTRACT mode."""
        mock_mesh_object.data.vertices[0].select = True
        mock_vg = MagicMock()
        mock_mesh_object.vertex_groups = {'Spine': mock_vg}

        bpy.data.objects = {'Mesh': mock_mesh_object}
        bpy.context.view_layer = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        mock_mesh_object.mode = 'EDIT'

        result = armature_handler.weight_paint_assign(
            object_name='Mesh',
            vertex_group='Spine',
            weight=0.2,
            mode='SUBTRACT'
        )

        mock_vg.add.assert_called_with([0], 0.2, 'SUBTRACT')
        assert "mode=SUBTRACT" in result

    def test_assign_weight_creates_group(self, armature_handler, mock_mesh_object):
        """Should create vertex group if it doesn't exist."""
        mock_mesh_object.data.vertices[0].select = True
        mock_vg = MagicMock()
        mock_vertex_groups = MagicMock()
        mock_vertex_groups.__contains__ = MagicMock(return_value=False)
        mock_vertex_groups.__getitem__ = MagicMock(return_value=mock_vg)
        mock_vertex_groups.new = MagicMock(return_value=mock_vg)
        mock_mesh_object.vertex_groups = mock_vertex_groups

        bpy.data.objects = {'Mesh': mock_mesh_object}
        bpy.context.view_layer = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        mock_mesh_object.mode = 'EDIT'

        result = armature_handler.weight_paint_assign(
            object_name='Mesh',
            vertex_group='NewGroup',
            weight=1.0
        )

        mock_vertex_groups.new.assert_called_with(name='NewGroup')

    def test_assign_weight_no_selection_raises(self, armature_handler, mock_mesh_object):
        """Should raise ValueError when no vertices selected."""
        # No vertices selected - create fresh vertices that are not selected
        mock_mesh_object.data.vertices = [
            MagicMock(index=i, select=False) for i in range(8)
        ]
        mock_vertex_groups = MagicMock()
        mock_vertex_groups.__contains__ = MagicMock(return_value=True)
        mock_mesh_object.vertex_groups = mock_vertex_groups

        bpy.data.objects = {'Mesh': mock_mesh_object}
        bpy.context.view_layer = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        mock_mesh_object.mode = 'EDIT'

        with pytest.raises(ValueError, match="No vertices selected"):
            armature_handler.weight_paint_assign(
                object_name='Mesh',
                vertex_group='Group'
            )

    def test_assign_weight_object_not_found_raises(self, armature_handler):
        """Should raise ValueError when object not found."""
        bpy.data.objects = {}

        with pytest.raises(ValueError, match="not found"):
            armature_handler.weight_paint_assign(
                object_name='NonExistent',
                vertex_group='Group'
            )

    def test_assign_weight_not_mesh_raises(self, armature_handler, mock_armature_object):
        """Should raise ValueError when object is not a mesh."""
        bpy.data.objects = {'Armature': mock_armature_object}

        with pytest.raises(ValueError, match="not a mesh"):
            armature_handler.weight_paint_assign(
                object_name='Armature',
                vertex_group='Group'
            )

    def test_assign_weight_invalid_mode_raises(self, armature_handler, mock_mesh_object):
        """Should raise ValueError for invalid mode."""
        mock_mesh_object.data.vertices[0].select = True
        bpy.data.objects = {'Mesh': mock_mesh_object}
        bpy.context.view_layer = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        mock_mesh_object.mode = 'EDIT'

        with pytest.raises(ValueError, match="Invalid mode"):
            armature_handler.weight_paint_assign(
                object_name='Mesh',
                vertex_group='Group',
                mode='INVALID'
            )

    def test_assign_weight_clamps_value(self, armature_handler, mock_mesh_object):
        """Should clamp weight to 0.0-1.0 range."""
        mock_mesh_object.data.vertices[0].select = True
        mock_vg = MagicMock()
        mock_mesh_object.vertex_groups = {'Group': mock_vg}

        bpy.data.objects = {'Mesh': mock_mesh_object}
        bpy.context.view_layer = MagicMock()
        bpy.ops.object.mode_set = MagicMock()
        mock_mesh_object.mode = 'EDIT'

        # Test weight > 1.0 is clamped
        result = armature_handler.weight_paint_assign(
            object_name='Mesh',
            vertex_group='Group',
            weight=2.0
        )

        # Weight should be clamped to 1.0
        mock_vg.add.assert_called_with([0], 1.0, 'REPLACE')
        assert "weight 1.0" in result
