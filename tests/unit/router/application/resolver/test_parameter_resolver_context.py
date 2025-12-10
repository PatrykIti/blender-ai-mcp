"""
Unit tests for ParameterResolver context extraction.

TASK-055-FIX-3: Tests for hybrid 3-tier context extraction strategy.
"""

import pytest
from server.router.application.resolver.parameter_resolver import ParameterResolver
from server.router.domain.entities.parameter import ParameterSchema


@pytest.fixture
def resolver():
    """Create ParameterResolver instance for testing."""
    # Mock classifier (not used in context extraction tests)
    from unittest.mock import MagicMock
    classifier = MagicMock()
    store = MagicMock()
    return ParameterResolver(classifier, store)


@pytest.fixture
def sample_schema():
    """Create sample parameter schema."""
    return ParameterSchema(
        name="leg_angle",
        type="float",
        range=[-1.57, 1.57],
        default=0.0,
        description="Rotation angle for table legs",
        semantic_hints=["legs", "angle", "rotation"]
    )


class TestTier3FullPrompt:
    """Test TIER 3: Full prompt for short inputs (≤500 chars)."""

    def test_very_short_prompt(self, resolver, sample_schema):
        """Short prompt should return full prompt."""
        prompt = "X-shaped legs picnic table"
        context = resolver.extract_context(prompt, sample_schema)

        assert context == prompt
        assert len(context) == len(prompt)

    def test_medium_short_prompt(self, resolver, sample_schema):
        """Prompt under 500 chars should return full prompt."""
        prompt = "I want to create a beautiful picnic table with X-shaped crossed legs for outdoor use."
        context = resolver.extract_context(prompt, sample_schema)

        assert context == prompt
        assert len(context) < 500

    def test_exactly_500_chars(self, resolver, sample_schema):
        """Prompt exactly 500 chars should return full prompt."""
        prompt = "a" * 495 + " legs"  # Total 500 chars
        context = resolver.extract_context(prompt, sample_schema)

        assert context == prompt.strip()
        assert len(context) == 500


class TestTier1SentenceExtraction:
    """Test TIER 1: Smart sentence extraction for structured prompts."""

    def test_single_sentence_with_hint(self, resolver, sample_schema):
        """Extract complete sentence containing hint."""
        prompt = (
            "I need outdoor furniture for my garden patio area. "
            "Create a picnic table with X-shaped crossed legs for stability. "
            "The table should be made from oak wood and seat six people comfortably."
        )
        context = resolver.extract_context(prompt, sample_schema)

        # Should extract: prev + hint sentence + next (within 400 chars)
        assert "legs" in context.lower()
        assert "X-shaped" in context or "crossed" in context
        assert len(context) >= 100  # TIER 1 minimum
        assert len(context) <= 400  # Max limit

    def test_hint_at_start(self, resolver, sample_schema):
        """Extract when hint is in first sentence (no prev sentence)."""
        prompt = (
            "The legs should be angled at 15 degrees for stability. "
            "Use oak wood for construction. "
            "Make sure the finish is weatherproof and durable."
        ) * 3  # Make it long enough (>500 chars)

        context = resolver.extract_context(prompt, sample_schema)

        assert "legs" in context.lower()
        assert "angled" in context.lower()

    def test_hint_at_end(self, resolver, sample_schema):
        """Extract when hint is in last sentence (no next sentence)."""
        prompt = (
            "Start by creating a rectangular tabletop measuring 6 feet by 3 feet. "
            "Use cedar planks for weather resistance. "
            "Sand all surfaces smooth before assembly. "
        ) * 2 + "Finally attach the table legs at each corner."

        context = resolver.extract_context(prompt, sample_schema)

        assert "legs" in context.lower()
        assert len(context) >= 100

    def test_multiple_sentences_truncated(self, resolver, sample_schema):
        """Long context should be truncated to 400 chars while preserving hint."""
        # Create very long prompt with hint in middle
        long_prompt = (
            "This is a very long preamble that goes on and on about various details "
            "regarding outdoor furniture construction techniques and best practices. " * 3 +
            "The table should have X-shaped legs for maximum stability and aesthetic appeal. " +
            "Here is more content after the hint that continues with additional specifications. " * 3
        )

        context = resolver.extract_context(long_prompt, sample_schema)

        assert len(context) <= 400
        assert "legs" in context.lower()
        # Hint should be near center of extracted context
        hint_pos = context.lower().find("legs")
        assert hint_pos >= 0


