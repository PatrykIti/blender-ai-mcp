from __future__ import annotations

from typing import Any

import pytest
from server.application.tool_handlers.collection_handler import CollectionToolHandler
from server.application.tool_handlers.material_handler import MaterialToolHandler
from server.application.tool_handlers.scene_handler import SceneToolHandler
from server.application.tool_handlers.uv_handler import UVToolHandler
from server.domain.interfaces.rpc import IRpcClient
from server.domain.models.rpc import RpcResponse


class DummyRpc(IRpcClient):
    def __init__(self, responses: dict[str, RpcResponse]) -> None:
        self._responses = responses
        self.calls: list[tuple[str, dict[str, Any] | None]] = []

    def send_request(
        self,
        cmd: str,
        args: dict[str, Any] | None = None,
        timeout_seconds: float | None = None,
        *,
        rpc_timeout_seconds: float | None = None,
    ) -> RpcResponse:
        self.calls.append((cmd, args))
        return self._responses[cmd]


def _ok(result: object) -> RpcResponse:
    return RpcResponse(request_id="req-1", status="ok", result=result)


def test_scene_list_objects_requires_list_of_dicts_payload():
    handler = SceneToolHandler(DummyRpc({"scene.list_objects": _ok([{"name": "Cube", "type": "MESH"}])}))

    result = handler.list_objects()

    assert result == [{"name": "Cube", "type": "MESH"}]


def test_collection_list_collections_rejects_non_dict_items():
    handler = CollectionToolHandler(DummyRpc({"collection.list": _ok(["Environment"])}))

    with pytest.raises(RuntimeError, match="Expected a list of objects in RPC result"):
        handler.list_collections()


def test_material_list_materials_aligns_with_list_of_dict_payload_and_args():
    rpc = DummyRpc(
        {
            "material.list": _ok(
                [
                    {"name": "Steel", "users": 2},
                    {"name": "Glass", "users": 1},
                ]
            )
        }
    )
    handler = MaterialToolHandler(rpc)

    result = handler.list_materials(include_unassigned=False)

    assert result[0]["name"] == "Steel"
    assert rpc.calls == [("material.list", {"include_unassigned": False})]


def test_uv_list_maps_aligns_with_object_payload_and_args():
    rpc = DummyRpc(
        {
            "uv.list_maps": _ok(
                {
                    "object_name": "Wall",
                    "uv_map_count": 1,
                    "uv_maps": [{"name": "UVMap", "is_active": True}],
                }
            )
        }
    )
    handler = UVToolHandler(rpc)

    result = handler.list_maps(object_name="Wall", include_island_counts=True)

    assert result["uv_map_count"] == 1
    assert rpc.calls == [("uv.list_maps", {"object_name": "Wall", "include_island_counts": True})]


def test_scene_measure_tools_align_with_rpc_commands_and_args():
    rpc = DummyRpc(
        {
            "scene.measure_distance": _ok({"distance": 2.0, "reference": "ORIGIN"}),
            "scene.measure_dimensions": _ok({"dimensions": [1.0, 2.0, 3.0], "volume": 6.0}),
            "scene.measure_gap": _ok({"gap": 0.5, "relation": "separated"}),
            "scene.measure_alignment": _ok({"is_aligned": True, "aligned_axes": ["Y", "Z"]}),
            "scene.measure_overlap": _ok({"overlaps": False, "relation": "disjoint"}),
        }
    )
    handler = SceneToolHandler(rpc)

    distance = handler.measure_distance("Cube", "Sphere", reference="ORIGIN")
    dimensions = handler.measure_dimensions("Cube", world_space=False)
    gap = handler.measure_gap("Cube", "Sphere", tolerance=0.01)
    alignment = handler.measure_alignment("Cube", "Sphere", axes=["Y", "Z"], reference="CENTER", tolerance=0.01)
    overlap = handler.measure_overlap("Cube", "Sphere", tolerance=0.01)

    assert distance["distance"] == 2.0
    assert dimensions["volume"] == 6.0
    assert gap["relation"] == "separated"
    assert alignment["is_aligned"] is True
    assert overlap["overlaps"] is False
    assert rpc.calls == [
        ("scene.measure_distance", {"from_object": "Cube", "to_object": "Sphere", "reference": "ORIGIN"}),
        ("scene.measure_dimensions", {"object_name": "Cube", "world_space": False}),
        ("scene.measure_gap", {"from_object": "Cube", "to_object": "Sphere", "tolerance": 0.01}),
        (
            "scene.measure_alignment",
            {
                "from_object": "Cube",
                "to_object": "Sphere",
                "axes": ["Y", "Z"],
                "reference": "CENTER",
                "tolerance": 0.01,
            },
        ),
        ("scene.measure_overlap", {"from_object": "Cube", "to_object": "Sphere", "tolerance": 0.01}),
    ]


