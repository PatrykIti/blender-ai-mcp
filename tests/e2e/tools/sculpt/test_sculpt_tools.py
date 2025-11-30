"""
E2E Tests for TASK-027 (Sculpting Tools).

These tests require a running Blender instance with the addon loaded.
They connect via RPC to execute real Blender operations.

To run:
    1. Start Blender with the addon enabled
    2. Run: pytest tests/e2e/tools/sculpt/ -v
"""
import pytest
from server.application.tool_handlers.sculpt_handler import SculptToolHandler
from server.application.tool_handlers.modeling_handler import ModelingToolHandler
from server.application.tool_handlers.scene_handler import SceneToolHandler


@pytest.fixture
def sculpt_handler(rpc_client):
    """Provides a Sculpt handler instance using shared RPC client."""
    return SculptToolHandler(rpc_client)


@pytest.fixture
def modeling_handler(rpc_client):
    """Provides a modeling handler instance using shared RPC client."""
    return ModelingToolHandler(rpc_client)


@pytest.fixture
def scene_handler(rpc_client):
    """Provides a scene handler instance using shared RPC client."""
    return SceneToolHandler(rpc_client)


def create_test_sphere(modeling_handler, scene_handler, name="E2E_SculptTest"):
    """Creates a test sphere for sculpting operations."""
    try:
        scene_handler.delete_object(name)
    except RuntimeError:
        pass
    modeling_handler.create_primitive(
        primitive_type="SPHERE",
        radius=1.0,
        location=[0, 0, 0],
        name=name
    )
    return name


def cleanup_test_object(scene_handler, name):
    """Cleanup test object."""
    try:
        scene_handler.delete_object(name)
    except RuntimeError:
        pass


# =============================================================================
# TASK-027-1: sculpt_auto tests
# =============================================================================

class TestSculptAutoE2E:
    """E2E tests for sculpt_auto tool."""

    def test_sculpt_auto_smooth_basic(self, sculpt_handler, modeling_handler, scene_handler):
        """Test basic smooth operation on a mesh object."""
        obj_name = "E2E_SculptSmooth"
        try:
            create_test_sphere(modeling_handler, scene_handler, obj_name)
            result = sculpt_handler.auto_sculpt(
                object_name=obj_name,
                operation="smooth",
                strength=0.3,
                iterations=1
            )

            assert isinstance(result, str)
            assert "smooth" in result.lower()
            print(f"[PASSED] sculpt_auto smooth: {result}")

        except RuntimeError as e:
            error_msg = str(e).lower()
            if "could not connect" in error_msg or "unknown command" in error_msg:
                pytest.skip(f"Blender not available: {e}")
            raise
        finally:
            cleanup_test_object(scene_handler, obj_name)

    def test_sculpt_auto_inflate(self, sculpt_handler, modeling_handler, scene_handler):
        """Test inflate operation."""
        obj_name = "E2E_SculptInflate"
        try:
            create_test_sphere(modeling_handler, scene_handler, obj_name)
            result = sculpt_handler.auto_sculpt(
                object_name=obj_name,
                operation="inflate",
                strength=0.2,
                iterations=1
            )

            assert isinstance(result, str)
            assert "inflate" in result.lower()
            print(f"[PASSED] sculpt_auto inflate: {result}")

        except RuntimeError as e:
            error_msg = str(e).lower()
            if "could not connect" in error_msg or "unknown command" in error_msg:
                pytest.skip(f"Blender not available: {e}")
            raise
        finally:
            cleanup_test_object(scene_handler, obj_name)

    def test_sculpt_auto_flatten(self, sculpt_handler, modeling_handler, scene_handler):
        """Test flatten operation."""
        obj_name = "E2E_SculptFlatten"
        try:
            create_test_sphere(modeling_handler, scene_handler, obj_name)
            result = sculpt_handler.auto_sculpt(
                object_name=obj_name,
                operation="flatten",
                strength=0.4,
                iterations=2
            )

            assert isinstance(result, str)
            assert "flatten" in result.lower()
            print(f"[PASSED] sculpt_auto flatten: {result}")

        except RuntimeError as e:
            error_msg = str(e).lower()
            if "could not connect" in error_msg or "unknown command" in error_msg:
                pytest.skip(f"Blender not available: {e}")
            raise
        finally:
            cleanup_test_object(scene_handler, obj_name)

    def test_sculpt_auto_sharpen(self, sculpt_handler, modeling_handler, scene_handler):
        """Test sharpen operation."""
        obj_name = "E2E_SculptSharpen"
        try:
            create_test_sphere(modeling_handler, scene_handler, obj_name)
            result = sculpt_handler.auto_sculpt(
                object_name=obj_name,
                operation="sharpen",
                strength=0.5,
                iterations=1
            )

            assert isinstance(result, str)
            assert "sharpen" in result.lower()
            print(f"[PASSED] sculpt_auto sharpen: {result}")

        except RuntimeError as e:
            error_msg = str(e).lower()
            if "could not connect" in error_msg or "unknown command" in error_msg:
                pytest.skip(f"Blender not available: {e}")
            raise
        finally:
            cleanup_test_object(scene_handler, obj_name)

    def test_sculpt_auto_with_symmetry(self, sculpt_handler, modeling_handler, scene_handler):
        """Test smooth operation with X symmetry enabled."""
        obj_name = "E2E_SculptSymmetry"
        try:
            create_test_sphere(modeling_handler, scene_handler, obj_name)
            result = sculpt_handler.auto_sculpt(
                object_name=obj_name,
                operation="smooth",
                strength=0.3,
                iterations=1,
                use_symmetry=True,
                symmetry_axis="X"
            )

            assert isinstance(result, str)
            assert "symmetry" in result.lower()
            print(f"[PASSED] sculpt_auto with symmetry: {result}")

        except RuntimeError as e:
            error_msg = str(e).lower()
            if "could not connect" in error_msg or "unknown command" in error_msg:
                pytest.skip(f"Blender not available: {e}")
            raise
        finally:
            cleanup_test_object(scene_handler, obj_name)

    def test_sculpt_auto_multiple_iterations(self, sculpt_handler, modeling_handler, scene_handler):
        """Test smooth operation with multiple iterations."""
        obj_name = "E2E_SculptIterations"
        try:
            create_test_sphere(modeling_handler, scene_handler, obj_name)
            result = sculpt_handler.auto_sculpt(
                object_name=obj_name,
                operation="smooth",
                strength=0.3,
                iterations=3
            )

            assert isinstance(result, str)
            assert "3 iterations" in result
            print(f"[PASSED] sculpt_auto multiple iterations: {result}")

        except RuntimeError as e:
            error_msg = str(e).lower()
            if "could not connect" in error_msg or "unknown command" in error_msg:
                pytest.skip(f"Blender not available: {e}")
            raise
        finally:
            cleanup_test_object(scene_handler, obj_name)


