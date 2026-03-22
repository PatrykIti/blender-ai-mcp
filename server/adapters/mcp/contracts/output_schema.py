# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Helpers for deriving MCP output schemas from contract models."""

from __future__ import annotations

from pydantic import BaseModel


def get_output_schema(model_type: type[BaseModel]) -> dict:
    """Return the JSON schema used by FastMCP structured output delivery."""

    return model_type.model_json_schema()
