"""
E2E Tests for full extraction pipeline (TASK-044)

Tests the complete extraction workflow:
deep_topology -> detect_symmetry -> edge_loop_analysis -> face_group_analysis

These tests require a running Blender instance with the addon loaded.
"""
import pytest


def test_full_extraction_pipeline(extraction_handler, test_cube):
    """
    Test complete extraction pipeline:
    1. Deep topology analysis
    2. Symmetry detection
    3. Edge loop analysis
    4. Face group analysis
    """
    try:
        # Step 1: Deep topology
        topology = extraction_handler.deep_topology(test_cube)
        assert "vertex_count" in topology
        print(f"✓ Step 1: Deep topology - {topology['vertex_count']} vertices, {topology['face_count']} faces")
        print(f"  Base primitive: {topology['base_primitive']}")

        # Step 2: Symmetry detection
        symmetry = extraction_handler.detect_symmetry(test_cube)
        assert "x_symmetric" in symmetry
        symmetries = []
        if symmetry["x_symmetric"]:
            symmetries.append("X")
        if symmetry["y_symmetric"]:
            symmetries.append("Y")
        if symmetry["z_symmetric"]:
            symmetries.append("Z")
        print(f"✓ Step 2: Symmetry - {', '.join(symmetries) if symmetries else 'None'}")

        # Step 3: Edge loop analysis
        edges = extraction_handler.edge_loop_analysis(test_cube)
        assert "chamfer_edges" in edges
        print(f"✓ Step 3: Edge loops - {edges.get('parallel_edge_groups', 0)} parallel groups")
        print(f"  Has chamfer: {edges['has_chamfer']}")

        # Step 4: Face group analysis
        faces = extraction_handler.face_group_analysis(test_cube)
        assert "face_groups" in faces
        print(f"✓ Step 4: Face groups - {faces['normal_group_count']} normal groups")
        print(f"  Has insets: {faces['has_insets']}, Has extrusions: {faces['has_extrusions']}")

        print("\n✅ Full extraction pipeline completed successfully!")

    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "connection" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_extraction_for_workflow_generation(extraction_handler, test_cube):
    """
    Test extraction data is suitable for workflow generation.
    Checks that all data needed for TASK-042 workflow extraction is present.
    """
    try:
        # Get topology
        topology = extraction_handler.deep_topology(test_cube)

        # Verify workflow-critical data exists
        assert "base_primitive" in topology, "Need base_primitive for workflow start"
        assert "primitive_confidence" in topology, "Need confidence for decision making"
        assert "bounding_box" in topology, "Need bbox for proportion calculations"
        assert "has_beveled_edges" in topology, "Need bevel detection"
        assert "has_inset_faces" in topology, "Need inset detection"
        assert "has_extrusions" in topology, "Need extrusion detection"

        # Get symmetry for mirror modifier detection
        symmetry = extraction_handler.detect_symmetry(test_cube)
        assert "x_symmetric" in symmetry
        assert "x_confidence" in symmetry

        # Get face groups for operation detection
        faces = extraction_handler.face_group_analysis(test_cube)
        assert "detected_insets" in faces
        assert "detected_extrusions" in faces
        assert "height_levels" in faces

        print("✅ All workflow generation data is available!")
        print(f"  Base: {topology['base_primitive']} (confidence: {topology['primitive_confidence']})")
        print(f"  Features: bevel={topology['has_beveled_edges']}, inset={topology['has_inset_faces']}, extrude={topology['has_extrusions']}")
        print(f"  Symmetry: X={symmetry['x_confidence']:.2f}, Y={symmetry['y_confidence']:.2f}, Z={symmetry['z_confidence']:.2f}")

    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "connection" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise
