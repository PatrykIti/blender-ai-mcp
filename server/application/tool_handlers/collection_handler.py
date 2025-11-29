from typing import List, Dict, Any, Optional
from server.domain.interfaces.rpc import IRpcClient
from server.domain.tools.collection import ICollectionTool


class CollectionToolHandler(ICollectionTool):
    def __init__(self, rpc_client: IRpcClient):
        self.rpc = rpc_client

    def list_collections(self, include_objects: bool = False) -> List[Dict[str, Any]]:
        response = self.rpc.send_request("collection.list", {"include_objects": include_objects})
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def list_objects(self, collection_name: str, recursive: bool = True, include_hidden: bool = False) -> Dict[str, Any]:
        args = {
            "collection_name": collection_name,
            "recursive": recursive,
            "include_hidden": include_hidden
        }
        response = self.rpc.send_request("collection.list_objects", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result

    def manage_collection(
        self,
        action: str,
        collection_name: str,
        new_name: Optional[str] = None,
        parent_name: Optional[str] = None,
        object_name: Optional[str] = None,
    ) -> str:
        args = {
            "action": action,
            "collection_name": collection_name,
        }
        if new_name is not None:
            args["new_name"] = new_name
        if parent_name is not None:
            args["parent_name"] = parent_name
        if object_name is not None:
            args["object_name"] = object_name

        response = self.rpc.send_request("collection.manage", args)
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return response.result
