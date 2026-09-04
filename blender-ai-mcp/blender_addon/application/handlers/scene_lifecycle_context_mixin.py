import bpy


class SceneLifecycleContextMixin:
    """Lifecycle and context-read helpers for scene RPC methods."""

    def list_objects(self):
        """Returns a list of objects in the scene."""
        objects = []
        for obj in bpy.context.scene.objects:
            objects.append({"name": obj.name, "type": obj.type, "location": [round(c, 3) for c in obj.location]})
        return objects

    def delete_object(self, name):
        """Deletes an object by name."""
        if name not in bpy.data.objects:
            raise ValueError(f"Object '{name}' not found")

        obj = bpy.data.objects[name]
        bpy.data.objects.remove(obj, do_unlink=True)
        return {"deleted": name}

    def clean_scene(self, keep_lights_and_cameras=True):
        """
        Deletes objects from the scene.
        If keep_lights_and_cameras is True, preserves LIGHT and CAMERA objects.
        """
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        bpy.ops.object.select_all(action="DESELECT")

        to_delete = []
        for obj in bpy.context.scene.objects:
            if keep_lights_and_cameras:
                if obj.type in [
                    "MESH",
                    "CURVE",
                    "SURFACE",
                    "META",
                    "FONT",
                    "HAIR",
                    "POINTCLOUD",
                    "VOLUME",
                    "EMPTY",
                    "LATTICE",
                    "ARMATURE",
                ]:
                    to_delete.append(obj)
            else:
                to_delete.append(obj)

        for obj in to_delete:
            bpy.data.objects.remove(obj, do_unlink=True)

        if not keep_lights_and_cameras:
            for col in bpy.data.collections:
                if col.users == 0:
                    bpy.data.collections.remove(col)

        return {"count": len(to_delete), "kept_environment": keep_lights_and_cameras}

    def duplicate_object(self, name, translation=None):
        """Duplicates an object and optionally translates it."""
        if name not in bpy.data.objects:
            raise ValueError(f"Object '{name}' not found")

        obj = bpy.data.objects[name]

        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        bpy.ops.object.duplicate()
        new_obj = bpy.context.view_layer.objects.active

        if translation:
            bpy.ops.transform.translate(value=translation)

        return {"original": name, "new_object": new_obj.name, "location": [round(c, 3) for c in new_obj.location]}

    def set_active_object(self, name):
        """Sets the active object."""
        if name not in bpy.data.objects:
            raise ValueError(f"Object '{name}' not found")

        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        obj = bpy.data.objects[name]
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        return {"active": name}

    def get_mode(self):
        """Reports the current Blender interaction mode and selection summary."""
        mode = getattr(bpy.context, "mode", "UNKNOWN")
        active_obj = getattr(bpy.context, "active_object", None)
        active_name = active_obj.name if active_obj else None
        active_type = getattr(active_obj, "type", None) if active_obj else None

        selected_names = []
        try:
            selected = getattr(bpy.context, "selected_objects", [])
            if selected:
                selected_names = [obj.name for obj in selected if hasattr(obj, "name")]
        except Exception:
            selected_names = []

        return {
            "mode": mode,
            "active_object": active_name,
            "active_object_type": active_type,
            "selected_object_names": selected_names,
            "selection_count": len(selected_names),
        }

    def list_selection(self):
        """Summarizes current selection for Object and Edit modes."""
        mode = getattr(bpy.context, "mode", "UNKNOWN")
        selected = getattr(bpy.context, "selected_objects", []) or []
        selected_names = [obj.name for obj in selected if hasattr(obj, "name")]

        summary = {
            "mode": mode,
            "selected_object_names": selected_names,
            "selection_count": len(selected_names),
            "edit_mode_vertex_count": None,
            "edit_mode_edge_count": None,
            "edit_mode_face_count": None,
        }

        if mode.startswith("EDIT"):
            obj = getattr(bpy.context, "edit_object", None) or getattr(bpy.context, "active_object", None)
            if obj and obj.type == "MESH":
                try:
                    import bmesh

                    bm = bmesh.from_edit_mesh(obj.data)
                    summary["edit_mode_vertex_count"] = sum(1 for v in bm.verts if v.select)
                    summary["edit_mode_edge_count"] = sum(1 for e in bm.edges if e.select)
                    summary["edit_mode_face_count"] = sum(1 for f in bm.faces if f.select)
                except Exception:
                    pass

        return summary
