import sys
import pytest
from unittest.mock import MagicMock

# conftest.py handles bpy mocking
from blender_addon.application.handlers.lattice import LatticeHandler


class MockObjects(dict):
    """Helper to mock bpy.data.objects which acts as a dict but has methods like remove."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.remove = MagicMock()


class TestLatticeCreate:
    """Tests for lattice_create tool."""

    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]

        # Setup operators
        self.mock_bpy.ops.object.select_all = MagicMock()

        # Setup data
        self.mock_bpy.data.lattices = MagicMock()
        self.mock_bpy.data.objects = MockObjects()

        # Setup context
        self.mock_bpy.context.collection = MagicMock()
        self.mock_bpy.context.collection.objects = MagicMock()
        self.mock_bpy.context.view_layer = MagicMock()

        self.handler = LatticeHandler()

    def test_lattice_create_default(self):
        """Should create lattice with default parameters."""
        # Setup mock lattice data
        mock_lattice_data = MagicMock()
        self.mock_bpy.data.lattices.new.return_value = mock_lattice_data

        # Setup mock object
        mock_obj = MagicMock()
        mock_obj.name = "Lattice"
        self.mock_bpy.data.objects.new = MagicMock(return_value=mock_obj)

        # When
        result = self.handler.lattice_create()

        # Then
        self.mock_bpy.data.lattices.new.assert_called_once()
        assert mock_lattice_data.points_u == 2
        assert mock_lattice_data.points_v == 2
        assert mock_lattice_data.points_w == 2
        assert mock_lattice_data.interpolation_type_u == "KEY_LINEAR"
        assert "Created lattice" in result

    def test_lattice_create_custom_resolution(self):
        """Should create lattice with custom resolution."""
        # Setup
        mock_lattice_data = MagicMock()
        self.mock_bpy.data.lattices.new.return_value = mock_lattice_data

        mock_obj = MagicMock()
        mock_obj.name = "TowerLattice"
        self.mock_bpy.data.objects.new = MagicMock(return_value=mock_obj)

        # When
        result = self.handler.lattice_create(
            name="TowerLattice",
            points_u=2,
            points_v=2,
            points_w=4,
            interpolation="KEY_BSPLINE",
        )

        # Then
        assert mock_lattice_data.points_u == 2
        assert mock_lattice_data.points_v == 2
        assert mock_lattice_data.points_w == 4
        assert mock_lattice_data.interpolation_type_u == "KEY_BSPLINE"
        assert "TowerLattice" in result
        assert "2x2x4" in result

    def test_lattice_create_fitted_to_target(self):
        """Should create lattice fitted to target object bounds."""
        # Setup mock target object with bounding box
        mock_target = MagicMock()
        mock_target.name = "Tower"
        mock_target.type = "MESH"

        # Setup bound_box (8 corners of a cube centered at origin, size 2x2x6)
        mock_target.bound_box = [
            (-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0),  # Bottom
            (-1, -1, 6), (1, -1, 6), (1, 1, 6), (-1, 1, 6),  # Top
        ]

        # Mock matrix_world to return identity (no transformation)
        mock_target.matrix_world = MagicMock()
        mock_target.matrix_world.__matmul__ = lambda self, v: MagicMock(x=v[0], y=v[1], z=v[2])

        self.mock_bpy.data.objects["Tower"] = mock_target

        # Setup mock lattice
        mock_lattice_data = MagicMock()
        self.mock_bpy.data.lattices.new.return_value = mock_lattice_data

        mock_obj = MagicMock()
        mock_obj.name = "TowerLattice"
        self.mock_bpy.data.objects.new = MagicMock(return_value=mock_obj)

        # When
        result = self.handler.lattice_create(
            name="TowerLattice",
            target_object="Tower",
            points_w=4,
        )

        # Then
        assert "fitted to 'Tower'" in result

    def test_lattice_create_target_not_found_raises(self):
        """Should raise ValueError when target object not found."""
        with pytest.raises(ValueError, match="Target object 'NonExistent' not found"):
            self.handler.lattice_create(target_object="NonExistent")

    def test_lattice_create_invalid_interpolation_raises(self):
        """Should raise ValueError for invalid interpolation type."""
        # Setup
        mock_lattice_data = MagicMock()
        self.mock_bpy.data.lattices.new.return_value = mock_lattice_data

        with pytest.raises(ValueError, match="Invalid interpolation"):
            self.handler.lattice_create(interpolation="INVALID")

    def test_lattice_create_invalid_points_raises(self):
        """Should raise ValueError for invalid point counts."""
        with pytest.raises(ValueError, match="points_u must be between 2 and 64"):
            self.handler.lattice_create(points_u=1)

        with pytest.raises(ValueError, match="points_w must be between 2 and 64"):
            self.handler.lattice_create(points_w=100)


class TestLatticeBind:
    """Tests for lattice_bind tool."""

    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]

        # Setup data
        self.mock_bpy.data.objects = MockObjects()

        self.handler = LatticeHandler()

    def test_lattice_bind_success(self):
        """Should bind object to lattice."""
        # Setup mock objects
        mock_mesh = MagicMock()
        mock_mesh.name = "Tower"
        mock_mesh.type = "MESH"
        mock_modifier = MagicMock()
        mock_modifier.name = "Lattice_TowerLattice"
        mock_mesh.modifiers.new.return_value = mock_modifier

        mock_lattice = MagicMock()
        mock_lattice.name = "TowerLattice"
        mock_lattice.type = "LATTICE"

        self.mock_bpy.data.objects["Tower"] = mock_mesh
        self.mock_bpy.data.objects["TowerLattice"] = mock_lattice

        # When
        result = self.handler.lattice_bind(
            object_name="Tower",
            lattice_name="TowerLattice",
        )

        # Then
        mock_mesh.modifiers.new.assert_called_once_with(
            name="Lattice_TowerLattice", type='LATTICE'
        )
        assert mock_modifier.object == mock_lattice
        assert "Bound 'Tower' to lattice 'TowerLattice'" in result

    def test_lattice_bind_with_vertex_group(self):
        """Should bind with vertex group."""
        # Setup mock objects
        mock_mesh = MagicMock()
        mock_mesh.name = "Character"
        mock_mesh.type = "MESH"
        # Use MagicMock for vertex_groups to allow __contains__ customization
        mock_vertex_groups = MagicMock()
        mock_vertex_groups.__contains__ = MagicMock(return_value=True)
        mock_mesh.vertex_groups = mock_vertex_groups
        mock_modifier = MagicMock()
        mock_mesh.modifiers.new.return_value = mock_modifier

        mock_lattice = MagicMock()
        mock_lattice.name = "BendLattice"
        mock_lattice.type = "LATTICE"

        self.mock_bpy.data.objects["Character"] = mock_mesh
        self.mock_bpy.data.objects["BendLattice"] = mock_lattice

        # When
        result = self.handler.lattice_bind(
            object_name="Character",
            lattice_name="BendLattice",
            vertex_group="Torso",
        )

        # Then
        assert mock_modifier.vertex_group == "Torso"
        assert "vertex group 'Torso'" in result

    def test_lattice_bind_object_not_found_raises(self):
        """Should raise ValueError when object not found."""
        with pytest.raises(ValueError, match="Object 'NonExistent' not found"):
            self.handler.lattice_bind(
                object_name="NonExistent",
                lattice_name="SomeLattice",
            )

    def test_lattice_bind_lattice_not_found_raises(self):
        """Should raise ValueError when lattice not found."""
        mock_mesh = MagicMock()
        mock_mesh.name = "Tower"
        mock_mesh.type = "MESH"
        self.mock_bpy.data.objects["Tower"] = mock_mesh

        with pytest.raises(ValueError, match="Lattice 'NonExistent' not found"):
            self.handler.lattice_bind(
                object_name="Tower",
                lattice_name="NonExistent",
            )

    def test_lattice_bind_not_lattice_raises(self):
        """Should raise ValueError when target is not a lattice."""
        mock_mesh = MagicMock()
        mock_mesh.name = "Tower"
        mock_mesh.type = "MESH"

        mock_cube = MagicMock()
        mock_cube.name = "NotALattice"
        mock_cube.type = "MESH"

        self.mock_bpy.data.objects["Tower"] = mock_mesh
        self.mock_bpy.data.objects["NotALattice"] = mock_cube

        with pytest.raises(ValueError, match="is not a lattice"):
            self.handler.lattice_bind(
                object_name="Tower",
                lattice_name="NotALattice",
            )

    def test_lattice_bind_vertex_group_not_found_raises(self):
        """Should raise ValueError when vertex group not found."""
        mock_mesh = MagicMock()
        mock_mesh.name = "Character"
        mock_mesh.type = "MESH"
        # Use MagicMock for vertex_groups that returns False for __contains__
        mock_vertex_groups = MagicMock()
        mock_vertex_groups.__contains__ = MagicMock(return_value=False)
        mock_mesh.vertex_groups = mock_vertex_groups

        mock_lattice = MagicMock()
        mock_lattice.name = "Lattice"
        mock_lattice.type = "LATTICE"

        self.mock_bpy.data.objects["Character"] = mock_mesh
        self.mock_bpy.data.objects["Lattice"] = mock_lattice

        with pytest.raises(ValueError, match="Vertex group 'NonExistent' not found"):
            self.handler.lattice_bind(
                object_name="Character",
                lattice_name="Lattice",
                vertex_group="NonExistent",
            )


class TestLatticeEditPoint:
    """Tests for lattice_edit_point tool."""

    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]

        # Setup data
        self.mock_bpy.data.objects = MockObjects()

        self.handler = LatticeHandler()

    def test_lattice_edit_point_single_relative(self):
        """Should move single point relatively."""
        # Setup mock lattice with 8 points (2x2x2)
        mock_points = [MagicMock() for _ in range(8)]
        for i, p in enumerate(mock_points):
            p.co_deform = (0, 0, 0)

        mock_lattice_data = MagicMock()
        mock_lattice_data.points = mock_points

        mock_lattice = MagicMock()
        mock_lattice.name = "Lattice"
        mock_lattice.type = "LATTICE"
        mock_lattice.data = mock_lattice_data

        self.mock_bpy.data.objects["Lattice"] = mock_lattice

        # When
        result = self.handler.lattice_edit_point(
            lattice_name="Lattice",
            point_index=5,
            offset=[0.1, 0.2, 0.3],
            relative=True,
        )

        # Then
        assert "Moved 1 point(s)" in result
        assert "indices: [5]" in result

    def test_lattice_edit_point_multiple_points(self):
        """Should move multiple points."""
        # Setup mock lattice with 16 points (2x2x4)
        mock_points = [MagicMock() for _ in range(16)]
        for i, p in enumerate(mock_points):
            p.co_deform = (0, 0, 0)

        mock_lattice_data = MagicMock()
        mock_lattice_data.points = mock_points

        mock_lattice = MagicMock()
        mock_lattice.name = "TowerLattice"
        mock_lattice.type = "LATTICE"
        mock_lattice.data = mock_lattice_data

        self.mock_bpy.data.objects["TowerLattice"] = mock_lattice

        # When - move top 4 points inward (indices 12-15)
        result = self.handler.lattice_edit_point(
            lattice_name="TowerLattice",
            point_index=[12, 13, 14, 15],
            offset=[-0.3, -0.3, 0],
            relative=True,
        )

        # Then
        assert "Moved 4 point(s)" in result
        assert "[12, 13, 14, 15]" in result

    def test_lattice_edit_point_absolute(self):
        """Should set point to absolute position."""
        # Setup
        mock_points = [MagicMock() for _ in range(8)]
        for p in mock_points:
            p.co_deform = (0, 0, 0)

        mock_lattice_data = MagicMock()
        mock_lattice_data.points = mock_points

        mock_lattice = MagicMock()
        mock_lattice.name = "Lattice"
        mock_lattice.type = "LATTICE"
        mock_lattice.data = mock_lattice_data

        self.mock_bpy.data.objects["Lattice"] = mock_lattice

        # When
        result = self.handler.lattice_edit_point(
            lattice_name="Lattice",
            point_index=7,
            offset=[1.0, 1.0, 2.0],
            relative=False,
        )

        # Then
        assert "Set 1 point(s)" in result
        assert "position [1.0, 1.0, 2.0]" in result

    def test_lattice_edit_point_not_found_raises(self):
        """Should raise ValueError when lattice not found."""
        with pytest.raises(ValueError, match="Lattice 'NonExistent' not found"):
            self.handler.lattice_edit_point(
                lattice_name="NonExistent",
                point_index=0,
                offset=[0, 0, 1],
            )

    def test_lattice_edit_point_not_lattice_raises(self):
        """Should raise ValueError when object is not a lattice."""
        mock_mesh = MagicMock()
        mock_mesh.name = "Cube"
        mock_mesh.type = "MESH"

        self.mock_bpy.data.objects["Cube"] = mock_mesh

        with pytest.raises(ValueError, match="is not a lattice"):
            self.handler.lattice_edit_point(
                lattice_name="Cube",
                point_index=0,
                offset=[0, 0, 1],
            )

    def test_lattice_edit_point_index_out_of_range_raises(self):
        """Should raise ValueError for invalid point index."""
        # Setup mock lattice with 8 points
        mock_points = [MagicMock() for _ in range(8)]
        mock_lattice_data = MagicMock()
        mock_lattice_data.points = mock_points

        mock_lattice = MagicMock()
        mock_lattice.name = "Lattice"
        mock_lattice.type = "LATTICE"
        mock_lattice.data = mock_lattice_data

        self.mock_bpy.data.objects["Lattice"] = mock_lattice

        with pytest.raises(ValueError, match="Point index 10 out of range"):
            self.handler.lattice_edit_point(
                lattice_name="Lattice",
                point_index=10,
                offset=[0, 0, 1],
            )

    def test_lattice_edit_point_negative_index_raises(self):
        """Should raise ValueError for negative point index."""
        # Setup
        mock_points = [MagicMock() for _ in range(8)]
        mock_lattice_data = MagicMock()
        mock_lattice_data.points = mock_points

        mock_lattice = MagicMock()
        mock_lattice.name = "Lattice"
        mock_lattice.type = "LATTICE"
        mock_lattice.data = mock_lattice_data

        self.mock_bpy.data.objects["Lattice"] = mock_lattice

        with pytest.raises(ValueError, match="Point index -1 out of range"):
            self.handler.lattice_edit_point(
                lattice_name="Lattice",
                point_index=-1,
                offset=[0, 0, 1],
            )
