"""
E2E tests for the first scene assertion tools (TASK-117 start).
"""

import pytest
from server.application.tool_handlers.modeling_handler import ModelingToolHandler
from server.application.tool_handlers.scene_handler import SceneToolHandler


@pytest.fixture
def scene_handler(rpc_client):
    """Provides a scene handler instance using shared RPC client."""
    return SceneToolHandler(rpc_client)


@pytest.fixture
def modeling_handler(rpc_client):
    """Provides a modeling handler instance using shared RPC client."""
    return ModelingToolHandler(rpc_client)


def test_scene_assert_contact(scene_handler, modeling_handler):
    left_name = "E2E_Assert_Left"
    right_name = "E2E_Assert_Right"

    try:
        for name in (left_name, right_name):
            try:
                scene_handler.delete_object(name)
            except RuntimeError:
                pass

        modeling_handler.create_primitive(primitive_type="CUBE", name=left_name, size=2.0, location=[0, 0, 0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=right_name, size=2.0, location=[2, 0, 0])

        result = scene_handler.assert_contact(left_name, right_name, max_gap=0.0001)

        assert result["passed"] is True
        assert result["actual"]["relation"] == "contact"
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")
    finally:
        for name in (left_name, right_name):
            try:
                scene_handler.delete_object(name)
            except RuntimeError:
                pass


def test_scene_assert_contact_rejects_bbox_touching_but_visibly_gapped_spheres(scene_handler, modeling_handler):
    head_name = "E2E_Assert_Head"
    eye_name = "E2E_Assert_Eye"

    try:
        for name in (head_name, eye_name):
            try:
                scene_handler.delete_object(name)
            except RuntimeError:
                pass

        modeling_handler.create_primitive(primitive_type="Sphere", name=head_name, radius=1.0, location=[0, 0, 0])
        modeling_handler.create_primitive(primitive_type="Sphere", name=eye_name, radius=0.2, location=[0.5, 1.2, 0.5])

        gap = scene_handler.measure_gap(head_name, eye_name, tolerance=0.0001)
        result = scene_handler.assert_contact(head_name, eye_name, max_gap=0.001)

        assert gap["measurement_basis"] == "mesh_surface"
        assert gap["relation"] == "separated"
        assert gap["bbox_relation"] == "contact"
        assert gap["gap"] > 0.01
        assert result["passed"] is False
        assert result["actual"]["relation"] == "separated"
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")
    finally:
        for name in (head_name, eye_name):
            try:
                scene_handler.delete_object(name)
            except RuntimeError:
                pass


def test_scene_assert_contact_accepts_tail_body_attachment_pair(scene_handler, modeling_handler):
    body_name = "E2E_Assert_Body"
    tail_name = "E2E_Assert_Tail"

    try:
        for name in (body_name, tail_name):
            try:
                scene_handler.delete_object(name)
            except RuntimeError:
                pass

        modeling_handler.create_primitive(primitive_type="CUBE", name=body_name, size=2.0, location=[0, 0, 0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=tail_name, size=1.0, location=[1.3, 0, 0])
        modeling_handler.transform_object(name=tail_name, scale=[0.6, 0.25, 0.25])

        gap = scene_handler.measure_gap(tail_name, body_name, tolerance=0.0001)
        result = scene_handler.assert_contact(tail_name, body_name, max_gap=0.001)

        assert gap["relation"] == "contact"
        assert result["passed"] is True
        assert result["actual"]["relation"] == "contact"
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")
    finally:
        for name in (body_name, tail_name):
            try:
                scene_handler.delete_object(name)
            except RuntimeError:
                pass


def test_scene_assert_contact_accepts_forelimb_body_attachment_pair(scene_handler, modeling_handler):
    body_name = "E2E_Assert_LimbBody"
    forelimb_name = "E2E_Assert_Forelimb"

    try:
        for name in (body_name, forelimb_name):
            try:
                scene_handler.delete_object(name)
            except RuntimeError:
                pass

        modeling_handler.create_primitive(primitive_type="CUBE", name=body_name, size=2.0, location=[0, 0, 0])
        modeling_handler.create_primitive(
            primitive_type="CUBE", name=forelimb_name, size=1.0, location=[1.0, 0.0, -1.15]
        )
        modeling_handler.transform_object(name=forelimb_name, scale=[0.6, 0.3, 0.3])

        gap = scene_handler.measure_gap(forelimb_name, body_name, tolerance=0.0001)
        result = scene_handler.assert_contact(forelimb_name, body_name, max_gap=0.001)

        assert gap["relation"] == "contact"
        assert result["passed"] is True
        assert result["actual"]["relation"] == "contact"
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")
    finally:
        for name in (body_name, forelimb_name):
            try:
                scene_handler.delete_object(name)
            except RuntimeError:
                pass


def test_scene_assert_dimensions(scene_handler, modeling_handler):
    cube_name = "E2E_Assert_Dimensions"

    try:
        try:
            scene_handler.delete_object(cube_name)
        except RuntimeError:
            pass

        modeling_handler.create_primitive(primitive_type="CUBE", name=cube_name, size=2.0, location=[0, 0, 0])

        result = scene_handler.assert_dimensions(cube_name, [2.0, 2.0, 2.0], tolerance=0.0001)

        assert result["passed"] is True
        assert result["assertion"] == "scene_assert_dimensions"
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")
    finally:
        try:
            scene_handler.delete_object(cube_name)
        except RuntimeError:
            pass


def test_scene_assert_containment_and_symmetry(scene_handler, modeling_handler):
    inner_name = "E2E_Assert_Inner"
    outer_name = "E2E_Assert_Outer"
    left_name = "E2E_Assert_Left"
    right_name = "E2E_Assert_Right"

    try:
        for name in (inner_name, outer_name, left_name, right_name):
            try:
                scene_handler.delete_object(name)
            except RuntimeError:
                pass

        modeling_handler.create_primitive(primitive_type="CUBE", name=outer_name, size=4.0, location=[0, 0, 0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=inner_name, size=2.0, location=[0, 0, 0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=left_name, size=2.0, location=[-2, 0, 0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=right_name, size=2.0, location=[2, 0, 0])

        containment = scene_handler.assert_containment(inner_name, outer_name, min_clearance=0.0, tolerance=0.0001)
        symmetry = scene_handler.assert_symmetry(left_name, right_name, axis="X", mirror_coordinate=0.0)

        assert containment["passed"] is True
        assert symmetry["passed"] is True
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")
    finally:
        for name in (inner_name, outer_name, left_name, right_name):
            try:
                scene_handler.delete_object(name)
            except RuntimeError:
                pass
