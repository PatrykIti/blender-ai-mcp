from typing import List, Optional
from server.domain.interfaces.rpc import IRpcClient
from server.domain.tools.text import ITextTool


class TextToolHandler(ITextTool):
    """Application service for Text operations."""

    def __init__(self, rpc_client: IRpcClient):
        self.rpc = rpc_client

    # TASK-034-1: text_create
    def create(
        self,
        text: str = "Text",
        name: str = "Text",
        location: Optional[List[float]] = None,
        font: Optional[str] = None,
        size: float = 1.0,
        extrude: float = 0.0,
        bevel_depth: float = 0.0,
        bevel_resolution: int = 0,
        align_x: str = "LEFT",
        align_y: str = "BOTTOM_BASELINE",
    ) -> str:
        args = {
            "text": text,
            "name": name,
            "size": size,
            "extrude": extrude,
            "bevel_depth": bevel_depth,
            "bevel_resolution": bevel_resolution,
            "align_x": align_x,
            "align_y": align_y,
        }
        if location:
            args["location"] = location
        if font:
            args["font"] = font

        response = self.rpc.send_request("text.create", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-034-2: text_edit
    def edit(
        self,
        object_name: str,
        text: Optional[str] = None,
        size: Optional[float] = None,
        extrude: Optional[float] = None,
        bevel_depth: Optional[float] = None,
        bevel_resolution: Optional[int] = None,
        align_x: Optional[str] = None,
        align_y: Optional[str] = None,
    ) -> str:
        args = {"object_name": object_name}
        if text is not None:
            args["text"] = text
        if size is not None:
            args["size"] = size
        if extrude is not None:
            args["extrude"] = extrude
        if bevel_depth is not None:
            args["bevel_depth"] = bevel_depth
        if bevel_resolution is not None:
            args["bevel_resolution"] = bevel_resolution
        if align_x is not None:
            args["align_x"] = align_x
        if align_y is not None:
            args["align_y"] = align_y

        response = self.rpc.send_request("text.edit", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    # TASK-034-3: text_to_mesh
    def to_mesh(
        self,
        object_name: str,
        keep_original: bool = False,
    ) -> str:
        args = {
            "object_name": object_name,
            "keep_original": keep_original,
        }
        response = self.rpc.send_request("text.to_mesh", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result
