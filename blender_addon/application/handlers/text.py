import bpy
import os


class TextHandler:
    """Application service for Text operations."""

    # ==========================================================================
    # TASK-034: Text & Annotations
    # ==========================================================================

    def create(
        self,
        text="Text",
        name="Text",
        location=None,
        font=None,
        size=1.0,
        extrude=0.0,
        bevel_depth=0.0,
        bevel_resolution=0,
        align_x="LEFT",
        align_y="BOTTOM_BASELINE",
    ):
        """
        [OBJECT MODE][SCENE] Creates a 3D text object.
        """
        if location is None:
            location = (0, 0, 0)
        else:
            location = tuple(location)

        # Ensure we're in object mode
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # Create text object
        bpy.ops.object.text_add(location=location)
        text_obj = bpy.context.active_object
        text_obj.name = name

        # Set text content
        text_obj.data.body = text

        # Load custom font if provided
        if font:
            if not os.path.exists(font):
                raise ValueError(f"Font file not found: {font}")
            try:
                loaded_font = bpy.data.fonts.load(font)
                text_obj.data.font = loaded_font
            except Exception as e:
                raise ValueError(f"Failed to load font '{font}': {str(e)}")

        # Set geometry properties
        text_obj.data.size = size
        text_obj.data.extrude = extrude
        text_obj.data.bevel_depth = bevel_depth
        text_obj.data.bevel_resolution = bevel_resolution

        # Set alignment
        align_x_upper = align_x.upper()
        align_y_upper = align_y.upper()

        valid_align_x = ["LEFT", "CENTER", "RIGHT", "JUSTIFY", "FLUSH"]
        valid_align_y = ["TOP", "TOP_BASELINE", "MIDDLE", "BOTTOM_BASELINE", "BOTTOM"]

        if align_x_upper not in valid_align_x:
            raise ValueError(f"Invalid align_x '{align_x}'. Must be one of {valid_align_x}")
        if align_y_upper not in valid_align_y:
            raise ValueError(f"Invalid align_y '{align_y}'. Must be one of {valid_align_y}")

        text_obj.data.align_x = align_x_upper
        text_obj.data.align_y = align_y_upper

        result = f"Created text object '{text_obj.name}' with content \"{text}\" at {list(location)}"
        if extrude > 0:
            result += f", extrude={extrude}"
        if bevel_depth > 0:
            result += f", bevel_depth={bevel_depth}"

        return result

    def edit(
        self,
        object_name,
        text=None,
        size=None,
        extrude=None,
        bevel_depth=None,
        bevel_resolution=None,
        align_x=None,
        align_y=None,
    ):
        """
        [OBJECT MODE][NON-DESTRUCTIVE] Edits an existing text object.
        """
        if object_name not in bpy.data.objects:
            raise ValueError(f"Object '{object_name}' not found")

        obj = bpy.data.objects[object_name]

        if obj.type != 'FONT':
            raise ValueError(f"Object '{object_name}' is not a text object (type: {obj.type})")

        modified = []

        if text is not None:
            obj.data.body = text
            modified.append(f"text=\"{text}\"")

        if size is not None:
            obj.data.size = size
            modified.append(f"size={size}")

        if extrude is not None:
            obj.data.extrude = extrude
            modified.append(f"extrude={extrude}")

        if bevel_depth is not None:
            obj.data.bevel_depth = bevel_depth
            modified.append(f"bevel_depth={bevel_depth}")

        if bevel_resolution is not None:
            obj.data.bevel_resolution = bevel_resolution
            modified.append(f"bevel_resolution={bevel_resolution}")

        if align_x is not None:
            align_x_upper = align_x.upper()
            valid_align_x = ["LEFT", "CENTER", "RIGHT", "JUSTIFY", "FLUSH"]
            if align_x_upper not in valid_align_x:
                raise ValueError(f"Invalid align_x '{align_x}'. Must be one of {valid_align_x}")
            obj.data.align_x = align_x_upper
            modified.append(f"align_x={align_x_upper}")

        if align_y is not None:
            align_y_upper = align_y.upper()
            valid_align_y = ["TOP", "TOP_BASELINE", "MIDDLE", "BOTTOM_BASELINE", "BOTTOM"]
            if align_y_upper not in valid_align_y:
                raise ValueError(f"Invalid align_y '{align_y}'. Must be one of {valid_align_y}")
            obj.data.align_y = align_y_upper
            modified.append(f"align_y={align_y_upper}")

        if not modified:
            return f"Text object '{object_name}' unchanged (no parameters provided)"

        return f"Modified text object '{object_name}': {', '.join(modified)}"

    def to_mesh(self, object_name, keep_original=False):
        """
        [OBJECT MODE][DESTRUCTIVE] Converts a text object to mesh.
        """
        if object_name not in bpy.data.objects:
            raise ValueError(f"Object '{object_name}' not found")

        obj = bpy.data.objects[object_name]

        if obj.type != 'FONT':
            raise ValueError(f"Object '{object_name}' is not a text object (type: {obj.type})")

        # Ensure we're in object mode
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # Select the object and make it active
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        original_name = obj.name
        text_content = obj.data.body

        if keep_original:
            # Duplicate before converting
            bpy.ops.object.duplicate()
            duplicated_obj = bpy.context.active_object
            duplicated_obj.name = f"{original_name}_mesh"
            # Now convert the duplicate
            try:
                bpy.ops.object.convert(target='MESH')
            except RuntimeError as e:
                raise ValueError(f"Failed to convert text to mesh: {str(e)}")
            converted_obj = bpy.context.active_object
            return f"Converted text '{original_name}' to mesh '{converted_obj.name}' (original preserved)"
        else:
            # Convert directly
            try:
                bpy.ops.object.convert(target='MESH')
            except RuntimeError as e:
                raise ValueError(f"Failed to convert text to mesh: {str(e)}")
            converted_obj = bpy.context.active_object
            return f"Converted text '{original_name}' to mesh '{converted_obj.name}'"
