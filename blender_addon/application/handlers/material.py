import bpy


class MaterialHandler:
    """Application service for material operations.

    Provides operations for managing Blender materials including
    creation, assignment, parameter modification, and texture binding.
    """

    def list_materials(self, include_unassigned=True):
        """Lists all materials with shader parameters."""
        # Build assignment count dictionary
        assignment_counts = {}
        for obj in bpy.data.objects:
            if hasattr(obj, 'material_slots'):
                for slot in obj.material_slots:
                    if slot.material:
                        mat_name = slot.material.name
                        assignment_counts[mat_name] = assignment_counts.get(mat_name, 0) + 1

        materials_data = []
        for mat in sorted(bpy.data.materials, key=lambda m: m.name):
            assigned_count = assignment_counts.get(mat.name, 0)

            # Filter unassigned if requested
            if not include_unassigned and assigned_count == 0:
                continue

            mat_data = {
                "name": mat.name,
                "use_nodes": mat.use_nodes,
                "assigned_object_count": assigned_count
            }

            # Try to extract Principled BSDF parameters
            if mat.use_nodes and mat.node_tree:
                principled = None
                for node in mat.node_tree.nodes:
                    if node.type == 'BSDF_PRINCIPLED':
                        principled = node
                        break

                if principled:
                    try:
                        base_color = principled.inputs['Base Color'].default_value
                        mat_data["base_color"] = [round(c, 3) for c in base_color[:3]]
                        mat_data["alpha"] = round(base_color[3], 3) if len(base_color) > 3 else 1.0
                        mat_data["roughness"] = round(principled.inputs['Roughness'].default_value, 3)
                        mat_data["metallic"] = round(principled.inputs['Metallic'].default_value, 3)
                    except Exception:
                        pass

            materials_data.append(mat_data)

        return materials_data

    def list_by_object(self, object_name, include_indices=False):
        """Lists material slots for a given object."""
        obj = bpy.data.objects.get(object_name)
        if not obj:
            raise ValueError(f"Object '{object_name}' not found")

        slots_data = []
        for idx, slot in enumerate(obj.material_slots):
            slot_info = {
                "slot_index": idx,
                "slot_name": slot.name,
                "material_name": slot.material.name if slot.material else None,
                "uses_nodes": slot.material.use_nodes if slot.material else False
            }

            # Optionally include material indices (face assignment would require bmesh in Edit Mode)
            if include_indices and slot.material:
                # This is a simplified version - full face-level assignment requires Edit Mode
                slot_info["note"] = "Face-level indices require Edit Mode analysis (not implemented yet)"

            slots_data.append(slot_info)

        return {
            "object_name": object_name,
            "slot_count": len(slots_data),
            "slots": slots_data
        }

    # TASK-023-1: material_create
    def create_material(
        self,
        name,
        base_color=None,
        metallic=0.0,
        roughness=0.5,
        emission_color=None,
        emission_strength=0.0,
        alpha=1.0,
    ):
        """Creates a new PBR material with Principled BSDF shader.

        Args:
            name: Material name.
            base_color: RGBA color [0-1] (default: [0.8, 0.8, 0.8, 1.0]).
            metallic: Metallic value 0-1.
            roughness: Roughness value 0-1.
            emission_color: Emission RGB [0-1].
            emission_strength: Emission strength.
            alpha: Alpha/opacity 0-1.

        Returns:
            Success message with created material name.
        """
        # Create new material
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True

        # Get Principled BSDF node
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if not bsdf:
            raise ValueError(f"Failed to create Principled BSDF for material '{name}'")

        # Set base color (with default)
        if base_color is None:
            base_color = [0.8, 0.8, 0.8, 1.0]
        elif len(base_color) == 3:
            base_color = list(base_color) + [1.0]
        bsdf.inputs["Base Color"].default_value = base_color

        # Set metallic and roughness
        bsdf.inputs["Metallic"].default_value = max(0.0, min(1.0, metallic))
        bsdf.inputs["Roughness"].default_value = max(0.0, min(1.0, roughness))

        # Set emission if provided
        if emission_color is not None:
            if len(emission_color) == 3:
                emission_color = list(emission_color) + [1.0]
            bsdf.inputs["Emission Color"].default_value = emission_color
            bsdf.inputs["Emission Strength"].default_value = emission_strength

        # Set alpha/transparency
        if alpha < 1.0:
            mat.blend_method = 'BLEND'
            # Note: shadow_method was removed in Blender 4.2+
            bsdf.inputs["Alpha"].default_value = max(0.0, min(1.0, alpha))

        return f"Created material '{mat.name}'"

    # TASK-023-2: material_assign
    def assign_material(
        self,
        material_name,
        object_name=None,
        slot_index=None,
        assign_to_selection=False,
    ):
        """Assigns material to object or selected faces.

        Args:
            material_name: Name of existing material.
            object_name: Target object (default: active object).
            slot_index: Material slot index (default: auto).
            assign_to_selection: If True and in Edit Mode, assign to selected faces.

        Returns:
            Success message with assignment details.
        """
        # Get material
        mat = bpy.data.materials.get(material_name)
        if not mat:
            raise ValueError(f"Material '{material_name}' not found")

        # Get target object
        if object_name:
            obj = bpy.data.objects.get(object_name)
            if not obj:
                raise ValueError(f"Object '{object_name}' not found")
        else:
            obj = bpy.context.active_object
            if not obj:
                raise ValueError("No active object selected")

        # Check if object can have materials
        if not hasattr(obj.data, 'materials'):
            raise ValueError(f"Object '{obj.name}' cannot have materials (type: {obj.type})")

        # Check if material is already in a slot
        existing_slot_idx = None
        for i, slot in enumerate(obj.material_slots):
            if slot.material and slot.material.name == material_name:
                existing_slot_idx = i
                break

        # Add material to slot if not present
        if existing_slot_idx is None:
            if slot_index is not None and slot_index < len(obj.material_slots):
                # Use specific slot
                obj.material_slots[slot_index].material = mat
                existing_slot_idx = slot_index
            else:
                # Append new slot
                obj.data.materials.append(mat)
                existing_slot_idx = len(obj.material_slots) - 1

        # Handle Edit Mode face assignment
        if assign_to_selection and obj.mode == 'EDIT':
            obj.active_material_index = existing_slot_idx
            bpy.ops.object.material_slot_assign()
            return f"Assigned '{material_name}' to selected faces on '{obj.name}'"

        return f"Assigned '{material_name}' to '{obj.name}' (slot {existing_slot_idx})"

    # TASK-023-3: material_set_params
    def set_material_params(
        self,
        material_name,
        base_color=None,
        metallic=None,
        roughness=None,
        emission_color=None,
        emission_strength=None,
        alpha=None,
    ):
        """Modifies parameters of existing material.

        Only provided parameters are changed; others remain unchanged.

        Args:
            material_name: Name of material to modify.
            base_color: New RGBA color [0-1].
            metallic: New metallic value 0-1.
            roughness: New roughness value 0-1.
            emission_color: New emission RGB [0-1].
            emission_strength: New emission strength.
            alpha: New alpha/opacity 0-1.

        Returns:
            Success message with modified parameters.
        """
        mat = bpy.data.materials.get(material_name)
        if not mat:
            raise ValueError(f"Material '{material_name}' not found")

        if not mat.use_nodes or not mat.node_tree:
            raise ValueError(f"Material '{material_name}' is not using nodes")

        # Find Principled BSDF node
        bsdf = None
        for node in mat.node_tree.nodes:
            if node.type == 'BSDF_PRINCIPLED':
                bsdf = node
                break

        if not bsdf:
            raise ValueError(f"Material '{material_name}' has no Principled BSDF node")

        modified = []

        # Update base color
        if base_color is not None:
            if len(base_color) == 3:
                base_color = list(base_color) + [1.0]
            bsdf.inputs["Base Color"].default_value = base_color
            modified.append("base_color")

        # Update metallic
        if metallic is not None:
            bsdf.inputs["Metallic"].default_value = max(0.0, min(1.0, metallic))
            modified.append("metallic")

        # Update roughness
        if roughness is not None:
            bsdf.inputs["Roughness"].default_value = max(0.0, min(1.0, roughness))
            modified.append("roughness")

        # Update emission
        if emission_color is not None:
            if len(emission_color) == 3:
                emission_color = list(emission_color) + [1.0]
            bsdf.inputs["Emission Color"].default_value = emission_color
            modified.append("emission_color")

        if emission_strength is not None:
            bsdf.inputs["Emission Strength"].default_value = emission_strength
            modified.append("emission_strength")

        # Update alpha
        if alpha is not None:
            bsdf.inputs["Alpha"].default_value = max(0.0, min(1.0, alpha))
            if alpha < 1.0:
                mat.blend_method = 'BLEND'
                # Note: shadow_method was removed in Blender 4.2+
            else:
                mat.blend_method = 'OPAQUE'
            modified.append("alpha")

        if not modified:
            return f"No parameters provided to update for '{material_name}'"

        return f"Updated '{material_name}': {', '.join(modified)}"

    # TASK-023-4: material_set_texture
    def set_material_texture(
        self,
        material_name,
        texture_path,
        input_name="Base Color",
        color_space="sRGB",
    ):
        """Binds image texture to material input.

        Automatically creates Image Texture node and connects to Principled BSDF.

        Args:
            material_name: Target material name.
            texture_path: Path to image file.
            input_name: BSDF input ('Base Color', 'Roughness', 'Normal', 'Metallic', 'Emission Color').
            color_space: Color space ('sRGB' for color, 'Non-Color' for data maps).

        Returns:
            Success message with connection details.
        """
        mat = bpy.data.materials.get(material_name)
        if not mat:
            raise ValueError(f"Material '{material_name}' not found")

        if not mat.use_nodes or not mat.node_tree:
            raise ValueError(f"Material '{material_name}' is not using nodes")

        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        # Find Principled BSDF node
        bsdf = None
        for node in nodes:
            if node.type == 'BSDF_PRINCIPLED':
                bsdf = node
                break

        if not bsdf:
            raise ValueError(f"Material '{material_name}' has no Principled BSDF node")

        # Load image
        try:
            img = bpy.data.images.load(texture_path)
        except Exception as e:
            raise ValueError(f"Failed to load image '{texture_path}': {e}")

        img.colorspace_settings.name = color_space

        # Create Image Texture node
        tex_node = nodes.new("ShaderNodeTexImage")
        tex_node.image = img
        tex_node.location = (bsdf.location[0] - 300, bsdf.location[1])

        # Handle Normal map special case
        if input_name == "Normal":
            # Create Normal Map node
            normal_node = nodes.new("ShaderNodeNormalMap")
            normal_node.location = (bsdf.location[0] - 150, bsdf.location[1] - 200)

            # Connect texture to normal map
            links.new(tex_node.outputs["Color"], normal_node.inputs["Color"])

            # Connect normal map to BSDF
            links.new(normal_node.outputs["Normal"], bsdf.inputs["Normal"])

            return f"Connected normal map texture to '{material_name}'"

        # Standard connection
        if input_name not in bsdf.inputs:
            raise ValueError(f"Unknown BSDF input: '{input_name}'. Valid: Base Color, Metallic, Roughness, Emission Color, Alpha, Normal")

        # For single-value inputs (Roughness, Metallic), use non-color output if available
        output_socket = "Color"
        if input_name in ["Roughness", "Metallic", "Alpha"]:
            # These should use Non-Color space
            if color_space != "Non-Color":
                img.colorspace_settings.name = "Non-Color"

        links.new(tex_node.outputs[output_socket], bsdf.inputs[input_name])

        return f"Connected texture to '{input_name}' on '{material_name}'"
