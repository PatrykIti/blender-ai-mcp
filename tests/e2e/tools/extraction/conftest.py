"""
Shared fixtures for extraction E2E tests.

These fixtures create test objects before tests run, ensuring
tests don't fail because expected objects don't exist in the scene.
"""
import pytest
from server.application.tool_handlers.extraction_handler import ExtractionToolHandler
from server.application.tool_handlers.modeling_handler import ModelingToolHandler
from server.application.tool_handlers.scene_handler import SceneToolHandler


@pytest.fixture
def extraction_handler(rpc_client):
    """Provides an extraction handler instance using shared RPC client."""
    return ExtractionToolHandler(rpc_client)


@pytest.fixture
def modeling_handler(rpc_client):
    """Provides a modeling handler instance using shared RPC client."""
    return ModelingToolHandler(rpc_client)


@pytest.fixture
def scene_handler(rpc_client):
    """Provides a scene handler instance using shared RPC client."""
    return SceneToolHandler(rpc_client)


@pytest.fixture
def test_cube(modeling_handler, scene_handler):
    """Creates a test cube for extraction tests.

    Creates a cube named "E2E_ExtractionCube" before the test,
    and cleans it up after the test completes.

    Returns:
        str: Name of the created test cube
    """
    name = "E2E_ExtractionCube"

    # Cleanup any existing object with this name
    try:
        scene_handler.delete_object(name)
    except RuntimeError:
        pass  # Object didn't exist, that's fine

    # Create the test cube
    modeling_handler.create_primitive(
        primitive_type="CUBE",
        size=2.0,
        location=[0, 0, 0],
        name=name
    )

    yield name

    # Cleanup after test
    try:
        scene_handler.delete_object(name)
    except RuntimeError:
        pass  # Cleanup failed, but test is done


@pytest.fixture
def test_cube_with_components(modeling_handler, scene_handler):
    """Creates a cube with multiple loose components for component_separate tests.

    Creates two cubes at different positions, joins them, then
    tests can verify they get separated.

    Returns:
        str: Name of the test object with multiple components
    """
    name = "E2E_MultiComponentObject"
    cube1_name = "E2E_TempCube1"
    cube2_name = "E2E_TempCube2"

    # Cleanup any existing objects
    for obj_name in [name, cube1_name, cube2_name]:
        try:
            scene_handler.delete_object(obj_name)
        except RuntimeError:
            pass

    # Create two cubes at different positions
    modeling_handler.create_primitive(
        primitive_type="CUBE",
        size=1.0,
        location=[0, 0, 0],
        name=cube1_name
    )
    modeling_handler.create_primitive(
        primitive_type="CUBE",
        size=1.0,
        location=[5, 0, 0],  # Far apart so they don't merge
        name=cube2_name
    )

    # Join them into one object
    try:
        modeling_handler.join_objects([cube1_name, cube2_name])
    except RuntimeError:
        # If join fails, just use cube1
        pass

    # Rename to final name
    try:
        scene_handler.rename_object(cube1_name, name)
    except RuntimeError:
        # Try with cube2 name if rename failed
        try:
            scene_handler.rename_object(cube2_name, name)
        except RuntimeError:
            name = cube1_name  # Use whatever name we ended up with

    yield name

    # Cleanup - also clean up any components that were created
    for obj_name in [name, cube1_name, cube2_name, f"{name}.001", f"{name}.002"]:
        try:
            scene_handler.delete_object(obj_name)
        except RuntimeError:
            pass
