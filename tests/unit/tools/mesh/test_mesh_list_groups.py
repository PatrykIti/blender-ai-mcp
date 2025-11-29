import pytest
import sys
from unittest.mock import MagicMock

# Import handler after conftest.py has set up bpy mocks
from blender_addon.application.handlers.mesh import MeshHandler

class TestMeshListGroups:
    def setup_method(self):
        self.handler = MeshHandler()
        # Access the mock bpy from sys.modules (set up by conftest.py)
        self.mock_bpy = sys.modules["bpy"]

    def test_list_vertex_groups(self):
        # Mock object with vertex groups
        mock_obj = MagicMock()
        mock_obj.type = 'MESH'
        mock_obj.name = "Cube"
        
        # Create mock vertex groups
        vg1 = MagicMock()
        vg1.name = "Group.001"
        vg1.index = 0
        vg1.lock_weight = False
        
        vg2 = MagicMock()
        vg2.name = "Group.002"
        vg2.index = 1
        vg2.lock_weight = True
        
        mock_obj.vertex_groups = [vg1, vg2]
        
        # Mock vertices with groups
        v1 = MagicMock()
        g1 = MagicMock(); g1.group = 0
        v1.groups = [g1]
        
        v2 = MagicMock()
        g2 = MagicMock(); g2.group = 1
        v2.groups = [g2]
        
        v3 = MagicMock()
        v3.groups = [] # No group
        
        mock_obj.data.vertices = [v1, v2, v3]

        self.mock_bpy.data.objects = {"Cube": mock_obj}
        
        result = self.handler.list_groups("Cube", "VERTEX")
        
        assert result["object_name"] == "Cube"
        assert result["group_type"] == "VERTEX"
        assert result["group_count"] == 2
        
        groups = result["groups"]
        assert len(groups) == 2
        assert groups[0]["name"] == "Group.001"
        assert groups[0]["member_count"] == 1
        assert groups[0]["lock_weight"] is False
        
        assert groups[1]["name"] == "Group.002"
        assert groups[1]["member_count"] == 1
        assert groups[1]["lock_weight"] is True

    def test_list_face_groups_attributes(self):
        # Mock object with face attributes (Blender 3.0+ style for face maps fallback)
        mock_obj = MagicMock()
        mock_obj.type = 'MESH'
        mock_obj.name = "Cube"
        
        # Make sure it DOES NOT have face_maps (simulate newer blender or just fallback path)
        del mock_obj.face_maps 
        # or rely on hasattr checking mock, usually mocks have everything unless deleted or spec set.
        # MagicMock has everything by default.
        # Let's ensure hasattr(mock_obj, 'face_maps') is False by raising AttributeError on access or something?
        # Actually MagicMock returns another MagicMock for any attribute.
        # We need to simulate hasattr failure.
        # Specifying spec set might work, or just let it use face_maps logic if it exists.
        
        # The implementation checks: if hasattr(obj, 'face_maps'):
        # MagicMock has everything. So it will enter face_maps block.
        # Let's test the face_maps block first.
        
        fm1 = MagicMock()
        fm1.name = "FaceMap.001"
        fm1.index = 0
        
        mock_obj.face_maps = [fm1]

        self.mock_bpy.data.objects = {"Cube": mock_obj}
        
        result = self.handler.list_groups("Cube", "FACE")
        
        assert result["group_type"] == "FACE"
        assert result["group_count"] == 1
        assert result["groups"][0]["name"] == "FaceMap.001"

    def test_object_not_found(self):
        self.mock_bpy.data.objects = {}
        with pytest.raises(ValueError, match="Object 'Ghost' not found"):
            self.handler.list_groups("Ghost")

    def test_invalid_type(self):
        mock_obj = MagicMock()
        mock_obj.type = 'CAMERA'
        self.mock_bpy.data.objects = {"Cam": mock_obj}
        
        with pytest.raises(ValueError, match="is not a MESH"):
            self.handler.list_groups("Cam")
