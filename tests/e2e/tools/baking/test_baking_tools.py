"""
E2E Tests for TASK-031: Baking Tools

Tests require a running Blender instance with the addon loaded.
Run: pytest tests/e2e/tools/baking/test_baking_tools.py -v

Tested tools:
- bake_normal_map
- bake_ao
- bake_combined
- bake_diffuse
"""
import pytest
import os
import tempfile
from server.application.tool_handlers.baking_handler import BakingToolHandler
from server.application.tool_handlers.modeling_handler import ModelingToolHandler
from server.application.tool_handlers.scene_handler import SceneToolHandler
from server.application.tool_handlers.uv_handler import UVToolHandler
from server.application.tool_handlers.material_handler import MaterialToolHandler


@pytest.fixture
def baking_handler(rpc_client):
    """Provides a baking handler instance using shared RPC client."""
    return BakingToolHandler(rpc_client)


@pytest.fixture
def modeling_handler(rpc_client):
    """Provides a modeling handler instance using shared RPC client."""
    return ModelingToolHandler(rpc_client)


@pytest.fixture
def scene_handler(rpc_client):
    """Provides a scene handler instance using shared RPC client."""
    return SceneToolHandler(rpc_client)


@pytest.fixture
def uv_handler(rpc_client):
    """Provides a UV handler instance using shared RPC client."""
    return UVToolHandler(rpc_client)


@pytest.fixture
def material_handler(rpc_client):
    """Provides a material handler instance using shared RPC client."""
    return MaterialToolHandler(rpc_client)


# ==============================================================================
# Setup Helpers
# ==============================================================================

def create_test_object_with_uv(modeling_handler, scene_handler, uv_handler, name="E2E_BakeTest"):
    """Creates a test object with UV map for baking."""
    try:
        # Clean up existing
        scene_handler.delete_object(name)
    except RuntimeError:
        pass  # Object didn't exist

    # Create UV sphere (better for baking than cube)
    result = modeling_handler.create_primitive(
        primitive_type="UV_SPHERE",
        radius=1.0,
        location=[0, 0, 0],
        name=name
    )

    # Parse actual object name from result (format: "Created UV_SPHERE named 'ActualName'")
    import re
    match = re.search(r"named '([^']+)'", result)
    actual_name = match.group(1) if match else name

    # Unwrap UV
    uv_handler.unwrap(object_name=actual_name, method="SMART_PROJECT")

    return actual_name


def get_temp_output_path(suffix=".png"):
    """Gets a temporary output path for baked images."""
    return os.path.join(tempfile.gettempdir(), f"blender_bake_test{suffix}")


# ==============================================================================
# TASK-031-1: bake_normal_map Tests
# ==============================================================================

def test_bake_normal_self(baking_handler, modeling_handler, scene_handler, uv_handler):
    """Test normal map self-bake from object's own geometry."""
    try:
        # Setup
        obj_name = create_test_object_with_uv(modeling_handler, scene_handler, uv_handler, "E2E_NormalBake1")
        output_path = get_temp_output_path("_normal.png")

        # Test
        result = baking_handler.bake_normal_map(
            object_name=obj_name,
            output_path=output_path,
            resolution=512
        )

        # Verify
        assert "normal map" in result.lower()
        assert "self-bake" in result
        assert os.path.exists(output_path), f"Baked image not found at {output_path}"
        print(f"✓ bake_normal_map (self): {result}")

        # Cleanup
        if os.path.exists(output_path):
            os.remove(output_path)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_bake_normal_high_to_low(baking_handler, modeling_handler, scene_handler, uv_handler):
    """Test normal map baking from high-poly to low-poly."""
    import re
    try:
        # Create low-poly target directly (UV_SPHERE has built-in UVs)
        try:
            scene_handler.delete_object("E2E_H2L_LowPoly")
        except RuntimeError:
            pass
        low_result = modeling_handler.create_primitive(
            primitive_type="UV_SPHERE",
            radius=1.0,
            location=[0, 0, 0],
            name="E2E_H2L_LowPoly"
        )
        match = re.search(r"named '([^']+)'", low_result)
        low_poly = match.group(1) if match else "E2E_H2L_LowPoly"

        # Create high-poly source (larger sphere)
        try:
            scene_handler.delete_object("E2E_H2L_HighPoly")
        except RuntimeError:
            pass
        high_result = modeling_handler.create_primitive(
            primitive_type="UV_SPHERE",
            radius=1.05,
            location=[0, 0, 0],
            name="E2E_H2L_HighPoly"
        )
        match = re.search(r"named '([^']+)'", high_result)
        high_poly = match.group(1) if match else "E2E_H2L_HighPoly"

        output_path = get_temp_output_path("_normal_h2l.png")

        # Test
        result = baking_handler.bake_normal_map(
            object_name=low_poly,
            output_path=output_path,
            resolution=512,
            high_poly_source=high_poly,
            cage_extrusion=0.1
        )

        # Verify
        assert "normal map" in result.lower()
        assert "high-to-low" in result
        print(f"✓ bake_normal_map (high-to-low): {result}")

        # Cleanup
        if os.path.exists(output_path):
            os.remove(output_path)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_bake_normal_no_uv_error(baking_handler, modeling_handler, scene_handler):
    """Test that baking fails gracefully when object doesn't exist."""
    try:
        output_path = get_temp_output_path("_nouv.png")

        # Test - should raise error for non-existent object
        baking_handler.bake_normal_map(
            object_name="NonExistentObject_12345",
            output_path=output_path
        )
        assert False, "Expected error for non-existent object"
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        elif "not found" in error_msg:
            print("✓ bake_normal_map properly handles non-existent object")
        else:
            raise


