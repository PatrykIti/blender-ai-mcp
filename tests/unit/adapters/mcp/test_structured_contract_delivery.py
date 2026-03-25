"""Integration-style tests for FastMCP structured contract delivery."""

from __future__ import annotations

import asyncio

from server.adapters.mcp.factory import build_server


class SceneHandler:
    def get_mode(self):
        return {
            "mode": "OBJECT",
            "active_object": "Cube",
            "active_object_type": "MESH",
            "selected_object_names": ["Cube"],
            "selection_count": 1,
        }

    def snapshot_state(self, include_mesh_stats=False, include_materials=False):
        return {
            "snapshot": {
                "object_count": 1,
                "mode": "OBJECT",
                "active_object": "Cube",
            },
            "hash": "abc123",
        }

    def get_custom_properties(self, object_name):
        return {
            "object_name": object_name,
            "property_count": 1,
            "properties": {"tag": "hero"},
        }

    def get_hierarchy(self, object_name=None, include_transforms=False):
        return {
            "roots": [{"name": "Cube"}],
            "total_objects": 1,
            "max_depth": 0,
        }

    def get_bounding_box(self, object_name, world_space=True):
        return {
            "object_name": object_name,
            "space": "world" if world_space else "local",
            "min": [0, 0, 0],
            "max": [1, 1, 1],
            "center": [0.5, 0.5, 0.5],
            "dimensions": [1, 1, 1],
            "volume": 1.0,
        }

    def get_origin_info(self, object_name):
        return {
            "origin_world": [0, 0, 0],
            "relative_to_bbox": {"x": 0.5, "y": 0.5, "z": 0.5},
            "suggestions": [],
        }

    def measure_distance(self, from_object, to_object, reference="ORIGIN"):
        return {
            "from_object": from_object,
            "to_object": to_object,
            "reference": reference,
            "distance": 2.0,
            "units": "blender_units",
        }

    def measure_dimensions(self, object_name, world_space=True):
        return {
            "object_name": object_name,
            "world_space": world_space,
            "dimensions": [1.0, 2.0, 3.0],
            "volume": 6.0,
            "units": "blender_units",
        }

    def measure_gap(self, from_object, to_object, tolerance=0.0001):
        return {
            "from_object": from_object,
            "to_object": to_object,
            "gap": 0.5,
            "relation": "separated",
            "units": "blender_units",
        }

    def measure_alignment(self, from_object, to_object, axes=None, reference="CENTER", tolerance=0.0001):
        return {
            "from_object": from_object,
            "to_object": to_object,
            "axes": axes or ["X", "Y", "Z"],
            "reference": reference,
            "is_aligned": True,
            "aligned_axes": axes or ["X", "Y", "Z"],
            "units": "blender_units",
        }

    def measure_overlap(self, from_object, to_object, tolerance=0.0001):
        return {
            "from_object": from_object,
            "to_object": to_object,
            "overlaps": False,
            "relation": "disjoint",
            "units": "blender_units",
        }

    def assert_contact(self, from_object, to_object, max_gap=0.0001, allow_overlap=False):
        return {
            "assertion": "scene_assert_contact",
            "passed": True,
            "subject": from_object,
            "target": to_object,
            "expected": {"max_gap": max_gap, "allow_overlap": allow_overlap},
            "actual": {"gap": 0.0, "relation": "contact"},
            "delta": {"gap_overage": 0.0},
            "tolerance": max_gap,
            "units": "blender_units",
        }

    def assert_dimensions(self, object_name, expected_dimensions, tolerance=0.0001, world_space=True):
        return {
            "assertion": "scene_assert_dimensions",
            "passed": True,
            "subject": object_name,
            "expected": {"dimensions": expected_dimensions},
            "actual": {"dimensions": expected_dimensions},
            "delta": {"x": 0.0, "y": 0.0, "z": 0.0},
            "tolerance": tolerance,
            "units": "blender_units",
        }


class MeshHandler:
    def get_shape_keys(self, object_name, include_deltas=False):
        return {"shape_key_count": 0}

    def get_loop_normals(self, object_name, selected_only=False):
        return {"custom_normals": False}

    def list_groups(self, object_name, group_type="VERTEX"):
        return {"groups": [{"name": "GroupA"}]}


class SceneInspectHandler:
    def inspect_mesh_topology(self, object_name, detailed=False):
        return {
            "vertex_count": 8,
            "edge_count": 12,
            "face_count": 6,
        }


class UVHandler:
    def list_maps(self, object_name, include_island_counts=False):
        return {"uv_map_count": 1}


class ModelingHandler:
    def get_modifiers(self, object_name):
        return [{"name": "Bevel"}]


def _unwrap_structured(result):
    structured = getattr(result, "structured_content", None)
    if structured is None:
        return None
    if isinstance(structured, dict) and "result" in structured:
        return structured["result"]
    return structured


def test_contract_enabled_tools_expose_output_schema_on_listed_surface():
    """Contract-enabled tools should declare outputSchema on the MCP surface."""

    server = build_server("legacy-flat")

    async def run():
        tools = await server.list_tools()
        by_name = {tool.name: tool for tool in tools}
        return by_name["scene_context"], by_name["mesh_inspect"], by_name["router_set_goal"]

    scene_context_tool, mesh_inspect_tool, router_tool = asyncio.run(run())

    assert scene_context_tool.output_schema is not None
    assert mesh_inspect_tool.output_schema is not None
    assert router_tool.output_schema is not None


