# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Backend interface sketch for bounded vision assistance."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Literal

from .config import VisionBackendKind, VisionRuntimeConfig

VisionImageRole = Literal["before", "after", "reference"]
VisionImageViewKind = Literal[
    "wide",
    "focus",
    "top",
    "oblique",
    "overlay",
    "reference",
    "grid",
    "depth",
    "normal",
    "object_id",
]


@dataclass(frozen=True, slots=True)
class VisionImageInput:
    """One normalized image input passed to a vision backend."""

    path: str
    role: VisionImageRole
    label: str | None = None
    media_type: str = "image/png"
    view_kind: VisionImageViewKind | None = None
    projection: Literal["orthographic", "perspective"] | None = None


@dataclass(frozen=True, slots=True)
class VisionRequest:
    """Normalized bounded request for visual interpretation."""

    goal: str
    images: tuple[VisionImageInput, ...]
    target_object: str | None = None
    prompt_hint: str | None = None
    truth_summary: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class VisionBackend(ABC):
    """Abstract backend for local/external bounded vision runtimes."""

    @property
    @abstractmethod
    def backend_kind(self) -> VisionBackendKind:
        """Return the backend family identifier."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the active model identifier for diagnostics."""

    @abstractmethod
    async def analyze(self, request: VisionRequest) -> dict[str, Any]:
        """Run bounded vision analysis and return adapter-neutral structured data."""

    @property
    def runtime_config(self) -> VisionRuntimeConfig | None:
        """Return a resolved runtime config when the backend refines it lazily."""

        value = getattr(self, "_runtime_config", None)
        return value if isinstance(value, VisionRuntimeConfig) else None

    async def prepare_for_request(self, request: VisionRequest) -> None:
        """Resolve lazy model/provider metadata before runner budget projection."""

        return None


class VisionBackendUnavailableError(RuntimeError):
    """Raised when a configured vision backend cannot be created or used."""
