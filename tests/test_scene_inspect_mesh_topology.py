import pytest
import sys
from unittest.mock import MagicMock

# conftest.py handles bpy mocking
from blender_addon.application.handlers.scene import SceneHandler

class TestSceneInspectMeshTopology:
    def setup_method(self):
        self.handler = SceneHandler()
        self.mock_bpy = sys.modules["bpy"]
        self.mock_bmesh = sys.modules["bmesh"]

    def test_inspect_basic_topology(self):
        # Mock object
        mock_obj = MagicMock()
        mock_obj.name = "Cube"
        mock_obj.type = 'MESH'
        self.mock_bpy.data.objects = {"Cube": mock_obj}
        
        # Mock BMesh
        mock_bm = MagicMock()
        self.mock_bmesh.new.return_value = mock_bm
        
        # Mock Geometry - Need to support ensure_lookup_table AND len() AND iteration
        verts_list = [MagicMock(), MagicMock(), MagicMock(), MagicMock()] # 4 verts
        edges_list = [MagicMock(), MagicMock(), MagicMock(), MagicMock()] # 4 edges
        
        # Configure verts
        mock_bm.verts = MagicMock()
        mock_bm.verts.__len__.return_value = len(verts_list)
        mock_bm.verts.__iter__.return_value = iter(verts_list)
        
        # Configure edges
        mock_bm.edges = MagicMock()
        mock_bm.edges.__len__.return_value = len(edges_list)
        mock_bm.edges.__iter__.return_value = iter(edges_list)
        
        # Configure faces
        f1 = MagicMock(); f1.verts = [1, 2, 3, 4] # Quad
        f2 = MagicMock(); f2.verts = [1, 2, 3] # Triangle
        faces_list = [f1, f2]
        
        mock_bm.faces = MagicMock()
        mock_bm.faces.__len__.return_value = len(faces_list)
        mock_bm.faces.__iter__.return_value = iter(faces_list)
        
        stats = self.handler.inspect_mesh_topology("Cube", detailed=False)
        
        assert stats["object_name"] == "Cube"
        assert stats["vertex_count"] == 4
        assert stats["edge_count"] == 4
        assert stats["face_count"] == 2
        assert stats["quad_count"] == 1
        assert stats["triangle_count"] == 1
        assert stats["ngon_count"] == 0
        
        # Detailed stats should be None/0
        assert stats["non_manifold_edges"] is None
        
        # Verify bmesh lifecycle
        self.mock_bmesh.new.assert_called_once()
        mock_bm.from_mesh.assert_called_with(mock_obj.data)
        mock_bm.free.assert_called_once()
        mock_bm.verts.ensure_lookup_table.assert_called()

    def test_inspect_detailed_topology(self):
        mock_obj = MagicMock()
        mock_obj.name = "BadMesh"
        mock_obj.type = 'MESH'
        self.mock_bpy.data.objects = {"BadMesh": mock_obj}
        
        mock_bm = MagicMock()
        self.mock_bmesh.new.return_value = mock_bm
        
        # Mock Edges
        e1 = MagicMock(); e1.is_manifold = True
        e2 = MagicMock(); e2.is_manifold = False # Non-manifold
        edges_list = [e1, e2]
        
        mock_bm.edges = MagicMock()
        mock_bm.edges.__len__.return_value = len(edges_list)
        mock_bm.edges.__iter__.return_value = iter(edges_list)
        
        # Mock Verts
        v1 = MagicMock(); v1.link_edges = [e1]
        v2 = MagicMock(); v2.link_edges = [] # Loose
        verts_list = [v1, v2]
        
        mock_bm.verts = MagicMock()
        mock_bm.verts.__len__.return_value = len(verts_list)
        mock_bm.verts.__iter__.return_value = iter(verts_list)
        
        # Mock Faces (needed for ensures)
        mock_bm.faces = MagicMock()
        mock_bm.faces.__len__.return_value = 0
        mock_bm.faces.__iter__.return_value = iter([])
        
        stats = self.handler.inspect_mesh_topology("BadMesh", detailed=True)
        
        assert stats["non_manifold_edges"] == 1
        assert stats["loose_vertices"] == 1

    def test_object_not_found(self):
        self.mock_bpy.data.objects = {}
        with pytest.raises(ValueError, match="Object 'Ghost' not found"):
            self.handler.inspect_mesh_topology("Ghost")

    def test_not_a_mesh(self):
        mock_obj = MagicMock()
        mock_obj.type = 'CAMERA'
        self.mock_bpy.data.objects = {"Cam": mock_obj}
        
        with pytest.raises(ValueError, match="is not a MESH"):
            self.handler.inspect_mesh_topology("Cam")
