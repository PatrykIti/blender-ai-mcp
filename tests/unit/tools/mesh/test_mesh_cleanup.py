"""
Unit tests for TASK-030: Mesh Cleanup & Optimization

Tests:
- mesh_dissolve
- mesh_tris_to_quads
- mesh_normals_make_consistent
- mesh_decimate
"""

import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock blender modules
if 'bpy' not in sys.modules:
    sys.modules['bpy'] = MagicMock()
if 'bmesh' not in sys.modules:
    sys.modules['bmesh'] = MagicMock()

import bpy
import bmesh

from blender_addon.application.handlers.mesh import MeshHandler


class TestMeshDissolve(unittest.TestCase):
    """Tests for mesh_dissolve (TASK-030-1)"""

    def setUp(self):
        self.handler = MeshHandler()

        # Reset mocks
        bpy.context.active_object = MagicMock()
        bpy.context.active_object.type = 'MESH'
        bpy.context.active_object.mode = 'EDIT'
        bpy.ops.object.mode_set = MagicMock()

        # Setup dissolve operation mocks
        bpy.ops.mesh.dissolve_limited = MagicMock()
        bpy.ops.mesh.dissolve_verts = MagicMock()
        bpy.ops.mesh.dissolve_edges = MagicMock()
        bpy.ops.mesh.dissolve_faces = MagicMock()

    def test_dissolve_limited_default(self):
        """Test limited dissolve with default parameters"""
        result = self.handler.dissolve()

        bpy.ops.mesh.dissolve_limited.assert_called_once()
        self.assertIn("Limited dissolve", result)
        self.assertIn("5.0", result)  # default angle

    def test_dissolve_limited_custom_angle(self):
        """Test limited dissolve with custom angle"""
        result = self.handler.dissolve(dissolve_type="limited", angle_limit=15.0)

        bpy.ops.mesh.dissolve_limited.assert_called_once()
        self.assertIn("15.0", result)

    def test_dissolve_verts(self):
        """Test dissolve vertices"""
        result = self.handler.dissolve(dissolve_type="verts")

        bpy.ops.mesh.dissolve_verts.assert_called_once()
        self.assertIn("Dissolved selected vertices", result)

    def test_dissolve_edges(self):
        """Test dissolve edges"""
        result = self.handler.dissolve(dissolve_type="edges")

        bpy.ops.mesh.dissolve_edges.assert_called_once()
        self.assertIn("Dissolved selected edges", result)

    def test_dissolve_faces(self):
        """Test dissolve faces"""
        result = self.handler.dissolve(dissolve_type="faces")

        bpy.ops.mesh.dissolve_faces.assert_called_once()
        self.assertIn("Dissolved selected faces", result)

    def test_dissolve_case_insensitive(self):
        """Test that dissolve_type is case-insensitive"""
        result = self.handler.dissolve(dissolve_type="LIMITED")
        self.assertIn("Limited dissolve", result)

        result = self.handler.dissolve(dissolve_type="VERTS")
        self.assertIn("Dissolved selected vertices", result)

    def test_dissolve_invalid_type_raises(self):
        """Test that invalid dissolve_type raises error"""
        with self.assertRaises(ValueError) as context:
            self.handler.dissolve(dissolve_type="invalid")

        self.assertIn("Invalid dissolve_type", str(context.exception))

    def test_dissolve_with_face_split(self):
        """Test dissolve verts with face_split option"""
        self.handler.dissolve(dissolve_type="verts", use_face_split=True)

        bpy.ops.mesh.dissolve_verts.assert_called_once_with(
            use_face_split=True,
            use_boundary_tear=False
        )

    def test_dissolve_with_boundary_tear(self):
        """Test dissolve verts with boundary_tear option"""
        self.handler.dissolve(dissolve_type="verts", use_boundary_tear=True)

        bpy.ops.mesh.dissolve_verts.assert_called_once_with(
            use_face_split=False,
            use_boundary_tear=True
        )


class TestMeshTrisToQuads(unittest.TestCase):
    """Tests for mesh_tris_to_quads (TASK-030-2)"""

    def setUp(self):
        self.handler = MeshHandler()

        # Reset mocks
        bpy.context.active_object = MagicMock()
        bpy.context.active_object.type = 'MESH'
        bpy.context.active_object.mode = 'EDIT'
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.mesh.tris_convert_to_quads = MagicMock()

    def test_tris_to_quads_default(self):
        """Test tris to quads with default thresholds"""
        result = self.handler.tris_to_quads()

        bpy.ops.mesh.tris_convert_to_quads.assert_called_once()
        self.assertIn("Converted triangles to quads", result)
        self.assertIn("40.0", result)  # default threshold

    def test_tris_to_quads_custom_face_threshold(self):
        """Test tris to quads with custom face threshold"""
        result = self.handler.tris_to_quads(face_threshold=30.0)

        self.assertIn("face threshold: 30.0", result)

    def test_tris_to_quads_custom_shape_threshold(self):
        """Test tris to quads with custom shape threshold"""
        result = self.handler.tris_to_quads(shape_threshold=50.0)

        self.assertIn("shape threshold: 50.0", result)

    def test_tris_to_quads_both_thresholds(self):
        """Test tris to quads with both custom thresholds"""
        result = self.handler.tris_to_quads(face_threshold=25.0, shape_threshold=35.0)

        self.assertIn("face threshold: 25.0", result)
        self.assertIn("shape threshold: 35.0", result)

    def test_tris_to_quads_runtime_error(self):
        """Test tris to quads handles runtime error"""
        bpy.ops.mesh.tris_convert_to_quads.side_effect = RuntimeError("Test error")

        with self.assertRaises(RuntimeError) as context:
            self.handler.tris_to_quads()

        self.assertIn("Tris to quads conversion failed", str(context.exception))


