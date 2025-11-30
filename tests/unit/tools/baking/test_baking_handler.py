"""
Unit tests for TASK-031: Baking Tools

Tests:
- bake_normal_map
- bake_ao
- bake_combined
- bake_diffuse
"""

import unittest
from unittest.mock import MagicMock, patch, PropertyMock
import sys
import os

# Mock blender modules
if 'bpy' not in sys.modules:
    sys.modules['bpy'] = MagicMock()

import bpy

from blender_addon.application.handlers.baking import BakingHandler


class TestBakeNormalMap(unittest.TestCase):
    """Tests for bake_normal_map (TASK-031-1)"""

    def setUp(self):
        self.handler = BakingHandler()

        # Reset mocks
        bpy.context.scene.render.engine = 'EEVEE'
        bpy.context.scene.render.bake = MagicMock()
        bpy.context.view_layer.objects = MagicMock()
        bpy.ops.object.select_all = MagicMock()
        bpy.ops.object.bake = MagicMock()

        # Mock object
        self.mock_obj = MagicMock()
        self.mock_obj.name = "TestObject"
        self.mock_obj.type = 'MESH'
        self.mock_obj.data.uv_layers = MagicMock()
        self.mock_obj.data.uv_layers.__bool__ = lambda x: True
        self.mock_obj.data.uv_layers.active = MagicMock()
        self.mock_obj.data.materials = [MagicMock()]
        self.mock_obj.data.materials[0].use_nodes = True
        self.mock_obj.data.materials[0].node_tree.nodes = MagicMock()
        self.mock_obj.data.materials[0].node_tree.nodes.__iter__ = lambda x: iter([])
        self.mock_obj.data.materials[0].node_tree.nodes.new = MagicMock(return_value=MagicMock())

        bpy.data.objects.get = MagicMock(return_value=self.mock_obj)

        # Mock image
        self.mock_image = MagicMock()
        self.mock_image.colorspace_settings = MagicMock()
        bpy.data.images.new = MagicMock(return_value=self.mock_image)
        bpy.data.images.__contains__ = MagicMock(return_value=False)

    def test_bake_normal_self_bake(self):
        """Test normal map self-bake (no high-poly source)"""
        result = self.handler.bake_normal_map(
            object_name="TestObject",
            output_path="/tmp/normal.png",
            resolution=1024
        )

        # Verify bake was called
        bpy.ops.object.bake.assert_called_once_with(type='NORMAL')

        # Verify result message
        self.assertIn("normal map", result.lower())
        self.assertIn("self-bake", result)
        self.assertIn("1024x1024", result)

    def test_bake_normal_high_to_low(self):
        """Test normal map baking from high-poly source"""
        # Setup high-poly source
        self.mock_high_poly = MagicMock()
        self.mock_high_poly.name = "HighPoly"

        def get_object(name):
            if name == "TestObject":
                return self.mock_obj
            elif name == "HighPoly":
                return self.mock_high_poly
            return None

        bpy.data.objects.get = MagicMock(side_effect=get_object)

        result = self.handler.bake_normal_map(
            object_name="TestObject",
            output_path="/tmp/normal.png",
            high_poly_source="HighPoly",
            cage_extrusion=0.2
        )

        # Verify high-to-low settings
        self.assertTrue(bpy.context.scene.render.bake.use_selected_to_active)
        self.assertEqual(bpy.context.scene.render.bake.cage_extrusion, 0.2)

        # Verify result message
        self.assertIn("high-to-low", result)
        self.assertIn("HighPoly", result)

    def test_bake_normal_tangent_space(self):
        """Test normal map with TANGENT space (default)"""
        result = self.handler.bake_normal_map(
            object_name="TestObject",
            output_path="/tmp/normal.png",
            normal_space="TANGENT"
        )

        self.assertEqual(bpy.context.scene.render.bake.normal_space, 'TANGENT')
        self.assertIn("TANGENT", result)

    def test_bake_normal_object_space(self):
        """Test normal map with OBJECT space"""
        result = self.handler.bake_normal_map(
            object_name="TestObject",
            output_path="/tmp/normal.png",
            normal_space="OBJECT"
        )

        self.assertEqual(bpy.context.scene.render.bake.normal_space, 'OBJECT')
        self.assertIn("OBJECT", result)

    def test_bake_normal_invalid_space_raises(self):
        """Test that invalid normal_space raises error"""
        with self.assertRaises(ValueError) as context:
            self.handler.bake_normal_map(
                object_name="TestObject",
                output_path="/tmp/normal.png",
                normal_space="INVALID"
            )

        self.assertIn("Invalid normal_space", str(context.exception))

    def test_bake_normal_object_not_found_raises(self):
        """Test that missing object raises error"""
        bpy.data.objects.get = MagicMock(return_value=None)

        with self.assertRaises(ValueError) as context:
            self.handler.bake_normal_map(
                object_name="NonExistent",
                output_path="/tmp/normal.png"
            )

        self.assertIn("not found", str(context.exception))

    def test_bake_normal_no_uv_raises(self):
        """Test that missing UV map raises error"""
        # Mock empty UV layers
        mock_uv = MagicMock()
        mock_uv.__bool__ = MagicMock(return_value=False)
        self.mock_obj.data.uv_layers = mock_uv

        with self.assertRaises(ValueError) as context:
            self.handler.bake_normal_map(
                object_name="TestObject",
                output_path="/tmp/normal.png"
            )

        self.assertIn("no UV map", str(context.exception))


