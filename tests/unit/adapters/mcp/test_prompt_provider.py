"""Tests for native FastMCP prompt provider/rendering."""

from __future__ import annotations

import asyncio

from fastmcp.prompts.prompt import PromptResult

from server.adapters.mcp.prompts.provider import build_prompt_assets_provider
from server.adapters.mcp.prompts.rendering import render_recommended_prompts


def test_prompt_provider_lists_curated_prompt_assets():
    """Local prompt provider should expose the curated prompt catalog as native prompts."""

    provider = build_prompt_assets_provider()

    async def run():
        prompts = await provider.list_prompts()
        return {prompt.name for prompt in prompts}

    names = asyncio.run(run())

    assert "getting_started" in names
    assert "workflow_router_first" in names
    assert "recommended_prompts" in names


def test_recommended_prompts_renderer_reflects_phase_and_profile():
    """Dynamic recommendation prompt should render session-aware prompt suggestions."""

    result = render_recommended_prompts(surface_profile="llm-guided", phase="planning")

    assert isinstance(result, PromptResult)
    message = result.messages[0].content.text
    assert "workflow_router_first" in message
    assert "llm-guided" in message