def test_scene_assert_tools_align_with_rpc_commands_and_args():
    rpc = DummyRpc(
        {
            "scene.assert_contact": _ok({"assertion": "scene_assert_contact", "passed": True}),
            "scene.assert_dimensions": _ok({"assertion": "scene_assert_dimensions", "passed": False}),
            "scene.assert_containment": _ok({"assertion": "scene_assert_containment", "passed": True}),
            "scene.assert_symmetry": _ok({"assertion": "scene_assert_symmetry", "passed": False}),
            "scene.assert_proportion": _ok({"assertion": "scene_assert_proportion", "passed": True}),
        }
    )
    handler = SceneToolHandler(rpc)

    contact = handler.assert_contact("Cube", "Sphere", max_gap=0.01, allow_overlap=True)
    dimensions = handler.assert_dimensions("Cube", [1.0, 2.0, 3.0], tolerance=0.01, world_space=False)
    containment = handler.assert_containment("Inner", "Outer", min_clearance=0.1, tolerance=0.01)
    symmetry = handler.assert_symmetry("Left", "Right", axis="X", mirror_coordinate=0.0, tolerance=0.01)
    proportion = handler.assert_proportion("Cube", axis_a="X", axis_b="Y", expected_ratio=0.5, tolerance=0.01)

    assert contact["passed"] is True
    assert dimensions["assertion"] == "scene_assert_dimensions"
    assert containment["assertion"] == "scene_assert_containment"
    assert symmetry["assertion"] == "scene_assert_symmetry"
    assert proportion["assertion"] == "scene_assert_proportion"
    assert rpc.calls == [
        (
            "scene.assert_contact",
            {"from_object": "Cube", "to_object": "Sphere", "max_gap": 0.01, "allow_overlap": True},
        ),
        (
            "scene.assert_dimensions",
            {
                "object_name": "Cube",
                "expected_dimensions": [1.0, 2.0, 3.0],
                "tolerance": 0.01,
                "world_space": False,
            },
        ),
        (
            "scene.assert_containment",
            {"inner_object": "Inner", "outer_object": "Outer", "min_clearance": 0.1, "tolerance": 0.01},
        ),
        (
            "scene.assert_symmetry",
            {
                "left_object": "Left",
                "right_object": "Right",
                "axis": "X",
                "mirror_coordinate": 0.0,
                "tolerance": 0.01,
            },
        ),
        (
            "scene.assert_proportion",
            {
                "object_name": "Cube",
                "axis_a": "X",
                "expected_ratio": 0.5,
                "axis_b": "Y",
                "reference_object": None,
                "reference_axis": None,
                "tolerance": 0.01,
                "world_space": True,
            },
        ),
    ]


