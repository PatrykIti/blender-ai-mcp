"""
Unit tests for Material Tools (TASK-023)

Tests material creation, assignment, parameter modification, and texture binding.
"""
import unittest
from unittest.mock import MagicMock, patch, PropertyMock
import sys

# Mock blender modules
if 'bpy' not in sys.modules:
    sys.modules['bpy'] = MagicMock()

import bpy

from blender_addon.application.handlers.material import MaterialHandler


class TestMaterialCreate(unittest.TestCase):
    """Tests for material_create (TASK-023-1)"""

    def setUp(self):
        self.handler = MaterialHandler()

        # Reset mocks
        bpy.data.materials = MagicMock()
        bpy.data.materials.new = MagicMock()

    def test_create_basic_material(self):
        """Test creating a basic material with default parameters."""
        # Setup mock material
        mock_mat = MagicMock()
        mock_mat.name = "TestMaterial"
        mock_mat.use_nodes = True

        mock_bsdf = MagicMock()
        mock_bsdf.inputs = {
            "Base Color": MagicMock(),
            "Metallic": MagicMock(),
            "Roughness": MagicMock(),
            "Emission Color": MagicMock(),
            "Emission Strength": MagicMock(),
            "Alpha": MagicMock(),
        }

        mock_mat.node_tree.nodes.get.return_value = mock_bsdf
        bpy.data.materials.new.return_value = mock_mat

        # Execute
        result = self.handler.create_material(name="TestMaterial")

        # Verify
        bpy.data.materials.new.assert_called_with(name="TestMaterial")
        self.assertIn("Created material", result)
        self.assertIn("TestMaterial", result)

    def test_create_material_with_color(self):
        """Test creating a material with custom base color."""
        mock_mat = MagicMock()
        mock_mat.name = "ColorMat"
        mock_mat.use_nodes = True

        mock_bsdf = MagicMock()
        mock_base_color_input = MagicMock()
        mock_bsdf.inputs = {
            "Base Color": mock_base_color_input,
            "Metallic": MagicMock(),
            "Roughness": MagicMock(),
            "Emission Color": MagicMock(),
            "Emission Strength": MagicMock(),
            "Alpha": MagicMock(),
        }

        mock_mat.node_tree.nodes.get.return_value = mock_bsdf
        bpy.data.materials.new.return_value = mock_mat

        # Execute with RGB color (should auto-add alpha)
        result = self.handler.create_material(
            name="ColorMat",
            base_color=[1.0, 0.0, 0.0]
        )

        # Verify material was created
        bpy.data.materials.new.assert_called_with(name="ColorMat")
        self.assertIn("Created material", result)

    def test_create_material_with_transparency(self):
        """Test creating a material with transparency."""
        mock_mat = MagicMock()
        mock_mat.name = "TransparentMat"
        mock_mat.use_nodes = True

        mock_bsdf = MagicMock()
        mock_alpha_input = MagicMock()
        mock_bsdf.inputs = {
            "Base Color": MagicMock(),
            "Metallic": MagicMock(),
            "Roughness": MagicMock(),
            "Emission Color": MagicMock(),
            "Emission Strength": MagicMock(),
            "Alpha": mock_alpha_input,
        }

        mock_mat.node_tree.nodes.get.return_value = mock_bsdf
        bpy.data.materials.new.return_value = mock_mat

        # Execute with alpha < 1.0
        result = self.handler.create_material(
            name="TransparentMat",
            alpha=0.5
        )

        # Verify blend method was set (shadow_method removed in Blender 4.2+)
        self.assertEqual(mock_mat.blend_method, 'BLEND')
        self.assertIn("Created material", result)


