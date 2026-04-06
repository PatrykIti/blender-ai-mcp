"""Tests for prompt bridge tools on FastMCP surfaces."""

from __future__ import annotations

import asyncio
import json

from server.adapters.mcp.factory import build_server


def _decode_text_tool_result(result) -> dict:
    blocks = getattr(result, "content", []) or []
    text = "".join(getattr(block, "text", "") for block in blocks).strip()
    return json.loads(text)


def test_native_prompt_components_are_available_on_built_server():
    """Servers should expose native prompts directly for prompt-capable clients."""

    server = build_server("llm-guided")

    async def run():
        prompts = await server.list_prompts()
        rendered = await server.render_prompt(
            "recommended_prompts",
            {
                "surface_profile": "llm-guided",
                "session_phase": "planning",
                "session_goal": "create a low-poly creature matching front and side reference images",
            },
        )
        return {prompt.name for prompt in prompts}, rendered

    names, rendered = asyncio.run(run())

    assert "reference_guided_creature_build" in names
    assert "workflow_router_first" in names
    assert "recommended_prompts" in names
    assert "reference_guided_creature_build" in rendered.messages[0].content.text
    assert "workflow_router_first" in rendered.messages[0].content.text


def test_prompt_bridge_tools_are_visible_on_guided_surface():
    """Tool-only clients should see canonical prompt bridge tools on llm-guided."""

    server = build_server("llm-guided")

    async def run():
        tools = await server.list_tools()
        prompts = await server.call_tool("list_prompts", {})
        rendered = await server.call_tool("get_prompt", {"name": "workflow_router_first"})
        return {tool.name for tool in tools}, prompts, rendered

    tool_names, prompts, rendered = asyncio.run(run())

    assert "list_prompts" in tool_names
    assert "get_prompt" in tool_names

    prompts_payload = _decode_text_tool_result(prompts)
    assert any(prompt["name"] == "workflow_router_first" for prompt in prompts_payload)
    assert any(prompt["name"] == "reference_guided_creature_build" for prompt in prompts_payload)

    rendered_payload = _decode_text_tool_result(rendered)
    assert rendered_payload["messages"]
