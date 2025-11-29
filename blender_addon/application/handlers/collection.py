import bpy
from typing import Optional


class CollectionHandler:
    """Application service for collection operations."""

    def list_collections(self, include_objects=False):
        """Lists all collections with hierarchy information."""
        collections_data = []

        # Traverse all collections in deterministic order (alphabetical)
        for collection in sorted(bpy.data.collections, key=lambda c: c.name):
            col_data = {
                "name": collection.name,
                "object_count": len(collection.objects),
                "child_count": len(collection.children),
                "hide_viewport": collection.hide_viewport,
                "hide_render": collection.hide_render,
                "hide_select": collection.hide_select,
            }

            # Find parent collection (if any)
            parent_name = None
            for other_col in bpy.data.collections:
                if collection.name in [child.name for child in other_col.children]:
                    parent_name = other_col.name
                    break

            # Check if it's in the scene's master collection
            if not parent_name and collection.name in [c.name for c in bpy.context.scene.collection.children]:
                parent_name = "Scene Collection"

            col_data["parent"] = parent_name

            # Optionally include object names
            if include_objects:
                col_data["objects"] = sorted([obj.name for obj in collection.objects])

            collections_data.append(col_data)

        return collections_data

    def list_objects(self, collection_name, recursive=True, include_hidden=False):
        """Lists all objects within a specified collection."""
        # Validate collection existence
        collection = bpy.data.collections.get(collection_name)
        if not collection:
            raise ValueError(f"Collection '{collection_name}' not found")

        objects_data = []
        collections_to_process = [collection]

        # Build list of collections to process (recursive if requested)
        if recursive:
            all_collections = [collection]
            i = 0
            while i < len(all_collections):
                current = all_collections[i]
                for child in current.children:
                    all_collections.append(child)
                i += 1
            collections_to_process = all_collections

        # Gather objects from all collections (avoiding duplicates)
        seen_objects = set()

        for col in collections_to_process:
            for obj in col.objects:
                # Skip if already processed
                if obj.name in seen_objects:
                    continue

                # Filter hidden objects if requested
                if not include_hidden and (obj.hide_viewport or obj.hide_render):
                    continue

                seen_objects.add(obj.name)

                obj_data = {
                    "name": obj.name,
                    "type": obj.type,
                    "visible_viewport": not obj.hide_viewport,
                    "visible_render": not obj.hide_render,
                    "selected": obj.select_get(),
                    "location": [round(c, 3) for c in obj.location]
                }

                objects_data.append(obj_data)

        # Sort for deterministic output
        objects_data.sort(key=lambda o: o["name"])

        return {
            "collection_name": collection_name,
            "object_count": len(objects_data),
            "recursive": recursive,
            "include_hidden": include_hidden,
            "objects": objects_data
        }

    def manage_collection(
        self,
        action: str,
        collection_name: str,
        new_name: Optional[str] = None,
        parent_name: Optional[str] = None,
        object_name: Optional[str] = None,
    ) -> str:
        """Manages collections: create, delete, rename, move/link/unlink objects.

        Args:
            action: Operation to perform ('create', 'delete', 'rename',
                    'move_object', 'link_object', 'unlink_object')
            collection_name: Target collection name
            new_name: New name for 'rename' action
            parent_name: Parent collection for 'create' action
            object_name: Object to move/link/unlink

        Returns:
            String describing the result of the operation.
        """
        if action == "create":
            return self._create_collection(collection_name, parent_name)
        elif action == "delete":
            return self._delete_collection(collection_name)
        elif action == "rename":
            return self._rename_collection(collection_name, new_name)
        elif action == "move_object":
            return self._move_object(object_name, collection_name)
        elif action == "link_object":
            return self._link_object(object_name, collection_name)
        elif action == "unlink_object":
            return self._unlink_object(object_name, collection_name)
        else:
            raise ValueError(f"Unknown action: '{action}'. Valid actions: create, delete, rename, move_object, link_object, unlink_object")

    def _create_collection(self, collection_name: str, parent_name: Optional[str] = None) -> str:
        """Creates a new collection, optionally under a parent collection."""
        # Check if collection already exists
        if bpy.data.collections.get(collection_name):
            raise ValueError(f"Collection '{collection_name}' already exists")

        # Create the new collection
        new_col = bpy.data.collections.new(collection_name)

        # Determine parent
        if parent_name:
            parent = bpy.data.collections.get(parent_name)
            if not parent:
                raise ValueError(f"Parent collection '{parent_name}' not found")
            parent.children.link(new_col)
            return f"Created collection '{collection_name}' under '{parent_name}'"
        else:
            # Link to scene's master collection
            bpy.context.scene.collection.children.link(new_col)
            return f"Created collection '{collection_name}' under Scene Collection"

    def _delete_collection(self, collection_name: str) -> str:
        """Deletes a collection. Objects are moved to scene root."""
        col = bpy.data.collections.get(collection_name)
        if not col:
            raise ValueError(f"Collection '{collection_name}' not found")

        # Move objects to scene collection before deleting
        objects_moved = []
        for obj in list(col.objects):
            objects_moved.append(obj.name)
            # Link to scene collection if not already linked elsewhere
            if len(obj.users_collection) == 1:
                bpy.context.scene.collection.objects.link(obj)
            col.objects.unlink(obj)

        # Remove the collection
        bpy.data.collections.remove(col)

        if objects_moved:
            return f"Deleted collection '{collection_name}'. Moved {len(objects_moved)} object(s) to Scene Collection: {', '.join(objects_moved)}"
        return f"Deleted collection '{collection_name}'"

    def _rename_collection(self, collection_name: str, new_name: Optional[str]) -> str:
        """Renames a collection."""
        if not new_name:
            raise ValueError("new_name is required for 'rename' action")

        col = bpy.data.collections.get(collection_name)
        if not col:
            raise ValueError(f"Collection '{collection_name}' not found")

        if bpy.data.collections.get(new_name):
            raise ValueError(f"Collection '{new_name}' already exists")

        old_name = col.name
        col.name = new_name
        return f"Renamed collection '{old_name}' to '{col.name}'"

    def _move_object(self, object_name: Optional[str], collection_name: str) -> str:
        """Moves an object to a collection, unlinking from all others."""
        if not object_name:
            raise ValueError("object_name is required for 'move_object' action")

        obj = bpy.data.objects.get(object_name)
        if not obj:
            raise ValueError(f"Object '{object_name}' not found")

        col = bpy.data.collections.get(collection_name)
        if not col:
            raise ValueError(f"Collection '{collection_name}' not found")

        # Unlink from all current collections
        old_collections = [c.name for c in obj.users_collection]
        for c in list(obj.users_collection):
            c.objects.unlink(obj)

        # Link to target collection
        col.objects.link(obj)
        return f"Moved '{object_name}' to '{collection_name}' (was in: {', '.join(old_collections) or 'none'})"

    def _link_object(self, object_name: Optional[str], collection_name: str) -> str:
        """Links an object to a collection, keeping other links."""
        if not object_name:
            raise ValueError("object_name is required for 'link_object' action")

        obj = bpy.data.objects.get(object_name)
        if not obj:
            raise ValueError(f"Object '{object_name}' not found")

        col = bpy.data.collections.get(collection_name)
        if not col:
            raise ValueError(f"Collection '{collection_name}' not found")

        # Check if already linked
        if obj.name in [o.name for o in col.objects]:
            return f"Object '{object_name}' is already linked to '{collection_name}'"

        col.objects.link(obj)
        return f"Linked '{object_name}' to '{collection_name}'"

    def _unlink_object(self, object_name: Optional[str], collection_name: str) -> str:
        """Unlinks an object from a collection."""
        if not object_name:
            raise ValueError("object_name is required for 'unlink_object' action")

        obj = bpy.data.objects.get(object_name)
        if not obj:
            raise ValueError(f"Object '{object_name}' not found")

        col = bpy.data.collections.get(collection_name)
        if not col:
            raise ValueError(f"Collection '{collection_name}' not found")

        # Check if object is in collection
        if obj.name not in [o.name for o in col.objects]:
            return f"Object '{object_name}' is not in collection '{collection_name}'"

        # Check if this is the only collection
        if len(obj.users_collection) == 1:
            raise ValueError(f"Cannot unlink '{object_name}' from '{collection_name}': it's the only collection. Use 'move_object' instead.")

        col.objects.unlink(obj)
        return f"Unlinked '{object_name}' from '{collection_name}'"
