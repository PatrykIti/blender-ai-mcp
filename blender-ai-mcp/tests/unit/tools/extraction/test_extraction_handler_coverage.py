from __future__ import annotations

import math
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

from blender_addon.application.handlers.extraction import ExtractionHandler


class LookupList(list):
    def ensure_lookup_table(self):
        return None


class Vec:
    def __init__(self, coords=(0.0, 0.0, 0.0)):
        if isinstance(coords, Vec):
            self._coords = list(coords._coords)
        else:
            self._coords = [float(value) for value in coords]

    def __iter__(self):
        return iter(self._coords)

    def __getitem__(self, idx):
        return self._coords[idx]

    def __setitem__(self, idx, value):
        self._coords[idx] = float(value)

    def __add__(self, other):
        other_vec = other if isinstance(other, Vec) else Vec(other)
        return Vec(a + b for a, b in zip(self._coords, other_vec._coords))

    def __radd__(self, other):
        if other == 0:
            return self
        return self.__add__(other)

    def __sub__(self, other):
        other_vec = other if isinstance(other, Vec) else Vec(other)
        return Vec(a - b for a, b in zip(self._coords, other_vec._coords))

    def __truediv__(self, scalar):
        return Vec(value / scalar for value in self._coords)

    @property
    def x(self):
        return self._coords[0]

    @property
    def y(self):
        return self._coords[1]

    @property
    def z(self):
        return self._coords[2]

    @property
    def length(self):
        return math.sqrt(sum(value * value for value in self._coords))

    def normalized(self):
        if self.length == 0:
            return Vec((0.0, 0.0, 0.0))
        return self / self.length

    def to_track_quat(self, *_args):
        return SimpleNamespace(to_euler=lambda: (0.0, 0.0, 0.0))


class IdentityMatrix:
    def __matmul__(self, other):
        return other if isinstance(other, Vec) else Vec(other)


class FakeNormal(Vec):
    def __init__(self, coords=(0.0, 0.0, 1.0), angle_value=0.0):
        super().__init__(coords)
        self._angle_value = angle_value

    def angle(self, _other):
        return self._angle_value


class FakeVert:
    def __init__(self, coords):
        self.co = Vec(coords)


class FakeEdge:
    def __init__(self, verts, *, is_boundary=False, is_manifold=True, link_faces=None):
        self.verts = verts
        self.is_boundary = is_boundary
        self.is_manifold = is_manifold
        self.link_faces = link_faces or []


class FakeFace:
    def __init__(self, *, verts, center, area, normal=None, edges=None):
        self.verts = verts
        self._center = Vec(center)
        self._area = area
        self.normal = normal or FakeNormal()
        self.edges = edges or []

    def calc_area(self):
        return self._area

    def calc_center_median(self):
        return self._center


class FakeBMesh:
    def __init__(self, *, verts, edges, faces):
        self.verts = LookupList(verts)
        self.edges = LookupList(edges)
        self.faces = LookupList(faces)

    def from_mesh(self, _mesh):
        return None

    def free(self):
        return None


def _install_object_map(mock_bpy, **objects):
    class ObjectMap:
        def __contains__(self, name):
            return name in objects

        def __getitem__(self, name):
            return objects[name]

        def __iter__(self):
            return iter(objects.values())

        def new(self, name, data):
            obj = MagicMock()
            obj.name = name
            obj.data = data
            obj.location = None
            obj.rotation_euler = None
            return obj

        def remove(self, _obj, do_unlink=True):
            return None

    mock_bpy.data.objects = ObjectMap()


