from typing import Any, cast

from server.domain.models.rpc import RpcResponse


def require_result(response: RpcResponse) -> Any:
    """Return the RPC result after enforcing the established response contract."""
    if response.status == "error":
        raise RuntimeError(f"Blender Error: {response.error}")
    if response.result is None:
        raise RuntimeError("Blender Error: RPC response did not include a result payload")
    return response.result


def require_str_result(response: RpcResponse) -> str:
    result = require_result(response)
    if not isinstance(result, str):
        raise RuntimeError(f"Blender Error: Expected string result, got {type(result).__name__}")
    return result


def require_dict_result(response: RpcResponse) -> dict[str, Any]:
    result = require_result(response)
    if not isinstance(result, dict):
        raise RuntimeError(f"Blender Error: Expected object result, got {type(result).__name__}")
    return cast(dict[str, Any], result)


def require_list_result(response: RpcResponse) -> list[Any]:
    result = require_result(response)
    if not isinstance(result, list):
        raise RuntimeError(f"Blender Error: Expected list result, got {type(result).__name__}")
    return result


def require_list_of_dicts_result(response: RpcResponse) -> list[dict[str, Any]]:
    result = require_list_result(response)
    if not all(isinstance(item, dict) for item in result):
        raise RuntimeError("Blender Error: Expected a list of objects in RPC result")
    return cast(list[dict[str, Any]], result)


def require_list_of_strings_result(response: RpcResponse) -> list[str]:
    result = require_list_result(response)
    if not all(isinstance(item, str) for item in result):
        raise RuntimeError("Blender Error: Expected a list of strings in RPC result")
    return cast(list[str], result)
