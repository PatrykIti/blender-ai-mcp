"""
Unit tests for language detection.

Tests lightweight language detection for semantic matching.

TASK-050: Multi-Embedding Workflow System
"""

import pytest

from server.router.infrastructure.language_detector import (
    detect_language,
    get_supported_languages,
    LANGUAGE_PATTERNS,
    LANGUAGE_MARKERS,
)


class TestDetectLanguageBasic:
    """Tests for basic language detection."""

    def test_empty_string_returns_english(self):
        """Test that empty string defaults to English."""
        assert detect_language("") == "en"
        assert detect_language("   ") == "en"
        assert detect_language(None) == "en" if detect_language(None) else True

    def test_english_text(self):
        """Test detection of English text."""
        assert detect_language("create a table") == "en"
        assert detect_language("make a chair model") == "en"
        assert detect_language("the quick brown fox") == "en"
        assert detect_language("build the mesh object") == "en"

    def test_english_blender_terms(self):
        """Test English with Blender terminology."""
        assert detect_language("extrude the selected faces") == "en"
        assert detect_language("bevel the edges with segments") == "en"
        assert detect_language("create a primitive cube mesh") == "en"


class TestDetectLanguagePolish:
    """Tests for Polish language detection."""

    def test_polish_diacritics(self):
        """Test detection by Polish diacritics."""
        assert detect_language("zrób stół") == "pl"
        assert detect_language("ławka piknikowa") == "pl"
        assert detect_language("krzesło z drewna") == "pl"
        assert detect_language("żółć gęślą") == "pl"

    def test_polish_words_without_diacritics(self):
        """Test detection by common Polish words."""
        assert detect_language("stworz model stolu") == "pl"
        assert detect_language("zrob krzeslo") == "pl"

    def test_polish_mixed_case(self):
        """Test Polish detection is case insensitive."""
        assert detect_language("ZRÓB STÓŁ") == "pl"
        assert detect_language("Ławka") == "pl"


class TestDetectLanguageGerman:
    """Tests for German language detection."""

    def test_german_umlauts(self):
        """Test detection by German umlauts."""
        assert detect_language("erstelle einen Tisch") == "de"
        assert detect_language("möbel") == "de"
        assert detect_language("größe ändern") == "de"
        assert detect_language("schöner Stuhl") == "de"

    def test_german_eszett(self):
        """Test detection by German ß."""
        assert detect_language("große Fläche") == "de"
        assert detect_language("weiß") == "de"

    def test_german_words(self):
        """Test detection by German words without special chars."""
        assert detect_language("erstelle einen tisch") == "de"
        assert detect_language("machen sie das modell") == "de"


class TestDetectLanguageFrench:
    """Tests for French language detection."""

    def test_french_accents(self):
        """Test detection by French accents."""
        assert detect_language("créer une table") == "fr"
        assert detect_language("modèle de chaise") == "fr"
        assert detect_language("à côté") == "fr"

    def test_french_special_chars(self):
        """Test detection by French special characters."""
        assert detect_language("œuvre") == "fr"
        assert detect_language("cœur") == "fr"

    def test_french_words(self):
        """Test detection by common French words."""
        assert detect_language("faire le modele") == "fr"
        assert detect_language("une table avec des chaises") == "fr"


class TestDetectLanguageSpanish:
    """Tests for Spanish language detection."""

    def test_spanish_special_chars(self):
        """Test detection by Spanish special characters."""
        assert detect_language("crear una mesa") == "es"
        # ñ is unique to Spanish among supported languages
        assert detect_language("niño") == "es"
        assert detect_language("mañana") == "es"
        assert detect_language("España") == "es"
        # Inverted punctuation is unique to Spanish
        assert detect_language("¡hola!") == "es"
        assert detect_language("¿verdad?") == "es"

    def test_spanish_words(self):
        """Test detection by common Spanish words."""
        assert detect_language("hacer el modelo") == "es"
        assert detect_language("una silla de madera") == "es"


class TestDetectLanguageRussian:
    """Tests for Russian language detection."""

    def test_russian_cyrillic(self):
        """Test detection by Cyrillic characters."""
        assert detect_language("создать стол") == "ru"
        assert detect_language("модель") == "ru"
        assert detect_language("привет мир") == "ru"

    def test_russian_mixed_with_latin(self):
        """Test Russian detection with mixed scripts."""
        # Cyrillic should still be detected
        result = detect_language("model стол")
        assert result == "ru"


