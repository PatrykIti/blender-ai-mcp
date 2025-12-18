"""
E2E Tests for Text & Annotations Tools (TASK-034)

Tests the complete workflow:
1. Create text object with various properties
2. Edit text content and parameters
3. Convert text to mesh for export
4. Complete workflow: Create text → extrude → convert to mesh
"""
import pytest
import time
from server.application.tool_handlers.text_handler import TextToolHandler
from server.application.tool_handlers.scene_handler import SceneToolHandler


@pytest.fixture
def text_handler(rpc_client):
    """Provides a text handler instance using shared RPC client."""
    return TextToolHandler(rpc_client)


@pytest.fixture
def scene_handler(rpc_client):
    """Provides a scene handler instance using shared RPC client."""
    return SceneToolHandler(rpc_client)


# ============================================================================
# TASK-034-1: text_create Tests
# ============================================================================


def test_text_create_default(text_handler, scene_handler):
    """Test creating text with default parameters."""
    try:
        text_name = f"TestText_{int(time.time())}"

        result = text_handler.create(
            text="Hello World",
            name=text_name,
        )

        assert "Created text object" in result
        assert text_name in result
        print(f"✓ text_create default: {result}")

        # Cleanup
        scene_handler.delete_object(text_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_text_create_with_location(text_handler, scene_handler):
    """Test creating text at specific location."""
    try:
        text_name = f"LocatedText_{int(time.time())}"

        result = text_handler.create(
            text="Located",
            name=text_name,
            location=[2, 3, 1],
        )

        assert "Created text object" in result
        assert "[2, 3, 1]" in result or "location" in result.lower()
        print(f"✓ text_create with location: {result}")

        # Cleanup
        scene_handler.delete_object(text_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_text_create_with_extrude(text_handler, scene_handler):
    """Test creating 3D extruded text."""
    try:
        text_name = f"ExtrudedText_{int(time.time())}"

        result = text_handler.create(
            text="3D Text",
            name=text_name,
            extrude=0.5,
        )

        assert "Created text object" in result
        assert "extrude=0.5" in result
        print(f"✓ text_create with extrude: {result}")

        # Cleanup
        scene_handler.delete_object(text_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_text_create_with_bevel(text_handler, scene_handler):
    """Test creating text with bevel."""
    try:
        text_name = f"BeveledText_{int(time.time())}"

        result = text_handler.create(
            text="Beveled",
            name=text_name,
            extrude=0.3,
            bevel_depth=0.02,
            bevel_resolution=4,
        )

        assert "Created text object" in result
        assert "bevel_depth=0.02" in result
        print(f"✓ text_create with bevel: {result}")

        # Cleanup
        scene_handler.delete_object(text_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_text_create_with_alignment(text_handler, scene_handler):
    """Test creating text with custom alignment."""
    try:
        text_name = f"CenteredText_{int(time.time())}"

        result = text_handler.create(
            text="Centered",
            name=text_name,
            align_x="CENTER",
            align_y="CENTER",
        )

        assert "Created text object" in result
        print(f"✓ text_create with alignment: {result}")

        # Cleanup
        scene_handler.delete_object(text_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_text_create_with_size(text_handler, scene_handler):
    """Test creating text with custom size."""
    try:
        text_name = f"LargeText_{int(time.time())}"

        result = text_handler.create(
            text="Large",
            name=text_name,
            size=2.5,
        )

        assert "Created text object" in result
        print(f"✓ text_create with size: {result}")

        # Cleanup
        scene_handler.delete_object(text_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_text_create_invalid_align_x(text_handler):
    """Test error handling for invalid align_x."""
    try:
        text_handler.create(
            text="Test",
            align_x="INVALID",
        )
        assert False, "Expected RuntimeError for invalid align_x"
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        elif "invalid align_x" in error_msg:
            print("✓ text_create properly handles invalid align_x")
        else:
            raise


def test_text_create_invalid_align_y(text_handler):
    """Test error handling for invalid align_y."""
    try:
        text_handler.create(
            text="Test",
            align_y="INVALID",
        )
        assert False, "Expected RuntimeError for invalid align_y"
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        elif "invalid align_y" in error_msg:
            print("✓ text_create properly handles invalid align_y")
        else:
            raise


# ============================================================================
# TASK-034-2: text_edit Tests
# ============================================================================


def test_text_edit_content(text_handler, scene_handler):
    """Test editing text content."""
    try:
        text_name = f"EditableText_{int(time.time())}"

        # Create text
        text_handler.create(text="Original", name=text_name)

        # Edit content
        result = text_handler.edit(
            object_name=text_name,
            text="Modified Content",
        )

        assert "Modified text object" in result
        assert 'text="Modified Content"' in result
        print(f"✓ text_edit content: {result}")

        # Cleanup
        scene_handler.delete_object(text_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_text_edit_size(text_handler, scene_handler):
    """Test editing text size."""
    try:
        text_name = f"ResizableText_{int(time.time())}"

        # Create text
        text_handler.create(text="Resize Me", name=text_name)

        # Edit size
        result = text_handler.edit(
            object_name=text_name,
            size=3.0,
        )

        assert "Modified text object" in result
        assert "size=3.0" in result
        print(f"✓ text_edit size: {result}")

        # Cleanup
        scene_handler.delete_object(text_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_text_edit_extrude(text_handler, scene_handler):
    """Test editing text extrusion."""
    try:
        text_name = f"ExtrudeText_{int(time.time())}"

        # Create flat text
        text_handler.create(text="Flat", name=text_name)

        # Add extrusion
        result = text_handler.edit(
            object_name=text_name,
            extrude=0.4,
        )

        assert "Modified text object" in result
        assert "extrude=0.4" in result
        print(f"✓ text_edit extrude: {result}")

        # Cleanup
        scene_handler.delete_object(text_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_text_edit_multiple_properties(text_handler, scene_handler):
    """Test editing multiple text properties at once."""
    try:
        text_name = f"MultiEditText_{int(time.time())}"

        # Create text
        text_handler.create(text="Original", name=text_name)

        # Edit multiple properties
        result = text_handler.edit(
            object_name=text_name,
            text="Updated",
            size=1.5,
            extrude=0.2,
            align_x="CENTER",
        )

        assert "Modified text object" in result
        print(f"✓ text_edit multiple: {result}")

        # Cleanup
        scene_handler.delete_object(text_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_text_edit_no_changes(text_handler, scene_handler):
    """Test editing text with no parameters returns appropriate message."""
    try:
        text_name = f"NoChangeText_{int(time.time())}"

        # Create text
        text_handler.create(text="Static", name=text_name)

        # Edit with no changes
        result = text_handler.edit(object_name=text_name)

        assert "unchanged" in result.lower()
        print(f"✓ text_edit no changes: {result}")

        # Cleanup
        scene_handler.delete_object(text_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_text_edit_not_found(text_handler):
    """Test error handling for non-existent object."""
    try:
        text_handler.edit(
            object_name="NonExistentText12345",
            text="Should Fail",
        )
        assert False, "Expected RuntimeError for non-existent object"
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        elif "not found" in error_msg:
            print("✓ text_edit properly handles non-existent object")
        else:
            raise


# ============================================================================
# TASK-034-3: text_to_mesh Tests
# ============================================================================


def test_text_to_mesh_basic(text_handler, scene_handler):
    """Test converting text to mesh."""
    try:
        text_name = f"MeshText_{int(time.time())}"

        # Create text
        text_handler.create(text="Convert Me", name=text_name)

        # Convert to mesh
        result = text_handler.to_mesh(object_name=text_name)

        assert "Converted text" in result
        assert "to mesh" in result
        print(f"✓ text_to_mesh basic: {result}")

        # Cleanup - object is now a mesh but still same name
        scene_handler.delete_object(text_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_text_to_mesh_keep_original(text_handler, scene_handler):
    """Test converting text to mesh while keeping original."""
    try:
        text_name = f"KeepOriginal_{int(time.time())}"

        # Create text
        text_handler.create(text="Keep Me", name=text_name)

        # Convert to mesh, keeping original
        result = text_handler.to_mesh(
            object_name=text_name,
            keep_original=True,
        )

        assert "Converted text" in result
        assert "original preserved" in result
        print(f"✓ text_to_mesh keep_original: {result}")

        # Cleanup - both original and converted
        scene_handler.delete_object(text_name)
        # The copy might have a different name like "Text.001" or "KeepOriginal_xxx_mesh"
        # We'll try to clean up common patterns
        try:
            scene_handler.delete_object(f"{text_name}.001")
        except:
            pass
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_text_to_mesh_not_found(text_handler):
    """Test error handling for non-existent object."""
    try:
        text_handler.to_mesh(object_name="NonExistentText12345")
        assert False, "Expected RuntimeError for non-existent object"
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        elif "not found" in error_msg:
            print("✓ text_to_mesh properly handles non-existent object")
        else:
            raise


# ============================================================================
# Complete Workflow Tests
# ============================================================================


def test_complete_3d_text_workflow(text_handler, scene_handler):
    """Test the complete 3D text workflow: create → extrude → bevel → convert."""
    try:
        text_name = f"Logo3D_{int(time.time())}"

        # 1. Create text
        result1 = text_handler.create(
            text="LOGO",
            name=text_name,
            size=2.0,
            align_x="CENTER",
        )
        assert "Created text object" in result1
        print(f"  Step 1: Created text '{text_name}'")

        # 2. Add extrusion and bevel
        result2 = text_handler.edit(
            object_name=text_name,
            extrude=0.3,
            bevel_depth=0.02,
            bevel_resolution=2,
        )
        assert "Modified text object" in result2
        print(f"  Step 2: Added extrusion and bevel")

        # 3. Convert to mesh for export
        result3 = text_handler.to_mesh(object_name=text_name)
        assert "Converted text" in result3
        print(f"  Step 3: Converted to mesh")

        print("✓ Complete 3D text workflow successful")

        # Cleanup
        scene_handler.delete_object(text_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_signage_workflow(text_handler, scene_handler):
    """Test creating signage: text with specific alignment and extrusion."""
    try:
        sign_name = f"ExitSign_{int(time.time())}"

        # Create exit sign text
        result = text_handler.create(
            text="EXIT",
            name=sign_name,
            size=1.5,
            extrude=0.1,
            align_x="CENTER",
            align_y="CENTER",
        )

        assert "Created text object" in result
        print(f"✓ Signage workflow: Created centered EXIT sign")

        # Cleanup
        scene_handler.delete_object(sign_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_multiline_text(text_handler, scene_handler):
    """Test creating multiline text."""
    try:
        text_name = f"MultilineText_{int(time.time())}"

        # Create multiline text
        result = text_handler.create(
            text="Line One\nLine Two\nLine Three",
            name=text_name,
        )

        assert "Created text object" in result
        print(f"✓ Multiline text: {result}")

        # Cleanup
        scene_handler.delete_object(text_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise
