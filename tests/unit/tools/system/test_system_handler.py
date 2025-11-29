"""Unit tests for System handler (blender_addon)."""
import os
import sys
import tempfile
import pytest
from unittest.mock import MagicMock, patch

# conftest.py handles bpy mocking
from blender_addon.application.handlers.system import SystemHandler


class TestSystemSetMode:
    """Tests for system_set_mode functionality."""

    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]
        self.handler = SystemHandler()

        # Create mock objects
        self.mesh_obj = MagicMock()
        self.mesh_obj.name = "Cube"
        self.mesh_obj.type = "MESH"

        self.armature_obj = MagicMock()
        self.armature_obj.name = "Armature"
        self.armature_obj.type = "ARMATURE"

        self.camera_obj = MagicMock()
        self.camera_obj.name = "Camera"
        self.camera_obj.type = "CAMERA"

        # Setup mock context
        self.mock_bpy.context.mode = "OBJECT"
        self.mock_bpy.context.active_object = self.mesh_obj
        self.mock_bpy.ops.object.mode_set = MagicMock()
        self.mock_bpy.ops.object.select_all = MagicMock()
        self.mock_bpy.data.objects = {
            "Cube": self.mesh_obj,
            "Armature": self.armature_obj,
            "Camera": self.camera_obj,
        }
        self.mock_bpy.context.view_layer = MagicMock()

    def test_set_mode_valid_edit(self):
        """Test switching to EDIT mode."""
        result = self.handler.set_mode("EDIT")

        self.mock_bpy.ops.object.mode_set.assert_called_with(mode="EDIT")
        assert "EDIT" in result
        assert "Cube" in result

    def test_set_mode_already_in_mode(self):
        """Test that mode switch is skipped when already in target mode."""
        self.mock_bpy.context.mode = "EDIT"

        result = self.handler.set_mode("EDIT")

        self.mock_bpy.ops.object.mode_set.assert_not_called()
        assert "Already in EDIT mode" in result

    def test_set_mode_with_object_name(self):
        """Test mode switch with specific object name."""
        result = self.handler.set_mode("EDIT", object_name="Cube")

        # Should set the object as active first
        self.mock_bpy.ops.object.select_all.assert_called()
        self.mesh_obj.select_set.assert_called_with(True)
        self.mock_bpy.ops.object.mode_set.assert_called()

    def test_set_mode_object_not_found(self):
        """Test error when object name doesn't exist."""
        with pytest.raises(ValueError, match="not found"):
            self.handler.set_mode("EDIT", object_name="NonExistent")

    def test_set_mode_invalid_mode(self):
        """Test error on invalid mode."""
        with pytest.raises(ValueError, match="Invalid mode"):
            self.handler.set_mode("INVALID_MODE")

    def test_set_mode_no_active_object(self):
        """Test error when no active object for non-OBJECT mode."""
        self.mock_bpy.context.active_object = None

        with pytest.raises(ValueError, match="no active object"):
            self.handler.set_mode("EDIT")

    def test_set_mode_edit_wrong_object_type(self):
        """Test that EDIT mode rejects non-editable types."""
        self.mock_bpy.context.active_object = self.camera_obj

        with pytest.raises(ValueError, match="Cannot enter EDIT mode"):
            self.handler.set_mode("EDIT")

    def test_set_mode_sculpt_requires_mesh(self):
        """Test that SCULPT mode requires MESH type."""
        self.mock_bpy.context.active_object = self.armature_obj

        with pytest.raises(ValueError, match="Cannot enter SCULPT mode"):
            self.handler.set_mode("SCULPT")

    def test_set_mode_pose_requires_armature(self):
        """Test that POSE mode requires ARMATURE type."""
        self.mock_bpy.context.active_object = self.mesh_obj

        with pytest.raises(ValueError, match="Cannot enter POSE mode"):
            self.handler.set_mode("POSE")

    def test_set_mode_pose_valid(self):
        """Test valid POSE mode on armature."""
        self.mock_bpy.context.active_object = self.armature_obj

        result = self.handler.set_mode("POSE")

        self.mock_bpy.ops.object.mode_set.assert_called_with(mode="POSE")
        assert "POSE" in result


