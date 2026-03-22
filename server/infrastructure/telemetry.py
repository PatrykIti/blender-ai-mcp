# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""OpenTelemetry bootstrap and repo-specific span helpers."""

from __future__ import annotations

import json
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Iterator

from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import ProxyTracerProvider


@dataclass(frozen=True)
class TelemetryState:
    """Current telemetry bootstrap state."""

    enabled: bool
    service_name: str
    exporter: str
    provider: TracerProvider | None = None
    memory_exporter: InMemorySpanExporter | None = None


_telemetry_state = TelemetryState(enabled=False, service_name="blender-ai-mcp", exporter="none")


def _build_exporter(exporter: str):
    if exporter == "console":
        return ConsoleSpanExporter(), None
    if exporter == "memory":
        memory_exporter = InMemorySpanExporter()
        return memory_exporter, memory_exporter
    if exporter == "none":
        return None, None
    raise ValueError(f"Unsupported OTEL exporter '{exporter}'. Expected one of: none, console, memory")


def initialize_telemetry(
    *,
    enabled: bool,
    service_name: str,
    exporter: str = "none",
    force: bool = False,
) -> TelemetryState:
    """Initialize OpenTelemetry provider/exporter for repo-specific spans."""

    global _telemetry_state

    if not enabled:
        _telemetry_state = TelemetryState(enabled=False, service_name=service_name, exporter=exporter)
        return _telemetry_state

    if _telemetry_state.enabled and not force:
        return _telemetry_state

    provider = TracerProvider(resource=Resource.create({SERVICE_NAME: service_name}))
    span_exporter, memory_exporter = _build_exporter(exporter)
    if span_exporter is not None:
        provider.add_span_processor(SimpleSpanProcessor(span_exporter))

    # Tests and repeated local runs need deterministic reconfiguration.
    trace._set_tracer_provider(provider, log=False)  # type: ignore[attr-defined]

    _telemetry_state = TelemetryState(
        enabled=True,
        service_name=service_name,
        exporter=exporter,
        provider=provider,
        memory_exporter=memory_exporter,
    )
    return _telemetry_state


def initialize_telemetry_from_config(config) -> TelemetryState:
    """Initialize telemetry from application config."""

    return initialize_telemetry(
        enabled=config.OTEL_ENABLED,
        service_name=config.OTEL_SERVICE_NAME,
        exporter=config.OTEL_EXPORTER,
    )


def get_telemetry_state() -> TelemetryState:
    """Return the current telemetry bootstrap state."""

    return _telemetry_state


def get_memory_exporter() -> InMemorySpanExporter | None:
    """Return the in-memory exporter when telemetry is configured for tests."""

    return _telemetry_state.memory_exporter


def reset_telemetry_for_tests() -> None:
    """Reset telemetry state for deterministic unit tests."""

    global _telemetry_state
    trace._set_tracer_provider(ProxyTracerProvider(), log=False)  # type: ignore[attr-defined]
    _telemetry_state = TelemetryState(enabled=False, service_name="blender-ai-mcp", exporter="none")


def _normalize_span_attributes(attributes: dict[str, Any] | None) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in (attributes or {}).items():
        if value is None:
            continue
        if isinstance(value, (str, bool, int, float)):
            normalized[key] = value
        else:
            normalized[key] = json.dumps(value, default=str)
    return normalized


@contextmanager
def telemetry_span(name: str, *, attributes: dict[str, Any] | None = None) -> Iterator[Any]:
    """Create a repo-specific OTEL span when telemetry is enabled."""

    state = _telemetry_state
    if not state.enabled or state.provider is None:
        yield None
        return

    tracer = state.provider.get_tracer("blender-ai-mcp")
    with tracer.start_as_current_span(name) as span:
        for key, value in _normalize_span_attributes(attributes).items():
            span.set_attribute(key, value)
        yield span


def emit_router_event_span(
    *,
    event_type: str,
    tool_name: str | None,
    session_id: str | None,
    data: dict[str, Any] | None = None,
) -> None:
    """Emit one repo-specific router span when telemetry is enabled."""

    attributes = {
        "router.event_type": event_type,
        "router.tool_name": tool_name,
        "router.session_id": session_id,
    }
    if data:
        for key, value in data.items():
            attributes[f"router.{key}"] = value

    with telemetry_span(f"router.{event_type}", attributes=attributes):
        return
