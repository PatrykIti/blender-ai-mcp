"""
Unit tests for collection_manage mega tool (TASK-022).

Tests the CollectionHandler.manage_collection method with all actions:
- create: Create new collection
- delete: Delete collection
- rename: Rename collection
- move_object: Move object to collection (exclusive)
- link_object: Link object to collection (additive)
- unlink_object: Unlink object from collection
"""
import sys
import pytest
from unittest.mock import MagicMock, PropertyMock

from blender_addon.application.handlers.collection import CollectionHandler


class TestCollectionManageCreate:
    """Tests for 'create' action."""

    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]
        self.handler = CollectionHandler()

        # Setup mock collections
        self.mock_collections = MagicMock()
        self.mock_bpy.data.collections = self.mock_collections
        self.mock_bpy.data.collections.get = MagicMock(return_value=None)

        # Setup scene collection
        self.mock_scene_collection = MagicMock()
        self.mock_bpy.context.scene.collection = self.mock_scene_collection

    def test_create_collection_at_root(self):
        """Test creating collection under Scene Collection."""
        new_col = MagicMock()
        new_col.name = "NewCollection"
        self.mock_collections.new.return_value = new_col

        result = self.handler.manage_collection(
            action="create",
            collection_name="NewCollection"
        )

        self.mock_collections.new.assert_called_with("NewCollection")
        self.mock_scene_collection.children.link.assert_called_with(new_col)
        assert "Created collection 'NewCollection'" in result
        assert "Scene Collection" in result

    def test_create_collection_under_parent(self):
        """Test creating collection under existing parent."""
        parent_col = MagicMock()
        parent_col.name = "ParentCollection"

        new_col = MagicMock()
        new_col.name = "ChildCollection"

        # get returns None for "ChildCollection" but parent for "ParentCollection"
        def get_collection(name):
            if name == "ParentCollection":
                return parent_col
            return None

        self.mock_collections.get = get_collection
        self.mock_collections.new.return_value = new_col

        result = self.handler.manage_collection(
            action="create",
            collection_name="ChildCollection",
            parent_name="ParentCollection"
        )

        self.mock_collections.new.assert_called_with("ChildCollection")
        parent_col.children.link.assert_called_with(new_col)
        assert "Created collection 'ChildCollection'" in result
        assert "ParentCollection" in result

    def test_create_collection_already_exists(self):
        """Test error when collection already exists."""
        existing_col = MagicMock()
        existing_col.name = "ExistingCollection"
        self.mock_collections.get.return_value = existing_col

        with pytest.raises(ValueError, match="already exists"):
            self.handler.manage_collection(
                action="create",
                collection_name="ExistingCollection"
            )

    def test_create_collection_parent_not_found(self):
        """Test error when parent collection doesn't exist."""
        self.mock_collections.new.return_value = MagicMock()

        with pytest.raises(ValueError, match="Parent collection .* not found"):
            self.handler.manage_collection(
                action="create",
                collection_name="NewCollection",
                parent_name="NonExistentParent"
            )


class TestCollectionManageDelete:
    """Tests for 'delete' action."""

    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]
        self.handler = CollectionHandler()

        # Setup mock collections
        self.mock_collections = MagicMock()
        self.mock_bpy.data.collections = self.mock_collections

        # Setup scene collection
        self.mock_scene_collection = MagicMock()
        self.mock_bpy.context.scene.collection = self.mock_scene_collection

    def test_delete_empty_collection(self):
        """Test deleting an empty collection."""
        col = MagicMock()
        col.name = "EmptyCollection"

        # col.objects should be a MagicMock that iterates like an empty list
        mock_objects = MagicMock()
        mock_objects.__iter__ = MagicMock(return_value=iter([]))
        col.objects = mock_objects
        self.mock_collections.get.return_value = col

        result = self.handler.manage_collection(
            action="delete",
            collection_name="EmptyCollection"
        )

        self.mock_collections.remove.assert_called_with(col)
        assert "Deleted collection 'EmptyCollection'" in result

    def test_delete_collection_with_objects(self):
        """Test deleting collection moves objects to scene root."""
        col = MagicMock()
        col.name = "CollectionWithObjects"

        obj1 = MagicMock()
        obj1.name = "Object1"
        obj1.users_collection = [col]

        obj2 = MagicMock()
        obj2.name = "Object2"
        obj2.users_collection = [col]

        # col.objects should be a MagicMock that iterates like a list
        mock_objects = MagicMock()
        mock_objects.__iter__ = MagicMock(return_value=iter([obj1, obj2]))
        col.objects = mock_objects
        self.mock_collections.get.return_value = col

        result = self.handler.manage_collection(
            action="delete",
            collection_name="CollectionWithObjects"
        )

        # Objects should be linked to scene collection
        assert self.mock_scene_collection.objects.link.call_count == 2
        self.mock_collections.remove.assert_called_with(col)
        assert "Moved 2 object(s)" in result
        assert "Object1" in result
        assert "Object2" in result

    def test_delete_collection_not_found(self):
        """Test error when collection doesn't exist."""
        self.mock_collections.get.return_value = None

        with pytest.raises(ValueError, match="not found"):
            self.handler.manage_collection(
                action="delete",
                collection_name="NonExistent"
            )


