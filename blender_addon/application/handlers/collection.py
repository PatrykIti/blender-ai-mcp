import bpy


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