class TestMaterialAssign(unittest.TestCase):
    """Tests for material_assign (TASK-023-2)"""

    def setUp(self):
        self.handler = MaterialHandler()

        # Reset mocks
        bpy.data.materials = MagicMock()
        bpy.data.objects = MagicMock()
        bpy.context.active_object = MagicMock()
        bpy.ops.object.material_slot_assign = MagicMock()

    def test_assign_to_object(self):
        """Test assigning material to an object."""
        # Setup mock material
        mock_mat = MagicMock()
        mock_mat.name = "TestMat"
        bpy.data.materials.get.return_value = mock_mat

        # Setup mock object
        mock_obj = MagicMock()
        mock_obj.name = "Cube"
        mock_obj.mode = 'OBJECT'
        mock_obj.material_slots = []
        mock_obj.data.materials = MagicMock()
        mock_obj.data.materials.append = MagicMock()

        bpy.data.objects.get.return_value = mock_obj

        # Execute
        result = self.handler.assign_material(
            material_name="TestMat",
            object_name="Cube"
        )

        # Verify
        mock_obj.data.materials.append.assert_called_with(mock_mat)
        self.assertIn("Assigned", result)
        self.assertIn("TestMat", result)
        self.assertIn("Cube", result)

    def test_assign_material_not_found(self):
        """Test error when material doesn't exist."""
        bpy.data.materials.get.return_value = None

        with self.assertRaises(ValueError) as context:
            self.handler.assign_material(material_name="NonExistent")

        self.assertIn("not found", str(context.exception))

    def test_assign_object_not_found(self):
        """Test error when object doesn't exist."""
        mock_mat = MagicMock()
        bpy.data.materials.get.return_value = mock_mat
        bpy.data.objects.get.return_value = None

        with self.assertRaises(ValueError) as context:
            self.handler.assign_material(
                material_name="TestMat",
                object_name="NonExistent"
            )

        self.assertIn("not found", str(context.exception))

    def test_assign_to_selection_edit_mode(self):
        """Test assigning material to selected faces in Edit Mode."""
        # Setup mock material
        mock_mat = MagicMock()
        mock_mat.name = "FaceMat"
        bpy.data.materials.get.return_value = mock_mat

        # Setup mock object in Edit Mode
        mock_obj = MagicMock()
        mock_obj.name = "Cube"
        mock_obj.mode = 'EDIT'

        # Material already in slot
        mock_slot = MagicMock()
        mock_slot.material = mock_mat
        mock_slot.material.name = "FaceMat"
        mock_obj.material_slots = [mock_slot]

        bpy.data.objects.get.return_value = mock_obj

        # Execute
        result = self.handler.assign_material(
            material_name="FaceMat",
            object_name="Cube",
            assign_to_selection=True
        )

        # Verify
        bpy.ops.object.material_slot_assign.assert_called()
        self.assertIn("selected faces", result)


class TestMaterialSetParams(unittest.TestCase):
    """Tests for material_set_params (TASK-023-3)"""

    def setUp(self):
        self.handler = MaterialHandler()
        bpy.data.materials = MagicMock()

    def test_set_single_param(self):
        """Test modifying a single parameter."""
        # Setup mock material with BSDF
        mock_mat = MagicMock()
        mock_mat.use_nodes = True
        mock_mat.node_tree = MagicMock()

        mock_bsdf = MagicMock()
        mock_bsdf.type = 'BSDF_PRINCIPLED'
        mock_roughness_input = MagicMock()
        mock_bsdf.inputs = {
            "Roughness": mock_roughness_input,
            "Metallic": MagicMock(),
            "Base Color": MagicMock(),
            "Emission Color": MagicMock(),
            "Emission Strength": MagicMock(),
            "Alpha": MagicMock(),
        }

        mock_mat.node_tree.nodes = [mock_bsdf]
        bpy.data.materials.get.return_value = mock_mat

        # Execute
        result = self.handler.set_material_params(
            material_name="TestMat",
            roughness=0.8
        )

        # Verify
        self.assertIn("Updated", result)
        self.assertIn("roughness", result)

    def test_set_multiple_params(self):
        """Test modifying multiple parameters."""
        mock_mat = MagicMock()
        mock_mat.use_nodes = True
        mock_mat.node_tree = MagicMock()

        mock_bsdf = MagicMock()
        mock_bsdf.type = 'BSDF_PRINCIPLED'
        mock_bsdf.inputs = {
            "Roughness": MagicMock(),
            "Metallic": MagicMock(),
            "Base Color": MagicMock(),
            "Emission Color": MagicMock(),
            "Emission Strength": MagicMock(),
            "Alpha": MagicMock(),
        }

        mock_mat.node_tree.nodes = [mock_bsdf]
        bpy.data.materials.get.return_value = mock_mat

        # Execute
        result = self.handler.set_material_params(
            material_name="TestMat",
            roughness=0.2,
            metallic=1.0
        )

        # Verify both params mentioned
        self.assertIn("roughness", result)
        self.assertIn("metallic", result)

    def test_set_params_material_not_found(self):
        """Test error when material doesn't exist."""
        bpy.data.materials.get.return_value = None

        with self.assertRaises(ValueError) as context:
            self.handler.set_material_params(
                material_name="NonExistent",
                roughness=0.5
            )

        self.assertIn("not found", str(context.exception))

    def test_set_params_no_params(self):
        """Test when no parameters provided."""
        mock_mat = MagicMock()
        mock_mat.use_nodes = True
        mock_mat.node_tree = MagicMock()

        mock_bsdf = MagicMock()
        mock_bsdf.type = 'BSDF_PRINCIPLED'
        mock_bsdf.inputs = {}

        mock_mat.node_tree.nodes = [mock_bsdf]
        bpy.data.materials.get.return_value = mock_mat

        # Execute without any params
        result = self.handler.set_material_params(material_name="TestMat")

        # Verify
        self.assertIn("No parameters provided", result)