class TestCollectionManageRename:
    """Tests for 'rename' action."""

    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]
        self.handler = CollectionHandler()

        self.mock_collections = MagicMock()
        self.mock_bpy.data.collections = self.mock_collections

    def test_rename_collection(self):
        """Test renaming a collection."""
        col = MagicMock()
        col.name = "OldName"

        def get_collection(name):
            if name == "OldName":
                return col
            return None

        self.mock_collections.get = get_collection

        result = self.handler.manage_collection(
            action="rename",
            collection_name="OldName",
            new_name="NewName"
        )

        assert col.name == "NewName"
        assert "Renamed" in result

    def test_rename_collection_not_found(self):
        """Test error when collection doesn't exist."""
        self.mock_collections.get.return_value = None

        with pytest.raises(ValueError, match="not found"):
            self.handler.manage_collection(
                action="rename",
                collection_name="NonExistent",
                new_name="NewName"
            )

    def test_rename_collection_new_name_exists(self):
        """Test error when new name already exists."""
        old_col = MagicMock()
        old_col.name = "OldName"
        existing_col = MagicMock()
        existing_col.name = "ExistingName"

        def get_collection(name):
            if name == "OldName":
                return old_col
            if name == "ExistingName":
                return existing_col
            return None

        self.mock_collections.get = get_collection

        with pytest.raises(ValueError, match="already exists"):
            self.handler.manage_collection(
                action="rename",
                collection_name="OldName",
                new_name="ExistingName"
            )

    def test_rename_collection_missing_new_name(self):
        """Test error when new_name is not provided."""
        col = MagicMock()
        col.name = "OldName"
        self.mock_collections.get.return_value = col

        with pytest.raises(ValueError, match="new_name is required"):
            self.handler.manage_collection(
                action="rename",
                collection_name="OldName"
            )


class TestCollectionManageMoveObject:
    """Tests for 'move_object' action."""

    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]
        self.handler = CollectionHandler()

        self.mock_collections = MagicMock()
        self.mock_bpy.data.collections = self.mock_collections

        self.mock_objects = MagicMock()
        self.mock_bpy.data.objects = self.mock_objects

    def test_move_object_to_collection(self):
        """Test moving object to a new collection."""
        old_col = MagicMock()
        old_col.name = "OldCollection"

        new_col = MagicMock()
        new_col.name = "NewCollection"

        obj = MagicMock()
        obj.name = "TestObject"
        obj.users_collection = [old_col]

        self.mock_objects.get.return_value = obj
        self.mock_collections.get.return_value = new_col

        result = self.handler.manage_collection(
            action="move_object",
            collection_name="NewCollection",
            object_name="TestObject"
        )

        old_col.objects.unlink.assert_called_with(obj)
        new_col.objects.link.assert_called_with(obj)
        assert "Moved 'TestObject'" in result
        assert "NewCollection" in result

    def test_move_object_not_found(self):
        """Test error when object doesn't exist."""
        self.mock_objects.get.return_value = None

        with pytest.raises(ValueError, match="Object .* not found"):
            self.handler.manage_collection(
                action="move_object",
                collection_name="SomeCollection",
                object_name="NonExistent"
            )

    def test_move_object_collection_not_found(self):
        """Test error when target collection doesn't exist."""
        obj = MagicMock()
        obj.name = "TestObject"
        self.mock_objects.get.return_value = obj
        self.mock_collections.get.return_value = None

        with pytest.raises(ValueError, match="Collection .* not found"):
            self.handler.manage_collection(
                action="move_object",
                collection_name="NonExistent",
                object_name="TestObject"
            )

    def test_move_object_missing_object_name(self):
        """Test error when object_name is not provided."""
        with pytest.raises(ValueError, match="object_name is required"):
            self.handler.manage_collection(
                action="move_object",
                collection_name="SomeCollection"
            )


