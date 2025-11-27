import bpy


class MaterialHandler:
    """Application service for material operations."""

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
