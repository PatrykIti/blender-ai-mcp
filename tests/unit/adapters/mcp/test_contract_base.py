"""Tests for shared MCP structured contract helpers."""

from pydantic import BaseModel

from server.adapters.mcp.contracts.base import MCPContract, to_contract
from server.adapters.mcp.contracts.output_schema import get_output_schema


class ExampleContract(MCPContract):
    status: str
    value: int


def test_contract_base_validates_and_coerces_payloads():
    """Shared contract helpers should normalize adapter payloads consistently."""

    contract = to_contract(ExampleContract, {"status": "ok", "value": 1})

    assert contract.status == "ok"
    assert contract.value == 1


def test_output_schema_comes_from_pydantic_contract_model():
    """Output schema helper should expose the MCP object schema for contract models."""

    schema = get_output_schema(ExampleContract)

    assert schema["type"] == "object"
    assert "status" in schema["properties"]
