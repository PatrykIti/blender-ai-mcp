import sys
import pytest
from unittest.mock import MagicMock

# conftest.py handles bpy mocking
from blender_addon.application.handlers.modeling import ModelingHandler

class MockObjects(dict):
    """Helper to mock self.mock_bpy.data.objects which acts as a dict but has methods like remove."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.remove = MagicMock()

class TestModelingTools:
    def setup_method(self):
        # Access the global bpy mock from conftest.py
        self.mock_bpy = sys.modules["bpy"]

        # 1. Setup bpy structure (conftest already reset it)
        # 2. Setup Operators
        self.mock_bpy.ops.mesh.primitive_cube_add = MagicMock()
        self.mock_bpy.ops.object.convert = MagicMock()
        self.mock_bpy.ops.object.join = MagicMock()
        self.mock_bpy.ops.object.mode_set = MagicMock()
        self.mock_bpy.ops.mesh.separate = MagicMock()
        self.mock_bpy.ops.object.origin_set = MagicMock()

        # 3. Setup Active Object
        self.cube = MagicMock()
        self.cube.name = "Cube"
        self.cube.location = (0,0,0)
        self.cube.scale = (1,1,1)
        self.cube.modifiers = MagicMock()

        self.mock_bpy.context.active_object = self.cube

        # 4. Setup self.mock_bpy.data.objects using MockObjects (dict)
        self.objects_mock = MockObjects()
        self.objects_mock["Cube"] = self.cube
        self.mock_bpy.data.objects = self.objects_mock

        self.handler = ModelingHandler()

    def test_create_cube(self):
        # When
        result = self.handler.create_primitive("Cube", size=3.0, location=(1,2,3))
        
        # Then
        self.mock_bpy.ops.mesh.primitive_cube_add.assert_called_with(size=3.0, location=(1,2,3), rotation=(0,0,0))
        assert result["name"] == "Cube"

    def test_transform_object(self):
        # When
        self.handler.transform_object("Cube", location=(10,10,10))
        
        # Then
        assert self.cube.location == (10,10,10)

    def test_add_modifier(self):
        # Setup
        mod_mock = MagicMock()
        mod_mock.name = "Subdiv"
        self.cube.modifiers.new.return_value = mod_mock
        
        # When
        result = self.handler.add_modifier("Cube", "subsurf", {"levels": 2}) # Lowercase input
        
        # Then
        # Expect Uppercase "SUBSURF" passed to new()
        self.cube.modifiers.new.assert_called_with(name="subsurf", type="SUBSURF")
        assert mod_mock.levels == 2
        assert result["modifier"] == "Subdiv"

    def test_add_modifier_boolean_object_by_name(self):
        # Setup
        cutter = MagicMock()
        cutter.name = "Cutter"
        self.objects_mock["Cutter"] = cutter

        mod_mock = MagicMock()
        mod_mock.name = "BOOLEAN"
        self.cube.modifiers.new.return_value = mod_mock

        # When
        result = self.handler.add_modifier(
            "Cube",
            "boolean",
            {"operation": "DIFFERENCE", "object": "Cutter", "solver": "EXACT"},
        )

        # Then
        self.cube.modifiers.new.assert_called_with(name="boolean", type="BOOLEAN")
        assert mod_mock.object == cutter
        assert result["modifier"] == "BOOLEAN"

    def test_add_modifier_boolean_object_name_alias(self):
        # Setup
        cutter = MagicMock()
        cutter.name = "Cutter"
        self.objects_mock["Cutter"] = cutter

        mod_mock = MagicMock()
        mod_mock.name = "BOOLEAN"
        self.cube.modifiers.new.return_value = mod_mock

        # When
        result = self.handler.add_modifier(
            "Cube",
            "BOOLEAN",
            {"operation": "DIFFERENCE", "object_name": "Cutter", "solver": "EXACT"},
        )

        # Then
        self.cube.modifiers.new.assert_called_with(name="BOOLEAN", type="BOOLEAN")
        assert mod_mock.object == cutter
        assert result["modifier"] == "BOOLEAN"

    def test_add_modifier_boolean_object_missing_raises(self):
        mod_mock = MagicMock()
        mod_mock.name = "BOOLEAN"
        self.cube.modifiers.new.return_value = mod_mock

        with pytest.raises(ValueError, match="Boolean modifier target object 'Missing' not found"):
            self.handler.add_modifier(
                "Cube",
                "BOOLEAN",
                {"operation": "DIFFERENCE", "object": "Missing", "solver": "EXACT"},
            )

    def test_apply_modifier(self):
        # Setup: Ensure the object has a modifier mock
        mod_name = "MirrorMod"
        mock_modifier = MagicMock()
        mock_modifier.name = mod_name
        
        # Update contains logic to support both direct check and iteration
        def contains_side_effect(key):
            return key == mod_name
        
        self.cube.modifiers.__contains__.side_effect = contains_side_effect
        self.cube.modifiers.__getitem__.side_effect = lambda k: mock_modifier if k == mod_name else KeyError(k)
        self.cube.modifiers.get.side_effect = lambda k, default=None: mock_modifier if k == mod_name else default
        
        # Mock iteration for case-insensitive search fallback
        self.cube.modifiers.__iter__.return_value = [mock_modifier]
        
        self.mock_bpy.ops.object.modifier_apply = MagicMock()
        
        # When
        result = self.handler.apply_modifier("Cube", mod_name)
        
        # Then
        self.mock_bpy.ops.object.select_all.assert_called_with(action='DESELECT')
        self.cube.select_set.assert_called_with(True)
        self.mock_bpy.ops.object.modifier_apply.assert_called_with(modifier=mod_name)
        assert result['applied_modifier'] == mod_name
        assert result['object'] == "Cube"

    def test_apply_modifier_enables_disabled_modifier(self):
        # Setup: Modifier exists but is disabled in viewport/render
        mod_name = "Bevel"
        mock_modifier = MagicMock()
        mock_modifier.name = mod_name
        mock_modifier.show_viewport = False
        mock_modifier.show_render = False

        self.cube.modifiers.__contains__.side_effect = lambda k: k == mod_name
        self.cube.modifiers.__iter__.return_value = [mock_modifier]
        self.cube.modifiers.get.side_effect = lambda k, default=None: mock_modifier if k == mod_name else default

        self.mock_bpy.ops.object.modifier_apply = MagicMock()

        # When
        result = self.handler.apply_modifier("Cube", mod_name)

        # Then
        assert mock_modifier.show_viewport is True
        assert mock_modifier.show_render is True
        self.mock_bpy.ops.object.modifier_apply.assert_called_with(modifier=mod_name)
        assert result["applied_modifier"] == mod_name

    def test_apply_modifier_case_insensitive(self):
        # Setup: Modifier is named "BEVEL", request is for "bevel"
        real_mod_name = "BEVEL"
        request_mod_name = "bevel"
        
        mock_modifier = MagicMock()
        mock_modifier.name = real_mod_name
        
        # Contains returns False for "bevel" to trigger fallback logic
        self.cube.modifiers.__contains__.side_effect = lambda k: k == real_mod_name
        
        # Iterator returns the modifier with Uppercase name
        self.cube.modifiers.__iter__.return_value = [mock_modifier]
        
        self.mock_bpy.ops.object.modifier_apply = MagicMock()
        
        # When
        result = self.handler.apply_modifier("Cube", request_mod_name)
        
        # Then
        # Should find "BEVEL" and use it
        self.mock_bpy.ops.object.modifier_apply.assert_called_with(modifier=real_mod_name)
        assert result['applied_modifier'] == real_mod_name

    def test_apply_modifier_object_not_found(self):
        with pytest.raises(ValueError, match="Object 'NonExistent' not found"):
            self.handler.apply_modifier("NonExistent", "SomeMod")

    def test_apply_modifier_not_found_on_object(self):
        # Setup: Object exists, but no such modifier
        mod_name = "NonExistentMod"
        
        # We need to mock modifiers collection for the 'Cube'
        modifiers_mock = MagicMock()
        modifiers_mock.__contains__.side_effect = lambda k: False # Not found directly
        modifiers_mock.__iter__.return_value = [] # Empty iteration (fallback fails)
        self.cube.modifiers = modifiers_mock

        with pytest.raises(ValueError, match=f"Modifier \'{mod_name}\' not found on object 'Cube'"):
            self.handler.apply_modifier("Cube", mod_name)

    def test_convert_to_mesh(self):
        # Setup a non-mesh object (e.g., Curve)
        curve_obj = MagicMock()
        curve_obj.name = "BezierCurve"
        curve_obj.type = 'CURVE'
        
        self.objects_mock["BezierCurve"] = curve_obj # Add to self.mock_bpy.data.objects
        self.mock_bpy.context.active_object = curve_obj # Set as active before conversion
        
        self.mock_bpy.ops.object.convert = MagicMock() # Mock the convert operator
        
        # When
        result = self.handler.convert_to_mesh("BezierCurve")
        
        # Then
        self.mock_bpy.ops.object.select_all.assert_called_with(action='DESELECT')
        curve_obj.select_set.assert_called_with(True)
        self.mock_bpy.ops.object.convert.assert_called_with(target='MESH')
        assert result['name'] == "BezierCurve"
        assert result['type'] == "MESH"
        assert result['status'] == "converted"

    def test_convert_to_mesh_already_mesh(self):
        # Setup a mesh object
        mesh_obj = MagicMock()
        mesh_obj.name = "Cube"
        mesh_obj.type = 'MESH'
        
        self.objects_mock["Cube"] = mesh_obj
        
        # When
        result = self.handler.convert_to_mesh("Cube")
        
        # Then
        self.mock_bpy.ops.object.convert.assert_not_called()
        assert result['name'] == "Cube"
        assert result['type'] == "MESH"
        assert result['status'] == "already_mesh"

    def test_convert_to_mesh_object_not_found(self):
        with pytest.raises(ValueError, match="Object 'NonExistent' not found"):
            self.handler.convert_to_mesh("NonExistent")

    def test_join_objects(self):
        # Setup two more objects
        obj1 = MagicMock()
        obj1.name = "Sphere"
        obj1.select_set = MagicMock()
        
        obj2 = MagicMock()
        obj2.name = "Cylinder"
        obj2.select_set = MagicMock()

        # Add them to our mock data
        self.objects_mock["Sphere"] = obj1
        self.objects_mock["Cylinder"] = obj2
        
        # Mock the active object after join. Blender operator replaces active object
        joined_obj = MagicMock()
        joined_obj.name = "Sphere"
        self.mock_bpy.context.active_object = joined_obj # This mock will be the result of join
        
        self.mock_bpy.ops.object.join = MagicMock() # Mock the join operator
        
        # When
        result = self.handler.join_objects(["Cube", "Sphere", "Cylinder"])
        
        # Then
        self.mock_bpy.ops.object.select_all.assert_called_with(action='DESELECT')
        self.cube.select_set.assert_called_with(True)
        obj1.select_set.assert_called_with(True)
        obj2.select_set.assert_called_with(True)
        self.mock_bpy.ops.object.join.assert_called_once()
        assert result['name'] == "Sphere"
        assert result['joined_count'] == 3

    def test_join_objects_no_objects(self):
        with pytest.raises(ValueError, match="No objects provided for joining."):
            self.handler.join_objects([])

    def test_join_objects_non_existent(self):
        # Setup one existing, one non-existent
        self.objects_mock["Sphere"] = MagicMock()
        
        with pytest.raises(ValueError, match="Object 'NonExistent' not found"):
            self.handler.join_objects(["Cube", "NonExistent"])

    def test_separate_object_loose(self):
        # Setup
        obj_to_separate = MagicMock()
        obj_to_separate.name = "ComplexMesh"
        obj_to_separate.type = 'MESH'
        obj_to_separate.select_set = MagicMock()

        self.objects_mock["ComplexMesh"] = obj_to_separate
        
        # Mock initial scene objects and new objects after separation
        self.mock_bpy.context.scene.objects = [obj_to_separate] # Initial
        
        new_part1 = MagicMock()
        new_part1.name = "ComplexMesh.001"
        new_part2 = MagicMock()
        new_part2.name = "ComplexMesh.002"

        def separate_side_effect(**kwargs):
            # Simulate new objects appearing in scene after separation
            self.mock_bpy.context.scene.objects.extend([new_part1, new_part2])
            
        self.mock_bpy.ops.mesh.separate.side_effect = separate_side_effect
        
        # When
        result = self.handler.separate_object("ComplexMesh", "LOOSE")

        # Then
        self.mock_bpy.ops.object.select_all.assert_called_with(action='DESELECT')
        obj_to_separate.select_set.assert_called_with(True)
        self.mock_bpy.ops.object.mode_set.assert_any_call(mode='EDIT')
        self.mock_bpy.ops.mesh.separate.assert_called_with(type='LOOSE')
        self.mock_bpy.ops.object.mode_set.assert_any_call(mode='OBJECT')
        assert "ComplexMesh.001" in result["separated_objects"]
        assert "ComplexMesh.002" in result["separated_objects"]
        assert result["original_object"] == "ComplexMesh"

    def test_separate_object_non_mesh(self):
        # Setup a non-mesh object
        curve_obj = MagicMock()
        curve_obj.name = "BezierCurve"
        curve_obj.type = 'CURVE'
        self.objects_mock["BezierCurve"] = curve_obj

        with pytest.raises(ValueError, match="Object 'BezierCurve' is not a mesh"):
            self.handler.separate_object("BezierCurve", "LOOSE")

    def test_separate_object_invalid_type(self):
        with pytest.raises(ValueError, match="Invalid separation type: 'INVALID'. Must be one of \\['LOOSE\', 'SELECTED\', 'MATERIAL'\\]"):
            self.handler.separate_object("Cube", "INVALID")

    def test_separate_object_not_found(self):
        with pytest.raises(ValueError, match="Object 'NonExistent' not found"):
            self.handler.separate_object("NonExistent", "LOOSE")

    def test_set_origin(self):
        # Setup
        obj = MagicMock()
        obj.name = "TestObject"
        obj.select_set = MagicMock()
        self.objects_mock["TestObject"] = obj
        
        self.mock_bpy.ops.object.origin_set = MagicMock()

        # When
        result = self.handler.set_origin("TestObject", "ORIGIN_GEOMETRY")
        
        # Then
        self.mock_bpy.ops.object.select_all.assert_called_with(action='DESELECT')
        obj.select_set.assert_called_with(True)
        self.mock_bpy.context.view_layer.objects.active = obj
        self.mock_bpy.ops.object.origin_set.assert_called_with(type='ORIGIN_GEOMETRY')
        assert result['object'] == "TestObject"
        assert result['origin_type'] == "ORIGIN_GEOMETRY"
        assert result['status'] == "success"

    def test_set_origin_invalid_type(self):
        with pytest.raises(ValueError, match="Invalid origin type: 'INVALID_TYPE'. Must be one of"):
            self.handler.set_origin("Cube", "INVALID_TYPE")

    def test_set_origin_object_not_found(self):
        with pytest.raises(ValueError, match="Object 'NonExistent' not found"):
            self.handler.set_origin("NonExistent", "ORIGIN_GEOMETRY")

    def test_get_modifiers(self):
        # Setup
        mod1 = MagicMock()
        mod1.name = "Subdiv"
        mod1.type = "SUBSURF"

        mod2 = MagicMock()
        mod2.name = "Mirror"
        mod2.type = "MIRROR"

        # Setup object with modifiers list
        obj = MagicMock()
        obj.name = "Cube"
        obj.modifiers = [mod1, mod2]

        self.objects_mock["Cube"] = obj

        # When
        result = self.handler.get_modifiers("Cube")

        # Then
        assert len(result) == 2
        assert result[0]["name"] == "Subdiv"
        assert result[0]["type"] == "SUBSURF"
        assert result[1]["name"] == "Mirror"


# =============================================================================
# TASK-038-1: Metaball Tools
# =============================================================================

class TestMetaballTools:
    """Tests for TASK-038 metaball tools."""

    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]

        # Setup operators
        self.mock_bpy.ops.object.select_all = MagicMock()
        self.mock_bpy.ops.object.convert = MagicMock()

        # Setup data
        self.mock_bpy.data.metaballs = MagicMock()
        self.mock_bpy.data.objects = MockObjects()

        # Setup context
        self.mock_bpy.context.collection = MagicMock()
        self.mock_bpy.context.collection.objects = MagicMock()
        self.mock_bpy.context.view_layer = MagicMock()

        self.handler = ModelingHandler()

    def test_metaball_create_default(self):
        """Should create metaball with default parameters."""
        # Setup mock metaball
        mock_mball = MagicMock()
        mock_elem = MagicMock()
        mock_mball.elements.new.return_value = mock_elem
        self.mock_bpy.data.metaballs.new.return_value = mock_mball

        # Setup mock object
        mock_obj = MagicMock()
        mock_obj.name = "Metaball"
        self.mock_bpy.data.objects.new = MagicMock(return_value=mock_obj)

        # When
        result = self.handler.metaball_create()

        # Then
        self.mock_bpy.data.metaballs.new.assert_called_once()
        assert mock_mball.resolution == 0.2
        assert mock_mball.threshold == 0.6
        assert mock_elem.type == "BALL"
        assert "Created metaball" in result

    def test_metaball_create_with_options(self):
        """Should create metaball with custom options."""
        # Setup mock metaball
        mock_mball = MagicMock()
        mock_elem = MagicMock()
        mock_mball.elements.new.return_value = mock_elem
        self.mock_bpy.data.metaballs.new.return_value = mock_mball

        # Setup mock object
        mock_obj = MagicMock()
        mock_obj.name = "Heart"
        self.mock_bpy.data.objects.new = MagicMock(return_value=mock_obj)

        # When
        result = self.handler.metaball_create(
            name="Heart",
            location=[1, 2, 3],
            element_type="ELLIPSOID",
            radius=1.5,
            resolution=0.1,
            threshold=0.5
        )

        # Then
        assert mock_mball.resolution == 0.1
        assert mock_mball.threshold == 0.5
        assert mock_elem.type == "ELLIPSOID"
        assert mock_elem.radius == 1.5
        assert "Heart" in result

    def test_metaball_create_invalid_type_raises(self):
        """Should raise ValueError for invalid element type."""
        with pytest.raises(ValueError, match="Invalid element type"):
            self.handler.metaball_create(element_type="INVALID")

    def test_metaball_add_element(self):
        """Should add element to existing metaball."""
        # Setup mock metaball object
        mock_mball_data = MagicMock()
        mock_elem = MagicMock()
        mock_mball_data.elements.new.return_value = mock_elem
        mock_mball_data.elements.__len__ = MagicMock(return_value=2)

        mock_obj = MagicMock()
        mock_obj.name = "Metaball"
        mock_obj.type = "META"
        mock_obj.data = mock_mball_data

        self.mock_bpy.data.objects["Metaball"] = mock_obj

        # When
        result = self.handler.metaball_add_element(
            metaball_name="Metaball",
            element_type="CAPSULE",
            location=[0.5, 0, 0],
            radius=0.3,
            stiffness=1.5
        )

        # Then
        mock_mball_data.elements.new.assert_called_once()
        assert mock_elem.type == "CAPSULE"
        assert mock_elem.radius == 0.3
        assert mock_elem.stiffness == 1.5
        assert "Added CAPSULE element" in result

    def test_metaball_add_element_object_not_found_raises(self):
        """Should raise ValueError when object not found."""
        with pytest.raises(ValueError, match="not found"):
            self.handler.metaball_add_element(metaball_name="NonExistent")

    def test_metaball_add_element_not_metaball_raises(self):
        """Should raise ValueError when object is not a metaball."""
        mock_obj = MagicMock()
        mock_obj.name = "Cube"
        mock_obj.type = "MESH"

        self.mock_bpy.data.objects["Cube"] = mock_obj

        with pytest.raises(ValueError, match="not a metaball"):
            self.handler.metaball_add_element(metaball_name="Cube")

    def test_metaball_to_mesh(self):
        """Should convert metaball to mesh."""
        # Setup mock metaball object
        mock_obj = MagicMock()
        mock_obj.name = "Metaball"
        mock_obj.type = "META"

        self.mock_bpy.data.objects["Metaball"] = mock_obj

        # Setup mock converted object
        mock_converted = MagicMock()
        mock_converted.name = "Metaball"
        mock_converted.data = MagicMock()
        mock_converted.data.vertices = [MagicMock()] * 100
        mock_converted.data.polygons = [MagicMock()] * 50

        self.mock_bpy.context.active_object = mock_converted

        # When
        result = self.handler.metaball_to_mesh(metaball_name="Metaball")

        # Then
        self.mock_bpy.ops.object.convert.assert_called_with(target='MESH')
        assert "Converted metaball" in result
        assert "100 vertices" in result
        assert "50 faces" in result

    def test_metaball_to_mesh_not_found_raises(self):
        """Should raise ValueError when object not found."""
        with pytest.raises(ValueError, match="not found"):
            self.handler.metaball_to_mesh(metaball_name="NonExistent")

    def test_metaball_to_mesh_not_metaball_raises(self):
        """Should raise ValueError when object is not a metaball."""
        mock_obj = MagicMock()
        mock_obj.name = "Cube"
        mock_obj.type = "MESH"

        self.mock_bpy.data.objects["Cube"] = mock_obj

        with pytest.raises(ValueError, match="not a metaball"):
            self.handler.metaball_to_mesh(metaball_name="Cube")


# =============================================================================
# TASK-038-6: Skin Modifier Workflow
# =============================================================================

class TestSkinModifierTools:
    """Tests for TASK-038 skin modifier tools."""

    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]

        # Setup operators
        self.mock_bpy.ops.object.select_all = MagicMock()

        # Setup data
        self.mock_bpy.data.meshes = MagicMock()
        self.mock_bpy.data.objects = MockObjects()

        # Setup context
        self.mock_bpy.context.collection = MagicMock()
        self.mock_bpy.context.collection.objects = MagicMock()
        self.mock_bpy.context.view_layer = MagicMock()

        self.handler = ModelingHandler()

    def test_skin_create_skeleton_default(self):
        """Should create skeleton with default parameters."""
        # Setup mock mesh
        mock_mesh = MagicMock()
        self.mock_bpy.data.meshes.new.return_value = mock_mesh

        # Setup mock object
        mock_obj = MagicMock()
        mock_obj.name = "Skeleton"
        mock_obj.modifiers = MagicMock()
        mock_mod = MagicMock()
        mock_obj.modifiers.new.return_value = mock_mod
        self.mock_bpy.data.objects.new = MagicMock(return_value=mock_obj)

        # When
        result = self.handler.skin_create_skeleton()

        # Then
        self.mock_bpy.data.meshes.new.assert_called_once()
        mock_mesh.from_pydata.assert_called_once()
        assert "Created skeleton" in result
        assert "Skin modifier added" in result

    def test_skin_create_skeleton_custom_vertices(self):
        """Should create skeleton with custom vertices and edges."""
        # Setup mock mesh
        mock_mesh = MagicMock()
        self.mock_bpy.data.meshes.new.return_value = mock_mesh

        # Setup mock object
        mock_obj = MagicMock()
        mock_obj.name = "Branch"
        mock_obj.modifiers = MagicMock()
        mock_mod = MagicMock()
        mock_obj.modifiers.new.return_value = mock_mod
        self.mock_bpy.data.objects.new = MagicMock(return_value=mock_obj)

        vertices = [[0, 0, 0], [0, 0, 1], [0.5, 0, 1.5], [-0.5, 0, 1.5]]
        edges = [[0, 1], [1, 2], [1, 3]]

        # When
        result = self.handler.skin_create_skeleton(
            name="Branch",
            vertices=vertices,
            edges=edges
        )

        # Then
        mock_mesh.from_pydata.assert_called_once_with(vertices, edges, [])
        assert "4 vertices" in result
        assert "3 edges" in result

    def test_skin_set_radius_specific_vertex(self):
        """Should set skin radius for specific vertex."""
        # Setup mock object with skin data
        mock_skin_vert = MagicMock()
        mock_skin_layer = MagicMock()
        mock_skin_layer.data = [mock_skin_vert, MagicMock(), MagicMock()]

        mock_mesh = MagicMock()
        mock_mesh.skin_vertices = [mock_skin_layer]

        mock_obj = MagicMock()
        mock_obj.name = "Artery"
        mock_obj.type = "MESH"
        mock_obj.data = mock_mesh
        mock_obj.modifiers = [MagicMock(type='SKIN')]

        self.mock_bpy.data.objects["Artery"] = mock_obj

        # When
        result = self.handler.skin_set_radius(
            object_name="Artery",
            vertex_index=0,
            radius_x=0.15,
            radius_y=0.15
        )

        # Then
        assert mock_skin_vert.radius == (0.15, 0.15)
        assert "vertex 0" in result

    def test_skin_set_radius_all_vertices(self):
        """Should set skin radius for all vertices."""
        # Setup mock object with skin data
        mock_skin_verts = [MagicMock() for _ in range(3)]
        mock_skin_layer = MagicMock()
        mock_skin_layer.data = mock_skin_verts

        mock_mesh = MagicMock()
        mock_mesh.skin_vertices = [mock_skin_layer]

        mock_obj = MagicMock()
        mock_obj.name = "Artery"
        mock_obj.type = "MESH"
        mock_obj.data = mock_mesh
        mock_obj.modifiers = [MagicMock(type='SKIN')]

        self.mock_bpy.data.objects["Artery"] = mock_obj

        # When
        result = self.handler.skin_set_radius(
            object_name="Artery",
            radius_x=0.05,
            radius_y=0.05
        )

        # Then
        for sv in mock_skin_verts:
            assert sv.radius == (0.05, 0.05)
        assert "all 3 vertices" in result

    def test_skin_set_radius_object_not_found_raises(self):
        """Should raise ValueError when object not found."""
        with pytest.raises(ValueError, match="not found"):
            self.handler.skin_set_radius(object_name="NonExistent")

    def test_skin_set_radius_no_skin_modifier_raises(self):
        """Should raise ValueError when no skin modifier present."""
        mock_obj = MagicMock()
        mock_obj.name = "Cube"
        mock_obj.type = "MESH"
        mock_obj.modifiers = []

        self.mock_bpy.data.objects["Cube"] = mock_obj

        with pytest.raises(ValueError, match="no Skin modifier"):
            self.handler.skin_set_radius(object_name="Cube")

    def test_skin_set_radius_invalid_vertex_index_raises(self):
        """Should raise ValueError for invalid vertex index."""
        # Setup mock object with skin data
        mock_skin_layer = MagicMock()
        mock_skin_layer.data = [MagicMock(), MagicMock()]  # Only 2 vertices

        mock_mesh = MagicMock()
        mock_mesh.skin_vertices = [mock_skin_layer]

        mock_obj = MagicMock()
        mock_obj.name = "Artery"
        mock_obj.type = "MESH"
        mock_obj.data = mock_mesh
        mock_obj.modifiers = [MagicMock(type='SKIN')]

        self.mock_bpy.data.objects["Artery"] = mock_obj

        with pytest.raises(ValueError, match="out of range"):
            self.handler.skin_set_radius(object_name="Artery", vertex_index=10)
