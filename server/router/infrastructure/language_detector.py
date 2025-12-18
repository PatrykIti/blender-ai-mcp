"""
Lightweight language detection for semantic matching.

Uses simple heuristics for fast detection without external dependencies.
Supports: English, Polish, German, French, Spanish, Russian.

TASK-050-2
"""

import re
from typing import Dict, Set


# Language-specific character patterns (diacritics, special chars)
LANGUAGE_PATTERNS: Dict[str, str] = {
    "pl": r"[ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]",  # Polish diacritics
    "de": r"[äöüßÄÖÜ]",  # German umlauts
    "fr": r"[àâçéèêëîïôùûüÿœæÀÂÇÉÈÊËÎÏÔÙÛÜŸŒÆ]",  # French accents
    "es": r"[áéíóúñüÁÉÍÓÚÑÜ¿¡]",  # Spanish
    "ru": r"[а-яА-ЯёЁ]",  # Russian Cyrillic
}

# Common words per language (lowercase)
LANGUAGE_MARKERS: Dict[str, Set[str]] = {
    "en": {
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "must",
        "shall",
        "can",
        "need",
        "create",
        "make",
        "build",
        "add",
        "remove",
        "delete",
        "get",
        "set",
        "update",
        "with",
        "from",
        "for",
        "and",
        "or",
        "not",
        "this",
        "that",
        "these",
        "those",
        "it",
        "its",
        "table",
        "chair",
        "object",
        "mesh",
        "model",
    },
    "pl": {
        "stworz",
        "zrob",
        "utworz",
        "dodaj",
        "usun",
        "jest",
        "sa",
        "byl",
        "byla",
        "bylo",
        "byly",
        "bedzie",
        "beda",
        "ma",
        "maja",
        "mial",
        "miala",
        "moze",
        "moga",
        "musi",
        "musza",
        "stol",
        "krzeslo",
        "obiekt",
        "model",
        "lawka",
        "ogrodowy",
        "piknikowy",
        "dom",
        "budynek",
        "z",
        "na",
        "do",
        "od",
        "dla",
        "i",
        "lub",
        "nie",
        "ten",
        "ta",
        "to",
        "te",
        "tamten",
    },
    "de": {
        "erstelle",
        "erstellen",
        "mache",
        "machen",
        "baue",
        "bauen",
        "ist",
        "sind",
        "war",
        "waren",
        "sein",
        "haben",
        "hat",
        "hatte",
        "werden",
        "wird",
        "wurde",
        "kann",
        "konnen",
        "muss",
        "mussen",
        "der",
        "die",
        "das",
        "ein",
        "eine",
        "einen",
        "einem",
        "einer",
        "und",
        "oder",
        "nicht",
        "mit",
        "von",
        "fur",
        "auf",
        "in",
        "an",
        "tisch",
        "stuhl",
        "objekt",
        "modell",
    },
    "fr": {
        "creer",
        "faire",
        "construire",
        "ajouter",
        "supprimer",
        "est",
        "sont",
        "etait",
        "etaient",
        "etre",
        "avoir",
        "a",
        "avait",
        "sera",
        "seront",
        "peut",
        "peuvent",
        "doit",
        "doivent",
        "le",
        "la",
        "les",
        "un",
        "une",
        "des",
        "et",
        "ou",
        "ne",
        "pas",
        "de",
        "du",
        "pour",
        "avec",
        "dans",
        "sur",
        "table",
        "chaise",
        "objet",
        "modele",
        "pique-nique",
    },
    "es": {
        "crear",
        "hacer",
        "construir",
        "agregar",
        "eliminar",
        "es",
        "son",
        "era",
        "eran",
        "ser",
        "estar",
        "tener",
        "tiene",
        "tenia",
        "sera",
        "seran",
        "puede",
        "pueden",
        "debe",
        "deben",
        "el",
        "la",
        "los",
        "las",
        "un",
        "una",
        "unos",
        "unas",
        "y",
        "o",
        "no",
        "de",
        "del",
        "para",
        "con",
        "en",
        "mesa",
        "silla",
        "objeto",
        "modelo",
    },
}


def detect_language(text: str) -> str:
    """Detect language of text.

    Uses character patterns first (most reliable for non-English),
    then falls back to word markers.

    Args:
        text: Input text to analyze.

    Returns:
        ISO 639-1 language code (e.g., "en", "pl", "de", "fr", "es", "ru").
        Defaults to "en" if no strong match found.
    """
    if not text or not text.strip():
        return "en"

    # Check character patterns first (most reliable for non-English)
    for lang, pattern in LANGUAGE_PATTERNS.items():
        if re.search(pattern, text):
            return lang

    # Normalize text for word matching
    text_lower = text.lower()
    words = set(re.findall(r"\b\w+\b", text_lower))

    if not words:
        return "en"

    # Count word matches for each language
    best_lang = "en"
    best_score = 0.0

    for lang, markers in LANGUAGE_MARKERS.items():
        matches = words & markers
        if not matches:
            continue

        # Calculate score as percentage of query words that match
        score = len(matches) / len(words)

        # Bonus for multiple matches
        if len(matches) >= 2:
            score *= 1.2

        if score > best_score:
            best_score = score
            best_lang = lang

    return best_lang


def get_supported_languages() -> list:
    """Get list of supported language codes.

    Returns:
        List of ISO 639-1 language codes.
    """
    # Combine pattern-detected and marker-detected languages
    langs = set(LANGUAGE_PATTERNS.keys()) | set(LANGUAGE_MARKERS.keys())
    return sorted(langs)
