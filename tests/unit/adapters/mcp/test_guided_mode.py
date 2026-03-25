"""Tests for guided-mode visibility diagnostics and session application."""

from __future__ import annotations

import asyncio

from server.adapters.mcp.guided_mode import apply_session_visibility, build_visibility_diagnostics
from server.adapters.mcp.session_phase import SessionPhase
from server.adapters.mcp.transforms.visibility_policy import GUIDED_INSPECT_ESCAPE_HATCH_TOOLS


class FakeAsyncContext:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    async def reset_visibility(self) -> None:
        self.calls.append(("reset_visibility", {}))

    async def enable_components(self, **kwargs) -> None:
        self.calls.append(("enable_components", kwargs))

    async def disable_components(self, **kwargs) -> None:
        self.calls.append(("disable_components", kwargs))


def test_guided_mode_bootstrap_visibility_is_tiny_and_entry_only():
    """llm-guided bootstrap should expose only the guided entry capabilities."""

    diagnostics = build_visibility_diagnostics("llm-guided", SessionPhase.BOOTSTRAP)

    assert diagnostics.visible_capability_ids == ("router", "workflow_catalog")
    assert diagnostics.visible_entry_capability_ids == ("router", "workflow_catalog")
    assert "scene" in diagnostics.hidden_capability_ids


def test_guided_mode_build_phase_exposes_build_capabilities_plus_entry_tools():
    """Build phase should expand beyond the tiny entry surface."""

    diagnostics = build_visibility_diagnostics("llm-guided", SessionPhase.BUILD)

    assert "router" in diagnostics.visible_capability_ids
    assert "workflow_catalog" in diagnostics.visible_capability_ids
    assert "modeling" in diagnostics.visible_capability_ids
    assert "mesh" in diagnostics.visible_capability_ids
    assert "scene" in diagnostics.visible_capability_ids
    assert "material" in diagnostics.visible_capability_ids
    assert "baking" not in diagnostics.visible_capability_ids
    assert "armature" not in diagnostics.visible_capability_ids
    assert "sculpt" not in diagnostics.visible_capability_ids
    assert "text" not in diagnostics.visible_capability_ids


def test_guided_mode_inspect_phase_prefers_verification_capabilities_over_build_families():
    """Inspect/validate phase should expose verification/capture families, not broad build families."""

    diagnostics = build_visibility_diagnostics("llm-guided", SessionPhase.INSPECT_VALIDATE)

    assert "scene" in diagnostics.visible_capability_ids
    assert "mesh" in diagnostics.visible_capability_ids
    assert "extraction" in diagnostics.visible_capability_ids
    assert "modeling" not in diagnostics.visible_capability_ids
    assert "armature" not in diagnostics.visible_capability_ids
    assert "sculpt" not in diagnostics.visible_capability_ids
    assert "system" not in diagnostics.visible_capability_ids


def test_legacy_flat_visibility_keeps_full_surface_visible():
    """Legacy compatibility profile should not hide capabilities by phase."""

    diagnostics = build_visibility_diagnostics("legacy-flat", SessionPhase.BOOTSTRAP)

    assert "scene" in diagnostics.visible_capability_ids
    assert "mesh" in diagnostics.visible_capability_ids
    assert "router" in diagnostics.visible_capability_ids
    assert diagnostics.hidden_capability_ids == ()


def test_apply_session_visibility_uses_native_fastmcp_session_api():
    """Session visibility should be applied through reset/enable/disable component calls."""

    ctx = FakeAsyncContext()

    diagnostics = asyncio.run(
        apply_session_visibility(
            ctx,
            surface_profile="llm-guided",
            phase=SessionPhase.INSPECT_VALIDATE,
        )
    )

    assert diagnostics.phase == SessionPhase.INSPECT_VALIDATE
    assert ctx.calls[0][0] == "reset_visibility"
    assert ctx.calls[1][0] == "disable_components"
    assert ctx.calls[1][1]["match_all"] is True
    assert any(name == "enable_components" and call["tags"] == {"entry:guided"} for name, call in ctx.calls[2:])
    assert any(
        name == "enable_components" and call["names"] == set(GUIDED_INSPECT_ESCAPE_HATCH_TOOLS)
        for name, call in ctx.calls[2:]
    )
