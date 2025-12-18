"""Extraction Analysis Handler (TASK-044).

Provides deep topology analysis, component detection, symmetry detection,
and multi-angle rendering for the Automatic Workflow Extraction System.
"""
import math
import os
from collections import defaultdict

import bpy
import bmesh
from mathutils import Vector, Euler
from mathutils.kdtree import KDTree


class ExtractionHandler:
    """Application service for extraction analysis operations."""

    # Base primitive detection thresholds
    CUBE_VERTEX_COUNT = 8
    CUBE_FACE_COUNT = 6

    # Angle presets for render_angles (camera location relative to object center)
    ANGLE_PRESETS = {
        "front": {"rotation": (math.pi / 2, 0, 0)},
        "back": {"rotation": (math.pi / 2, 0, math.pi)},
        "left": {"rotation": (math.pi / 2, 0, -math.pi / 2)},
        "right": {"rotation": (math.pi / 2, 0, math.pi / 2)},
        "top": {"rotation": (0, 0, 0)},
        "iso": {"rotation": (math.pi / 4, 0, math.pi / 4)},
    }

    def deep_topology(self, object_name: str) -> dict:
        """Extended topology analysis for workflow extraction.

        Args:
            object_name: Name of the mesh object to analyze.

        Returns:
            Dict with extended topology data.
        """
        if object_name not in bpy.data.objects:
            raise ValueError(f"Object '{object_name}' not found")

        obj = bpy.data.objects[object_name]
        if obj.type != 'MESH':
            raise ValueError(f"Object '{object_name}' is not a mesh (type: {obj.type})")

        # Create bmesh for analysis
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        # Basic counts
        vert_count = len(bm.verts)
        edge_count = len(bm.edges)
        face_count = len(bm.faces)

        # Face type counts
        tri_count = 0
        quad_count = 0
        ngon_count = 0
        for face in bm.faces:
            vert_num = len(face.verts)
            if vert_num == 3:
                tri_count += 1
            elif vert_num == 4:
                quad_count += 1
            else:
                ngon_count += 1

        # Boundary edge count
        boundary_edges = sum(1 for e in bm.edges if e.is_boundary)

        # Manifold check
        non_manifold_edges = sum(1 for e in bm.edges if not e.is_manifold)

        # Estimate base primitive
        base_primitive, primitive_confidence = self._detect_base_primitive(
            bm, vert_count, edge_count, face_count, obj
        )

        # Detect features
        has_beveled_edges = self._detect_beveled_edges(bm)
        has_inset_faces = self._detect_inset_faces(bm)
        has_extrusions = self._detect_extrusions(bm, obj)

        # Edge loop estimate (simplified: count edges with exactly 4 connected faces)
        edge_loop_candidates = sum(
            1 for e in bm.edges
            if len(e.link_faces) == 2 and all(len(f.verts) == 4 for f in e.link_faces)
        )

        # Bounding box
        bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        min_corner = Vector((
            min(c.x for c in bbox_corners),
            min(c.y for c in bbox_corners),
            min(c.z for c in bbox_corners)
        ))
        max_corner = Vector((
            max(c.x for c in bbox_corners),
            max(c.y for c in bbox_corners),
            max(c.z for c in bbox_corners)
        ))
        dimensions = max_corner - min_corner

        bm.free()

        return {
            "object_name": object_name,
            "vertex_count": vert_count,
            "edge_count": edge_count,
            "face_count": face_count,
            "tri_count": tri_count,
            "quad_count": quad_count,
            "ngon_count": ngon_count,
            "boundary_edges": boundary_edges,
            "non_manifold_edges": non_manifold_edges,
            "edge_loop_candidates": edge_loop_candidates,
            "base_primitive": base_primitive,
            "primitive_confidence": round(primitive_confidence, 2),
            "has_beveled_edges": has_beveled_edges,
            "has_inset_faces": has_inset_faces,
            "has_extrusions": has_extrusions,
            "bounding_box": {
                "min": [round(v, 4) for v in min_corner],
                "max": [round(v, 4) for v in max_corner],
                "dimensions": [round(v, 4) for v in dimensions]
            }
        }

    def _detect_base_primitive(self, bm, vert_count, edge_count, face_count, obj) -> tuple:
        """Detect the likely base primitive of the mesh."""
        # Calculate aspect ratios from bounding box
        dims = obj.dimensions

        # Plane detection: 4 verts, 1 face, very flat (check BEFORE zero-dim check)
        # Planes have one zero dimension, so we check this first
        if vert_count == 4 and face_count == 1:
            return "PLANE", 0.95

        # If all dimensions are zero (degenerate mesh)
        if dims.x == 0 and dims.y == 0 and dims.z == 0:
            return "CUSTOM", 0.0

        # Safe division with fallback for zero dimensions
        aspect_xy = dims.x / dims.y if dims.y > 0 else 1.0
        aspect_xz = dims.x / dims.z if dims.z > 0 else 1.0
        aspect_yz = dims.y / dims.z if dims.z > 0 else 1.0

        # Cube detection: 8 verts, 6 faces, roughly cubic proportions
        if vert_count == 8 and face_count == 6:
            if 0.8 <= aspect_xy <= 1.2 and 0.8 <= aspect_xz <= 1.2:
                return "CUBE", 0.95
            else:
                return "CUBE", 0.7  # Box shape but not cubic

        # Cylinder detection: many verts, circular cross-section
        if vert_count >= 12 and face_count >= 3:
            # Check for circular distribution of vertices
            z_levels = defaultdict(list)
            for v in bm.verts:
                z_key = round(v.co.z, 2)
                z_levels[z_key].append(v)

            # Cylinder typically has 2-3 distinct z levels with many verts each
            if len(z_levels) <= 4:
                for level_verts in z_levels.values():
                    if len(level_verts) >= 8:
                        # Check circularity
                        center = sum((v.co for v in level_verts), Vector()) / len(level_verts)
                        distances = [((v.co - center).length) for v in level_verts]
                        if distances:
                            avg_dist = sum(distances) / len(distances)
                            variance = sum((d - avg_dist) ** 2 for d in distances) / len(distances)
                            if variance < 0.01:  # Low variance = circular
                                return "CYLINDER", 0.8

        # Sphere detection: high vert count, all equidistant from center
        if vert_count >= 32:
            center = sum((v.co for v in bm.verts), Vector()) / vert_count
            distances = [(v.co - center).length for v in bm.verts]
            avg_dist = sum(distances) / len(distances)
            variance = sum((d - avg_dist) ** 2 for d in distances) / len(distances)
            if variance < 0.01:
                return "SPHERE", 0.8

        # Default to custom
        return "CUSTOM", 0.0

    def _detect_beveled_edges(self, bm) -> bool:
        """Detect if mesh has beveled edges (extra edge loops between surfaces)."""
        # Look for edges where connected faces have very similar normals
        # and the edge itself is part of a narrow strip
        bevel_candidates = 0
        for edge in bm.edges:
            if len(edge.link_faces) == 2:
                f1, f2 = edge.link_faces
                angle = f1.normal.angle(f2.normal)
                # Beveled edges often have small angles between faces (chamfer)
                if 0.1 < angle < 0.8:  # ~6° to ~46°
                    bevel_candidates += 1

        # If more than 10% of edges show bevel characteristics
        return bevel_candidates > len(bm.edges) * 0.1 if bm.edges else False

    def _detect_inset_faces(self, bm) -> bool:
        """Detect if mesh has inset faces (faces surrounded by thin quad borders)."""
        # Look for faces that are surrounded by quads with small area ratio
        for face in bm.faces:
            if len(face.verts) == 4:
                # Check adjacent faces
                adjacent_faces = set()
                for edge in face.edges:
                    for f in edge.link_faces:
                        if f != face:
                            adjacent_faces.add(f)

                if len(adjacent_faces) == 4:  # Surrounded by 4 faces
                    # Check if surrounding faces are smaller (thin border)
                    face_area = face.calc_area()
                    border_areas = [f.calc_area() for f in adjacent_faces]
                    if border_areas:
                        avg_border = sum(border_areas) / len(border_areas)
                        if avg_border < face_area * 0.5:  # Border is thin
                            return True
        return False

    def _detect_extrusions(self, bm, obj) -> bool:
        """Detect if mesh has extruded regions (face groups at different heights)."""
        # Group faces by their center Z coordinate
        z_groups = defaultdict(list)
        for face in bm.faces:
            center_z = round(face.calc_center_median().z, 2)
            z_groups[center_z].append(face)

        # Multiple distinct Z levels with faces indicate extrusions
        return len(z_groups) > 2

    def component_separate(self, object_name: str, min_vertex_count: int = 4) -> dict:
        """Separates mesh into loose parts (components).

        Args:
            object_name: Name of the mesh object to separate.
            min_vertex_count: Minimum vertices to keep component.

        Returns:
            Dict with component names and stats.
        """
        if object_name not in bpy.data.objects:
            raise ValueError(f"Object '{object_name}' not found")

        obj = bpy.data.objects[object_name]
        if obj.type != 'MESH':
            raise ValueError(f"Object '{object_name}' is not a mesh (type: {obj.type})")

        # Store original object count
        original_count = len(bpy.data.objects)

        # Ensure object mode
        if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # Deselect all, select target
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        # Enter edit mode, select all, separate by loose parts
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.separate(type='LOOSE')
        bpy.ops.object.mode_set(mode='OBJECT')

        # Find all components (objects with similar names)
        components = []
        objects_to_delete = []

        for o in bpy.data.objects:
            if o.name == object_name or o.name.startswith(object_name + "."):
                if o.type == 'MESH':
                    vert_count = len(o.data.vertices)
                    if vert_count >= min_vertex_count:
                        components.append({
                            "name": o.name,
                            "vertex_count": vert_count,
                            "face_count": len(o.data.polygons)
                        })
                    else:
                        objects_to_delete.append(o)

        # Delete tiny components
        for o in objects_to_delete:
            bpy.data.objects.remove(o, do_unlink=True)

        return {
            "original_object": object_name,
            "component_count": len(components),
            "components": components,
            "deleted_small_components": len(objects_to_delete)
        }

    def detect_symmetry(self, object_name: str, tolerance: float = 0.001) -> dict:
        """Detects symmetry planes in mesh geometry.

        Args:
            object_name: Name of the mesh object to analyze.
            tolerance: Distance tolerance for symmetry matching.

        Returns:
            Dict with symmetry info for each axis.
        """
        if object_name not in bpy.data.objects:
            raise ValueError(f"Object '{object_name}' not found")

        obj = bpy.data.objects[object_name]
        if obj.type != 'MESH':
            raise ValueError(f"Object '{object_name}' is not a mesh (type: {obj.type})")

        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.verts.ensure_lookup_table()

        vert_count = len(bm.verts)
        if vert_count == 0:
            bm.free()
            return {
                "object_name": object_name,
                "x_symmetric": False, "x_confidence": 0.0,
                "y_symmetric": False, "y_confidence": 0.0,
                "z_symmetric": False, "z_confidence": 0.0,
                "total_vertices": 0
            }

        # Build KD-tree for efficient spatial lookup
        kd = KDTree(vert_count)
        for i, v in enumerate(bm.verts):
            kd.insert(v.co, i)
        kd.balance()

        # Check symmetry for each axis
        def check_axis_symmetry(flip_index):
            matches = 0
            for v in bm.verts:
                mirror_co = list(v.co)
                mirror_co[flip_index] = -mirror_co[flip_index]
                mirror_co = Vector(mirror_co)

                _, _, dist = kd.find(mirror_co)
                if dist is not None and dist < tolerance:
                    matches += 1
            return matches / vert_count if vert_count > 0 else 0.0

        x_confidence = check_axis_symmetry(0)  # Mirror X
        y_confidence = check_axis_symmetry(1)  # Mirror Y
        z_confidence = check_axis_symmetry(2)  # Mirror Z

        # Threshold for "symmetric" (80% of vertices have mirrors)
        threshold = 0.8

        bm.free()

        return {
            "object_name": object_name,
            "x_symmetric": x_confidence >= threshold,
            "x_confidence": round(x_confidence, 3),
            "y_symmetric": y_confidence >= threshold,
            "y_confidence": round(y_confidence, 3),
            "z_symmetric": z_confidence >= threshold,
            "z_confidence": round(z_confidence, 3),
            "total_vertices": vert_count,
            "tolerance": tolerance
        }

    def edge_loop_analysis(self, object_name: str) -> dict:
        """Analyzes edge loops for feature detection.

        Args:
            object_name: Name of the mesh object to analyze.

        Returns:
            Dict with edge loop analysis.
        """
        if object_name not in bpy.data.objects:
            raise ValueError(f"Object '{object_name}' not found")

        obj = bpy.data.objects[object_name]
        if obj.type != 'MESH':
            raise ValueError(f"Object '{object_name}' is not a mesh (type: {obj.type})")

        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.edges.ensure_lookup_table()

        # Count edge types
        boundary_count = 0
        manifold_count = 0
        non_manifold_count = 0

        for edge in bm.edges:
            if edge.is_boundary:
                boundary_count += 1
            elif edge.is_manifold:
                manifold_count += 1
            else:
                non_manifold_count += 1

        # Detect parallel edge loops by analyzing edge directions
        edge_directions = defaultdict(list)
        for edge in bm.edges:
            if len(edge.verts) == 2:
                direction = (edge.verts[1].co - edge.verts[0].co).normalized()
                # Quantize direction to detect parallel groups
                key = (
                    round(abs(direction.x), 1),
                    round(abs(direction.y), 1),
                    round(abs(direction.z), 1)
                )
                edge_directions[key].append(edge)

        # Find groups of parallel edges (potential edge loops)
        parallel_groups = []
        for key, edges in edge_directions.items():
            if len(edges) >= 4:  # Minimum for a loop
                parallel_groups.append({
                    "direction": list(key),
                    "edge_count": len(edges)
                })

        # Estimate support loops (edges near corners with many connected faces)
        support_loop_candidates = 0
        for edge in bm.edges:
            if len(edge.link_faces) >= 2:
                # Check if this is a "support" edge (between two different face normals)
                normals = [f.normal for f in edge.link_faces]
                if len(normals) >= 2:
                    angle = normals[0].angle(normals[1])
                    if 0.3 < angle < 1.2:  # ~17° to ~69°
                        support_loop_candidates += 1

        # Detect chamfered edges (small bevels)
        chamfer_edges = 0
        for edge in bm.edges:
            if len(edge.link_faces) == 2:
                f1, f2 = edge.link_faces
                angle = f1.normal.angle(f2.normal)
                if 0.05 < angle < 0.3:  # Very small angle (chamfer)
                    chamfer_edges += 1

        # Calculate total edges before freeing bmesh
        total_edges = boundary_count + manifold_count + non_manifold_count

        bm.free()

        return {
            "object_name": object_name,
            "total_edges": total_edges,
            "boundary_edges": boundary_count,
            "manifold_edges": manifold_count,
            "non_manifold_edges": non_manifold_count,
            "parallel_edge_groups": len(parallel_groups),
            "parallel_groups_detail": parallel_groups[:5],  # Top 5
            "support_loop_candidates": support_loop_candidates,
            "chamfer_edges": chamfer_edges,
            "has_chamfer": chamfer_edges > 0,
            "estimated_bevel_segments": min(3, chamfer_edges // 4) if chamfer_edges > 0 else 0
        }

    def face_group_analysis(self, object_name: str, angle_threshold: float = 5.0) -> dict:
        """Analyzes face groups for feature detection.

        Args:
            object_name: Name of the mesh object to analyze.
            angle_threshold: Max angle difference for coplanar grouping (degrees).

        Returns:
            Dict with face group analysis.
        """
        if object_name not in bpy.data.objects:
            raise ValueError(f"Object '{object_name}' not found")

        obj = bpy.data.objects[object_name]
        if obj.type != 'MESH':
            raise ValueError(f"Object '{object_name}' is not a mesh (type: {obj.type})")

        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.faces.ensure_lookup_table()

        angle_rad = math.radians(angle_threshold)

        # Group faces by normal direction
        normal_groups = defaultdict(list)
        for face in bm.faces:
            # Quantize normal for grouping
            n = face.normal
            key = (
                round(n.x, 1),
                round(n.y, 1),
                round(n.z, 1)
            )
            normal_groups[key].append(face)

        # Group faces by Z height
        height_groups = defaultdict(list)
        for face in bm.faces:
            center_z = round(face.calc_center_median().z, 2)
            height_groups[center_z].append(face)

        # Build face groups with analysis
        face_groups = []
        for i, (key, faces) in enumerate(normal_groups.items()):
            avg_height = sum(f.calc_center_median().z for f in faces) / len(faces)
            total_area = sum(f.calc_area() for f in faces)

            face_groups.append({
                "id": i,
                "normal": list(key),
                "face_count": len(faces),
                "avg_height": round(avg_height, 3),
                "total_area": round(total_area, 4)
            })

        # Detect inset faces
        detected_insets = 0
        for face in bm.faces:
            if len(face.verts) == 4:
                # Check if surrounded by thin borders
                adjacent = set()
                for edge in face.edges:
                    for f in edge.link_faces:
                        if f != face:
                            adjacent.add(f)

                if len(adjacent) >= 3:
                    face_area = face.calc_area()
                    avg_adjacent_area = sum(f.calc_area() for f in adjacent) / len(adjacent)
                    if avg_adjacent_area < face_area * 0.4:
                        detected_insets += 1

        # Detect extrusions (multiple height levels with same normal)
        detected_extrusions = 0
        for key, faces in normal_groups.items():
            z_values = set(round(f.calc_center_median().z, 2) for f in faces)
            if len(z_values) > 1:
                detected_extrusions += len(z_values) - 1

        height_levels = sorted(set(height_groups.keys()))

        # Calculate total faces before freeing bmesh
        total_faces = len(bm.faces)

        bm.free()

        return {
            "object_name": object_name,
            "total_faces": total_faces,
            "face_groups": face_groups[:10],  # Top 10 groups
            "normal_group_count": len(normal_groups),
            "height_level_count": len(height_levels),
            "height_levels": height_levels[:10],
            "detected_insets": detected_insets,
            "detected_extrusions": detected_extrusions,
            "has_insets": detected_insets > 0,
            "has_extrusions": detected_extrusions > 0
        }

    def render_angles(
        self,
        object_name: str,
        angles: list = None,
        resolution: int = 512,
        output_dir: str = "/tmp/extraction_renders"
    ) -> dict:
        """Renders object from multiple angles for LLM Vision analysis.

        Args:
            object_name: Object to render.
            angles: List of angle names to render.
            resolution: Image resolution in pixels.
            output_dir: Directory to save renders.

        Returns:
            Dict with render paths.
        """
        if object_name not in bpy.data.objects:
            raise ValueError(f"Object '{object_name}' not found")

        obj = bpy.data.objects[object_name]

        if angles is None:
            angles = ["front", "back", "left", "right", "top", "iso"]

        # Validate angles
        valid_angles = set(self.ANGLE_PRESETS.keys())
        for angle in angles:
            if angle not in valid_angles:
                raise ValueError(f"Invalid angle '{angle}'. Valid: {valid_angles}")

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Calculate object center and size
        bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        center = sum(bbox_corners, Vector()) / 8
        max_dist = max((corner - center).length for corner in bbox_corners)
        camera_distance = max_dist * 3.0  # Distance from object

        # Create temporary camera
        cam_data = bpy.data.cameras.new("ExtractCam")
        cam_data.lens = 50
        cam_obj = bpy.data.objects.new("ExtractCam", cam_data)
        bpy.context.scene.collection.objects.link(cam_obj)

        # Store original visibility
        original_visibility = {}
        for o in bpy.data.objects:
            if o.type == 'MESH' and o != obj:
                original_visibility[o.name] = o.hide_render
                o.hide_render = True

        # Configure render settings
        scene = bpy.context.scene
        scene.camera = cam_obj
        scene.render.resolution_x = resolution
        scene.render.resolution_y = resolution
        scene.render.image_settings.file_format = 'PNG'

        renders = []

        try:
            for angle_name in angles:
                preset = self.ANGLE_PRESETS[angle_name]

                # Position camera
                rotation = Euler(preset["rotation"])

                # Calculate camera position based on angle
                if angle_name == "front":
                    cam_pos = center + Vector((0, -camera_distance, 0))
                elif angle_name == "back":
                    cam_pos = center + Vector((0, camera_distance, 0))
                elif angle_name == "left":
                    cam_pos = center + Vector((-camera_distance, 0, 0))
                elif angle_name == "right":
                    cam_pos = center + Vector((camera_distance, 0, 0))
                elif angle_name == "top":
                    cam_pos = center + Vector((0, 0, camera_distance))
                else:  # iso
                    offset = camera_distance / math.sqrt(3)
                    cam_pos = center + Vector((offset, -offset, offset))

                cam_obj.location = cam_pos
                cam_obj.rotation_euler = rotation

                # Point camera at object center
                direction = center - cam_pos
                cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

                # Render
                filepath = os.path.join(output_dir, f"{object_name}_{angle_name}.png")
                scene.render.filepath = filepath
                bpy.ops.render.render(write_still=True)

                renders.append({
                    "angle": angle_name,
                    "path": filepath
                })

        finally:
            # Restore visibility
            for name, was_hidden in original_visibility.items():
                if name in bpy.data.objects:
                    bpy.data.objects[name].hide_render = was_hidden

            # Remove temporary camera
            bpy.data.objects.remove(cam_obj, do_unlink=True)
            bpy.data.cameras.remove(cam_data)

        return {
            "object_name": object_name,
            "resolution": resolution,
            "output_dir": output_dir,
            "renders": renders
        }