class TestBakeAO(unittest.TestCase):
    """Tests for bake_ao (TASK-031-2)"""

    def setUp(self):
        self.handler = BakingHandler()

        # Reset mocks
        bpy.context.scene.render.engine = 'EEVEE'
        bpy.context.scene.render.bake = MagicMock()
        bpy.context.scene.cycles = MagicMock()
        bpy.context.scene.world = MagicMock()
        bpy.context.scene.world.light_settings = MagicMock()
        bpy.context.view_layer.objects = MagicMock()
        bpy.ops.object.select_all = MagicMock()
        bpy.ops.object.bake = MagicMock()

        # Mock object
        self.mock_obj = MagicMock()
        self.mock_obj.name = "TestObject"
        self.mock_obj.type = 'MESH'
        self.mock_obj.data.uv_layers = MagicMock()
        self.mock_obj.data.uv_layers.__bool__ = lambda x: True
        self.mock_obj.data.uv_layers.active = MagicMock()
        self.mock_obj.data.materials = [MagicMock()]
        self.mock_obj.data.materials[0].use_nodes = True
        self.mock_obj.data.materials[0].node_tree.nodes = MagicMock()
        self.mock_obj.data.materials[0].node_tree.nodes.__iter__ = lambda x: iter([])
        self.mock_obj.data.materials[0].node_tree.nodes.new = MagicMock(return_value=MagicMock())

        bpy.data.objects.get = MagicMock(return_value=self.mock_obj)

        # Mock image
        self.mock_image = MagicMock()
        self.mock_image.colorspace_settings = MagicMock()
        bpy.data.images.new = MagicMock(return_value=self.mock_image)
        bpy.data.images.__contains__ = MagicMock(return_value=False)

    def test_bake_ao_default(self):
        """Test AO baking with default parameters"""
        result = self.handler.bake_ao(
            object_name="TestObject",
            output_path="/tmp/ao.png"
        )

        # Verify bake was called with AO type
        bpy.ops.object.bake.assert_called_once_with(type='AO')

        # Verify result message
        self.assertIn("AO map", result)
        self.assertIn("1024x1024", result)

    def test_bake_ao_custom_samples(self):
        """Test AO baking with custom samples"""
        result = self.handler.bake_ao(
            object_name="TestObject",
            output_path="/tmp/ao.png",
            samples=256
        )

        self.assertEqual(bpy.context.scene.cycles.samples, 256)
        self.assertIn("256 samples", result)

    def test_bake_ao_custom_distance(self):
        """Test AO baking with custom distance"""
        result = self.handler.bake_ao(
            object_name="TestObject",
            output_path="/tmp/ao.png",
            distance=2.0
        )

        self.assertEqual(bpy.context.scene.world.light_settings.distance, 2.0)