def test_scene_spatial_graph_handlers_reuse_existing_scene_truth_rpc_commands():
    rpc = DummyRpc(
        {
            "scene.get_bounding_box": _ok({"dimensions": [2.0, 2.0, 2.0], "center": [0.0, 0.0, 0.0]}),
            "scene.measure_gap": _ok({"gap": 0.1, "relation": "separated", "measurement_basis": "bounding_box"}),
            "scene.measure_alignment": _ok({"is_aligned": False, "aligned_axes": ["Y", "Z"]}),
            "scene.measure_overlap": _ok(
                {"overlaps": False, "relation": "disjoint", "measurement_basis": "bounding_box"}
            ),
            "scene.assert_contact": _ok(
                {
                    "assertion": "scene_assert_contact",
                    "passed": False,
                    "actual": {"gap": 0.1, "relation": "separated"},
                    "details": {"measurement_basis": "bounding_box"},
                }
            ),
        }
    )
    handler = SceneToolHandler(rpc)

    scope = handler.get_scope_graph(target_objects=["Head", "Body"])
    relations = handler.get_relation_graph(target_objects=["Head", "Body"], goal_hint="assembled creature")

    assert scope["primary_target"] == "Body"
    assert scope["object_roles"][0]["object_name"] == "Head"
    assert relations["summary"]["pair_count"] == 1
    assert relations["pairs"][0]["from_object"] == "Head"
    assert "contact" in relations["pairs"][0]["relation_kinds"]
    assert rpc.calls[:6] == [
        ("scene.get_bounding_box", {"object_name": "Head", "world_space": True}),
        ("scene.get_bounding_box", {"object_name": "Body", "world_space": True}),
        ("scene.get_bounding_box", {"object_name": "Head", "world_space": True}),
        ("scene.get_bounding_box", {"object_name": "Body", "world_space": True}),
        ("scene.get_bounding_box", {"object_name": "Head", "world_space": True}),
        ("scene.get_bounding_box", {"object_name": "Body", "world_space": True}),
    ]
    assert rpc.calls[6:] == [
        ("scene.measure_gap", {"from_object": "Head", "to_object": "Body", "tolerance": 0.0001}),
        (
            "scene.measure_alignment",
            {
                "from_object": "Head",
                "to_object": "Body",
                "axes": ["X", "Y", "Z"],
                "reference": "CENTER",
                "tolerance": 0.0001,
            },
        ),
        ("scene.measure_overlap", {"from_object": "Head", "to_object": "Body", "tolerance": 0.0001}),
        (
            "scene.assert_contact",
            {"from_object": "Head", "to_object": "Body", "max_gap": 0.0001, "allow_overlap": False},
        ),
    ]


def test_scene_relation_graph_treats_forel_hindr_names_as_limb_body_pairs():
    rpc = DummyRpc(
        {
            "scene.get_bounding_box": _ok({"dimensions": [2.0, 2.0, 2.0], "center": [0.0, 0.0, 0.0]}),
            "scene.measure_gap": _ok({"gap": 0.1, "relation": "separated", "measurement_basis": "bounding_box"}),
            "scene.measure_alignment": _ok({"is_aligned": True, "aligned_axes": ["X", "Y"]}),
            "scene.measure_overlap": _ok(
                {"overlaps": False, "relation": "disjoint", "measurement_basis": "bounding_box"}
            ),
            "scene.assert_contact": _ok(
                {
                    "assertion": "scene_assert_contact",
                    "passed": False,
                    "actual": {"gap": 0.1, "relation": "separated"},
                    "details": {"measurement_basis": "bounding_box"},
                }
            ),
        }
    )
    handler = SceneToolHandler(rpc)

    relations = handler.get_relation_graph(target_objects=["Body", "ForeL", "HindR"], goal_hint="assembled creature")
    pair_ids = {item["pair_id"] for item in relations["pairs"]}
    seam_kinds = {
        item["pair_id"]: item["attachment_semantics"]["seam_kind"]
        for item in relations["pairs"]
        if item.get("attachment_semantics")
    }

    assert "forel__body" in pair_ids
    assert "hindr__body" in pair_ids
    assert seam_kinds["forel__body"] == "limb_body"
    assert seam_kinds["hindr__body"] == "limb_body"