class TestMeshNormalsMakeConsistent(unittest.TestCase):
    """Tests for mesh_normals_make_consistent (TASK-030-3)"""

    def setUp(self):
        self.handler = MeshHandler()

        # Reset mocks
        bpy.context.active_object = MagicMock()
        bpy.context.active_object.type = 'MESH'
        bpy.context.active_object.mode = 'EDIT'
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.mesh.normals_make_consistent = MagicMock()

    def test_normals_outward_default(self):
        """Test normals make consistent outward (default)"""
        result = self.handler.normals_make_consistent()

        bpy.ops.mesh.normals_make_consistent.assert_called_once_with(inside=False)
        self.assertIn("outward", result)

    def test_normals_inward(self):
        """Test normals make consistent inward"""
        result = self.handler.normals_make_consistent(inside=True)

        bpy.ops.mesh.normals_make_consistent.assert_called_once_with(inside=True)
        self.assertIn("inward", result)

    def test_normals_runtime_error(self):
        """Test normals handles runtime error"""
        bpy.ops.mesh.normals_make_consistent.side_effect = RuntimeError("Test error")

        with self.assertRaises(RuntimeError) as context:
            self.handler.normals_make_consistent()

        self.assertIn("Normals recalculation failed", str(context.exception))


class TestMeshDecimate(unittest.TestCase):
    """Tests for mesh_decimate (TASK-030-4)"""

    def setUp(self):
        self.handler = MeshHandler()

        # Reset mocks
        bpy.context.active_object = MagicMock()
        bpy.context.active_object.type = 'MESH'
        bpy.context.active_object.mode = 'EDIT'
        bpy.ops.object.mode_set = MagicMock()
        bpy.ops.mesh.decimate = MagicMock()

    def test_decimate_default(self):
        """Test decimate with default ratio"""
        result = self.handler.decimate()

        bpy.ops.mesh.decimate.assert_called_once_with(
            ratio=0.5,
            use_symmetry=False,
            symmetry_axis='X'
        )
        self.assertIn("50.0%", result)

    def test_decimate_custom_ratio(self):
        """Test decimate with custom ratio"""
        result = self.handler.decimate(ratio=0.25)

        self.assertIn("25.0%", result)

    def test_decimate_with_symmetry(self):
        """Test decimate with symmetry enabled"""
        result = self.handler.decimate(ratio=0.5, use_symmetry=True, symmetry_axis='Y')

        bpy.ops.mesh.decimate.assert_called_once_with(
            ratio=0.5,
            use_symmetry=True,
            symmetry_axis='Y'
        )
        self.assertIn("with Y symmetry", result)

    def test_decimate_clamps_ratio(self):
        """Test that ratio is clamped to 0.0-1.0 range"""
        # Value above 1.0 should be clamped
        result = self.handler.decimate(ratio=1.5)
        self.assertIn("100.0%", result)

        # Value below 0.0 should be clamped
        result = self.handler.decimate(ratio=-0.5)
        self.assertIn("0.0%", result)

    def test_decimate_symmetry_axis_case_insensitive(self):
        """Test that symmetry_axis is case-insensitive"""
        result = self.handler.decimate(use_symmetry=True, symmetry_axis='x')
        self.assertIn("X symmetry", result)

        result = self.handler.decimate(use_symmetry=True, symmetry_axis='z')
        self.assertIn("Z symmetry", result)

    def test_decimate_invalid_axis_raises(self):
        """Test that invalid symmetry axis raises error"""
        with self.assertRaises(ValueError) as context:
            self.handler.decimate(use_symmetry=True, symmetry_axis='W')

        self.assertIn("Invalid symmetry_axis", str(context.exception))

    def test_decimate_runtime_error(self):
        """Test decimate handles runtime error"""
        bpy.ops.mesh.decimate.side_effect = RuntimeError("Test error")

        with self.assertRaises(RuntimeError) as context:
            self.handler.decimate()

        self.assertIn("Decimate failed", str(context.exception))


if __name__ == '__main__':
    unittest.main()