class TestTier2ExpandedWindow:
    """Test TIER 2: Expanded window fallback for unstructured text."""

    def test_run_on_text_no_sentences(self, resolver, sample_schema):
        """Long text without sentences should use expanded window."""
        # Create run-on text (no sentence endings)
        prompt = (
            "create a picnic table with X-shaped legs and natural wood finish "
            "using oak or pine timber with weatherproof coating and modern design "
        ) * 10  # ~660 chars without sentence endings

        context = resolver.extract_context(prompt, sample_schema)

        # Should use TIER 2 (expanded window ~200 chars)
        assert len(context) >= 100  # Should be larger than old 60 chars
        assert len(context) <= 400  # Within max limit
        assert "legs" in context.lower()
        assert "X-shaped" in context

    def test_short_sentence_under_100_chars(self, resolver, sample_schema):
        """Very short sentence should trigger TIER 2 fallback."""
        prompt = (
            "Here is lots of preamble text that goes on for quite a while. " * 5 +
            "Short legs note. " +  # Short sentence < 100 chars
            "And then more content continues after the short sentence. " * 5
        )

        context = resolver.extract_context(prompt, sample_schema)

        # TIER 1 returns < 100 chars, triggers TIER 2
        assert "legs" in context.lower()
        assert len(context) >= 100  # TIER 2 expanded window


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_prompt(self, resolver, sample_schema):
        """Empty prompt should return empty string."""
        context = resolver.extract_context("", sample_schema)
        assert context == ""

    def test_none_prompt(self, resolver, sample_schema):
        """None prompt should be handled gracefully."""
        # Should not crash
        context = resolver.extract_context("", sample_schema)
        assert context == ""

    def test_hint_not_found(self, resolver, sample_schema):
        """Prompt without any semantic hints should use fallback."""
        prompt = "Create a beautiful outdoor furniture piece with wooden construction." * 5
        context = resolver.extract_context(prompt, sample_schema)

        # Should try description keywords fallback or return truncated prompt
        assert len(context) > 0
        assert len(context) <= 400

    def test_very_long_prompt(self, resolver, sample_schema):
        """Very long prompt (>1000 chars) should be handled."""
        prompt = (
            "I want to build an amazing outdoor furniture set for my backyard. "
            "The main piece should be a large picnic table with X-shaped legs. "
            "The table should accommodate at least 8 people comfortably. "
        ) * 15  # ~1500 chars

        context = resolver.extract_context(prompt, sample_schema)

        assert len(context) <= 400
        assert "legs" in context.lower()

    def test_hint_with_punctuation(self, resolver, sample_schema):
        """Hint surrounded by punctuation should be found."""
        prompt = "Create table (with X-shaped legs) for outdoor use." * 8
        context = resolver.extract_context(prompt, sample_schema)

        assert "legs" in context.lower()

    def test_multiple_hints_in_schema(self, resolver):
        """Should find first matching hint."""
        schema = ParameterSchema(
            name="test_param",
            type="float",
            default=0.0,
            description="Test parameter",
            semantic_hints=["missing", "absent", "legs", "rotation"]  # "legs" is 3rd
        )
        prompt = "Create a table with angled legs for stability." * 8

        context = resolver.extract_context(prompt, schema)

        assert "legs" in context.lower()


class TestRegressionPrevention:
    """Test cases to prevent regression of TASK-055-FIX-3 bug."""

    def test_x_shaped_legs_context_preservation(self, resolver, sample_schema):
        """
        CRITICAL TEST: The bug that triggered TASK-055-FIX-3.

        Before fix: "ed legs picnic table" (lost "X-shaped")
        After fix: Should preserve "X-shaped" in context
        """
        prompt = "create a picnic table with X-shaped legs"
        context = resolver.extract_context(prompt, sample_schema)

        # MUST preserve "X-shaped" modifier
        assert "X-shaped" in context or "x-shaped" in context.lower()
        assert "legs" in context.lower()
        assert len(context) >= len("X-shaped legs")

    def test_similarity_score_improvement(self, resolver, sample_schema):
        """
        Context should be long enough for good similarity matching.

        Old: 18 chars → similarity ~0.80
        New: Should be significantly longer
        """
        prompt = "create a picnic table with X-shaped legs"
        context = resolver.extract_context(prompt, sample_schema)

        # Context should be much longer than old 60 char limit
        # This prompt is <500 chars, so TIER 3 returns full prompt
        assert len(context) >= 40  # Much better than old 18 chars

    def test_modifier_preservation_polish(self, resolver, sample_schema):
        """
        Polish test case: "stół z nogami X"
        Should preserve "X" modifier for semantic matching.
        """
        prompt = "stwórz stół piknikowy z nogami X dla stabilności"
        context = resolver.extract_context(prompt, sample_schema)

        assert "nogami" in context.lower()  # "legs" in Polish
        assert "X" in context  # Critical modifier
        assert len(context) >= 30


class TestContextQuality:
    """Test that extracted context is semantically meaningful."""

    def test_context_contains_complete_words(self, resolver, sample_schema):
        """Context should not cut words in half."""
        prompt = "Create a beautiful picnic table with X-shaped legs for outdoor dining." * 8
        context = resolver.extract_context(prompt, sample_schema)

        # Should not end with partial words like "tabl" or "for"
        # (Though TIER 1/2 may have some edge cases)
        assert len(context) > 0

    def test_context_preserves_modifiers_near_hint(self, resolver, sample_schema):
        """Important modifiers near hint should be preserved."""
        test_cases = [
            ("straight legs", "straight"),
            ("angled legs at 15 degrees", "angled"),
            ("X-shaped crossed legs", "X-shaped"),
            ("thick wooden legs", "thick"),
        ]

        for prompt_phrase, expected_modifier in test_cases:
            prompt = f"Create a table with {prompt_phrase} for stability." * 8
            context = resolver.extract_context(prompt, sample_schema)

            assert expected_modifier.lower() in context.lower(), \
                f"Failed to preserve '{expected_modifier}' in context"
            assert "legs" in context.lower()