class TestCollectionManageLinkObject:
    """Tests for 'link_object' action."""

    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]
        self.handler = CollectionHandler()

        self.mock_collections = MagicMock()
        self.mock_bpy.data.collections = self.mock_collections

        self.mock_objects = MagicMock()
        self.mock_bpy.data.objects = self.mock_objects

    def test_link_object_to_collection(self):
        """Test linking object to additional collection."""
        col = MagicMock()
        col.name = "TargetCollection"

        obj = MagicMock()
        obj.name = "TestObject"

        # col.objects should be a MagicMock that iterates like an empty list
        mock_objects = MagicMock()
        mock_objects.__iter__ = MagicMock(return_value=iter([]))
        col.objects = mock_objects

        self.mock_objects.get.return_value = obj
        self.mock_collections.get.return_value = col

        result = self.handler.manage_collection(
            action="link_object",
            collection_name="TargetCollection",
            object_name="TestObject"
        )

        col.objects.link.assert_called_with(obj)
        assert "Linked 'TestObject'" in result

    def test_link_object_already_linked(self):
        """Test that linking already linked object returns message."""
        obj = MagicMock()
        obj.name = "TestObject"

        col = MagicMock()
        col.name = "TargetCollection"

        # col.objects should be a MagicMock that iterates like a list containing obj
        mock_objects = MagicMock()
        mock_objects.__iter__ = MagicMock(return_value=iter([obj]))
        col.objects = mock_objects

        self.mock_objects.get.return_value = obj
        self.mock_collections.get.return_value = col

        result = self.handler.manage_collection(
            action="link_object",
            collection_name="TargetCollection",
            object_name="TestObject"
        )

        col.objects.link.assert_not_called()
        assert "already linked" in result


class TestCollectionManageUnlinkObject:
    """Tests for 'unlink_object' action."""

    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]
        self.handler = CollectionHandler()

        self.mock_collections = MagicMock()
        self.mock_bpy.data.collections = self.mock_collections

        self.mock_objects = MagicMock()
        self.mock_bpy.data.objects = self.mock_objects

    def test_unlink_object_from_collection(self):
        """Test unlinking object from collection."""
        col1 = MagicMock()
        col1.name = "Collection1"

        col2 = MagicMock()
        col2.name = "Collection2"

        obj = MagicMock()
        obj.name = "TestObject"
        obj.users_collection = [col1, col2]

        # col1.objects should be a MagicMock that iterates like a list containing obj
        mock_objects = MagicMock()
        mock_objects.__iter__ = MagicMock(return_value=iter([obj]))
        col1.objects = mock_objects

        self.mock_objects.get.return_value = obj
        self.mock_collections.get.return_value = col1

        result = self.handler.manage_collection(
            action="unlink_object",
            collection_name="Collection1",
            object_name="TestObject"
        )

        col1.objects.unlink.assert_called_with(obj)
        assert "Unlinked 'TestObject'" in result

    def test_unlink_object_only_collection(self):
        """Test error when unlinking from only collection."""
        col = MagicMock()
        col.name = "OnlyCollection"

        obj = MagicMock()
        obj.name = "TestObject"
        obj.users_collection = [col]

        # col.objects should be a MagicMock that iterates like a list containing obj
        mock_objects = MagicMock()
        mock_objects.__iter__ = MagicMock(return_value=iter([obj]))
        col.objects = mock_objects

        self.mock_objects.get.return_value = obj
        self.mock_collections.get.return_value = col

        with pytest.raises(ValueError, match="only collection"):
            self.handler.manage_collection(
                action="unlink_object",
                collection_name="OnlyCollection",
                object_name="TestObject"
            )

    def test_unlink_object_not_in_collection(self):
        """Test message when object is not in collection."""
        col = MagicMock()
        col.name = "Collection1"

        obj = MagicMock()
        obj.name = "TestObject"

        # col.objects should be a MagicMock that iterates like an empty list
        mock_objects = MagicMock()
        mock_objects.__iter__ = MagicMock(return_value=iter([]))
        col.objects = mock_objects

        self.mock_objects.get.return_value = obj
        self.mock_collections.get.return_value = col

        result = self.handler.manage_collection(
            action="unlink_object",
            collection_name="Collection1",
            object_name="TestObject"
        )

        col.objects.unlink.assert_not_called()
        assert "not in collection" in result


class TestCollectionManageInvalidAction:
    """Tests for invalid action handling."""

    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]
        self.handler = CollectionHandler()

    def test_invalid_action(self):
        """Test error for invalid action."""
        with pytest.raises(ValueError, match="Unknown action"):
            self.handler.manage_collection(
                action="invalid_action",
                collection_name="SomeCollection"
            )
