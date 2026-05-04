import bpy


class SceneInspectionMixin:
    """Inspection and topology helpers for scene RPC methods."""

    def inspect_object(self, name):
        """Returns a structured report containing object metadata."""
        obj = bpy.data.objects.get(name)
        if obj is None:
            raise ValueError(f"Object '{name}' not found")

        data = {
            "object_name": obj.name,
            "type": obj.type,
            "location": self._vec_to_list(getattr(obj, "location", (0.0, 0.0, 0.0))),
            "rotation": self._vec_to_list(getattr(obj, "rotation_euler", (0.0, 0.0, 0.0))),
            "scale": self._vec_to_list(getattr(obj, "scale", (1.0, 1.0, 1.0))),
            "dimensions": self._vec_to_list(getattr(obj, "dimensions", (0.0, 0.0, 0.0))),
            "collections": [col.name for col in getattr(obj, "users_collection", [])],
            "material_slots": self._gather_material_slots(obj),
            "modifiers": self._gather_modifiers(obj),
            "custom_properties": self._gather_custom_properties(obj),
        }

        mesh_stats = self._gather_mesh_stats(obj)
        if mesh_stats:
            data["mesh_stats"] = mesh_stats

        return data

    def _gather_material_slots(self, obj):
        slots = []
        for index, slot in enumerate(getattr(obj, "material_slots", []) or []):
            material = getattr(slot, "material", None)
            slots.append(
                {
                    "slot_index": index,
                    "slot_name": getattr(slot, "name", None),
                    "material_name": material.name if material else None,
                }
            )
        return slots

    def _gather_modifiers(self, obj):
        mods = []
        for mod in getattr(obj, "modifiers", []) or []:
            mods.append(
                {
                    "name": getattr(mod, "name", None),
                    "type": getattr(mod, "type", None),
                    "show_viewport": getattr(mod, "show_viewport", True),
                    "show_render": getattr(mod, "show_render", True),
                }
            )
        return mods

    def _gather_custom_properties(self, obj):
        custom = {}
        try:
            for key in obj.keys():
                if key.startswith("_"):
                    continue
                value = obj.get(key)
                if isinstance(value, (int, float, str, bool)):
                    custom[key] = value
                else:
                    custom[key] = str(value)
        except Exception:
            return {}
        return custom

    def inspect_mesh_topology(self, object_name, detailed=False):
        """Reports detailed topology stats for a given mesh."""
        if object_name not in bpy.data.objects:
            raise ValueError(f"Object '{object_name}' not found")

        obj = bpy.data.objects[object_name]
        if obj.type != "MESH":
            raise ValueError(f"Object '{object_name}' is not a MESH (type: {obj.type})")

        import bmesh

        # Create a new BMesh to inspect data safely without affecting the scene
        bm = bmesh.new()

        try:
            # Load mesh data
            # Note: If object is in Edit Mode, this gets the underlying mesh data
            # which might not include uncommitted bmesh changes.
            # For 100% accuracy in Edit Mode, we'd need bmesh.from_edit_mesh,
            # but that requires being in Edit Mode context.
            # For a general introspection tool, looking at obj.data is standard.
            bm.from_mesh(obj.data)

            bm.verts.ensure_lookup_table()
            bm.edges.ensure_lookup_table()
            bm.faces.ensure_lookup_table()

            stats = {
                "object_name": obj.name,
                "vertex_count": len(bm.verts),
                "edge_count": len(bm.edges),
                "face_count": len(bm.faces),
                "triangle_count": 0,
                "quad_count": 0,
                "ngon_count": 0,
                # Default these to 0/None unless detailed check runs
                "non_manifold_edges": 0 if detailed else None,
                "loose_vertices": 0 if detailed else None,
                "loose_edges": 0 if detailed else None,
            }

            # Face type counts
            for f in bm.faces:
                v_count = len(f.verts)
                if v_count == 3:
                    stats["triangle_count"] += 1
                elif v_count == 4:
                    stats["quad_count"] += 1
                else:
                    stats["ngon_count"] += 1

            if detailed:
                # Non-manifold edges (wire edges or edges shared by >2 faces)
                # is_manifold property handles this check
                stats["non_manifold_edges"] = sum(1 for e in bm.edges if not e.is_manifold)

                # Loose geometry
                stats["loose_vertices"] = sum(1 for v in bm.verts if not v.link_edges)
                stats["loose_edges"] = sum(1 for e in bm.edges if not e.link_faces)

            return stats

        finally:
            bm.free()

    def inspect_material_slots(self, material_filter=None, include_empty_slots=True):
        """Audits material slot assignments across the entire scene."""
        slot_data = []
        warnings = []

        # Iterate all objects in deterministic order
        for obj in sorted(bpy.context.scene.objects, key=lambda o: o.name):
            # Only process objects that can have materials
            if not hasattr(obj, "material_slots") or len(obj.material_slots) == 0:
                continue

            for slot_idx, slot in enumerate(obj.material_slots):
                mat_name = slot.material.name if slot.material else None

                # Apply material filter if provided
                if material_filter and mat_name != material_filter:
                    continue

                # Skip empty slots if requested
                if not include_empty_slots and mat_name is None:
                    continue

                slot_info = {
                    "object_name": obj.name,
                    "object_type": obj.type,
                    "slot_index": slot_idx,
                    "slot_name": slot.name,
                    "material_name": mat_name,
                    "is_empty": mat_name is None,
                }

                # Add warnings for problematic slots
                slot_warnings = []
                if mat_name is None:
                    slot_warnings.append("Empty slot (no material assigned)")
                elif mat_name not in bpy.data.materials:
                    slot_warnings.append(f"Material '{mat_name}' not found in bpy.data.materials")

                if slot_warnings:
                    slot_info["warnings"] = slot_warnings
                    warnings.extend([f"{obj.name}[{slot_idx}]: {w}" for w in slot_warnings])

                slot_data.append(slot_info)

        # Build summary
        empty_count = sum(1 for s in slot_data if s["is_empty"])
        assigned_count = len(slot_data) - empty_count

        return {
            "total_slots": len(slot_data),
            "assigned_slots": assigned_count,
            "empty_slots": empty_count,
            "warnings": warnings,
            "slots": slot_data,
        }

    def inspect_modifiers(self, object_name=None, include_disabled=True):
        """Audits modifier stacks for a specific object or the entire scene."""
        result = {"object_count": 0, "modifier_count": 0, "objects": []}

        objects_to_check = []
        if object_name:
            if object_name not in bpy.data.objects:
                raise ValueError(f"Object '{object_name}' not found")
            objects_to_check.append(bpy.data.objects[object_name])
        else:
            # Deterministic order
            objects_to_check = sorted(bpy.context.scene.objects, key=lambda o: o.name)

        for obj in objects_to_check:
            # Skip objects that don't support modifiers (e.g. Empty, Light)
            if not hasattr(obj, "modifiers") or len(obj.modifiers) == 0:
                continue

            modifiers = []
            for mod in obj.modifiers:
                # Check visibility (viewport or render)
                is_enabled = mod.show_viewport or mod.show_render
                if not include_disabled and not is_enabled:
                    continue

                mod_info = {
                    "name": mod.name,
                    "type": mod.type,
                    "is_enabled": is_enabled,
                    "show_viewport": mod.show_viewport,
                    "show_render": mod.show_render,
                }

                # Extract key properties based on type
                if mod.type == "SUBSURF":
                    mod_info["levels"] = mod.levels
                    mod_info["render_levels"] = mod.render_levels
                elif mod.type == "BEVEL":
                    mod_info["width"] = mod.width
                    mod_info["segments"] = mod.segments
                    mod_info["limit_method"] = mod.limit_method
                elif mod.type == "MIRROR":
                    mod_info["use_axis"] = [mod.use_axis[0], mod.use_axis[1], mod.use_axis[2]]
                    mod_info["mirror_object"] = mod.mirror_object.name if mod.mirror_object else None
                elif mod.type == "BOOLEAN":
                    mod_info["operation"] = mod.operation
                    mod_info["object"] = mod.object.name if mod.object else None
                    mod_info["solver"] = mod.solver
                elif mod.type == "ARRAY":
                    mod_info["count"] = mod.count
                    mod_info["use_relative_offset"] = mod.use_relative_offset
                    mod_info["use_constant_offset"] = mod.use_constant_offset
                elif mod.type == "SOLIDIFY":
                    mod_info["thickness"] = mod.thickness
                    mod_info["offset"] = mod.offset

                modifiers.append(mod_info)

            if modifiers:
                result["objects"].append({"name": obj.name, "modifiers": modifiers})
                result["modifier_count"] += len(modifiers)
                result["object_count"] += 1

        return result

    def get_constraints(self, object_name, include_bones=False):
        """
        [OBJECT MODE][READ-ONLY][SAFE] Returns object (and optional bone) constraints.
        """
        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise ValueError(f"Object '{object_name}' not found")

        constraints = self._serialize_constraints(getattr(obj, "constraints", []))
        bone_constraints = []

        if include_bones and obj.type == "ARMATURE":
            pose = getattr(obj, "pose", None)
            if pose and hasattr(pose, "bones"):
                for bone in pose.bones:
                    bone_list = self._serialize_constraints(getattr(bone, "constraints", []))
                    if bone_list:
                        bone_constraints.append({"bone_name": bone.name, "constraints": bone_list})

        return {
            "object_name": object_name,
            "constraint_count": len(constraints),
            "constraints": constraints,
            "bone_constraints": bone_constraints,
        }

    def _serialize_constraints(self, constraints):
        return [self._serialize_constraint(constraint) for constraint in constraints]

    def _serialize_constraint(self, constraint):
        object_refs = []
        seen_refs = set()
        properties = {}

        for prop in sorted(constraint.bl_rna.properties, key=lambda p: p.identifier):
            if prop.identifier == "rna_type":
                continue
            try:
                value = getattr(constraint, prop.identifier)
            except Exception:
                continue

            properties[prop.identifier] = self._serialize_constraint_value(value, prop, object_refs, seen_refs)

        return {"name": constraint.name, "type": constraint.type, "properties": properties, "object_refs": object_refs}

    def _serialize_constraint_value(self, value, prop, object_refs, seen_refs):
        if prop.type == "POINTER":
            if value is None:
                return None
            if hasattr(value, "name"):
                key = (prop.identifier, value.name)
                if key not in seen_refs:
                    seen_refs.add(key)
                    object_refs.append({"property": prop.identifier, "object_name": value.name})
                return value.name
            return str(value)

        if prop.type == "COLLECTION":
            items = []
            try:
                for item in value:
                    items.append(self._serialize_constraint_collection_item(item))
            except Exception:
                return []
            return items

        return self._serialize_simple_value(value)

    def _serialize_constraint_collection_item(self, item):
        if hasattr(item, "target"):
            target = getattr(item, "target", None)
            entry = {"target": target.name if target else None}
            subtarget = getattr(item, "subtarget", None)
            if subtarget:
                entry["subtarget"] = subtarget
            if hasattr(item, "weight"):
                entry["weight"] = round(float(item.weight), 6)
            return entry

        if hasattr(item, "name"):
            return item.name

        return self._serialize_simple_value(item)

    def _serialize_simple_value(self, value):
        if isinstance(value, bool):
            return bool(value)
        if isinstance(value, int):
            return int(value)
        if isinstance(value, float):
            return round(float(value), 6)
        if isinstance(value, str):
            return value
        if isinstance(value, set):
            return sorted(value)
        if hasattr(value, "__iter__"):
            try:
                return [self._serialize_simple_value(v) for v in value]
            except Exception:
                pass
        if hasattr(value, "x") and hasattr(value, "y"):
            coords = [value.x, value.y]
            if hasattr(value, "z"):
                coords.append(value.z)
            if hasattr(value, "w"):
                coords.append(value.w)
            return [round(float(c), 6) for c in coords]
        if hasattr(value, "name"):
            return value.name
        return str(value)
