from __future__ import annotations

import pytest
from server.application.tool_handlers._rpc_utils import (
    require_dict_result,
    require_list_of_dicts_result,
    require_list_of_strings_result,
    require_list_result,
    require_result,
    require_str_result,
)
from server.domain.models.rpc import RpcResponse


def _response(*, result: object | None = None, status: str = "ok", error: str | None = None) -> RpcResponse:
    return RpcResponse(request_id="req-1", status=status, result=result, error=error)


def test_require_result_returns_payload_on_success():
    payload = {"mode": "EDIT"}

    assert require_result(_response(result=payload)) == payload


def test_require_result_rejects_error_status():
    with pytest.raises(RuntimeError, match="Blender Error: boom"):
        require_result(_response(status="error", error="boom"))


def test_require_result_rejects_missing_payload():
    with pytest.raises(RuntimeError, match="RPC response did not include a result payload"):
        require_result(_response(result=None))


@pytest.mark.parametrize(
    ("helper", "payload", "expected"),
    [
        (require_str_result, "ok", "ok"),
        (require_dict_result, {"name": "Cube"}, {"name": "Cube"}),
        (require_list_result, [1, 2, 3], [1, 2, 3]),
        (require_list_of_dicts_result, [{"name": "Bevel"}], [{"name": "Bevel"}]),
        (require_list_of_strings_result, ["Cube", "Light"], ["Cube", "Light"]),
    ],
)
def test_rpc_result_helpers_accept_expected_shapes(helper, payload, expected):
    assert helper(_response(result=payload)) == expected


@pytest.mark.parametrize(
    ("helper", "payload", "message"),
    [
        (require_str_result, {"status": "ok"}, "Expected string result, got dict"),
        (require_dict_result, ["Cube"], "Expected object result, got list"),
        (require_list_result, {"items": []}, "Expected list result, got dict"),
        (require_list_of_dicts_result, ["not-a-dict"], "Expected a list of objects in RPC result"),
        (require_list_of_strings_result, [{"name": "Cube"}], "Expected a list of strings in RPC result"),
    ],
)
def test_rpc_result_helpers_reject_wrong_shapes(helper, payload, message):
    with pytest.raises(RuntimeError, match=message):
        helper(_response(result=payload))
