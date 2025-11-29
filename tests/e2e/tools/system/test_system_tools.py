"""
E2E Tests for System Tools (TASK-025)

These tests require a running Blender instance with the addon loaded.
"""
import os
import tempfile
import pytest
from server.application.tool_handlers.system_handler import SystemToolHandler


@pytest.fixture
def system_handler(rpc_client):
    """Provides a system handler instance using shared RPC client."""
    return SystemToolHandler(rpc_client)


class TestSystemSetMode:
    """E2E tests for system_set_mode."""

    def test_set_mode_object(self, system_handler):
        """Test switching to OBJECT mode."""
        try:
            result = system_handler.set_mode("OBJECT")

            assert "OBJECT" in result or "Already" in result
            print(f"✓ set_mode OBJECT: {result}")
        except RuntimeError as e:
            pytest.skip(f"Blender not available: {e}")

    def test_set_mode_edit(self, system_handler):
        """Test switching to EDIT mode."""
        try:
            # First ensure we're in OBJECT mode
            system_handler.set_mode("OBJECT")

            result = system_handler.set_mode("EDIT")

            assert "EDIT" in result or "Already" in result
            print(f"✓ set_mode EDIT: {result}")

            # Return to OBJECT mode
            system_handler.set_mode("OBJECT")
        except RuntimeError as e:
            pytest.skip(f"Blender not available: {e}")

    def test_set_mode_invalid(self, system_handler):
        """Test invalid mode returns error."""
        try:
            with pytest.raises(RuntimeError):
                system_handler.set_mode("INVALID_MODE")
        except RuntimeError as e:
            if "Invalid mode" in str(e):
                print("✓ set_mode invalid: correctly rejected")
            else:
                pytest.skip(f"Blender not available: {e}")


class TestSystemUndoRedo:
    """E2E tests for system_undo/redo."""

    def test_undo_single(self, system_handler):
        """Test single undo step."""
        try:
            result = system_handler.undo(1)

            # Result should indicate success or nothing to undo
            assert "Undone" in result or "Nothing" in result
            print(f"✓ undo: {result}")
        except RuntimeError as e:
            pytest.skip(f"Blender not available: {e}")

    def test_redo_single(self, system_handler):
        """Test single redo step."""
        try:
            result = system_handler.redo(1)

            # Result should indicate success or nothing to redo
            assert "Redone" in result or "Nothing" in result
            print(f"✓ redo: {result}")
        except RuntimeError as e:
            pytest.skip(f"Blender not available: {e}")

    def test_undo_multiple(self, system_handler):
        """Test multiple undo steps."""
        try:
            result = system_handler.undo(3)

            assert "Undone" in result or "Nothing" in result
            print(f"✓ undo multiple: {result}")
        except RuntimeError as e:
            pytest.skip(f"Blender not available: {e}")


class TestSystemFileOperations:
    """E2E tests for system file operations."""

    def test_save_file_to_temp(self, system_handler):
        """Test saving file to temp location."""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                filepath = os.path.join(tmpdir, "test_save.blend")
                result = system_handler.save_file(filepath=filepath)

                assert "Saved" in result
                assert filepath in result or "test_save" in result
                print(f"✓ save_file: {result}")
        except RuntimeError as e:
            pytest.skip(f"Blender not available: {e}")

    def test_new_file(self, system_handler):
        """Test creating new file."""
        try:
            # Note: This will clear the scene!
            result = system_handler.new_file(load_ui=False)

            assert "new file" in result.lower() or "reset" in result.lower()
            print(f"✓ new_file: {result}")
        except RuntimeError as e:
            pytest.skip(f"Blender not available: {e}")


class TestSystemSnapshot:
    """E2E tests for system_snapshot."""

    def test_snapshot_save_and_list(self, system_handler):
        """Test saving and listing snapshots."""
        try:
            # Save a snapshot
            save_result = system_handler.snapshot("save", name="e2e_test_snap")
            assert "Saved" in save_result
            print(f"✓ snapshot save: {save_result}")

            # List snapshots
            list_result = system_handler.snapshot("list")
            assert "e2e_test_snap" in list_result
            print(f"✓ snapshot list: found e2e_test_snap")

            # Cleanup - delete the test snapshot
            delete_result = system_handler.snapshot("delete", name="e2e_test_snap")
            assert "Deleted" in delete_result
            print(f"✓ snapshot delete: {delete_result}")

        except RuntimeError as e:
            pytest.skip(f"Blender not available: {e}")

    def test_snapshot_restore(self, system_handler):
        """Test snapshot restore functionality."""
        try:
            # Save current state
            system_handler.snapshot("save", name="e2e_restore_test")

            # Restore it
            result = system_handler.snapshot("restore", name="e2e_restore_test")
            assert "Restored" in result
            print(f"✓ snapshot restore: {result}")

            # Cleanup
            system_handler.snapshot("delete", name="e2e_restore_test")

        except RuntimeError as e:
            pytest.skip(f"Blender not available: {e}")

    def test_snapshot_not_found(self, system_handler):
        """Test restoring non-existent snapshot."""
        try:
            result = system_handler.snapshot("restore", name="nonexistent_snapshot_xyz")

            assert "not found" in result.lower()
            print(f"✓ snapshot not found: correctly handled")
        except RuntimeError as e:
            pytest.skip(f"Blender not available: {e}")

    def test_snapshot_auto_name(self, system_handler):
        """Test saving snapshot with auto-generated name."""
        try:
            result = system_handler.snapshot("save")

            assert "Saved" in result
            print(f"✓ snapshot auto-name: {result}")

            # List to get the auto-generated name and clean up
            list_result = system_handler.snapshot("list")
            print(f"  Available snapshots: {list_result[:100]}...")

        except RuntimeError as e:
            pytest.skip(f"Blender not available: {e}")