def test_deep_topology_success(monkeypatch):
    mock_bpy = sys.modules["bpy"]
    handler = ExtractionHandler()

    cube = MagicMock()
    cube.name = "Cube"
    cube.type = "MESH"
    cube.dimensions = SimpleNamespace(x=2.0, y=2.0, z=2.0)
    cube.data = MagicMock()
    cube.matrix_world = IdentityMatrix()
    cube.bound_box = [
        (-1, -1, -1),
        (1, -1, -1),
        (1, 1, -1),
        (-1, 1, -1),
        (-1, -1, 1),
        (1, -1, 1),
        (1, 1, 1),
        (-1, 1, 1),
    ]
    _install_object_map(mock_bpy, Cube=cube)

    faces = [FakeFace(verts=[1, 2, 3, 4], center=(0, 0, 0), area=1.0) for _ in range(6)]
    edges = [
        FakeEdge((FakeVert((0, 0, 0)), FakeVert((1, 0, 0))), is_boundary=False, is_manifold=True) for _ in range(12)
    ]
    bm = FakeBMesh(verts=[FakeVert((0, 0, 0)) for _ in range(8)], edges=edges, faces=faces)

    monkeypatch.setattr("blender_addon.application.handlers.extraction.bmesh.new", lambda: bm)
    monkeypatch.setattr(handler, "_detect_base_primitive", lambda *args: ("CUBE", 0.95))
    monkeypatch.setattr(handler, "_detect_beveled_edges", lambda _bm: True)
    monkeypatch.setattr(handler, "_detect_inset_faces", lambda _bm: False)
    monkeypatch.setattr(handler, "_detect_extrusions", lambda _bm, _obj: True)

    result = handler.deep_topology("Cube")

    assert result["base_primitive"] == "CUBE"
    assert result["vertex_count"] == 8
    assert result["face_count"] == 6
    assert result["has_extrusions"] is True


def test_component_separate_deletes_small_components(monkeypatch):
    mock_bpy = sys.modules["bpy"]
    handler = ExtractionHandler()

    cube = MagicMock(name="Cube")
    cube.name = "Cube"
    cube.type = "MESH"
    cube.data.vertices = [object()] * 8
    cube.data.polygons = [object()] * 6
    cube.mode = "EDIT"
    big = MagicMock(name="Cube.001")
    big.name = "Cube.001"
    big.type = "MESH"
    big.data.vertices = [object()] * 10
    big.data.polygons = [object()] * 4
    small = MagicMock(name="Cube.002")
    small.name = "Cube.002"
    small.type = "MESH"
    small.data.vertices = [object()] * 2
    small.data.polygons = [object()] * 1

    class ObjectMap(list):
        def __contains__(self, name):
            return name == "Cube"

        def __getitem__(self, key):
            if key == "Cube":
                return cube
            raise KeyError(key)

        def remove(self, obj, do_unlink=True):
            self.removed = obj

    objects = ObjectMap([cube, big, small])
    mock_bpy.data.objects = objects
    mock_bpy.context.active_object = cube
    mock_bpy.context.view_layer.objects.active = None
    mock_bpy.ops = MagicMock()

    result = handler.component_separate("Cube", min_vertex_count=4)

    assert result["component_count"] == 2
    assert result["deleted_small_components"] == 1
    assert objects.removed is small
    mock_bpy.ops.object.mode_set.assert_any_call(mode="OBJECT")
    mock_bpy.ops.mesh.separate.assert_called_once_with(type="LOOSE")


def test_detect_symmetry_empty_mesh(monkeypatch):
    mock_bpy = sys.modules["bpy"]
    handler = ExtractionHandler()

    cube = MagicMock()
    cube.name = "Cube"
    cube.type = "MESH"
    cube.data = MagicMock()
    _install_object_map(mock_bpy, Cube=cube)

    bm = FakeBMesh(verts=[], edges=[], faces=[])
    monkeypatch.setattr("blender_addon.application.handlers.extraction.bmesh.new", lambda: bm)

    result = handler.detect_symmetry("Cube")

    assert result["total_vertices"] == 0
    assert result["x_symmetric"] is False


