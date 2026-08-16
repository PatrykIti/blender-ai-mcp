import bpy


class SceneModeVisibilityUtilityMixin:
    """Mode, visibility, and isolation helpers for scene utility RPC methods."""

    def set_mode(self, mode="OBJECT"):
        """Switch Blender context mode."""
        mode = mode.upper()
        valid_modes = ["OBJECT", "EDIT", "SCULPT", "VERTEX_PAINT", "WEIGHT_PAINT", "TEXTURE_PAINT", "POSE"]

        if mode not in valid_modes:
            raise ValueError(f"Invalid mode '{mode}'. Valid: {valid_modes}")

        current_mode = bpy.context.mode
        if current_mode == mode or current_mode.startswith(mode):
            return f"Already in {mode} mode"

        active_obj = bpy.context.active_object
        if mode != "OBJECT" and not active_obj:
            raise ValueError(f"Cannot enter {mode} mode: no active object")

        if mode == "EDIT":
            valid_types = ["MESH", "CURVE", "SURFACE", "META", "FONT", "LATTICE", "ARMATURE"]
            if active_obj.type not in valid_types:
                raise ValueError(
                    f"Cannot enter {mode} mode: active object '{active_obj.name}' "
                    f"is type '{active_obj.type}'. Supported types: {', '.join(valid_types)}"
                )
        elif mode == "SCULPT":
            if active_obj.type != "MESH":
                raise ValueError(
                    f"Cannot enter SCULPT mode: active object '{active_obj.name}' is type '{active_obj.type}'. Only MESH supported."
                )
        elif mode == "POSE":
            if active_obj.type != "ARMATURE":
                raise ValueError(
                    f"Cannot enter POSE mode: active object '{active_obj.name}' is type '{active_obj.type}'. Only ARMATURE supported."
                )

        bpy.ops.object.mode_set(mode=mode)
        return f"Switched to {mode} mode"

    def rename_object(self, old_name, new_name):
        """Renames an object in the scene."""
        obj = bpy.data.objects.get(old_name)
        if obj is None:
            raise ValueError(f"Object '{old_name}' not found")

        obj.name = new_name
        actual_name = obj.name
        if actual_name != new_name:
            return f"Renamed '{old_name}' to '{actual_name}' (suffix added due to name collision)"
        return f"Renamed '{old_name}' to '{actual_name}'"

    def hide_object(self, object_name, hide=True, hide_render=False):
        """Hides or shows an object in the viewport and/or render."""
        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise ValueError(f"Object '{object_name}' not found")

        obj.hide_viewport = hide
        if hide:
            if hide_render:
                obj.hide_render = True
        else:
            obj.hide_render = False

        state = "hidden" if hide else "visible"
        render_state = ""
        if hide and hide_render:
            render_state = " (also in render)"
        elif not hide:
            render_state = " (including render visibility)"
        return f"Object '{object_name}' is now {state}{render_state}"

    def show_all_objects(self, include_render=False):
        """Shows all hidden objects in the scene."""
        viewport_count = 0
        render_count = 0
        for obj in bpy.data.objects:
            if obj.hide_viewport:
                obj.hide_viewport = False
                viewport_count += 1
            if include_render and obj.hide_render:
                obj.hide_render = False
                render_count += 1

        if include_render:
            return (
                f"Made {viewport_count} object(s) visible in viewport and restored "
                f"render visibility for {render_count} object(s)"
            )
        return f"Made {viewport_count} object(s) visible"

    def isolate_object(self, object_names):
        """Isolates object(s) by hiding all others in viewport and render."""
        keep_visible = set(object_names)
        for name in keep_visible:
            if name not in bpy.data.objects:
                raise ValueError(f"Object '{name}' not found")

        hidden_count = 0
        for obj in bpy.data.objects:
            if obj.name not in keep_visible:
                if not obj.hide_viewport:
                    obj.hide_viewport = True
                    hidden_count += 1
                obj.hide_render = True
            else:
                obj.hide_viewport = False
                obj.hide_render = False

        return f"Isolated {len(keep_visible)} object(s), hid {hidden_count} others in viewport and render"
