"""Blender-backed creature profile proof for TASK-135-03-02-02.

Limb seating and tail-arc proof already live in the existing macro E2E lanes.
This file closes the remaining body, ear, and snout profile cases with the
current bounded mesh tools only.
"""

from __future__ import annotations

import pytest
from server.application.tool_handlers.mesh_handler import MeshToolHandler
from server.application.tool_handlers.modeling_handler import ModelingToolHandler
from server.application.tool_handlers.scene_handler import SceneToolHandler

pytestmark = pytest.mark.e2e


def _skip_if_blender_unavailable(error: RuntimeError) -> None:
    error_msg = str(error).lower()
    if "could not connect" in error_msg or "is blender running" in error_msg:
        pytest.skip(f"Blender not available: {error}")
    raise error


@pytest.fixture(scope="session")
def mesh_handler(rpc_client):
    return MeshToolHandler(rpc_client)


@pytest.fixture(scope="session")
def modeling_handler(rpc_client):
    return ModelingToolHandler(rpc_client)


@pytest.fixture(scope="session")
def scene_handler(rpc_client):
    return SceneToolHandler(rpc_client)


@pytest.fixture
def clean_scene(scene_handler):
    scene_handler.clean_scene(keep_lights_and_cameras=False)
    yield
    scene_handler.clean_scene(keep_lights_and_cameras=False)


def test_creature_body_mass_can_be_profiled_with_extrude_and_support_cuts(
    clean_scene,
    mesh_handler,
    modeling_handler,
    scene_handler,
):
    body_name = "ProfileBody"

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=body_name, size=2.0, location=[0.0, 0.0, 0.0])

        baseline_bbox = scene_handler.get_bounding_box(body_name)
        baseline_topology = scene_handler.inspect_mesh_topology(body_name, detailed=False)

        scene_handler.set_active_object(body_name)
        scene_handler.set_mode("EDIT")
        mesh_handler.select_by_location(axis="X", min_coord=0.95, max_coord=1.05, mode="FACE")
        mesh_handler.extrude_region(move=[0.9, 0.0, 0.0])
        mesh_handler.select_by_location(axis="X", min_coord=-1.05, max_coord=-0.95, mode="FACE")
        mesh_handler.extrude_region(move=[-0.6, 0.0, 0.0])
        mesh_handler.select_all(deselect=False)
        mesh_handler.loop_cut(number_cuts=1)
        scene_handler.set_mode("OBJECT")

        profiled_bbox = scene_handler.get_bounding_box(body_name)
        profiled_topology = scene_handler.inspect_mesh_topology(body_name, detailed=False)
        inspect_payload = scene_handler.inspect_object(body_name)

        assert profiled_bbox["dimensions"][0] > baseline_bbox["dimensions"][0] + 1.0
        assert profiled_topology["face_count"] > baseline_topology["face_count"]
        assert inspect_payload["object_name"] == body_name
    except RuntimeError as error:
        _skip_if_blender_unavailable(error)


def test_creature_ear_pair_can_be_pointed_without_losing_head_contact(
    clean_scene,
    mesh_handler,
    modeling_handler,
    scene_handler,
):
    head_name = "ProfileHead"
    ear_names = ("ProfileEarLeft", "ProfileEarRight")

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=head_name, size=2.0, location=[0.0, 0.0, 0.0])
        modeling_handler.create_primitive(
            primitive_type="CUBE",
            name=ear_names[0],
            size=0.6,
            location=[-0.45, 0.0, 1.3],
        )
        modeling_handler.create_primitive(
            primitive_type="CUBE",
            name=ear_names[1],
            size=0.6,
            location=[0.45, 0.0, 1.3],
        )

        baseline = {name: scene_handler.inspect_mesh_topology(name, detailed=False) for name in ear_names}

        for ear_name in ear_names:
            scene_handler.set_active_object(ear_name)
            scene_handler.set_mode("EDIT")
            mesh_handler.select_by_location(axis="Z", min_coord=0.25, max_coord=0.35, mode="VERT")
            mesh_handler.merge_by_distance(distance=1.0)
            scene_handler.set_mode("OBJECT")

        profiled = {name: scene_handler.inspect_mesh_topology(name, detailed=False) for name in ear_names}
        left_bbox = scene_handler.get_bounding_box(ear_names[0])
        right_bbox = scene_handler.get_bounding_box(ear_names[1])

        for ear_name in ear_names:
            gap = scene_handler.measure_gap(ear_name, head_name)
            contact = scene_handler.assert_contact(ear_name, head_name, max_gap=0.001)

            assert profiled[ear_name]["vertex_count"] < baseline[ear_name]["vertex_count"]
            assert gap["gap"] == pytest.approx(0.0, abs=1e-4)
            assert contact["passed"] is True

        assert left_bbox["dimensions"] == pytest.approx(right_bbox["dimensions"], abs=1e-4)
    except RuntimeError as error:
        _skip_if_blender_unavailable(error)


def test_creature_snout_can_be_wedged_with_existing_mesh_selection_tools(
    clean_scene,
    mesh_handler,
    modeling_handler,
    scene_handler,
):
    head_name = "ProfileSnoutHead"
    snout_name = "ProfileSnout"

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=head_name, size=1.6, location=[0.0, 0.0, 0.0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=snout_name, size=0.8, location=[1.2, 0.0, 0.0])

        baseline_topology = scene_handler.inspect_mesh_topology(snout_name, detailed=False)

        scene_handler.set_active_object(snout_name)
        scene_handler.set_mode("EDIT")
        mesh_handler.select_by_location(axis="X", min_coord=0.35, max_coord=0.45, mode="VERT")
        mesh_handler.merge_by_distance(distance=2.0)
        scene_handler.set_mode("OBJECT")

        profiled_topology = scene_handler.inspect_mesh_topology(snout_name, detailed=False)
        gap = scene_handler.measure_gap(snout_name, head_name)
        contact = scene_handler.assert_contact(snout_name, head_name, max_gap=0.001)

        assert profiled_topology["vertex_count"] < baseline_topology["vertex_count"]
        assert profiled_topology["face_count"] <= baseline_topology["face_count"]
        assert gap["gap"] == pytest.approx(0.0, abs=1e-4)
        assert contact["passed"] is True
    except RuntimeError as error:
        _skip_if_blender_unavailable(error)