def test_edge_loop_analysis_detects_parallel_groups_and_chamfer(monkeypatch):
    mock_bpy = sys.modules["bpy"]
    handler = ExtractionHandler()

    cube = MagicMock()
    cube.name = "Cube"
    cube.type = "MESH"
    cube.data = MagicMock()
    _install_object_map(mock_bpy, Cube=cube)

    face_a = FakeFace(verts=[1, 2, 3, 4], center=(0, 0, 0), area=1.0, normal=FakeNormal(angle_value=0.2))
    face_b = FakeFace(verts=[1, 2, 3, 4], center=(0, 0, 1), area=1.0, normal=FakeNormal(angle_value=0.2))
    parallel_edges = [
        FakeEdge(
            (FakeVert((0, 0, 0)), FakeVert((1, 0, 0))), is_boundary=False, is_manifold=True, link_faces=[face_a, face_b]
        )
        for _ in range(4)
    ]
    boundary_edge = FakeEdge((FakeVert((0, 0, 0)), FakeVert((0, 1, 0))), is_boundary=True, is_manifold=False)
    bm = FakeBMesh(verts=[], edges=parallel_edges + [boundary_edge], faces=[])
    monkeypatch.setattr("blender_addon.application.handlers.extraction.bmesh.new", lambda: bm)

    result = handler.edge_loop_analysis("Cube")

    assert result["parallel_edge_groups"] >= 1
    assert result["has_chamfer"] is True


def test_face_group_analysis_detects_insets_and_extrusions(monkeypatch):
    mock_bpy = sys.modules["bpy"]
    handler = ExtractionHandler()

    cube = MagicMock()
    cube.name = "Cube"
    cube.type = "MESH"
    cube.data = MagicMock()
    _install_object_map(mock_bpy, Cube=cube)

    center_face = FakeFace(verts=[1, 2, 3, 4], center=(0, 0, 0), area=4.0, normal=FakeNormal((0, 0, 1)))
    adjacent_faces = [
        FakeFace(verts=[1, 2, 3, 4], center=(0, 0, 1), area=1.0, normal=FakeNormal((0, 0, 1))) for _ in range(4)
    ]
    edges = []
    for adjacent in adjacent_faces:
        edge = FakeEdge((FakeVert((0, 0, 0)), FakeVert((1, 0, 0))), link_faces=[center_face, adjacent])
        edges.append(edge)
    center_face.edges = edges
    bm = FakeBMesh(verts=[], edges=edges, faces=[center_face, *adjacent_faces])
    monkeypatch.setattr("blender_addon.application.handlers.extraction.bmesh.new", lambda: bm)

    result = handler.face_group_analysis("Cube")

    assert result["detected_insets"] >= 1
    assert result["has_extrusions"] is True


def test_render_angles_success_restores_visibility_and_reports_progress(monkeypatch, tmp_path):
    module = sys.modules["blender_addon.application.handlers.extraction"]
    mock_bpy = sys.modules["bpy"]
    handler = ExtractionHandler()

    cube = MagicMock()
    cube.name = "Cube"
    cube.type = "MESH"
    cube.bound_box = [
        (-1, -1, -1),
        (1, -1, -1),
        (1, 1, -1),
        (-1, 1, -1),
        (-1, -1, 1),
        (1, -1, 1),
        (1, 1, 1),
        (-1, 1, 1),
    ]
    cube.matrix_world = IdentityMatrix()
    other = MagicMock()
    other.name = "Other"
    other.type = "MESH"
    other.hide_render = False

    _install_object_map(mock_bpy, Cube=cube, Other=other)
    mock_bpy.data.cameras = MagicMock()
    mock_bpy.data.cameras.new.return_value = MagicMock()
    mock_bpy.context.scene = MagicMock()
    mock_bpy.context.scene.collection.objects.link = MagicMock()
    mock_bpy.context.scene.render = MagicMock()
    mock_bpy.context.scene.render.image_settings = MagicMock()
    mock_bpy.ops = MagicMock()

    monkeypatch.setattr(module, "Vector", Vec)
    monkeypatch.setattr(module, "Euler", lambda rotation: rotation)

    progress = []
    result = handler.render_angles(
        "Cube",
        angles=["front", "iso"],
        resolution=128,
        output_dir=str(tmp_path),
        progress_callback=lambda current, total=None, message=None: progress.append((current, total, message)),
    )

    assert len(result["renders"]) == 2
    assert progress[0] == (0, 2, "Preparing multi-angle render job")
    assert progress[-1] == (2, 2, "Rendered iso view")
    assert other.hide_render is False
    assert mock_bpy.ops.render.render.call_count == 2
