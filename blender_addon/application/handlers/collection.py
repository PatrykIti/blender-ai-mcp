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
