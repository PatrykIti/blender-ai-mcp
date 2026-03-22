# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Compatibility helpers for structured adapter contracts."""

from __future__ import annotations

from pydantic import BaseModel


def to_compat_dict(value: BaseModel | dict) -> dict:
    """Convert structured contract payloads to plain dicts when explicitly needed."""

    if isinstance(value, BaseModel):
        return value.model_dump()
    return value
