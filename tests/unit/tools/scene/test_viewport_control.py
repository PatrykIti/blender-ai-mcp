import sys
import unittest
from unittest.mock import MagicMock, mock_open, patch

# Mock blender modules before import
if "bpy" not in sys.modules:
    sys.modules["bpy"] = MagicMock()
import bpy
from blender_addon.application.handlers.scene import SceneHandler


class TestViewportControl(unittest.TestCase):
    def setUp(self):
        # Reset OPS mocks to ensure isolation between tests
        bpy.ops.object = MagicMock()
        bpy.ops.render = MagicMock()
        bpy.ops.view3d = MagicMock()

        self.handler = SceneHandler()

        # Setup Viewport Mock Structure
        self.mock_shading = MagicMock()
        # Initial state
        self.mock_shading.type = "SOLID"

        self.mock_space = MagicMock()
        self.mock_space.type = "VIEW_3D"
        self.mock_space.shading = self.mock_shading

        self.mock_region = MagicMock()
        self.mock_region.type = "WINDOW"

        self.mock_area = MagicMock()
        self.mock_area.type = "VIEW_3D"
        self.mock_area.spaces = [self.mock_space]
        self.mock_area.regions = [self.mock_region]

        # Mock screen areas
        bpy.context.screen.areas = [self.mock_area]

        # Mock temp_override context manager
        self.mock_override = MagicMock()
        self.mock_override.__enter__ = MagicMock()
        self.mock_override.__exit__ = MagicMock()
        bpy.context.temp_override = MagicMock(return_value=self.mock_override)

        # Mock Objects Collection (supports dict access AND .remove)
        self.mock_objects_collection = MagicMock()
        self._objects_storage = {}

        # Bind dictionary methods
        self.mock_objects_collection.__getitem__.side_effect = self._objects_storage.__getitem__
        self.mock_objects_collection.__contains__.side_effect = self._objects_storage.__contains__
        self.mock_objects_collection.get.side_effect = self._objects_storage.get

        bpy.data.objects = self.mock_objects_collection

        # Helper to add objects in tests
        self.add_object("Cube")

        # Mock scene render properties
        self.render_mock = bpy.context.scene.render
        self.render_mock.resolution_x = 1920
        self.render_mock.resolution_y = 1080
        self.render_mock.filepath = "/tmp/old.png"

    def add_object(self, name):
        obj = MagicMock()
        obj.name = name
        self._objects_storage[name] = obj
        return obj

    @patch("os.path.getsize")
    @patch("os.rmdir")
    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=b"img_data")
    @patch("tempfile.mkdtemp")
    @patch("os.remove")
    def test_dynamic_view_with_shading(
        self, mock_remove, mock_mkdtemp, mock_open, mock_exists, mock_rmdir, mock_getsize
    ):
        # Setup
        mock_mkdtemp.return_value = "/tmp/render_dir"
        # Mock file existence logic:
        # We need to simulate that the file exists AFTER render.opengl is called.
        mock_exists.return_value = True
        mock_getsize.return_value = 100  # Non-empty file

        # Initial Camera
        original_cam = MagicMock()
        bpy.context.scene.camera = original_cam

        cube = self._objects_storage["Cube"]

        # Execute: Get Wireframe View of 'Cube'
        self.handler.get_viewport(
            width=800, height=600, shading="WIREFRAME", camera_name="USER_PERSPECTIVE", focus_target="Cube"
        )

        # 1. USER_PERSPECTIVE should prefer the live viewport OpenGL path without creating a temp camera.
        bpy.ops.object.camera_add.assert_not_called()

        # 2. Verify Target Selected
        cube.select_set.assert_called_with(True)

        # 3. Verify OpenGL render used the active 3D view directly.
        bpy.context.temp_override.assert_any_call(area=self.mock_area, region=self.mock_region)
        bpy.ops.view3d.camera_to_view_selected.assert_not_called()
        bpy.ops.view3d.camera_to_view.assert_not_called()

        # 4. Verify Render (OpenGL attempted first)
        bpy.ops.render.opengl.assert_called_with(write_still=True)

        # 5. Verify Cleanup/Restore
        # Original camera restored
        self.assertEqual(bpy.context.scene.camera, original_cam)
        # Resolution restored
        self.assertEqual(self.render_mock.resolution_x, 1920)

    @patch("os.path.getsize")
    @patch("os.rmdir")
    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=b"img_data")
    @patch("tempfile.mkdtemp")
    @patch("os.remove")
    def test_specific_camera(self, mock_remove, mock_mkdtemp, mock_open, mock_exists, mock_rmdir, mock_getsize):
        # Setup
        mock_mkdtemp.return_value = "/tmp/render_dir"
        mock_exists.return_value = True
        mock_getsize.return_value = 100

        # Mock existing camera in scene
        self.add_object("MyCamera")

        # Execute
        self.handler.get_viewport(camera_name="MyCamera")

        # Verify:
        # 1. NO temp camera created
        bpy.ops.object.camera_add.assert_not_called()
        # 2. Explicit camera renders should not use the live user viewport OpenGL path
        bpy.ops.render.opengl.assert_not_called()
        # 3. Render should use the scene camera path instead
        bpy.ops.render.render.assert_called_with(write_still=True)

    @patch("os.path.getsize")
    @patch("os.rmdir")
    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=b"img_data")
    @patch("tempfile.mkdtemp")
    @patch("os.remove")
    def test_user_view_adjustments_copy_view_to_temp_camera_and_restore(
        self, mock_remove, mock_mkdtemp, mock_open, mock_exists, mock_rmdir, mock_getsize
    ):
        mock_mkdtemp.return_value = "/tmp/render_dir"
        mock_exists.return_value = True
        mock_getsize.return_value = 100

        self.handler.set_standard_view = MagicMock(return_value="view ok")
        self.handler.camera_focus = MagicMock(return_value="focus ok")
        self.handler.camera_orbit = MagicMock(return_value="orbit ok")
        self.handler.get_view_state = MagicMock(
            return_value={
                "available": True,
                "view_location": [1.0, 2.0, 3.0],
                "view_distance": 10.0,
                "view_rotation": [1.0, 0.0, 0.0, 0.0],
                "view_perspective": "PERSP",
            }
        )
        self.handler.restore_view_state = MagicMock(return_value="restored")

        self.handler.get_viewport(
            width=640,
            height=480,
            shading="SOLID",
            camera_name="USER_PERSPECTIVE",
            focus_target="Cube",
            view_name="TOP",
            orbit_horizontal=25.0,
            orbit_vertical=-10.0,
            zoom_factor=1.5,
            persist_view=False,
        )

        self.handler.set_standard_view.assert_called_once_with("TOP")
        self.handler.camera_focus.assert_called_once_with("Cube", zoom_factor=1.5)
        self.handler.camera_orbit.assert_called_once_with(
            angle_horizontal=25.0,
            angle_vertical=-10.0,
            target_object="Cube",
        )
        bpy.ops.object.camera_add.assert_not_called()
        bpy.ops.view3d.camera_to_view.assert_not_called()
        bpy.ops.view3d.camera_to_view_selected.assert_not_called()
        self.handler.restore_view_state.assert_called_once()

    @patch("os.path.getsize")
    @patch("os.rmdir")
    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=b"img_data")
    @patch("tempfile.mkdtemp")
    @patch("os.remove")
    def test_user_perspective_fallback_copies_current_view_to_temp_camera(
        self, mock_remove, mock_mkdtemp, mock_open, mock_exists, mock_rmdir, mock_getsize
    ):
        mock_mkdtemp.return_value = "/tmp/render_dir"
        mock_exists.side_effect = [False, True, True]
        mock_getsize.return_value = 100

        self.handler.get_viewport(
            width=640,
            height=480,
            shading="SOLID",
            camera_name="USER_PERSPECTIVE",
        )

        bpy.ops.render.opengl.assert_called_with(write_still=True)
        bpy.ops.object.camera_add.assert_called_once()
        bpy.ops.view3d.camera_to_view.assert_called_once()
        bpy.ops.view3d.camera_to_view_selected.assert_not_called()
        bpy.ops.render.render.assert_called_with(write_still=True)

    @patch("os.path.getsize")
    @patch("os.rmdir")
    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=b"img_data")
    @patch("tempfile.mkdtemp")
    @patch("os.remove")
    def test_explicit_camera_rejects_user_view_adjustments(
        self, mock_remove, mock_mkdtemp, mock_open, mock_exists, mock_rmdir, mock_getsize
    ):
        mock_mkdtemp.return_value = "/tmp/render_dir"
        mock_exists.return_value = True
        mock_getsize.return_value = 100
        self.add_object("MyCamera")

        with self.assertRaisesRegex(ValueError, "only supported with USER_PERSPECTIVE"):
            self.handler.get_viewport(
                camera_name="MyCamera",
                view_name="TOP",
            )

    def test_view_diagnostics_user_view_adjustments_restore_state(self):
        self.handler.set_standard_view = MagicMock(return_value="view ok")
        self.handler.camera_focus = MagicMock(return_value="focus ok")
        self.handler.camera_orbit = MagicMock(return_value="orbit ok")
        self.handler.get_view_state = MagicMock(
            return_value={
                "available": True,
                "view_location": [1.0, 2.0, 3.0],
                "view_distance": 10.0,
                "view_rotation": [1.0, 0.0, 0.0, 0.0],
                "view_perspective": "PERSP",
            }
        )
        self.handler.restore_view_state = MagicMock(return_value="restored")
        self.handler._mirror_user_view_to_temp_camera = MagicMock(return_value=MagicMock(name="TempCamera"))
        self.handler._build_view_target_diagnostic = MagicMock(
            return_value={
                "object_name": "Cube",
                "visibility_verdict": "visible",
                "projection_status": "projected",
                "projection": {
                    "projected_center": {"x": 0.5, "y": 0.5},
                    "center_offset": {"x": 0.0, "y": 0.0},
                    "frame_coverage_ratio": 1.0,
                    "frame_occupancy_ratio": 0.04,
                    "centered": True,
                    "sample_count": 7,
                    "in_front_sample_count": 7,
                    "in_frame_sample_count": 7,
                    "visible_sample_count": 7,
                    "occluded_sample_count": 0,
                    "occlusion_test_available": True,
                },
            }
        )
        self.handler._summarize_view_diagnostics = MagicMock(
            return_value={
                "target_count": 1,
                "visible_count": 1,
                "partially_visible_count": 0,
                "fully_occluded_count": 0,
                "outside_frame_count": 0,
                "unavailable_count": 0,
                "centered_target_count": 1,
                "framing_issue_count": 0,
            }
        )

        diagnostics = self.handler.get_view_diagnostics(
            target_object="Cube",
            camera_name="USER_PERSPECTIVE",
            focus_target="Cube",
            view_name="TOP",
            orbit_horizontal=25.0,
            orbit_vertical=-10.0,
            zoom_factor=1.5,
            persist_view=False,
        )

        self.handler.set_standard_view.assert_called_once_with("TOP")
        self.handler.camera_focus.assert_called_once_with("Cube", zoom_factor=1.5)
        self.handler.camera_orbit.assert_called_once_with(
            angle_horizontal=25.0,
            angle_vertical=-10.0,
            target_object="Cube",
        )
        self.handler.restore_view_state.assert_called_once()
        assert diagnostics["view_query"]["requested_view_source"] == "user_perspective"
        assert diagnostics["view_query"]["state_restored"] is True

    def test_view_diagnostics_explicit_camera_rejects_user_view_adjustments(self):
        self.add_object("MyCamera")

        with self.assertRaisesRegex(ValueError, "only supported with USER_PERSPECTIVE diagnostics"):
            self.handler.get_view_diagnostics(
                target_object="Cube",
                camera_name="MyCamera",
                view_name="TOP",
            )

    def test_view_diagnostics_explicit_camera_rejects_non_camera_object(self):
        non_camera = self.add_object("MeshObject")
        non_camera.type = "MESH"

        with self.assertRaisesRegex(ValueError, "is not a camera"):
            self.handler.get_view_diagnostics(
                target_object="Cube",
                camera_name="MeshObject",
            )


if __name__ == "__main__":
    unittest.main()
