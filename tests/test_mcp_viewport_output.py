import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from fastmcp.utilities.types import Image
# Update import to new location
from server.adapters.mcp.areas import scene as mcp_scene

SCENE_GET_VIEWPORT = mcp_scene.scene_get_viewport.fn


class TestMcpViewportOutputModes(unittest.TestCase):
    def setUp(self) -> None:
        self.ctx = MagicMock()

    @patch("server.adapters.mcp.areas.scene.get_scene_handler")
    def test_default_outputs_image_resource(self, mock_get_scene_handler):
        handler = MagicMock()
        handler.get_viewport.return_value = "aGVsbG8="  # "hello" in base64
        mock_get_scene_handler.return_value = handler

        result = SCENE_GET_VIEWPORT(self.ctx)

        self.assertIsInstance(result, Image)
        handler.get_viewport.assert_called_once()

    @patch("server.adapters.mcp.areas.scene.get_scene_handler")
    def test_base64_mode_returns_raw_string(self, mock_get_scene_handler):
        handler = MagicMock()
        handler.get_viewport.return_value = "dGVzdF9iYXNlNjQ="
        mock_get_scene_handler.return_value = handler

        result = SCENE_GET_VIEWPORT(self.ctx, output_mode="BASE64")

        self.assertEqual(result, "dGVzdF9iYXNlNjQ=")

    @patch("server.adapters.mcp.areas.scene.get_scene_handler")
    def test_file_mode_writes_and_returns_paths(self, mock_get_scene_handler):
        handler = MagicMock()
        handler.get_viewport.return_value = "dGVzdF9pbWFnZQ=="  # arbitrary base64
        mock_get_scene_handler.return_value = handler

        with tempfile.TemporaryDirectory() as internal_tmp, tempfile.TemporaryDirectory() as external_tmp:
            with patch.dict(
                os.environ,
                {
                    "BLENDER_AI_TMP_INTERNAL_DIR": internal_tmp,
                    "BLENDER_AI_TMP_EXTERNAL_DIR": external_tmp,
                },
                clear=False,
            ):
                result = SCENE_GET_VIEWPORT(
                    self.ctx,
                    width=800,
                    height=600,
                    shading="SOLID",
                    output_mode="FILE",
                )

        self.assertIn("Timestamped file:", result)
        self.assertIn("Latest file:", result)
        self.assertIn("Resolution: 800x600, shading: SOLID.", result)
        # external_tmp should be reflected in returned paths
        self.assertIn(str(os.path.join(external_tmp, "blender-ai-mcp")), result)

    @patch("server.adapters.mcp.areas.scene.get_scene_handler")
    def test_markdown_mode_returns_data_url_and_path(self, mock_get_scene_handler):
        handler = MagicMock()
        handler.get_viewport.return_value = "dGVzdF9pbWFnZQ=="
        mock_get_scene_handler.return_value = handler

        result = SCENE_GET_VIEWPORT(
            self.ctx,
            width=640,
            height=480,
            shading="WIREFRAME",
            output_mode="MARKDOWN",
        )

        self.assertIn("![Viewport](data:image/jpeg;base64,", result)
        self.assertIn("Viewport render saved to:", result)
        self.assertIn("open the file at", result)

    @patch("server.adapters.mcp.areas.scene.get_scene_handler")
    def test_invalid_mode_returns_error_string(self, mock_get_scene_handler):
        handler = MagicMock()
        handler.get_viewport.return_value = "dGVzdF9pbWFnZQ=="
        mock_get_scene_handler.return_value = handler

        result = SCENE_GET_VIEWPORT(self.ctx, output_mode="INVALID")

        self.assertIsInstance(result, str)
        self.assertIn("Invalid output_mode", result)


if __name__ == "__main__":
    unittest.main()


if __name__ == "__main__":
    unittest.main()
