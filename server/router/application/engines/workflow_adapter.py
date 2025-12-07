"""
Workflow Adaptation Engine.

Adapts workflow steps based on confidence level.
TASK-051: Confidence-Based Workflow Adaptation.

Adaptation Strategy:
- HIGH (≥0.90): Execute ALL steps (no adaptation)
- MEDIUM (≥0.75): Core steps + semantically relevant optional steps
- LOW (≥0.60): Core steps only (skip all optional)
- NONE (<0.60): Core steps only (fallback)
"""

import logging
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, TYPE_CHECKING

from server.router.application.workflows.base import WorkflowStep, WorkflowDefinition
from server.router.infrastructure.config import RouterConfig

if TYPE_CHECKING:
    from server.router.application.classifier.workflow_intent_classifier import (
        WorkflowIntentClassifier,
    )

logger = logging.getLogger(__name__)


@dataclass
class AdaptationResult:
    """Result of workflow adaptation.

    Attributes:
        original_step_count: Number of steps before adaptation.
        adapted_step_count: Number of steps after adaptation.
        skipped_steps: List of step descriptions that were skipped.
        included_optional: List of optional steps that were included.
        confidence_level: Confidence level used for adaptation.
        adaptation_strategy: Strategy used (FULL, FILTERED, CORE_ONLY).
    """

    original_step_count: int = 0
    adapted_step_count: int = 0
    skipped_steps: List[str] = field(default_factory=list)
    included_optional: List[str] = field(default_factory=list)
    confidence_level: str = "NONE"
    adaptation_strategy: str = "CORE_ONLY"  # FULL, FILTERED, CORE_ONLY

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "original_step_count": self.original_step_count,
            "adapted_step_count": self.adapted_step_count,
            "skipped_steps": self.skipped_steps,
            "included_optional": self.included_optional,
            "confidence_level": self.confidence_level,
            "adaptation_strategy": self.adaptation_strategy,
        }


class WorkflowAdapter:
    """Adapts workflow steps based on confidence level.

    Workflow Adaptation Engine that filters workflow steps based on:
    1. Confidence level of the match
    2. Tag matching between optional steps and user prompt
    3. Semantic similarity (fallback for steps without tags)

    Example:
        ```python
        adapter = WorkflowAdapter(config)
        steps, result = adapter.adapt(
            definition=picnic_table_workflow,
            confidence_level="LOW",
            user_prompt="simple table with 4 legs",
        )
        # Returns only core steps (table top, legs, frame)
        # Skips optional bench steps
        ```
    """

    def __init__(
        self,
        config: Optional[RouterConfig] = None,
        classifier: Optional["WorkflowIntentClassifier"] = None,
    ):
        """Initialize adapter.

        Args:
            config: Router configuration.
            classifier: WorkflowIntentClassifier for semantic filtering (optional).
        """
        self._config = config or RouterConfig()
        self._classifier = classifier
        self._semantic_threshold = getattr(
            self._config, "adaptation_semantic_threshold", 0.6
        )

    def adapt(
        self,
        definition: WorkflowDefinition,
        confidence_level: str,
        user_prompt: str,
    ) -> Tuple[List[WorkflowStep], AdaptationResult]:
        """Adapt workflow steps based on confidence level.

        Args:
            definition: Full workflow definition.
            confidence_level: Match confidence level (HIGH, MEDIUM, LOW, NONE).
            user_prompt: Original user prompt for relevance filtering.

        Returns:
            Tuple of (adapted_steps, adaptation_result).
        """
        all_steps = definition.steps
        result = AdaptationResult(
            original_step_count=len(all_steps),
            confidence_level=confidence_level,
        )

        # HIGH confidence: return all steps
        if confidence_level == "HIGH":
            result.adapted_step_count = len(all_steps)
            result.adaptation_strategy = "FULL"
            logger.debug(
                f"HIGH confidence - returning all {len(all_steps)} steps "
                f"for workflow '{definition.name}'"
            )
            return all_steps, result

        # Separate core and optional steps
        core_steps = [s for s in all_steps if not s.optional]
        optional_steps = [s for s in all_steps if s.optional]

        # LOW or NONE confidence: core steps only
        if confidence_level in ("LOW", "NONE"):
            result.adapted_step_count = len(core_steps)
            result.adaptation_strategy = "CORE_ONLY"
            result.skipped_steps = [
                s.description or s.tool for s in optional_steps
            ]
            logger.info(
                f"{confidence_level} confidence - returning {len(core_steps)} core steps, "
                f"skipping {len(optional_steps)} optional steps "
                f"for workflow '{definition.name}'"
            )
            return core_steps, result

        # MEDIUM confidence: core + semantically relevant optional steps
        relevant_optional = self._filter_by_relevance(optional_steps, user_prompt)
        adapted_steps = core_steps + relevant_optional

        result.adapted_step_count = len(adapted_steps)
        result.adaptation_strategy = "FILTERED"
        result.included_optional = [
            s.description or s.tool for s in relevant_optional
        ]
        result.skipped_steps = [
            s.description or s.tool
            for s in optional_steps
            if s not in relevant_optional
        ]

        logger.info(
            f"MEDIUM confidence - returning {len(core_steps)} core + "
            f"{len(relevant_optional)} relevant optional steps, "
            f"skipping {len(result.skipped_steps)} optional steps "
            f"for workflow '{definition.name}'"
        )

        return adapted_steps, result

    def _filter_by_relevance(
        self,
        optional_steps: List[WorkflowStep],
        user_prompt: str,
    ) -> List[WorkflowStep]:
        """Filter optional steps by relevance to user prompt.

        Uses fallback strategy:
        1. Tag matching (fast, keyword-based)
        2. Semantic similarity (slower, embedding-based)

        Args:
            optional_steps: List of optional workflow steps.
            user_prompt: User's original prompt.

        Returns:
            List of relevant optional steps.
        """
        relevant = []
        prompt_lower = user_prompt.lower()

        for step in optional_steps:
            # 1. Tag matching (fast)
            if step.tags:
                if any(tag.lower() in prompt_lower for tag in step.tags):
                    relevant.append(step)
                    logger.debug(
                        f"Step '{step.tool}' included by tag match: {step.tags}"
                    )
                    continue

            # 2. Semantic similarity (fallback for steps without tags or no tag match)
            if step.description and self._classifier:
                try:
                    similarity = self._classifier.similarity(
                        user_prompt, step.description
                    )
                    if similarity >= self._semantic_threshold:
                        relevant.append(step)
                        logger.debug(
                            f"Step '{step.tool}' included by semantic similarity: "
                            f"{similarity:.2f} >= {self._semantic_threshold}"
                        )
                except Exception as e:
                    logger.warning(f"Semantic similarity failed: {e}")

        return relevant

    def should_adapt(
        self,
        confidence_level: str,
        definition: WorkflowDefinition,
    ) -> bool:
        """Check if workflow needs adaptation.

        Args:
            confidence_level: Match confidence level.
            definition: Workflow definition.

        Returns:
            True if adaptation should be applied.
        """
        # No adaptation for HIGH confidence
        if confidence_level == "HIGH":
            return False

        # Check if workflow has any optional steps
        has_optional = any(s.optional for s in definition.steps)
        return has_optional

    def get_info(self):
        """Get adapter information.

        Returns:
            Dictionary with adapter configuration.
        """
        return {
            "semantic_threshold": self._semantic_threshold,
            "has_classifier": self._classifier is not None,
            "config": {
                "enable_workflow_adaptation": getattr(
                    self._config, "enable_workflow_adaptation", True
                ),
                "adaptation_semantic_threshold": self._semantic_threshold,
            },
        }
