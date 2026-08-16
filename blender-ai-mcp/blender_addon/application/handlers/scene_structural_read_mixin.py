import hashlib
import json
from datetime import datetime, timezone

import bpy


class SceneStructuralReadMixin:
    """Snapshot and structural-read helpers for scene RPC methods."""

    def _vec_to_list(self, value):
        try:
            return [round(float(v), 4) for v in value]
        except Exception:
            return [float(value) if isinstance(value, (int, float)) else 0.0]

    def _gather_mesh_stats(self, obj):
        if obj.type != "MESH":
            return None

        mesh = None
        try:
            depsgraph = bpy.context.evaluated_depsgraph_get()
        except Exception:
            depsgraph = None

        obj_eval = obj
        if depsgraph is not None:
            try:
                obj_eval = obj.evaluated_get(depsgraph)
            except Exception:
                obj_eval = obj

        try:
            mesh = obj_eval.to_mesh()
        except Exception:
            mesh = getattr(obj_eval, "data", None)

        if mesh is None:
            return None

        stats = {
            "vertices": len(getattr(mesh, "vertices", [])),
            "edges": len(getattr(mesh, "edges", [])),
            "faces": len(getattr(mesh, "polygons", [])),
        }
        try:
            mesh.calc_loop_triangles()
            stats["triangles"] = len(getattr(mesh, "loop_triangles", []))
        except Exception:
            stats["triangles"] = None

        if hasattr(obj_eval, "to_mesh_clear"):
            try:
                obj_eval.to_mesh_clear()
            except Exception:
                pass

        return stats

    def snapshot_state(self, include_mesh_stats=False, include_materials=False):
        """Captures a lightweight JSON snapshot of the scene state."""

        objects_data = []
        for obj in sorted(bpy.context.scene.objects, key=lambda o: o.name):
            obj_data = {
                "name": obj.name,
                "type": obj.type,
                "location": self._vec_to_list(obj.location),
                "rotation": self._vec_to_list(obj.rotation_euler),
                "scale": self._vec_to_list(obj.scale),
                "parent": obj.parent.name if obj.parent else None,
                "visible": not bool(getattr(obj, "hide_viewport", False)),
                "selected": obj.select_get(),
                "collections": [col.name for col in obj.users_collection],
            }

            if obj.modifiers:
                obj_data["modifiers"] = [{"name": mod.name, "type": mod.type} for mod in obj.modifiers]
            if include_mesh_stats and obj.type == "MESH":
                mesh_stats = self._gather_mesh_stats(obj)
                if mesh_stats:
                    obj_data["mesh_stats"] = mesh_stats
            if include_materials and obj.material_slots:
                obj_data["materials"] = [slot.material.name if slot.material else None for slot in obj.material_slots]

            objects_data.append(obj_data)

        snapshot = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "object_count": len(objects_data),
            "objects": objects_data,
            "active_object": bpy.context.active_object.name if bpy.context.active_object else None,
            "mode": getattr(bpy.context, "mode", "UNKNOWN"),
        }

        state_for_hash = {
            "object_count": snapshot["object_count"],
            "objects": snapshot["objects"],
            "active_object": snapshot["active_object"],
            "mode": snapshot["mode"],
        }
        state_json = json.dumps(state_for_hash, sort_keys=True)
        snapshot_hash = hashlib.sha256(state_json.encode("utf-8")).hexdigest()
        return {"hash": snapshot_hash, "snapshot": snapshot}

    def _get_object_or_raise(self, object_name):
        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise ValueError(f"Object '{object_name}' not found")
        return obj

    def _get_bbox_data(self, obj, world_space=True):
        from mathutils import Vector

        corners = (
            [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
            if world_space
            else [Vector(corner) for corner in obj.bound_box]
        )
        min_corner = [float(min(corner[index] for corner in corners)) for index in range(3)]
        max_corner = [float(max(corner[index] for corner in corners)) for index in range(3)]
        center = [(min_corner[index] + max_corner[index]) / 2.0 for index in range(3)]
        dimensions = [max_corner[index] - min_corner[index] for index in range(3)]

        return {
            "min": min_corner,
            "max": max_corner,
            "center": center,
            "dimensions": dimensions,
            "corners": corners,
        }

    def get_hierarchy(self, object_name=None, include_transforms=False):
        """Gets parent-child hierarchy for objects."""

        def build_hierarchy(obj, include_transforms):
            node = {"name": obj.name, "type": obj.type, "children": []}

            if include_transforms:
                node["location"] = self._vec_to_list(obj.location)
                node["rotation"] = self._vec_to_list(obj.rotation_euler)
                node["scale"] = self._vec_to_list(obj.scale)

            for child in obj.children:
                node["children"].append(build_hierarchy(child, include_transforms))

            return node

        if object_name:
            obj = bpy.data.objects.get(object_name)
            if obj is None:
                raise ValueError(f"Object '{object_name}' not found")

            hierarchy = build_hierarchy(obj, include_transforms)
            parent_chain = []
            current = obj.parent
            while current:
                parent_chain.append(current.name)
                current = current.parent

            return {"root": hierarchy, "parent_chain": parent_chain}

        roots = []
        for obj in sorted(bpy.context.scene.objects, key=lambda o: o.name):
            if obj.parent is None:
                roots.append(build_hierarchy(obj, include_transforms))

        return {"root_count": len(roots), "hierarchy": roots}

    def _round_values(self, values, precision=6):
        return [round(float(value), precision) for value in values]

    def get_bounding_box(self, object_name, world_space=True):
        """Gets bounding box corners for an object."""
        obj = self._get_object_or_raise(object_name)
        bbox_data = self._get_bbox_data(obj, world_space=world_space)

        return {
            "object_name": object_name,
            "world_space": world_space,
            "min": self._round_values(bbox_data["min"], precision=4),
            "max": self._round_values(bbox_data["max"], precision=4),
            "center": self._round_values(bbox_data["center"], precision=4),
            "dimensions": self._round_values(bbox_data["dimensions"], precision=4),
            "corners": [self._round_values(corner, precision=4) for corner in bbox_data["corners"]],
        }

    def get_origin_info(self, object_name):
        """Gets origin (pivot point) information for an object."""
        import math

        obj = self._get_object_or_raise(object_name)
        origin = [float(obj.location[i]) for i in range(3)]
        bbox_data = self._get_bbox_data(obj, world_space=True)
        bbox_center = bbox_data["center"]
        offset_from_center = [origin[i] - bbox_center[i] for i in range(3)]

        origin_type = "CUSTOM"
        offset_magnitude = math.sqrt(sum(value * value for value in offset_from_center))
        if offset_magnitude < 0.001:
            origin_type = "CENTER"
        else:
            min_z = bbox_data["min"][2]
            if (
                abs(origin[2] - min_z) < 0.001
                and abs(offset_from_center[0]) < 0.001
                and abs(offset_from_center[1]) < 0.001
            ):
                origin_type = "BOTTOM_CENTER"

        return {
            "object_name": object_name,
            "origin_world": self._round_values(origin, precision=4),
            "bbox_center": self._round_values(bbox_center, precision=4),
            "offset_from_center": self._round_values(offset_from_center, precision=4),
            "estimated_type": origin_type,
        }