class TestSystemUndoRedo:
    """Tests for undo/redo functionality."""

    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]
        self.handler = SystemHandler()

        self.mock_bpy.ops.ed.undo = MagicMock()
        self.mock_bpy.ops.ed.redo = MagicMock()

    def test_undo_single_step(self):
        """Test single undo step."""
        result = self.handler.undo(1)

        self.mock_bpy.ops.ed.undo.assert_called_once()
        assert "Undone 1 step" in result

    def test_undo_multiple_steps(self):
        """Test multiple undo steps."""
        result = self.handler.undo(3)

        assert self.mock_bpy.ops.ed.undo.call_count == 3
        assert "Undone 3 step" in result

    def test_undo_clamped_to_max(self):
        """Test that steps are clamped to max 10."""
        result = self.handler.undo(20)

        assert self.mock_bpy.ops.ed.undo.call_count == 10
        assert "Undone 10 step" in result

    def test_undo_clamped_to_min(self):
        """Test that steps are clamped to min 1."""
        result = self.handler.undo(0)

        assert self.mock_bpy.ops.ed.undo.call_count == 1
        assert "Undone 1 step" in result

    def test_undo_nothing_to_undo(self):
        """Test when there's nothing to undo."""
        self.mock_bpy.ops.ed.undo.side_effect = RuntimeError("Nothing to undo")

        result = self.handler.undo(1)

        assert "Nothing to undo" in result

    def test_redo_single_step(self):
        """Test single redo step."""
        result = self.handler.redo(1)

        self.mock_bpy.ops.ed.redo.assert_called_once()
        assert "Redone 1 step" in result

    def test_redo_multiple_steps(self):
        """Test multiple redo steps."""
        result = self.handler.redo(5)

        assert self.mock_bpy.ops.ed.redo.call_count == 5
        assert "Redone 5 step" in result

    def test_redo_nothing_to_redo(self):
        """Test when there's nothing to redo."""
        self.mock_bpy.ops.ed.redo.side_effect = RuntimeError("Nothing to redo")

        result = self.handler.redo(1)

        assert "Nothing to redo" in result


class TestSystemSaveFile:
    """Tests for save_file functionality."""

    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]
        self.handler = SystemHandler()

        self.mock_bpy.ops.wm.save_as_mainfile = MagicMock()
        self.mock_bpy.ops.wm.save_mainfile = MagicMock()
        self.mock_bpy.data.filepath = ""

    def test_save_file_with_filepath(self):
        """Test saving to specific filepath."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.blend")

            result = self.handler.save_file(filepath=filepath)

            self.mock_bpy.ops.wm.save_as_mainfile.assert_called_once()
            assert filepath in result

    def test_save_file_adds_blend_extension(self):
        """Test that .blend extension is added if missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test")

            result = self.handler.save_file(filepath=filepath)

            call_args = self.mock_bpy.ops.wm.save_as_mainfile.call_args
            assert call_args[1]["filepath"].endswith(".blend")

    def test_save_file_to_current_path(self):
        """Test saving to current filepath when file is already saved."""
        self.mock_bpy.data.filepath = "/existing/file.blend"

        result = self.handler.save_file()

        self.mock_bpy.ops.wm.save_mainfile.assert_called_once()
        assert "/existing/file.blend" in result

    def test_save_file_to_temp_when_unsaved(self):
        """Test saving to temp when file has never been saved."""
        self.mock_bpy.data.filepath = ""

        result = self.handler.save_file()

        self.mock_bpy.ops.wm.save_as_mainfile.assert_called_once()
        assert "autosave" in result.lower() or "temp" in result.lower()


class TestSystemNewFile:
    """Tests for new_file functionality."""

    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]
        self.handler = SystemHandler()

        self.mock_bpy.ops.wm.read_homefile = MagicMock()

    def test_new_file_default(self):
        """Test creating new file with default settings."""
        result = self.handler.new_file()

        self.mock_bpy.ops.wm.read_homefile.assert_called_once_with(load_ui=False)
        assert "new file" in result.lower()

    def test_new_file_with_ui(self):
        """Test creating new file loading UI."""
        result = self.handler.new_file(load_ui=True)

        self.mock_bpy.ops.wm.read_homefile.assert_called_once_with(load_ui=True)


