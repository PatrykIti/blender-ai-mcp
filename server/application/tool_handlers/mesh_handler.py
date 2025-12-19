from typing import List, Optional
from server.domain.interfaces.rpc import IRpcClient
from server.domain.tools.mesh import IMeshTool

class MeshToolHandler(IMeshTool):
    def __init__(self, rpc_client: IRpcClient):
        self.rpc = rpc_client

    def select_all(self, deselect: bool = False) -> str:
        response = self.rpc.send_request("mesh.select_all", {"deselect": deselect})
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def delete_selected(self, type: str = 'VERT') -> str:
        response = self.rpc.send_request("mesh.delete_selected", {"type": type})
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def select_by_index(self, indices: List[int], type: str = 'VERT', selection_mode: str = 'SET') -> str:
        response = self.rpc.send_request("mesh.select_by_index", {"indices": indices, "type": type, "selection_mode": selection_mode})
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def extrude_region(self, move: List[float] = None) -> str:
        args = {"move": move} if move else {}
        response = self.rpc.send_request("mesh.extrude_region", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def fill_holes(self) -> str:
        response = self.rpc.send_request("mesh.fill_holes")
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def bevel(self, offset: float, segments: int = 1, profile: float = 0.5, affect: str = 'EDGES') -> str:
        args = {"offset": offset, "segments": segments, "profile": profile, "affect": affect}
        response = self.rpc.send_request("mesh.bevel", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def loop_cut(self, number_cuts: int = 1, smoothness: float = 0.0) -> str:
        args = {"number_cuts": number_cuts, "smoothness": smoothness}
        response = self.rpc.send_request("mesh.loop_cut", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def inset(self, thickness: float, depth: float = 0.0) -> str:
        args = {"thickness": thickness, "depth": depth}
        response = self.rpc.send_request("mesh.inset", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def boolean(self, operation: str, solver: str = 'FAST') -> str:
        args = {"operation": operation, "solver": solver}
        response = self.rpc.send_request("mesh.boolean", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def merge_by_distance(self, distance: float = 0.001) -> str:
        args = {"distance": distance}
        response = self.rpc.send_request("mesh.merge_by_distance", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def subdivide(self, number_cuts: int = 1, smoothness: float = 0.0) -> str:
        args = {"number_cuts": number_cuts, "smoothness": smoothness}
        response = self.rpc.send_request("mesh.subdivide", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def smooth_vertices(self, iterations: int = 1, factor: float = 0.5) -> str:
        args = {"iterations": iterations, "factor": factor}
        response = self.rpc.send_request("mesh.smooth_vertices", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def flatten_vertices(self, axis: str) -> str:
        args = {"axis": axis}
        response = self.rpc.send_request("mesh.flatten_vertices", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def list_groups(self, object_name: str, group_type: str = 'VERTEX') -> dict:
        args = {"object_name": object_name, "group_type": group_type}
        response = self.rpc.send_request("mesh.list_groups", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def select_loop(self, edge_index: int) -> str:
        args = {"edge_index": edge_index}
        response = self.rpc.send_request("mesh.select_loop", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def select_ring(self, edge_index: int) -> str:
        args = {"edge_index": edge_index}
        response = self.rpc.send_request("mesh.select_ring", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def select_linked(self) -> str:
        response = self.rpc.send_request("mesh.select_linked")
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def select_more(self) -> str:
        response = self.rpc.send_request("mesh.select_more")
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def select_less(self) -> str:
        response = self.rpc.send_request("mesh.select_less")
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def get_vertex_data(self, object_name: str, selected_only: bool = False) -> dict:
        args = {"object_name": object_name, "selected_only": selected_only}
        response = self.rpc.send_request("mesh.get_vertex_data", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def get_edge_data(self, object_name: str, selected_only: bool = False) -> dict:
        args = {"object_name": object_name, "selected_only": selected_only}
        response = self.rpc.send_request("mesh.get_edge_data", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def get_face_data(self, object_name: str, selected_only: bool = False) -> dict:
        args = {"object_name": object_name, "selected_only": selected_only}
        response = self.rpc.send_request("mesh.get_face_data", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def get_uv_data(
        self,
        object_name: str,
        uv_layer: Optional[str] = None,
        selected_only: bool = False
    ) -> dict:
        args = {"object_name": object_name, "selected_only": selected_only}
        if uv_layer is not None:
            args["uv_layer"] = uv_layer
        response = self.rpc.send_request("mesh.get_uv_data", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def select_by_location(self, axis: str, min_coord: float, max_coord: float, mode: str = 'VERT') -> str:
        args = {"axis": axis, "min_coord": min_coord, "max_coord": max_coord, "mode": mode}
        response = self.rpc.send_request("mesh.select_by_location", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def select_boundary(self, mode: str = 'EDGE') -> str:
        args = {"mode": mode}
        response = self.rpc.send_request("mesh.select_boundary", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-016-1: Mesh Randomize Tool
    def randomize(self, amount: float = 0.1, uniform: float = 0.0, normal: float = 0.0, seed: int = 0) -> str:
        args = {"amount": amount, "uniform": uniform, "normal": normal, "seed": seed}
        response = self.rpc.send_request("mesh.randomize", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-016-2: Mesh Shrink/Fatten Tool
    def shrink_fatten(self, value: float) -> str:
        args = {"value": value}
        response = self.rpc.send_request("mesh.shrink_fatten", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-017-1: Mesh Create Vertex Group Tool
    def create_vertex_group(self, object_name: str, name: str) -> str:
        args = {"object_name": object_name, "name": name}
        response = self.rpc.send_request("mesh.create_vertex_group", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-017-2: Mesh Assign/Remove Vertex Group Tools
    def assign_to_group(self, object_name: str, group_name: str, weight: float = 1.0) -> str:
        args = {"object_name": object_name, "group_name": group_name, "weight": weight}
        response = self.rpc.send_request("mesh.assign_to_group", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def remove_from_group(self, object_name: str, group_name: str) -> str:
        args = {"object_name": object_name, "group_name": group_name}
        response = self.rpc.send_request("mesh.remove_from_group", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-018-1: Mesh Bisect Tool
    def bisect(self, plane_co: list, plane_no: list, clear_inner: bool = False, clear_outer: bool = False, fill: bool = False) -> str:
        args = {
            "plane_co": plane_co,
            "plane_no": plane_no,
            "clear_inner": clear_inner,
            "clear_outer": clear_outer,
            "fill": fill
        }
        response = self.rpc.send_request("mesh.bisect", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-018-2: Mesh Edge/Vertex Slide Tools
    def edge_slide(self, value: float = 0.0) -> str:
        args = {"value": value}
        response = self.rpc.send_request("mesh.edge_slide", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def vert_slide(self, value: float = 0.0) -> str:
        args = {"value": value}
        response = self.rpc.send_request("mesh.vert_slide", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-018-3: Mesh Triangulate Tool
    def triangulate(self) -> str:
        response = self.rpc.send_request("mesh.triangulate")
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-018-4: Mesh Remesh Voxel Tool
    def remesh_voxel(self, voxel_size: float = 0.1, adaptivity: float = 0.0) -> str:
        args = {"voxel_size": voxel_size, "adaptivity": adaptivity}
        response = self.rpc.send_request("mesh.remesh_voxel", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-019-1: Mesh Transform Selected Tool
    def transform_selected(
        self,
        translate: list = None,
        rotate: list = None,
        scale: list = None,
        pivot: str = 'MEDIAN_POINT'
    ) -> str:
        args = {"pivot": pivot}
        if translate:
            args["translate"] = translate
        if rotate:
            args["rotate"] = rotate
        if scale:
            args["scale"] = scale
        response = self.rpc.send_request("mesh.transform_selected", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-019-2: Mesh Bridge Edge Loops Tool
    def bridge_edge_loops(
        self,
        number_cuts: int = 0,
        interpolation: str = 'LINEAR',
        smoothness: float = 0.0,
        twist: int = 0
    ) -> str:
        args = {
            "number_cuts": number_cuts,
            "interpolation": interpolation,
            "smoothness": smoothness,
            "twist": twist
        }
        response = self.rpc.send_request("mesh.bridge_edge_loops", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-019-3: Mesh Duplicate Selected Tool
    def duplicate_selected(self, translate: list = None) -> str:
        args = {}
        if translate:
            args["translate"] = translate
        response = self.rpc.send_request("mesh.duplicate_selected", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-021-3: Mesh Spin Tool
    def spin(
        self,
        steps: int = 12,
        angle: float = 6.283185,
        axis: str = 'Z',
        center: list = None,
        dupli: bool = False
    ) -> str:
        args = {
            "steps": steps,
            "angle": angle,
            "axis": axis,
            "dupli": dupli
        }
        if center:
            args["center"] = center
        response = self.rpc.send_request("mesh.spin", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-021-4: Mesh Screw Tool
    def screw(
        self,
        steps: int = 12,
        turns: int = 1,
        axis: str = 'Z',
        center: list = None,
        offset: float = 0.0
    ) -> str:
        args = {
            "steps": steps,
            "turns": turns,
            "axis": axis,
            "offset": offset
        }
        if center:
            args["center"] = center
        response = self.rpc.send_request("mesh.screw", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-021-5: Mesh Add Geometry Tools
    def add_vertex(self, position: list) -> str:
        args = {"position": position}
        response = self.rpc.send_request("mesh.add_vertex", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def add_edge_face(self) -> str:
        response = self.rpc.send_request("mesh.add_edge_face")
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-029-1: Mesh Edge Crease Tool
    def edge_crease(self, crease_value: float = 1.0) -> str:
        args = {"crease_value": crease_value}
        response = self.rpc.send_request("mesh.edge_crease", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-029-2: Mesh Bevel Weight Tool
    def bevel_weight(self, weight: float = 1.0) -> str:
        args = {"weight": weight}
        response = self.rpc.send_request("mesh.bevel_weight", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-029-3: Mesh Mark Sharp Tool
    def mark_sharp(self, action: str = "mark") -> str:
        args = {"action": action}
        response = self.rpc.send_request("mesh.mark_sharp", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-030-1: Mesh Dissolve Tool
    def dissolve(
        self,
        dissolve_type: str = "limited",
        angle_limit: float = 5.0,
        use_face_split: bool = False,
        use_boundary_tear: bool = False
    ) -> str:
        args = {
            "dissolve_type": dissolve_type,
            "angle_limit": angle_limit,
            "use_face_split": use_face_split,
            "use_boundary_tear": use_boundary_tear
        }
        response = self.rpc.send_request("mesh.dissolve", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-030-2: Mesh Tris To Quads Tool
    def tris_to_quads(
        self,
        face_threshold: float = 40.0,
        shape_threshold: float = 40.0
    ) -> str:
        args = {
            "face_threshold": face_threshold,
            "shape_threshold": shape_threshold
        }
        response = self.rpc.send_request("mesh.tris_to_quads", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-030-3: Mesh Normals Make Consistent Tool
    def normals_make_consistent(self, inside: bool = False) -> str:
        args = {"inside": inside}
        response = self.rpc.send_request("mesh.normals_make_consistent", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-030-4: Mesh Decimate Tool
    def decimate(
        self,
        ratio: float = 0.5,
        use_symmetry: bool = False,
        symmetry_axis: str = "X"
    ) -> str:
        args = {
            "ratio": ratio,
            "use_symmetry": use_symmetry,
            "symmetry_axis": symmetry_axis
        }
        response = self.rpc.send_request("mesh.decimate", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-032-1: Mesh Knife Project Tool
    def knife_project(self, cut_through: bool = True) -> str:
        args = {"cut_through": cut_through}
        response = self.rpc.send_request("mesh.knife_project", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-032-2: Mesh Rip Tool
    def rip(self, use_fill: bool = False) -> str:
        args = {"use_fill": use_fill}
        response = self.rpc.send_request("mesh.rip", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-032-3: Mesh Split Tool
    def split(self) -> str:
        response = self.rpc.send_request("mesh.split")
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-032-4: Mesh Edge Split Tool
    def edge_split(self) -> str:
        response = self.rpc.send_request("mesh.edge_split")
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-038-5: Proportional Editing
    def set_proportional_edit(
        self,
        enabled: bool = True,
        falloff_type: str = "SMOOTH",
        size: float = 1.0,
        use_connected: bool = False,
    ) -> str:
        """Configures proportional editing settings."""
        args = {
            "enabled": enabled,
            "falloff_type": falloff_type,
            "size": size,
            "use_connected": use_connected,
        }
        response = self.rpc.send_request("mesh.set_proportional_edit", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-036-1: Mesh Symmetrize Tool
    def symmetrize(self, direction: str = "NEGATIVE_X", threshold: float = 0.0001) -> str:
        args = {"direction": direction, "threshold": threshold}
        response = self.rpc.send_request("mesh.symmetrize", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-036-2: Mesh Grid Fill Tool
    def grid_fill(self, span: int = 1, offset: int = 0, use_interp_simple: bool = False) -> str:
        args = {"span": span, "offset": offset, "use_interp_simple": use_interp_simple}
        response = self.rpc.send_request("mesh.grid_fill", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-036-3: Mesh Poke Faces Tool
    def poke_faces(self, offset: float = 0.0, use_relative_offset: bool = False, center_mode: str = "MEDIAN_WEIGHTED") -> str:
        args = {"offset": offset, "use_relative_offset": use_relative_offset, "center_mode": center_mode}
        response = self.rpc.send_request("mesh.poke_faces", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-036-4: Mesh Beautify Fill Tool
    def beautify_fill(self, angle_limit: float = 180.0) -> str:
        args = {"angle_limit": angle_limit}
        response = self.rpc.send_request("mesh.beautify_fill", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-036-5: Mesh Mirror Tool
    def mirror(self, axis: str = "X", use_mirror_merge: bool = True, merge_threshold: float = 0.001) -> str:
        args = {"axis": axis, "use_mirror_merge": use_mirror_merge, "merge_threshold": merge_threshold}
        response = self.rpc.send_request("mesh.mirror", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result
