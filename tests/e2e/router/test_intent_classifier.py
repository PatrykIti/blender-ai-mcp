"""
E2E tests for Intent Classifier.

Tests multilingual prompt classification using LaBSE embeddings.
Requires running Blender instance.

TASK-040
"""

import pytest

from server.router.application.router import SupervisorRouter
from server.router.infrastructure.config import RouterConfig


class TestMultilingualClassification:
    """Tests for multilingual prompt classification."""

    def test_english_prompt_classification(self, router, rpc_client, clean_scene):
        """Test: English prompts are correctly processed."""
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})
        rpc_client.send_request("mesh.select", {"action": "all"})

        # English prompt
        tools = router.process_llm_tool_call(
            "mesh_bevel",
            {"width": 0.1},
            prompt="bevel the edges smoothly for rounded corners"
        )

        # Should return valid tool sequence
        assert len(tools) > 0, "Should return at least one tool"
        tool_names = [t["tool"] for t in tools]
        assert "mesh_bevel" in tool_names, f"Bevel should be in tools, got: {tool_names}"

    def test_polish_prompt_classification(self, router, rpc_client, clean_scene):
        """Test: Polish prompts are correctly processed."""
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})
        rpc_client.send_request("mesh.select", {"action": "all"})

        # Polish prompt
        tools = router.process_llm_tool_call(
            "mesh_extrude_region",
            {"depth": 0.5},
            prompt="wyciągnij górną ścianę w górę"
        )

        # Should return valid tool sequence
        assert len(tools) > 0, "Should return at least one tool"
        tool_names = [t["tool"] for t in tools]
        assert "mesh_extrude_region" in tool_names, f"Extrude should be in tools, got: {tool_names}"

    def test_german_prompt_classification(self, router, rpc_client, clean_scene):
        """Test: German prompts are correctly processed."""
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})
        rpc_client.send_request("mesh.select", {"action": "all"})

        # German prompt
        tools = router.process_llm_tool_call(
            "mesh_subdivide",
            {"number_cuts": 2},
            prompt="unterteile die Fläche in mehrere Segmente"
        )

        assert len(tools) > 0
        tool_names = [t["tool"] for t in tools]
        assert "mesh_subdivide" in tool_names


class TestPromptFallback:
    """Tests for fallback behavior with unknown prompts."""

    def test_unknown_prompt_uses_original_tool(self, router, rpc_client, clean_scene):
        """Test: Unknown/gibberish prompt still returns original tool."""
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})
        rpc_client.send_request("mesh.select", {"action": "all"})

        # Gibberish prompt
        tools = router.process_llm_tool_call(
            "mesh_subdivide",
            {"number_cuts": 2},
            prompt="xyzzy flibbertigibbet nonsense words"
        )

        # Should still return the original tool
        assert len(tools) > 0
        tool_names = [t["tool"] for t in tools]
        assert "mesh_subdivide" in tool_names, \
            f"Original tool should be preserved, got: {tool_names}"

    def test_empty_prompt_uses_original_tool(self, router, rpc_client, clean_scene):
        """Test: Empty prompt still processes tool correctly."""
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})
        rpc_client.send_request("mesh.select", {"action": "all"})

        # No prompt
        tools = router.process_llm_tool_call(
            "mesh_bevel",
            {"width": 0.05, "segments": 3}
        )

        assert len(tools) > 0
        tool_names = [t["tool"] for t in tools]
        assert "mesh_bevel" in tool_names

    def test_none_prompt_uses_original_tool(self, router, rpc_client, clean_scene):
        """Test: None prompt still processes tool correctly."""
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})
        rpc_client.send_request("mesh.select", {"action": "all"})

        # Explicit None prompt
        tools = router.process_llm_tool_call(
            "mesh_inset",
            {"thickness": 0.1},
            prompt=None
        )

        assert len(tools) > 0
        tool_names = [t["tool"] for t in tools]
        assert "mesh_inset" in tool_names


class TestPromptInfluence:
    """Tests for prompt influence on tool processing."""

    def test_prompt_with_workflow_keywords(self, router, rpc_client, clean_scene):
        """Test: Prompt with workflow keywords may trigger expansion."""
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("modeling.transform_object", {
            "scale": [0.4, 0.8, 0.05]  # Phone-like
        })
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})

        router.invalidate_cache()

        # Prompt with phone/screen keywords
        tools = router.process_llm_tool_call(
            "mesh_extrude_region",
            {"depth": -0.02},
            prompt="create a phone screen cutout"
        )

        # Should return tools (may be expanded or not)
        assert len(tools) > 0
        assert isinstance(tools, list)

    def test_prompt_affects_context_analysis(self, router, rpc_client, clean_scene):
        """Test: Prompt is used in context analysis."""
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})

        # Two different prompts for same tool
        tools1 = router.process_llm_tool_call(
            "mesh_subdivide",
            {"number_cuts": 2},
            prompt="prepare for organic sculpting"
        )

        rpc_client.send_request("mesh.select", {"action": "all"})

        tools2 = router.process_llm_tool_call(
            "mesh_subdivide",
            {"number_cuts": 2},
            prompt="add edge loops for hard surface"
        )

        # Both should return valid tools
        assert len(tools1) > 0
        assert len(tools2) > 0
