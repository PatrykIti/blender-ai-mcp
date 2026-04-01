"""Tests for OpenTelemetry bootstrap and repo-specific span helpers."""

from server.infrastructure.telemetry import (
    get_memory_exporter,
    get_telemetry_state,
    initialize_telemetry,
    reset_telemetry_for_tests,
    telemetry_span,
)
from server.router.infrastructure.logger import RouterLogger


def setup_function():
    reset_telemetry_for_tests()


def teardown_function():
    reset_telemetry_for_tests()


def test_initialize_telemetry_with_memory_exporter_emits_spans():
    state = initialize_telemetry(
        enabled=True,
        service_name="blender-ai-mcp-test",
        exporter="memory",
        force=True,
    )

    assert state.enabled is True
    assert state.exporter == "memory"

    with telemetry_span("test.span", attributes={"tool.name": "scene_context"}):
        pass

    exporter = get_memory_exporter()
    finished_spans = exporter.get_finished_spans()

    assert len(finished_spans) == 1
    assert finished_spans[0].name == "test.span"
    assert finished_spans[0].attributes["tool.name"] == "scene_context"


def test_router_logger_emits_repo_specific_router_spans():
    initialize_telemetry(
        enabled=True,
        service_name="blender-ai-mcp-test",
        exporter="memory",
        force=True,
    )
    logger = RouterLogger()
    logger.set_session_id("session-1")

    logger.log_intercept("mesh_extrude_region", {"depth": 0.5}, prompt="extrude")

    exporter = get_memory_exporter()
    finished_spans = exporter.get_finished_spans()

    assert any(span.name == "router.intercept" for span in finished_spans)
    router_span = next(span for span in finished_spans if span.name == "router.intercept")
    assert router_span.attributes["router.tool_name"] == "mesh_extrude_region"
    assert router_span.attributes["router.session_id"] == "session-1"


def test_initialize_telemetry_disabled_keeps_noop_state():
    state = initialize_telemetry(
        enabled=False,
        service_name="blender-ai-mcp-test",
        exporter="memory",
        force=True,
    )

    assert state.enabled is False
    assert get_telemetry_state().enabled is False
    assert get_memory_exporter() is None