class TestBakeCombined(unittest.TestCase):
    """Tests for bake_combined (TASK-031-3)"""

    def setUp(self):
        self.handler = BakingHandler()

        # Reset mocks
        bpy.context.scene.render.engine = 'EEVEE'
        bpy.context.scene.render.bake = MagicMock()
        bpy.context.scene.cycles = MagicMock()
        bpy.context.view_layer.objects = MagicMock()
        bpy.ops.object.select_all = MagicMock()
        bpy.ops.object.bake = MagicMock()

        # Mock object
        self.mock_obj = MagicMock()
        self.mock_obj.name = "TestObject"
        self.mock_obj.type = 'MESH'
        self.mock_obj.data.uv_layers = MagicMock()
        self.mock_obj.data.uv_layers.__bool__ = lambda x: True
        self.mock_obj.data.uv_layers.active = MagicMock()
        self.mock_obj.data.materials = [MagicMock()]
        self.mock_obj.data.materials[0].use_nodes = True
        self.mock_obj.data.materials[0].node_tree.nodes = MagicMock()
        self.mock_obj.data.materials[0].node_tree.nodes.__iter__ = lambda x: iter([])
        self.mock_obj.data.materials[0].node_tree.nodes.new = MagicMock(return_value=MagicMock())

        bpy.data.objects.get = MagicMock(return_value=self.mock_obj)

        # Mock image
        self.mock_image = MagicMock()
        self.mock_image.colorspace_settings = MagicMock()
        bpy.data.images.new = MagicMock(return_value=self.mock_image)
        bpy.data.images.__contains__ = MagicMock(return_value=False)

    def test_bake_combined_default(self):
        """Test combined baking with default parameters"""
        result = self.handler.bake_combined(
            object_name="TestObject",
            output_path="/tmp/combined.png"
        )

        # Verify bake was called with COMBINED type
        bpy.ops.object.bake.assert_called_once_with(type='COMBINED')

        # Verify pass settings
        self.assertTrue(bpy.context.scene.render.bake.use_pass_direct)
        self.assertTrue(bpy.context.scene.render.bake.use_pass_indirect)
        self.assertTrue(bpy.context.scene.render.bake.use_pass_color)

        # Verify result message
        self.assertIn("combined map", result)

    def test_bake_combined_direct_only(self):
        """Test combined baking with only direct lighting"""
        result = self.handler.bake_combined(
            object_name="TestObject",
            output_path="/tmp/combined.png",
            use_pass_direct=True,
            use_pass_indirect=False,
            use_pass_color=False
        )

        self.assertTrue(bpy.context.scene.render.bake.use_pass_direct)
        self.assertFalse(bpy.context.scene.render.bake.use_pass_indirect)
        self.assertFalse(bpy.context.scene.render.bake.use_pass_color)


class TestBakeDiffuse(unittest.TestCase):
    """Tests for bake_diffuse (TASK-031-4)"""

    def setUp(self):
        self.handler = BakingHandler()

        # Reset mocks
        bpy.context.scene.render.engine = 'EEVEE'
        bpy.context.scene.render.bake = MagicMock()
        bpy.context.view_layer.objects = MagicMock()
        bpy.ops.object.select_all = MagicMock()
        bpy.ops.object.bake = MagicMock()

        # Mock object
        self.mock_obj = MagicMock()
        self.mock_obj.name = "TestObject"
        self.mock_obj.type = 'MESH'
        self.mock_obj.data.uv_layers = MagicMock()
        self.mock_obj.data.uv_layers.__bool__ = lambda x: True
        self.mock_obj.data.uv_layers.active = MagicMock()
        self.mock_obj.data.materials = [MagicMock()]
        self.mock_obj.data.materials[0].use_nodes = True
        self.mock_obj.data.materials[0].node_tree.nodes = MagicMock()
        self.mock_obj.data.materials[0].node_tree.nodes.__iter__ = lambda x: iter([])
        self.mock_obj.data.materials[0].node_tree.nodes.new = MagicMock(return_value=MagicMock())

        bpy.data.objects.get = MagicMock(return_value=self.mock_obj)

        # Mock image
        self.mock_image = MagicMock()
        self.mock_image.colorspace_settings = MagicMock()
        bpy.data.images.new = MagicMock(return_value=self.mock_image)
        bpy.data.images.__contains__ = MagicMock(return_value=False)

    def test_bake_diffuse_default(self):
        """Test diffuse baking with default parameters"""
        result = self.handler.bake_diffuse(
            object_name="TestObject",
            output_path="/tmp/diffuse.png"
        )

        # Verify bake was called with DIFFUSE type
        bpy.ops.object.bake.assert_called_once_with(type='DIFFUSE')

        # Verify lighting passes are disabled
        self.assertFalse(bpy.context.scene.render.bake.use_pass_direct)
        self.assertFalse(bpy.context.scene.render.bake.use_pass_indirect)
        self.assertTrue(bpy.context.scene.render.bake.use_pass_color)

        # Verify result message
        self.assertIn("diffuse map", result)
        self.assertIn("1024x1024", result)

    def test_bake_diffuse_custom_resolution(self):
        """Test diffuse baking with custom resolution"""
        result = self.handler.bake_diffuse(
            object_name="TestObject",
            output_path="/tmp/diffuse.png",
            resolution=2048
        )

        # Verify image was created
        bpy.data.images.new.assert_called()

        # Verify result mentions the resolution
        self.assertIn("2048x2048", result)


if __name__ == '__main__':
    unittest.main()
