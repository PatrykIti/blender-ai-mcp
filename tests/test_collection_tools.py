"""
Tests for Collection Tools (TASK-014-6, 014-7)
"""
import pytest
from server.application.tool_handlers.collection_handler import CollectionToolHandler
from server.adapters.rpc.client import RpcClient
from server.infrastructure.config import get_config


@pytest.fixture
def collection_handler():
    """Provides a collection handler instance."""
    config = get_config()
    rpc_client = RpcClient(host=config.BLENDER_RPC_HOST, port=config.BLENDER_RPC_PORT)
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
        with pytest.raises(RuntimeError, match="not found"):
            collection_handler.list_objects(
                collection_name="NonExistentCollection12345",
                recursive=True,
                include_hidden=False
            )
        print("✓ collection_list_objects properly handles invalid collection name")
    except RuntimeError as e:
        if "not found" not in str(e).lower():
            pytest.skip(f"Blender not available: {e}")