def test_scene_context_and_snapshot_deliver_structured_content(monkeypatch):
    """Scene contract tools should surface machine-readable structured content."""

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_scene_handler", lambda: SceneHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.scene.ctx_info", lambda ctx, message: None)

    server = build_server("legacy-flat")

    async def run():
        scene_context = await server.call_tool("scene_context", {"action": "mode"})
        snapshot = await server.call_tool("scene_snapshot_state", {})
        return scene_context, snapshot

    scene_context, snapshot = asyncio.run(run())

    scene_payload = _unwrap_structured(scene_context)
    snapshot_payload = _unwrap_structured(snapshot)

    assert scene_payload["action"] == "mode"
    assert scene_payload["payload"]["active_object"] == "Cube"
    assert snapshot_payload["snapshot"]["object_count"] == 1
    assert snapshot_payload["hash"] == "abc123"


def test_scene_read_contract_tools_deliver_structured_content(monkeypatch):
    """Additional scene read tools should surface structured contracts instead of prose blobs."""

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_scene_handler", lambda: SceneHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.scene.ctx_info", lambda ctx, message: None)

    server = build_server("legacy-flat")

    async def run():
        props = await server.call_tool("scene_get_custom_properties", {"object_name": "Cube"})
        hierarchy = await server.call_tool("scene_get_hierarchy", {})
        bbox = await server.call_tool("scene_get_bounding_box", {"object_name": "Cube"})
        origin = await server.call_tool("scene_get_origin_info", {"object_name": "Cube"})
        return props, hierarchy, bbox, origin

    props, hierarchy, bbox, origin = asyncio.run(run())

    assert _unwrap_structured(props)["properties"]["tag"] == "hero"
    assert _unwrap_structured(hierarchy)["payload"]["total_objects"] == 1
    assert _unwrap_structured(bbox)["payload"]["volume"] == 1.0
    assert _unwrap_structured(origin)["payload"]["origin_world"] == [0, 0, 0]


def test_scene_measure_contract_tools_deliver_structured_content(monkeypatch):
    """Truth-layer measurement tools should surface structured contracts instead of prose blobs."""

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_scene_handler", lambda: SceneHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.scene.ctx_info", lambda ctx, message: None)

    server = build_server("legacy-flat")

    async def run():
        distance = await server.call_tool(
            "scene_measure_distance", {"from_object": "Cube", "to_object": "Sphere", "reference": "ORIGIN"}
        )
        dimensions = await server.call_tool("scene_measure_dimensions", {"object_name": "Cube"})
        gap = await server.call_tool("scene_measure_gap", {"from_object": "Cube", "to_object": "Sphere"})
        alignment = await server.call_tool(
            "scene_measure_alignment",
            {"from_object": "Cube", "to_object": "Sphere", "axes": ["Y", "Z"]},
        )
        overlap = await server.call_tool("scene_measure_overlap", {"from_object": "Cube", "to_object": "Sphere"})
        return distance, dimensions, gap, alignment, overlap

    distance, dimensions, gap, alignment, overlap = asyncio.run(run())

    assert _unwrap_structured(distance)["payload"]["distance"] == 2.0
    assert _unwrap_structured(dimensions)["payload"]["volume"] == 6.0
    assert _unwrap_structured(gap)["payload"]["relation"] == "separated"
    assert _unwrap_structured(alignment)["payload"]["is_aligned"] is True
    assert _unwrap_structured(overlap)["payload"]["relation"] == "disjoint"


def test_scene_assert_contract_tools_deliver_structured_content(monkeypatch):
    """Scene assertion tools should surface structured assertion contracts instead of prose blobs."""

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_scene_handler", lambda: SceneHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.scene.ctx_info", lambda ctx, message: None)

    server = build_server("legacy-flat")

    async def run():
        contact = await server.call_tool(
            "scene_assert_contact",
            {"from_object": "Cube", "to_object": "Sphere", "max_gap": 0.001},
        )
        dimensions = await server.call_tool(
            "scene_assert_dimensions",
            {"object_name": "Cube", "expected_dimensions": [1.0, 2.0, 3.0]},
        )
        return contact, dimensions

    contact, dimensions = asyncio.run(run())

    assert _unwrap_structured(contact)["payload"]["passed"] is True
    assert _unwrap_structured(contact)["payload"]["actual"]["relation"] == "contact"
    assert _unwrap_structured(dimensions)["payload"]["assertion"] == "scene_assert_dimensions"
    assert _unwrap_structured(dimensions)["payload"]["passed"] is True


def test_mesh_inspect_contract_delivers_structured_content(monkeypatch):
    """Mesh contract tools should surface machine-readable structured content."""

    monkeypatch.setattr("server.adapters.mcp.areas.mesh.get_mesh_handler", lambda: MeshHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.mesh.get_scene_handler", lambda: SceneInspectHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.mesh.get_uv_handler", lambda: UVHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.mesh.get_modeling_handler", lambda: ModelingHandler())
    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)

    server = build_server("legacy-flat")

    async def run():
        return await server.call_tool("mesh_inspect", {"action": "summary", "object_name": "Cube"})

    result = asyncio.run(run())
    payload = _unwrap_structured(result)

    assert payload["action"] == "summary"
    assert payload["object_name"] == "Cube"
    assert payload["summary"]["vertex_count"] == 8
    assert payload["summary"]["modifiers"] == ["Bevel"]