class TestMaterialSetTexture(unittest.TestCase):
    """Tests for material_set_texture (TASK-023-4)"""

    def setUp(self):
        self.handler = MaterialHandler()
        bpy.data.materials = MagicMock()
        bpy.data.images = MagicMock()

    def test_set_base_color_texture(self):
        """Test binding a base color texture."""
        # Setup mock material
        mock_mat = MagicMock()
        mock_mat.use_nodes = True
        mock_mat.node_tree = MagicMock()

        mock_bsdf = MagicMock()
        mock_bsdf.type = 'BSDF_PRINCIPLED'
        mock_bsdf.location = (0, 0)
        mock_bsdf.inputs = {
            "Base Color": MagicMock(),
            "Normal": MagicMock(),
        }

        mock_mat.node_tree.nodes = MagicMock()
        mock_mat.node_tree.nodes.__iter__ = MagicMock(return_value=iter([mock_bsdf]))
        mock_mat.node_tree.links = MagicMock()

        # Mock texture node creation
        mock_tex_node = MagicMock()
        mock_tex_node.outputs = {"Color": MagicMock()}
        mock_mat.node_tree.nodes.new.return_value = mock_tex_node

        bpy.data.materials.get.return_value = mock_mat

        # Mock image loading
        mock_img = MagicMock()
        mock_img.colorspace_settings = MagicMock()
        bpy.data.images.load.return_value = mock_img

        # Execute
        result = self.handler.set_material_texture(
            material_name="TestMat",
            texture_path="/path/to/texture.png",
            input_name="Base Color"
        )

        # Verify
        bpy.data.images.load.assert_called_with("/path/to/texture.png")
        mock_mat.node_tree.nodes.new.assert_called_with("ShaderNodeTexImage")
        mock_mat.node_tree.links.new.assert_called()
        self.assertIn("Connected texture", result)

    def test_set_normal_texture(self):
        """Test binding a normal map texture (special case)."""
        # Setup mock material
        mock_mat = MagicMock()
        mock_mat.use_nodes = True
        mock_mat.node_tree = MagicMock()

        mock_bsdf = MagicMock()
        mock_bsdf.type = 'BSDF_PRINCIPLED'
        mock_bsdf.location = (0, 0)
        mock_bsdf.inputs = {
            "Normal": MagicMock(),
        }

        mock_mat.node_tree.nodes = MagicMock()
        mock_mat.node_tree.nodes.__iter__ = MagicMock(return_value=iter([mock_bsdf]))
        mock_mat.node_tree.links = MagicMock()

        # Mock node creation - return different nodes for each call
        mock_tex_node = MagicMock()
        mock_tex_node.outputs = {"Color": MagicMock()}

        mock_normal_node = MagicMock()
        mock_normal_node.inputs = {"Color": MagicMock()}
        mock_normal_node.outputs = {"Normal": MagicMock()}

        mock_mat.node_tree.nodes.new.side_effect = [mock_tex_node, mock_normal_node]

        bpy.data.materials.get.return_value = mock_mat

        # Mock image loading
        mock_img = MagicMock()
        mock_img.colorspace_settings = MagicMock()
        bpy.data.images.load.return_value = mock_img

        # Execute
        result = self.handler.set_material_texture(
            material_name="TestMat",
            texture_path="/path/to/normal.png",
            input_name="Normal",
            color_space="Non-Color"
        )

        # Verify normal map node was created
        self.assertEqual(mock_mat.node_tree.nodes.new.call_count, 2)
        self.assertIn("normal map", result.lower())

    def test_set_texture_material_not_found(self):
        """Test error when material doesn't exist."""
        bpy.data.materials.get.return_value = None

        with self.assertRaises(ValueError) as context:
            self.handler.set_material_texture(
                material_name="NonExistent",
                texture_path="/path/to/texture.png"
            )

        self.assertIn("not found", str(context.exception))


if __name__ == '__main__':
    unittest.main()