def test_scene_view_diagnostics_handler_resolves_collection_scope_and_forwards_view_args():
    rpc = DummyRpc(
        {
            "collection.list_objects": _ok({"objects": [{"name": "Head"}, {"name": "Body"}]}),
            "scene.get_view_diagnostics": _ok(
                {
                    "view_query": {
                        "requested_view_source": "user_perspective",
                        "resolved_view_source": "user_perspective",
                        "analysis_backend": "mirrored_user_perspective",
                        "available": True,
                        "state_restored": True,
                    },
                    "targets": [
                        {
                            "object_name": "Head",
                            "visibility_verdict": "visible",
                            "projection_status": "projected",
                        }
                    ],
                    "summary": {
                        "target_count": 2,
                        "visible_count": 1,
                        "partially_visible_count": 1,
                    },
                }
            ),
        }
    )
    handler = SceneToolHandler(rpc)

    diagnostics = handler.get_view_diagnostics(
        target_object="Head",
        collection_name="CreatureParts",
        view_name="TOP",
        orbit_horizontal=20.0,
        zoom_factor=1.2,
    )

    assert diagnostics["summary"]["target_count"] == 2
    assert diagnostics["view_query"]["analysis_backend"] == "mirrored_user_perspective"
    assert rpc.calls == [
        (
            "collection.list_objects",
            {"collection_name": "CreatureParts", "recursive": True, "include_hidden": False},
        ),
        (
            "scene.get_view_diagnostics",
            {
                "target_object": "Head",
                "target_objects": ["Head", "Body"],
                "camera_name": None,
                "focus_target": None,
                "view_name": "TOP",
                "orbit_horizontal": 20.0,
                "orbit_vertical": 0.0,
                "zoom_factor": 1.2,
                "persist_view": False,
            },
        ),
    ]


def test_scene_inspect_scene_state_handlers_align_with_rpc_commands():
    rpc = DummyRpc(
        {
            "scene.inspect_render_settings": _ok({"render_engine": "BLENDER_EEVEE_NEXT"}),
            "scene.inspect_color_management": _ok({"view_transform": "AgX"}),
            "scene.inspect_world": _ok({"world_name": "Studio"}),
        }
    )
    handler = SceneToolHandler(rpc)

    render = handler.inspect_render_settings()
    color = handler.inspect_color_management()
    world = handler.inspect_world()

    assert render["render_engine"] == "BLENDER_EEVEE_NEXT"
    assert color["view_transform"] == "AgX"
    assert world["world_name"] == "Studio"
    assert rpc.calls == [
        ("scene.inspect_render_settings", None),
        ("scene.inspect_color_management", None),
        ("scene.inspect_world", None),
    ]


def test_scene_view_state_handlers_align_with_rpc_commands():
    rpc = DummyRpc(
        {
            "scene.get_view_state": _ok({"available": True, "view_distance": 10.0}),
            "scene.restore_view_state": _ok("Restored 3D viewport state"),
        }
    )
    handler = SceneToolHandler(rpc)

    view_state = handler.get_view_state()
    restored = handler.restore_view_state({"view_distance": 10.0})

    assert view_state["available"] is True
    assert restored == "Restored 3D viewport state"
    assert rpc.calls == [
        ("scene.get_view_state", None),
        ("scene.restore_view_state", {"view_state": {"view_distance": 10.0}}),
    ]


def test_scene_standard_view_handler_aligns_with_rpc_command():
    rpc = DummyRpc({"scene.set_standard_view": _ok("Set 3D viewport to FRONT view")})
    handler = SceneToolHandler(rpc)

    result = handler.set_standard_view("FRONT")

    assert result == "Set 3D viewport to FRONT view"
    assert rpc.calls == [("scene.set_standard_view", {"view_name": "FRONT"})]


def test_scene_configure_handlers_align_with_rpc_commands():
    rpc = DummyRpc(
        {
            "scene.configure_render_settings": _ok({"render_engine": "CYCLES"}),
            "scene.configure_color_management": _ok({"view_transform": "AgX"}),
            "scene.configure_world": _ok({"world_name": "Studio"}),
        }
    )
    handler = SceneToolHandler(rpc)

    render = handler.configure_render_settings({"render_engine": "CYCLES"})
    color = handler.configure_color_management({"view_transform": "AgX"})
    world = handler.configure_world({"world_name": "Studio"})

    assert render["render_engine"] == "CYCLES"
    assert color["view_transform"] == "AgX"
    assert world["world_name"] == "Studio"
    assert rpc.calls == [
        ("scene.configure_render_settings", {"settings": {"render_engine": "CYCLES"}}),
        ("scene.configure_color_management", {"settings": {"view_transform": "AgX"}}),
        ("scene.configure_world", {"settings": {"world_name": "Studio"}}),
    ]