class TestSystemSnapshot:
    """Tests for snapshot functionality."""

    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]
        self.handler = SystemHandler()

        self.mock_bpy.ops.wm.save_as_mainfile = MagicMock()
        self.mock_bpy.ops.wm.open_mainfile = MagicMock()

        # Use a unique temp dir for each test
        self.test_snapshot_dir = tempfile.mkdtemp()
        self.handler.SNAPSHOT_DIR = self.test_snapshot_dir

    def teardown_method(self):
        """Cleanup temp directory after each test."""
        import shutil
        if os.path.exists(self.test_snapshot_dir):
            shutil.rmtree(self.test_snapshot_dir)

    def test_snapshot_save_with_name(self):
        """Test saving snapshot with custom name."""
        result = self.handler.snapshot("save", name="my_checkpoint")

        self.mock_bpy.ops.wm.save_as_mainfile.assert_called_once()
        call_args = self.mock_bpy.ops.wm.save_as_mainfile.call_args
        assert "my_checkpoint" in call_args[1]["filepath"]
        assert call_args[1]["copy"] is True
        assert "my_checkpoint" in result

    def test_snapshot_save_auto_name(self):
        """Test saving snapshot with auto-generated name."""
        result = self.handler.snapshot("save")

        self.mock_bpy.ops.wm.save_as_mainfile.assert_called_once()
        assert "Saved snapshot" in result

    def test_snapshot_restore_requires_name(self):
        """Test that restore requires name."""
        result = self.handler.snapshot("restore")

        assert "Error" in result or "required" in result.lower()

    def test_snapshot_restore_not_found(self):
        """Test restoring non-existent snapshot."""
        result = self.handler.snapshot("restore", name="nonexistent")

        assert "not found" in result.lower()

    def test_snapshot_restore_success(self):
        """Test successful snapshot restore."""
        # Create a fake snapshot file
        snapshot_path = os.path.join(self.test_snapshot_dir, "test_snap.blend")
        with open(snapshot_path, "w") as f:
            f.write("fake blend file")

        result = self.handler.snapshot("restore", name="test_snap")

        self.mock_bpy.ops.wm.open_mainfile.assert_called_once()
        assert "Restored" in result

    def test_snapshot_list_empty(self):
        """Test listing when no snapshots exist."""
        result = self.handler.snapshot("list")

        assert "No snapshots" in result

    def test_snapshot_list_with_files(self):
        """Test listing available snapshots."""
        # Create fake snapshot files
        for name in ["snap1", "snap2"]:
            with open(os.path.join(self.test_snapshot_dir, f"{name}.blend"), "w") as f:
                f.write("fake")

        result = self.handler.snapshot("list")

        assert "snap1" in result
        assert "snap2" in result

    def test_snapshot_delete_requires_name(self):
        """Test that delete requires name."""
        result = self.handler.snapshot("delete")

        assert "Error" in result or "required" in result.lower()

    def test_snapshot_delete_not_found(self):
        """Test deleting non-existent snapshot."""
        result = self.handler.snapshot("delete", name="nonexistent")

        assert "not found" in result.lower()

    def test_snapshot_delete_success(self):
        """Test successful snapshot deletion."""
        # Create a fake snapshot file
        snapshot_path = os.path.join(self.test_snapshot_dir, "to_delete.blend")
        with open(snapshot_path, "w") as f:
            f.write("fake blend file")

        result = self.handler.snapshot("delete", name="to_delete")

        assert "Deleted" in result
        assert not os.path.exists(snapshot_path)

    def test_snapshot_invalid_action(self):
        """Test invalid action."""
        result = self.handler.snapshot("invalid_action")

        assert "Unknown action" in result

    def test_snapshot_name_sanitization(self):
        """Test that snapshot names are sanitized."""
        result = self.handler.snapshot("save", name="my/../dangerous/../../name")

        # Name should be sanitized to safe characters only
        call_args = self.mock_bpy.ops.wm.save_as_mainfile.call_args
        filepath = call_args[1]["filepath"]
        assert "../" not in filepath
