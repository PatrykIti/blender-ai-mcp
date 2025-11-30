"""
Blender Addon: Baking Handler

Implements texture baking operations using Cycles renderer.
"""

try:
    import bpy
    import os
except ImportError:
    bpy = None


class BakingHandler:
    """Handler for texture baking operations in Blender."""

    def _ensure_cycles(self):
        """Ensures Cycles renderer is active. Returns previous engine."""
        previous_engine = bpy.context.scene.render.engine
        if previous_engine != 'CYCLES':
            bpy.context.scene.render.engine = 'CYCLES'
        return previous_engine

    def _restore_engine(self, previous_engine):
        """Restores the previous render engine."""
        if previous_engine != 'CYCLES':
            bpy.context.scene.render.engine = previous_engine

    def _get_object(self, object_name):
        """Gets object by name or raises error."""
        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise ValueError(f"Object '{object_name}' not found")
        return obj

    def _ensure_uv_map(self, obj):
        """Ensures object has UV map. Raises error if missing."""
        if obj.type != 'MESH':
            raise ValueError(f"Object '{obj.name}' is not a mesh")
        if not obj.data.uv_layers:
            raise ValueError(f"Object '{obj.name}' has no UV map. Use uv_unwrap first.")
        return obj.data.uv_layers.active

    def _create_bake_image(self, name, resolution):
        """Creates a new image for baking."""
        # Remove existing image with same name
        if name in bpy.data.images:
            bpy.data.images.remove(bpy.data.images[name])

        image = bpy.data.images.new(
            name=name,
            width=resolution,
            height=resolution,
            alpha=True,
            float_buffer=False
        )
        image.colorspace_settings.name = 'sRGB'
        return image

    def _setup_bake_material(self, obj, image):
        """
        Ensures object has a material with an Image Texture node for baking.
        Returns the image texture node that should be active for baking.
        """
        # Ensure object has at least one material
        if not obj.data.materials:
            mat = bpy.data.materials.new(name=f"{obj.name}_BakeMaterial")
            mat.use_nodes = True
            obj.data.materials.append(mat)
        else:
            mat = obj.data.materials[0]
            if mat is None:
                mat = bpy.data.materials.new(name=f"{obj.name}_BakeMaterial")
                mat.use_nodes = True
                obj.data.materials[0] = mat

        # Ensure material uses nodes
        if not mat.use_nodes:
            mat.use_nodes = True

        nodes = mat.node_tree.nodes

        # Create or get image texture node for baking
        bake_node = None
        for node in nodes:
            if node.type == 'TEX_IMAGE' and node.name == 'BakeTarget':
                bake_node = node
                break

        if bake_node is None:
            bake_node = nodes.new(type='ShaderNodeTexImage')
            bake_node.name = 'BakeTarget'
            bake_node.label = 'Bake Target'
            bake_node.location = (-300, 300)

        # Set the image
        bake_node.image = image

        # Make this node active (required for baking)
        nodes.active = bake_node

        return bake_node

    def _save_image(self, image, output_path):
        """Saves the baked image to file."""
        # Ensure directory exists
        directory = os.path.dirname(output_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        # Determine format from extension
        ext = os.path.splitext(output_path)[1].lower()
        if ext == '.exr':
            image.file_format = 'OPEN_EXR'
        elif ext in ['.jpg', '.jpeg']:
            image.file_format = 'JPEG'
        else:
            image.file_format = 'PNG'

        image.filepath_raw = output_path
        image.save()

    def bake_normal_map(
        self,
        object_name,
        output_path,
        resolution=1024,
        high_poly_source=None,
        cage_extrusion=0.1,
        margin=16,
        normal_space="TANGENT"
    ):
        """
        Bakes normal map from high-poly to low-poly or from geometry.
        """
        previous_engine = self._ensure_cycles()

        try:
            # Get target object
            target_obj = self._get_object(object_name)
            self._ensure_uv_map(target_obj)

            # Create bake image
            image_name = f"{object_name}_NormalMap"
            image = self._create_bake_image(image_name, resolution)

            # For normal maps, use non-color data
            image.colorspace_settings.name = 'Non-Color'

            # Setup material with image texture
            self._setup_bake_material(target_obj, image)

            # Configure bake settings
            bake_settings = bpy.context.scene.render.bake
            bake_settings.margin = margin

            # Validate normal space
            normal_space = normal_space.upper()
            if normal_space not in ['TANGENT', 'OBJECT']:
                raise ValueError(f"Invalid normal_space '{normal_space}'. Must be 'TANGENT' or 'OBJECT'.")
            bake_settings.normal_space = normal_space

            # High-to-low baking setup
            if high_poly_source:
                source_obj = self._get_object(high_poly_source)

                bake_settings.use_selected_to_active = True
                bake_settings.cage_extrusion = cage_extrusion

                # Deselect all, select source, then target (active)
                bpy.ops.object.select_all(action='DESELECT')
                source_obj.select_set(True)
                target_obj.select_set(True)
                bpy.context.view_layer.objects.active = target_obj

                bake_mode = f"high-to-low from '{high_poly_source}'"
            else:
                bake_settings.use_selected_to_active = False

                # Select only target
                bpy.ops.object.select_all(action='DESELECT')
                target_obj.select_set(True)
                bpy.context.view_layer.objects.active = target_obj

                bake_mode = "self-bake"

            # Perform bake
            bpy.ops.object.bake(type='NORMAL')

            # Save image
            self._save_image(image, output_path)

            return f"Baked normal map ({bake_mode}) to '{output_path}' [{resolution}x{resolution}, {normal_space} space]"

        finally:
            self._restore_engine(previous_engine)

    def bake_ao(
        self,
        object_name,
        output_path,
        resolution=1024,
        samples=128,
        distance=1.0,
        margin=16
    ):
        """
        Bakes ambient occlusion map.
        """
        previous_engine = self._ensure_cycles()

        try:
            # Get target object
            target_obj = self._get_object(object_name)
            self._ensure_uv_map(target_obj)

            # Create bake image
            image_name = f"{object_name}_AO"
            image = self._create_bake_image(image_name, resolution)

            # Setup material with image texture
            self._setup_bake_material(target_obj, image)

            # Configure render samples
            bpy.context.scene.cycles.samples = samples

            # Configure bake settings
            bake_settings = bpy.context.scene.render.bake
            bake_settings.margin = margin
            bake_settings.use_selected_to_active = False

            # Configure world for AO
            if bpy.context.scene.world:
                bpy.context.scene.world.light_settings.distance = distance

            # Select target
            bpy.ops.object.select_all(action='DESELECT')
            target_obj.select_set(True)
            bpy.context.view_layer.objects.active = target_obj

            # Perform bake
            bpy.ops.object.bake(type='AO')

            # Save image
            self._save_image(image, output_path)

            return f"Baked AO map to '{output_path}' [{resolution}x{resolution}, {samples} samples]"

        finally:
            self._restore_engine(previous_engine)

    def bake_combined(
        self,
        object_name,
        output_path,
        resolution=1024,
        samples=128,
        margin=16,
        use_pass_direct=True,
        use_pass_indirect=True,
        use_pass_color=True
    ):
        """
        Bakes combined render (full material + lighting) to texture.
        """
        previous_engine = self._ensure_cycles()

        try:
            # Get target object
            target_obj = self._get_object(object_name)
            self._ensure_uv_map(target_obj)

            # Create bake image
            image_name = f"{object_name}_Combined"
            image = self._create_bake_image(image_name, resolution)

            # Setup material with image texture
            self._setup_bake_material(target_obj, image)

            # Configure render samples
            bpy.context.scene.cycles.samples = samples

            # Configure bake settings
            bake_settings = bpy.context.scene.render.bake
            bake_settings.margin = margin
            bake_settings.use_selected_to_active = False
            bake_settings.use_pass_direct = use_pass_direct
            bake_settings.use_pass_indirect = use_pass_indirect
            bake_settings.use_pass_color = use_pass_color

            # Select target
            bpy.ops.object.select_all(action='DESELECT')
            target_obj.select_set(True)
            bpy.context.view_layer.objects.active = target_obj

            # Perform bake
            bpy.ops.object.bake(type='COMBINED')

            # Save image
            self._save_image(image, output_path)

            passes = []
            if use_pass_direct:
                passes.append("direct")
            if use_pass_indirect:
                passes.append("indirect")
            if use_pass_color:
                passes.append("color")
            passes_str = ", ".join(passes) if passes else "none"

            return f"Baked combined map to '{output_path}' [{resolution}x{resolution}, {samples} samples, passes: {passes_str}]"

        finally:
            self._restore_engine(previous_engine)

    def bake_diffuse(
        self,
        object_name,
        output_path,
        resolution=1024,
        margin=16
    ):
        """
        Bakes diffuse/albedo color only.
        """
        previous_engine = self._ensure_cycles()

        try:
            # Get target object
            target_obj = self._get_object(object_name)
            self._ensure_uv_map(target_obj)

            # Create bake image
            image_name = f"{object_name}_Diffuse"
            image = self._create_bake_image(image_name, resolution)

            # Setup material with image texture
            self._setup_bake_material(target_obj, image)

            # Configure bake settings
            bake_settings = bpy.context.scene.render.bake
            bake_settings.margin = margin
            bake_settings.use_selected_to_active = False

            # For diffuse, disable lighting passes
            bake_settings.use_pass_direct = False
            bake_settings.use_pass_indirect = False
            bake_settings.use_pass_color = True

            # Select target
            bpy.ops.object.select_all(action='DESELECT')
            target_obj.select_set(True)
            bpy.context.view_layer.objects.active = target_obj

            # Perform bake
            bpy.ops.object.bake(type='DIFFUSE')

            # Save image
            self._save_image(image, output_path)

            return f"Baked diffuse map to '{output_path}' [{resolution}x{resolution}]"

        finally:
            self._restore_engine(previous_engine)
