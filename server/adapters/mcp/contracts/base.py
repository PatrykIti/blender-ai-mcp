# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Base classes and helpers for structured MCP adapter contracts."""

from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict


class MCPContract(BaseModel):
    """Base class for structured MCP adapter contracts."""

    model_config = ConfigDict(extra="forbid")


ContractT = TypeVar("ContractT", bound=MCPContract)


def to_contract(model_type: type[ContractT], data: Any) -> ContractT:
    """Validate arbitrary adapter data against a contract model."""

    if isinstance(data, model_type):
        return data
    return model_type.model_validate(data)
