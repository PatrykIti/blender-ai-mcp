from typing import Any, Dict, List, Optional

from server.application.tool_handlers._rpc_utils import (
    require_dict_result,
    require_list_of_dicts_result,
    require_str_result,
)
from server.domain.interfaces.rpc import IRpcClient
from server.domain.tools.collection import ICollectionTool


class CollectionToolHandler(ICollectionTool):
    def __init__(self, rpc_client: IRpcClient):
        self.rpc = rpc_client

    def list_collections(self, include_objects: bool = False) -> List[Dict[str, Any]]:
        return require_list_of_dicts_result(
            self.rpc.send_request("collection.list", {"include_objects": include_objects})
        )

    def list_objects(
        self, collection_name: str, recursive: bool = True, include_hidden: bool = False
    ) -> Dict[str, Any]:
        args = {"collection_name": collection_name, "recursive": recursive, "include_hidden": include_hidden}
        return require_dict_result(self.rpc.send_request("collection.list_objects", args))

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

        return require_str_result(self.rpc.send_request("collection.manage", args))
