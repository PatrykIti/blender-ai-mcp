"""
Modifier Extractor for Ensemble Matching System.

TASK-053-6: Consolidates modifier extraction logic from router.py and registry.py
into standalone component implementing IModifierExtractor interface.

Extracts parametric modifiers from user prompts based on workflow definitions.
"""

from typing import Dict, Any, List, Optional, TYPE_CHECKING
import logging

from server.router.domain.interfaces.matcher import IModifierExtractor
from server.router.domain.entities.ensemble import ModifierResult

if TYPE_CHECKING:
    from server.router.application.workflows.registry import WorkflowRegistry

logger = logging.getLogger(__name__)


class ModifierExtractor(IModifierExtractor):
    """Extracts parametric modifiers from prompts.

    Consolidates logic from:
    - SupervisorRouter._build_variables() (router.py:601-630)
    - WorkflowRegistry._extract_modifiers() (registry.py:283-308)

    Scans prompt for modifier keywords and builds variable overrides.
    This ensures modifiers are ALWAYS extracted regardless of which
    matcher wins the ensemble vote.

    Example:
        >>> extractor = ModifierExtractor(registry)
        >>> result = extractor.extract("proste nogi", "table_workflow")
        >>> print(result.modifiers)  # {"leg_style": "straight"}
        >>> print(result.matched_keywords)  # ["proste nogi"]
    """

    def __init__(self, registry: "WorkflowRegistry"):
        """Initialize modifier extractor.

        Args:
            registry: Workflow registry for accessing workflow definitions.
        """
        self._registry = registry

    def extract(self, prompt: str, workflow_name: str) -> ModifierResult:
        """Extract modifiers from prompt for given workflow.

        Scans prompt for modifier keywords defined in workflow.modifiers.
        Returns merged defaults + modifier overrides.

        Args:
            prompt: User prompt/goal (e.g., "proste nogi").
            workflow_name: Target workflow name (e.g., "table_workflow").

        Returns:
            ModifierResult with:
            - modifiers: Dict of variable overrides (defaults + matched modifiers)
            - matched_keywords: List of keywords that matched
            - confidence_map: Dict mapping keywords to confidence (1.0 for exact match)

        Example:
            >>> result = extractor.extract("proste nogi", "table_workflow")
            >>> result.modifiers  # {"leg_style": "straight", ...defaults...}
            >>> result.matched_keywords  # ["proste nogi"]
            >>> result.confidence_map  # {"proste nogi": 1.0}
        """
        # Get workflow definition
        definition = self._registry.get_definition(workflow_name)
        if not definition:
            logger.warning(f"No definition found for workflow: {workflow_name}")
            return ModifierResult(
                modifiers={},
                matched_keywords=[],
                confidence_map={}
            )

        # Start with defaults
        modifiers = {}
        if definition.defaults:
            modifiers = dict(definition.defaults)

        # Extract modifier overrides
        matched_keywords = []
        confidence_map = {}

        if prompt and definition.modifiers:
            prompt_lower = prompt.lower()

            for keyword, values in definition.modifiers.items():
                if keyword.lower() in prompt_lower:
                    logger.debug(f"Modifier matched: '{keyword}' → {values}")
                    modifiers.update(values)
                    matched_keywords.append(keyword)
                    confidence_map[keyword] = 1.0  # Exact match = full confidence

        return ModifierResult(
            modifiers=modifiers,
            matched_keywords=matched_keywords,
            confidence_map=confidence_map
        )