# ==============================================================================
# TASK-031-2: bake_ao Tests
# ==============================================================================

def test_bake_ao_default(baking_handler, modeling_handler, scene_handler, uv_handler):
    """Test AO baking with default parameters."""
    try:
        # Setup
        obj_name = create_test_object_with_uv(modeling_handler, scene_handler, uv_handler, "E2E_AOBake1")
        output_path = get_temp_output_path("_ao.png")

        # Test
        result = baking_handler.bake_ao(
            object_name=obj_name,
            output_path=output_path,
            resolution=512,
            samples=32  # Low samples for faster test
        )

        # Verify
        assert "ao map" in result.lower()
        assert os.path.exists(output_path), f"Baked AO not found at {output_path}"
        print(f"✓ bake_ao: {result}")

        # Cleanup
        if os.path.exists(output_path):
            os.remove(output_path)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


# ==============================================================================
# TASK-031-3: bake_combined Tests
# ==============================================================================

def test_bake_combined_default(baking_handler, modeling_handler, scene_handler, uv_handler, material_handler):
    """Test combined baking with default parameters."""
    try:
        # Setup
        obj_name = create_test_object_with_uv(modeling_handler, scene_handler, uv_handler, "E2E_CombinedBake1")

        # Add a material for better combined bake
        material_handler.create_material(
            name="E2E_BakeMaterial",
            base_color=[0.8, 0.2, 0.2, 1.0]
        )
        material_handler.assign_material(
            object_name=obj_name,
            material_name="E2E_BakeMaterial"
        )

        output_path = get_temp_output_path("_combined.png")

        # Test
        result = baking_handler.bake_combined(
            object_name=obj_name,
            output_path=output_path,
            resolution=512,
            samples=32  # Low samples for faster test
        )

        # Verify
        assert "combined map" in result.lower()
        print(f"✓ bake_combined: {result}")

        # Cleanup
        if os.path.exists(output_path):
            os.remove(output_path)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


# ==============================================================================
# TASK-031-4: bake_diffuse Tests
# ==============================================================================

def test_bake_diffuse_default(baking_handler, modeling_handler, scene_handler, uv_handler, material_handler):
    """Test diffuse baking with default parameters."""
    try:
        # Setup
        obj_name = create_test_object_with_uv(modeling_handler, scene_handler, uv_handler, "E2E_DiffuseBake1")

        # Add a material
        material_handler.create_material(
            name="E2E_DiffuseMaterial",
            base_color=[0.2, 0.8, 0.2, 1.0]
        )
        material_handler.assign_material(
            object_name=obj_name,
            material_name="E2E_DiffuseMaterial"
        )

        output_path = get_temp_output_path("_diffuse.png")

        # Test
        result = baking_handler.bake_diffuse(
            object_name=obj_name,
            output_path=output_path,
            resolution=512
        )

        # Verify
        assert "diffuse map" in result.lower()
        print(f"✓ bake_diffuse: {result}")

        # Cleanup
        if os.path.exists(output_path):
            os.remove(output_path)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


# ==============================================================================
# Integration Workflow Tests
# ==============================================================================

def test_workflow_game_asset_baking(baking_handler, modeling_handler, scene_handler, uv_handler, material_handler):
    """
    Integration test: Complete game asset baking workflow.
    Create object → UV unwrap → material → bake normal + AO + diffuse.
    """
    try:
        # Setup: Create object with UV
        obj_name = create_test_object_with_uv(modeling_handler, scene_handler, uv_handler, "E2E_GameAsset")

        # Add material
        material_handler.create_material(
            name="E2E_GameMaterial",
            base_color=[0.6, 0.4, 0.2, 1.0],
            metallic=0.0,
            roughness=0.7
        )
        material_handler.assign_material(
            object_name=obj_name,
            material_name="E2E_GameMaterial"
        )

        # Bake normal map
        normal_path = get_temp_output_path("_game_normal.png")
        normal_result = baking_handler.bake_normal_map(
            object_name=obj_name,
            output_path=normal_path,
            resolution=512
        )
        assert "normal map" in normal_result.lower()
        print(f"  Step 1 - Normal: {normal_result}")

        # Bake AO
        ao_path = get_temp_output_path("_game_ao.png")
        ao_result = baking_handler.bake_ao(
            object_name=obj_name,
            output_path=ao_path,
            resolution=512,
            samples=32
        )
        assert "ao map" in ao_result.lower()
        print(f"  Step 2 - AO: {ao_result}")

        # Bake diffuse
        diffuse_path = get_temp_output_path("_game_diffuse.png")
        diffuse_result = baking_handler.bake_diffuse(
            object_name=obj_name,
            output_path=diffuse_path,
            resolution=512
        )
        assert "diffuse map" in diffuse_result.lower()
        print(f"  Step 3 - Diffuse: {diffuse_result}")

        print("✓ Game asset baking workflow completed successfully")

        # Cleanup
        for path in [normal_path, ao_path, diffuse_path]:
            if os.path.exists(path):
                os.remove(path)

    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise
