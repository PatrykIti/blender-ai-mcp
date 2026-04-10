"""
E2E tests for the first measure/assert scene tools (TASK-116).
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


def test_scene_measure_distance_and_gap(scene_handler, modeling_handler):
    left_name = "E2E_Measure_Left"
    right_name = "E2E_Measure_Right"

    try:
        for name in (left_name, right_name):
            try:
                scene_handler.delete_object(name)
            except RuntimeError:
                pass

        modeling_handler.create_primitive(primitive_type="CUBE", name=left_name, size=2.0, location=[0, 0, 0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=right_name, size=2.0, location=[4, 0, 0])

        distance = scene_handler.measure_distance(left_name, right_name, reference="ORIGIN")
        gap = scene_handler.measure_gap(left_name, right_name)

        assert distance["distance"] == pytest.approx(4.0, abs=1e-4)
        assert gap["gap"] == pytest.approx(2.0, abs=1e-4)
        assert gap["relation"] == "separated"
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")
    finally:
        for name in (left_name, right_name):
            try:
                scene_handler.delete_object(name)
            except RuntimeError:
                pass


def test_scene_measure_dimensions_alignment_and_overlap(scene_handler, modeling_handler):
    base_name = "E2E_Measure_Base"
    overlap_name = "E2E_Measure_Overlap"

    try:
        for name in (base_name, overlap_name):
            try:
                scene_handler.delete_object(name)
            except RuntimeError:
                pass

        modeling_handler.create_primitive(primitive_type="CUBE", name=base_name, size=2.0, location=[0, 0, 0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=overlap_name, size=2.0, location=[1, 0, 0])

        dimensions = scene_handler.measure_dimensions(base_name)
        alignment = scene_handler.measure_alignment(base_name, overlap_name, axes=["Y", "Z"], reference="CENTER")
        overlap = scene_handler.measure_overlap(base_name, overlap_name)

        assert dimensions["dimensions"] == pytest.approx([2.0, 2.0, 2.0], abs=1e-4)
        assert dimensions["volume"] == pytest.approx(8.0, abs=1e-4)
        assert alignment["is_aligned"] is True
        assert alignment["aligned_axes"] == ["Y", "Z"]
        assert overlap["overlaps"] is True
        assert overlap["relation"] == "overlap"
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")
    finally:
        for name in (base_name, overlap_name):
            try:
                scene_handler.delete_object(name)
            except RuntimeError:
                pass


def test_scene_spatial_graph_handlers_expose_scope_and_relation_state(scene_handler, modeling_handler):
    head_name = "E2E_Scope_Head"
    body_name = "E2E_Scope_Body"

    try:
        for name in (head_name, body_name):
            try:
                scene_handler.delete_object(name)
            except RuntimeError:
                pass

        modeling_handler.create_primitive(primitive_type="CUBE", name=head_name, size=2.0, location=[0, 0, 0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=body_name, size=2.5, location=[4, 0, 0])

        scope = scene_handler.get_scope_graph(target_objects=[head_name, body_name])
        relations = scene_handler.get_relation_graph(
            target_objects=[head_name, body_name], goal_hint="assembled creature"
        )

        assert scope["primary_target"] == body_name
        assert any(item["object_name"] == body_name and item["role"] == "anchor_core" for item in scope["object_roles"])
        assert relations["summary"]["pair_count"] == 1
        assert relations["pairs"][0]["from_object"] == head_name
        assert "attachment" in relations["pairs"][0]["relation_kinds"]
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")
    finally:
        for name in (head_name, body_name):
            try:
                scene_handler.delete_object(name)
            except RuntimeError:
                pass


def test_scene_relation_graph_treats_forel_hindr_names_as_limb_body_pairs(scene_handler, modeling_handler):
    object_names = {
        "Body": "E2E_Abbrev_Body",
        "ForeL": "E2E_Abbrev_ForeL",
        "HindR": "E2E_Abbrev_HindR",
    }

    try:
        for name in object_names.values():
            try:
                scene_handler.delete_object(name)
            except RuntimeError:
                pass

        modeling_handler.create_primitive(
            primitive_type="CUBE", name=object_names["Body"], size=2.5, location=[0, 0, 0]
        )
        modeling_handler.create_primitive(
            primitive_type="CUBE", name=object_names["ForeL"], size=0.8, location=[-2, 0, -1]
        )
        modeling_handler.create_primitive(
            primitive_type="CUBE", name=object_names["HindR"], size=0.8, location=[2, 0, -1]
        )

        relations = scene_handler.get_relation_graph(
            target_objects=list(object_names.values()),
            goal_hint="assembled creature limb placement",
        )
        seam_kinds = {
            item["pair_id"]: item["attachment_semantics"]["seam_kind"]
            for item in relations["pairs"]
            if item.get("attachment_semantics")
        }

        assert f"{object_names['ForeL'].lower()}__{object_names['Body'].lower()}" in seam_kinds
        assert f"{object_names['HindR'].lower()}__{object_names['Body'].lower()}" in seam_kinds
        assert seam_kinds[f"{object_names['ForeL'].lower()}__{object_names['Body'].lower()}"] == "limb_body"
        assert seam_kinds[f"{object_names['HindR'].lower()}__{object_names['Body'].lower()}"] == "limb_body"
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")
    finally:
        for name in object_names.values():
            try:
                scene_handler.delete_object(name)
            except RuntimeError:
                pass
