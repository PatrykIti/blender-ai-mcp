"""Tests for the FastMCP transform pipeline baseline."""

from __future__ import annotations

from server.adapters.mcp.surfaces import get_surface_profile
from server.adapters.mcp.transforms import (
    build_surface_transform_pipeline,
    materialize_transforms,
)


def test_transform_pipeline_uses_deterministic_stage_order():
    """Surface transform stages should be ordered once and reused everywhere."""

    pipeline = build_surface_transform_pipeline(get_surface_profile("legacy-flat"))

    assert tuple(stage.name for stage in pipeline) == (
        "version_filter",
        "naming",
        "prompts_bridge",
        "visibility",
        "discovery",
    )


def test_transform_pipeline_materializes_only_active_transforms():
    """The baseline factory should materialize only the active transforms for a surface."""

    transforms = materialize_transforms(get_surface_profile("llm-guided"))

    assert len(transforms) == 9