# =============================================================================
# TASK-027-2: sculpt_brush_smooth tests
# =============================================================================

class TestSculptBrushSmoothE2E:
    """E2E tests for sculpt_brush_smooth tool."""

    def test_brush_smooth_setup(self, sculpt_handler, modeling_handler, scene_handler):
        """Test smooth brush setup."""
        obj_name = "E2E_BrushSmooth"
        try:
            create_test_sphere(modeling_handler, scene_handler, obj_name)
            result = sculpt_handler.brush_smooth(
                object_name=obj_name,
                radius=0.1,
                strength=0.5
            )

            assert isinstance(result, str)
            assert "smooth brush ready" in result.lower()
            print(f"[PASSED] sculpt_brush_smooth: {result}")

        except RuntimeError as e:
            error_msg = str(e).lower()
            if "could not connect" in error_msg or "unknown command" in error_msg:
                pytest.skip(f"Blender not available: {e}")
            raise
        finally:
            cleanup_test_object(scene_handler, obj_name)

    def test_brush_smooth_with_location(self, sculpt_handler, modeling_handler, scene_handler):
        """Test smooth brush with location."""
        obj_name = "E2E_BrushSmoothLoc"
        try:
            create_test_sphere(modeling_handler, scene_handler, obj_name)
            result = sculpt_handler.brush_smooth(
                object_name=obj_name,
                location=[0.0, 0.0, 1.0],
                radius=0.15,
                strength=0.6
            )

            assert isinstance(result, str)
            assert "smooth brush ready" in result.lower()
            print(f"[PASSED] sculpt_brush_smooth with location: {result}")

        except RuntimeError as e:
            error_msg = str(e).lower()
            if "could not connect" in error_msg or "unknown command" in error_msg:
                pytest.skip(f"Blender not available: {e}")
            raise
        finally:
            cleanup_test_object(scene_handler, obj_name)


# =============================================================================
# TASK-027-3: sculpt_brush_grab tests
# =============================================================================

