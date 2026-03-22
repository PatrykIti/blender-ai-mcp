"""Tests for the first provider inventory slice."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from server.adapters.mcp.areas.modeling import register_modeling_tools
from server.adapters.mcp.providers import core_tools


EXPECTED_MODELING_TOOLS = {
    "modeling_create_primitive",
    "modeling_transform_object",
    "modeling_add_modifier",
    "modeling_apply_modifier",
    "modeling_convert_to_mesh",
    "modeling_join_objects",
    "modeling_separate_object",
    "modeling_list_modifiers",
    "modeling_set_origin",
    "metaball_create",
    "metaball_add_element",
    "metaball_to_mesh",
    "skin_create_skeleton",
    "skin_set_radius",
}


@dataclass
class RegisteredTool:
    """Minimal stand-in for a registered tool object."""

    name: str
    fn_name: str


class FakeRegistrarTarget:
    """A FastMCP-compatible target exposing the .tool(...) registration shape."""

    def __init__(self) -> None:
        self.registered: dict[str, RegisteredTool] = {}

    def tool(self, name_or_fn=None, **kwargs):
        explicit_name = kwargs.get("name")

        def register(fn):
            tool_name = explicit_name or (name_or_fn if isinstance(name_or_fn, str) else fn.__name__)
            tool = RegisteredTool(name=tool_name, fn_name=fn.__name__)
            self.registered[tool_name] = tool
            return tool

        if callable(name_or_fn):
            return register(name_or_fn)

        return register


def test_register_modeling_tools_registers_expected_public_surface():
    """Modeling registrar should expose the expected public tool names."""

    target = FakeRegistrarTarget()

    registered = register_modeling_tools(target)

    assert set(registered) == EXPECTED_MODELING_TOOLS
    assert set(target.registered) == EXPECTED_MODELING_TOOLS


def test_register_core_tools_delegates_to_modeling_slice():
    """The first core provider slice should contain the extracted modeling family."""

    target = FakeRegistrarTarget()

    registered = core_tools.register_core_tools(target)

    assert set(registered) == EXPECTED_MODELING_TOOLS
    assert set(target.registered) == EXPECTED_MODELING_TOOLS


def test_build_core_tools_provider_uses_local_provider_when_available(monkeypatch):
    """Provider builder should register the same modeling surface on a LocalProvider-like target."""

    class FakeLocalProvider(FakeRegistrarTarget):
        pass

    monkeypatch.setattr(core_tools, "LocalProvider", FakeLocalProvider)

    provider = core_tools.build_core_tools_provider()

    assert isinstance(provider, FakeLocalProvider)
    assert set(provider.registered) == EXPECTED_MODELING_TOOLS


def test_build_core_tools_provider_requires_local_provider():
    """Provider builder should fail clearly when FastMCP 3.x LocalProvider is unavailable."""

    original = core_tools.LocalProvider
    core_tools.LocalProvider = None
    try:
        with pytest.raises(RuntimeError, match="LocalProvider requires FastMCP >=3.0"):
            core_tools.build_core_tools_provider()
    finally:
        core_tools.LocalProvider = original