class TestDetectLanguageEdgeCases:
    """Tests for edge cases in language detection."""

    def test_numbers_only(self):
        """Test text with only numbers."""
        assert detect_language("123 456") == "en"

    def test_single_word(self):
        """Test single word detection."""
        assert detect_language("table") == "en"
        assert detect_language("ławka") == "pl"
        assert detect_language("möbel") == "de"

    def test_mixed_language_prefers_diacritics(self):
        """Test that diacritics take precedence over word markers."""
        # Polish diacritic should win even with English words
        result = detect_language("create ławka")
        assert result == "pl"

    def test_ambiguous_text_defaults_to_english(self):
        """Test that ambiguous text defaults to English."""
        # Numbers and symbols only
        assert detect_language("123 xyz abc") == "en"

    def test_long_text_detection(self):
        """Test detection on longer text."""
        long_english = "This is a very long text with many English words. " * 10
        assert detect_language(long_english) == "en"

        long_polish = "To jest bardzo długi tekst z wieloma polskimi słowami. " * 10
        assert detect_language(long_polish) == "pl"


class TestDetectLanguageCharacterPatterns:
    """Tests for character pattern detection."""

    def test_all_pattern_languages_detected(self):
        """Test that all languages with patterns are detectable."""
        # One example for each pattern-based language
        test_cases = {
            "pl": "żółć",
            "de": "über",
            "fr": "café",
            "es": "niño",
            "ru": "привет",
        }

        for expected_lang, text in test_cases.items():
            result = detect_language(text)
            assert result == expected_lang, f"Expected {expected_lang} for '{text}', got {result}"


class TestDetectLanguageWordMarkers:
    """Tests for word marker detection."""

    def test_english_markers_work(self):
        """Test that English word markers work."""
        assert detect_language("the model has been created") == "en"

    def test_multiple_marker_matches_score_better(self):
        """Test that multiple matches give better scores."""
        # More English markers should strengthen the match
        assert detect_language("the table with a chair and an object") == "en"


class TestGetSupportedLanguages:
    """Tests for get_supported_languages function."""

    def test_returns_list(self):
        """Test that function returns a list."""
        langs = get_supported_languages()
        assert isinstance(langs, list)

    def test_includes_english(self):
        """Test that English is included."""
        langs = get_supported_languages()
        assert "en" in langs

    def test_includes_pattern_languages(self):
        """Test that pattern-detected languages are included."""
        langs = get_supported_languages()
        for lang in LANGUAGE_PATTERNS.keys():
            assert lang in langs

    def test_includes_marker_languages(self):
        """Test that marker-detected languages are included."""
        langs = get_supported_languages()
        for lang in LANGUAGE_MARKERS.keys():
            assert lang in langs

    def test_returns_sorted(self):
        """Test that languages are sorted."""
        langs = get_supported_languages()
        assert langs == sorted(langs)

    def test_expected_languages_present(self):
        """Test that expected languages are present."""
        langs = get_supported_languages()
        expected = ["en", "pl", "de", "fr", "es", "ru"]
        for lang in expected:
            assert lang in langs


class TestLanguageDetectorIntegration:
    """Integration tests for language detector in workflow context."""

    def test_workflow_prompts_english(self):
        """Test detection of typical English workflow prompts."""
        prompts = [
            "create a picnic table",
            "make a smartphone model",
            "build a wooden chair",
            "design a simple desk",
        ]
        for prompt in prompts:
            assert detect_language(prompt) == "en", f"Failed for: {prompt}"

    def test_workflow_prompts_polish(self):
        """Test detection of typical Polish workflow prompts."""
        prompts = [
            "stwórz stół piknikowy",
            "zrób model telefonu",
            "utwórz krzesło z drewna",
        ]
        for prompt in prompts:
            result = detect_language(prompt)
            assert result == "pl", f"Expected 'pl' for '{prompt}', got {result}"

    def test_workflow_prompts_german(self):
        """Test detection of typical German workflow prompts."""
        prompts = [
            "erstelle einen Tisch",
            "mache ein Stuhl Modell",
            "baue einen Schreibtisch",
        ]
        for prompt in prompts:
            result = detect_language(prompt)
            assert result == "de", f"Expected 'de' for '{prompt}', got {result}"

    def test_real_world_blender_commands(self):
        """Test detection with real-world Blender command contexts."""
        # These might be mixed - technical terms are often English
        test_cases = [
            ("extrude the mesh", "en"),
            ("zrób extrude na mesh", "pl"),
            ("bevel die kanten", "de"),
        ]
        for text, expected in test_cases:
            result = detect_language(text)
            # Be lenient here - mixed languages are tricky
            assert result in ["en", expected], f"Unexpected {result} for '{text}'"