class TestSculptBrushGrabE2E:
    """E2E tests for sculpt_brush_grab tool."""

    def test_brush_grab_setup(self, sculpt_handler, modeling_handler, scene_handler):
        """Test grab brush setup."""
        obj_name = "E2E_BrushGrab"
        try:
            create_test_sphere(modeling_handler, scene_handler, obj_name)
            result = sculpt_handler.brush_grab(
                object_name=obj_name,
                radius=0.2,
                strength=0.7
            )

            assert isinstance(result, str)
            assert "grab brush ready" in result.lower()
            print(f"[PASSED] sculpt_brush_grab: {result}")

        except RuntimeError as e:
            error_msg = str(e).lower()
            if "could not connect" in error_msg or "unknown command" in error_msg:
                pytest.skip(f"Blender not available: {e}")
            raise
        finally:
            cleanup_test_object(scene_handler, obj_name)

    def test_brush_grab_with_locations(self, sculpt_handler, modeling_handler, scene_handler):
        """Test grab brush with from/to locations."""
        obj_name = "E2E_BrushGrabLoc"
        try:
            create_test_sphere(modeling_handler, scene_handler, obj_name)
            result = sculpt_handler.brush_grab(
                object_name=obj_name,
                from_location=[0.0, 0.0, 0.0],
                to_location=[0.0, 0.0, 0.5],
                radius=0.15,
                strength=0.5
            )

            assert isinstance(result, str)
            assert "grab brush ready" in result.lower()
            print(f"[PASSED] sculpt_brush_grab with locations: {result}")

        except RuntimeError as e:
            error_msg = str(e).lower()
            if "could not connect" in error_msg or "unknown command" in error_msg:
                pytest.skip(f"Blender not available: {e}")
            raise
        finally:
            cleanup_test_object(scene_handler, obj_name)


# =============================================================================
# TASK-027-4: sculpt_brush_crease tests
# =============================================================================

class TestSculptBrushCreaseE2E:
    """E2E tests for sculpt_brush_crease tool."""

    def test_brush_crease_setup(self, sculpt_handler, modeling_handler, scene_handler):
        """Test crease brush setup."""
        obj_name = "E2E_BrushCrease"
        try:
            create_test_sphere(modeling_handler, scene_handler, obj_name)
            result = sculpt_handler.brush_crease(
                object_name=obj_name,
                radius=0.05,
                strength=0.8,
                pinch=0.7
            )

            assert isinstance(result, str)
            assert "crease brush ready" in result.lower()
            print(f"[PASSED] sculpt_brush_crease: {result}")

        except RuntimeError as e:
            error_msg = str(e).lower()
            if "could not connect" in error_msg or "unknown command" in error_msg:
                pytest.skip(f"Blender not available: {e}")
            raise
        finally:
            cleanup_test_object(scene_handler, obj_name)

    def test_brush_crease_with_location(self, sculpt_handler, modeling_handler, scene_handler):
        """Test crease brush with location."""
        obj_name = "E2E_BrushCreaseLoc"
        try:
            create_test_sphere(modeling_handler, scene_handler, obj_name)
            result = sculpt_handler.brush_crease(
                object_name=obj_name,
                location=[0.5, 0.5, 1.0],
                radius=0.08,
                strength=0.9,
                pinch=0.5
            )

            assert isinstance(result, str)
            assert "crease brush ready" in result.lower()
            print(f"[PASSED] sculpt_brush_crease with location: {result}")

        except RuntimeError as e:
            error_msg = str(e).lower()
            if "could not connect" in error_msg or "unknown command" in error_msg:
                pytest.skip(f"Blender not available: {e}")
            raise
        finally:
            cleanup_test_object(scene_handler, obj_name)


# =============================================================================
# Error handling tests
# =============================================================================

class TestSculptErrorHandlingE2E:
    """E2E tests for sculpt tool error handling."""

    def test_sculpt_auto_invalid_object(self, sculpt_handler):
        """Test error handling for non-existent object."""
        try:
            with pytest.raises(RuntimeError) as exc_info:
                sculpt_handler.auto_sculpt(object_name="NonExistentObject12345")

            error_msg = str(exc_info.value).lower()
            if "not found" in error_msg:
                print("[PASSED] sculpt_auto properly handles invalid object")
            elif "could not connect" in error_msg or "unknown command" in error_msg:
                pytest.skip(f"Blender not available: {exc_info.value}")

        except RuntimeError as e:
            error_msg = str(e).lower()
            if "not found" in error_msg:
                print("[PASSED] sculpt_auto properly handles invalid object")
            elif "could not connect" in error_msg or "unknown command" in error_msg:
                pytest.skip(f"Blender not available: {e}")
            else:
                raise
