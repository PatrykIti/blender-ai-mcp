"""Tests for bounded MCP sampling assistants."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from server.adapters.mcp.contracts.base import MCPContract
from server.adapters.mcp.sampling.assistant_runner import run_typed_assistant
from server.adapters.mcp.sampling.result_types import AssistantPolicy


class ExampleResultContract(MCPContract):
    value: int


@dataclass
class FakeSession:
    has_sampling: bool = True
    has_tools: bool = False

    def check_client_capability(self, capability) -> bool:
        sampling = getattr(capability, "sampling", None)
        tools = getattr(sampling, "tools", None) if sampling is not None else None
        if tools is not None:
            return self.has_sampling and self.has_tools
        return self.has_sampling


@dataclass
class FakeFastMCP:
    sampling_handler_behavior: str | None = None
    sampling_handler: object | None = None


class FakeSamplingResult:
    def __init__(self, result):
        self.result = result
        self.text = None
        self.history = []


class FakeContext:
    def __init__(self, *, has_sampling: bool = True, has_tools: bool = False) -> None:
        self.fastmcp = FakeFastMCP()
        self.session = FakeSession(has_sampling=has_sampling, has_tools=has_tools)
        self.request_id = "req_123"
        self.is_background_task = False
        self.task_id = None

    async def sample(self, messages, **kwargs):
        return FakeSamplingResult(ExampleResultContract(value=1))


def _policy(**overrides) -> AssistantPolicy:
    payload: dict[str, Any] = {
        "assistant_name": "test_assistant",
        "responsibility": "diagnostic_summary",
        "max_input_chars": 2000,
        "max_messages": 1,
        "max_tokens": 128,
    }
    payload.update(overrides)
    return AssistantPolicy(
        **payload,
    )


def test_runner_returns_typed_success_when_sampling_is_available():
    """Typed assistants should return validated structured output on success."""

    ctx = FakeContext()
    result = asyncio.run(
        run_typed_assistant(
            ctx,
            policy=_policy(),
            messages=("hello",),
            system_prompt="test",
            result_type=ExampleResultContract,
        )
    )

    assert result.status == "success"
    assert result.result.value == 1
    assert result.request_id == "req_123"
    assert result.capability_source == "client"


def test_runner_uses_fallback_handler_capability_when_client_sampling_is_missing():
    """Configured fallback handlers should keep assistants available when the client lacks sampling."""

    ctx = FakeContext(has_sampling=False)
    ctx.fastmcp.sampling_handler_behavior = "fallback"
    ctx.fastmcp.sampling_handler = object()

    result = asyncio.run(
        run_typed_assistant(
            ctx,
            policy=_policy(),
            messages=("hello",),
            system_prompt="test",
            result_type=ExampleResultContract,
        )
    )

    assert result.status == "success"
    assert result.capability_source == "fallback_handler"


def test_runner_returns_unavailable_when_sampling_capability_is_missing():
    """Unavailable sampling should degrade into a typed unavailable outcome."""

    ctx = FakeContext(has_sampling=False)
    result = asyncio.run(
        run_typed_assistant(
            ctx,
            policy=_policy(),
            messages=("hello",),
            system_prompt="test",
            result_type=ExampleResultContract,
        )
    )

    assert result.status == "unavailable"
    assert result.rejection_reason == "sampling_capability_missing"


def test_runner_rejects_background_task_contexts_by_policy():
    """Assistants should stay bound to foreground MCP requests."""

    ctx = FakeContext()
    ctx.is_background_task = True
    ctx.task_id = "task_1"

    result = asyncio.run(
        run_typed_assistant(
            ctx,
            policy=_policy(),
            messages=("hello",),
            system_prompt="test",
            result_type=ExampleResultContract,
        )
    )

    assert result.status == "rejected_by_policy"
    assert result.rejection_reason == "background_request_forbidden"


def test_runner_returns_masked_error_on_sampling_failure():
    """Unexpected sampling exceptions should surface as masked_error outcomes."""

    class BrokenContext(FakeContext):
        async def sample(self, messages, **kwargs):
            raise RuntimeError("boom")

    result = asyncio.run(
        run_typed_assistant(
            BrokenContext(),
            policy=_policy(mask_error_details=True),
            messages=("hello",),
            system_prompt="test",
            result_type=ExampleResultContract,
        )
    )

    assert result.status == "masked_error"
    assert "masked" in result.message
    assert result.rejection_reason == "sampling_execution_failed"


def test_runner_rejects_inputs_that_exceed_budget():
    """Budget overflow should reject assistant execution deterministically."""

    ctx = FakeContext()
    result = asyncio.run(
        run_typed_assistant(
            ctx,
            policy=_policy(max_input_chars=4),
            messages=("hello",),
            system_prompt="test",
            result_type=ExampleResultContract,
        )
    )

    assert result.status == "rejected_by_policy"
    assert result.rejection_reason == "input_budget_exceeded"
