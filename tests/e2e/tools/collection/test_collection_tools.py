"""
Tests for Collection Tools (TASK-014-6, 014-7)
"""
import pytest
from server.application.tool_handlers.collection_handler import CollectionToolHandler


@pytest.fixture
def collection_handler(rpc_client):
    """Provides a collection handler instance using shared RPC client."""
    return CollectionToolHandler(rpc_client)


def test_collection_list(collection_handler):
    """Test listing collections."""
    try:
        result = collection_handler.list_collections(include_objects=False)
        assert isinstance(result, list)
        print(f"✓ collection_list returned {len(result)} collections")
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_collection_list_with_objects(collection_handler):
    """Test listing collections with objects."""
    try:
        result = collection_handler.list_collections(include_objects=True)
        assert isinstance(result, list)
        if result:
            # Check if objects key exists when include_objects=True
            first_col = result[0]
            assert "name" in first_col
            assert "object_count" in first_col
        print(f"✓ collection_list with objects: {len(result)} collections")
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_collection_list_objects(collection_handler):
    """Test listing objects in a collection."""
    try:
        # First get available collections
        collections = collection_handler.list_collections(include_objects=False)
        if not collections:
            pytest.skip("No collections available for testing")

        # Test with first available collection
        collection_name = collections[0]["name"]
        result = collection_handler.list_objects(
            collection_name=collection_name,
            recursive=True,
            include_hidden=False
        )

        assert isinstance(result, dict)
        assert "collection_name" in result
        assert "object_count" in result
        assert "objects" in result
        assert isinstance(result["objects"], list)

        print(f"✓ collection_list_objects: '{collection_name}' has {result['object_count']} objects")
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_collection_list_objects_invalid(collection_handler):
    """Test listing objects with invalid collection name."""
    try:
        collection_handler.list_objects(
            collection_name="NonExistentCollection12345",
            recursive=True,
            include_hidden=False
        )
        # If we get here without exception, test should fail
        assert False, "Expected RuntimeError for invalid collection name"
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        elif "not found" in error_msg:
            print("✓ collection_list_objects properly handles invalid collection name")
        else:
            raise  # Re-raise unexpected errors


# ============================================================================
# TASK-022: collection_manage Tests
# ============================================================================

def test_collection_manage_create(collection_handler):
    """Test creating a new collection."""
    try:
        # Create a unique collection name to avoid conflicts
        import time
        collection_name = f"TestCollection_{int(time.time())}"

        result = collection_handler.manage_collection(
            action="create",
            collection_name=collection_name
        )

        assert "Created collection" in result
        assert collection_name in result
        print(f"✓ collection_manage create: {result}")

        # Cleanup: delete the created collection
        collection_handler.manage_collection(
            action="delete",
            collection_name=collection_name
        )
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_collection_manage_create_with_parent(collection_handler):
    """Test creating a collection under a parent."""
    try:
        import time
        parent_name = f"ParentCollection_{int(time.time())}"
        child_name = f"ChildCollection_{int(time.time())}"

        # First create parent
        collection_handler.manage_collection(
            action="create",
            collection_name=parent_name
        )

        # Then create child under parent
        result = collection_handler.manage_collection(
            action="create",
            collection_name=child_name,
            parent_name=parent_name
        )

        assert "Created collection" in result
        assert child_name in result
        assert parent_name in result
        print(f"✓ collection_manage create with parent: {result}")

        # Cleanup
        collection_handler.manage_collection(action="delete", collection_name=child_name)
        collection_handler.manage_collection(action="delete", collection_name=parent_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_collection_manage_rename(collection_handler):
    """Test renaming a collection."""
    try:
        import time
        old_name = f"OldName_{int(time.time())}"
        new_name = f"NewName_{int(time.time())}"

        # Create collection
        collection_handler.manage_collection(
            action="create",
            collection_name=old_name
        )

        # Rename it
        result = collection_handler.manage_collection(
            action="rename",
            collection_name=old_name,
            new_name=new_name
        )

        assert "Renamed" in result
        print(f"✓ collection_manage rename: {result}")

        # Cleanup
        collection_handler.manage_collection(action="delete", collection_name=new_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_collection_manage_delete(collection_handler):
    """Test deleting a collection."""
    try:
        import time
        collection_name = f"ToDelete_{int(time.time())}"

        # Create collection
        collection_handler.manage_collection(
            action="create",
            collection_name=collection_name
        )

        # Delete it
        result = collection_handler.manage_collection(
            action="delete",
            collection_name=collection_name
        )

        assert "Deleted collection" in result
        assert collection_name in result
        print(f"✓ collection_manage delete: {result}")
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_collection_manage_invalid_action(collection_handler):
    """Test error handling for invalid action."""
    try:
        collection_handler.manage_collection(
            action="invalid_action",
            collection_name="SomeCollection"
        )
        assert False, "Expected RuntimeError for invalid action"
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        elif "unknown action" in error_msg:
            print("✓ collection_manage properly handles invalid action")
        else:
            raise


def test_collection_manage_create_already_exists(collection_handler):
    """Test error when creating collection that already exists."""
    try:
        import time
        collection_name = f"Duplicate_{int(time.time())}"

        # Create collection
        collection_handler.manage_collection(
            action="create",
            collection_name=collection_name
        )

        # Try to create again - should fail
        try:
            collection_handler.manage_collection(
                action="create",
                collection_name=collection_name
            )
            assert False, "Expected error for duplicate collection"
        except RuntimeError as e:
            if "already exists" in str(e).lower():
                print("✓ collection_manage properly handles duplicate collection name")
            else:
                raise

        # Cleanup
        collection_handler.manage_collection(action="delete", collection_name=collection_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise
