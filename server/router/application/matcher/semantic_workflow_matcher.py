"""
Semantic Workflow Matcher.

Combines workflow matching with generalization capabilities.
When no exact workflow match exists, it can:
1. Find similar workflows by semantic similarity
2. Combine rules from multiple workflows
3. Generate hybrid workflows for unknown objects

TASK-046-3
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple, Optional, TYPE_CHECKING

from server.router.application.classifier.workflow_intent_classifier import (
    WorkflowIntentClassifier,
)
from server.router.infrastructure.config import RouterConfig

if TYPE_CHECKING:
    from server.router.application.workflows.registry import WorkflowRegistry

logger = logging.getLogger(__name__)


@dataclass
class MatchResult:
    """Result of workflow matching.

    Attributes:
        workflow_name: Name of matched workflow (or None if no match).
        confidence: Confidence score (0.0 to 1.0).
        match_type: Type of match - exact, semantic, generalized, or none.
        confidence_level: Confidence classification - HIGH, MEDIUM, LOW, NONE.
        requires_adaptation: True if workflow should be adapted based on confidence.
        similar_workflows: List of similar workflows for generalization.
        applied_rules: List of rules applied from similar workflows.
        metadata: Additional metadata about the match.
    """

    workflow_name: Optional[str] = None
    confidence: float = 0.0
    match_type: str = "none"  # exact, semantic, generalized, none, error
    confidence_level: str = "NONE"  # HIGH, MEDIUM, LOW, NONE (TASK-051)
    requires_adaptation: bool = False  # True if workflow should be adapted (TASK-051)
    similar_workflows: List[Tuple[str, float]] = field(default_factory=list)
    applied_rules: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_match(self) -> bool:
        """Check if a match was found."""
        return self.workflow_name is not None and self.match_type != "none"

    def is_exact(self) -> bool:
        """Check if match is exact keyword match."""
        return self.match_type == "exact"

    def is_generalized(self) -> bool:
        """Check if match is generalized from similar workflows."""
        return self.match_type == "generalized"

    def needs_adaptation(self) -> bool:
        """Check if workflow needs adaptation based on confidence.

        TASK-051: Only HIGH confidence matches get full workflow.
        MEDIUM/LOW confidence matches require adaptation.
        """
        return self.requires_adaptation and self.confidence_level != "HIGH"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "workflow_name": self.workflow_name,
            "confidence": self.confidence,
            "match_type": self.match_type,
            "confidence_level": self.confidence_level,
            "requires_adaptation": self.requires_adaptation,
            "similar_workflows": self.similar_workflows,
            "applied_rules": self.applied_rules,
            "metadata": self.metadata,
        }


class SemanticWorkflowMatcher:
    """Matches prompts to workflows using semantic understanding.

    Matching hierarchy:
    1. Exact keyword match (fastest, highest confidence)
    2. Semantic similarity match (LaBSE embeddings)
    3. Generalization from similar workflows (combines knowledge)

    Example:
        ```python
        matcher = SemanticWorkflowMatcher(config)
        matcher.initialize(registry)

        result = matcher.match("create a chair")
        # If no chair_workflow exists, might return:
        # MatchResult(
        #     workflow_name="table_workflow",
        #     confidence=0.72,
        #     match_type="generalized",
        #     similar_workflows=[("table_workflow", 0.72), ("tower_workflow", 0.45)]
        # )
        ```
    """

    def __init__(
        self,
        config: Optional[RouterConfig] = None,
        registry: Optional["WorkflowRegistry"] = None,
        classifier: Optional[WorkflowIntentClassifier] = None,
    ):
        """Initialize matcher.

        Args:
            config: Router configuration.
            registry: Workflow registry (can be set later via initialize).
            classifier: WorkflowIntentClassifier instance (injected via DI).
                       If None, creates a new instance (fallback for tests).
        """
        self._config = config or RouterConfig()
        self._registry = registry
        # Use injected classifier or create new (fallback for tests)
        self._classifier = classifier or WorkflowIntentClassifier(config=self._config)
        self._is_initialized = False

    def initialize(self, registry: "WorkflowRegistry") -> None:
        """Initialize with workflow registry.

        This must be called before matching. It loads workflow embeddings
        for semantic matching.

        Args:
            registry: Workflow registry to use.
        """
        self._registry = registry

        # Build workflow dict for classifier
        workflows = {}
        for name in registry.get_all_workflows():
            workflow = registry.get_workflow(name)
            if workflow:
                workflows[name] = workflow
            else:
                definition = registry.get_definition(name)
                if definition:
                    workflows[name] = definition

        # Load embeddings
        self._classifier.load_workflow_embeddings(workflows)
        self._is_initialized = True

        logger.info(
            f"SemanticWorkflowMatcher initialized with {len(workflows)} workflows"
        )

    def is_initialized(self) -> bool:
        """Check if matcher is initialized."""
        return self._is_initialized

    def match(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> MatchResult:
        """Match prompt to workflow.

        Tries matching in order:
        1. Exact keyword match (from WorkflowRegistry)
        2. Semantic similarity match (LaBSE embeddings)
        3. Generalization from similar workflows

        Args:
            prompt: User prompt or intent.
            context: Optional scene context (mode, dimensions, etc.).

        Returns:
            MatchResult with workflow and confidence.
        """
        if not self._is_initialized or not self._registry:
            return MatchResult(
                match_type="error",
                metadata={"error": "Matcher not initialized"},
            )

        # Step 1: Try exact keyword match
        keyword_match = self._registry.find_by_keywords(prompt)
        if keyword_match:
            return MatchResult(
                workflow_name=keyword_match,
                confidence=1.0,
                match_type="exact",
                confidence_level="HIGH",
                requires_adaptation=False,  # Exact matches don't need adaptation
                metadata={"matched_by": "keyword"},
            )

        # Step 2: Try pattern match
        pattern_match = self._match_by_pattern(prompt, context)
        if pattern_match:
            return MatchResult(
                workflow_name=pattern_match,
                confidence=0.95,
                match_type="exact",
                confidence_level="HIGH",
                requires_adaptation=False,  # Pattern matches don't need adaptation
                metadata={"matched_by": "pattern"},
            )

        # Step 3: Try semantic similarity with confidence levels (TASK-051)
        confidence_result = self._classifier.find_best_match_with_confidence(prompt)
        confidence_level = confidence_result.get("confidence_level", "NONE")
        workflow_id = confidence_result.get("workflow_id")
        score = confidence_result.get("score", 0.0)

        # If we have a match (any confidence level except NONE with no workflow)
        if workflow_id and confidence_level != "NONE":
            return MatchResult(
                workflow_name=workflow_id,
                confidence=score,
                match_type="semantic",
                confidence_level=confidence_level,
                requires_adaptation=confidence_level != "HIGH",  # TASK-051
                metadata={
                    "matched_by": "embedding",
                    "source_type": confidence_result.get("source_type"),
                    "matched_text": confidence_result.get("matched_text"),
                    "language_detected": confidence_result.get("language_detected"),
                },
            )

        # Step 4: Check fallback candidates for LOW confidence or NONE
        fallback_candidates = confidence_result.get("fallback_candidates", [])
        if fallback_candidates and self._config.enable_generalization:
            # Use the best fallback candidate if above generalization threshold
            best_fallback = fallback_candidates[0]
            if best_fallback["score"] >= self._config.generalization_threshold:
                similar = [
                    (c["workflow_id"], c["score"])
                    for c in fallback_candidates
                    if c["score"] >= self._config.generalization_threshold
                ]
                return self._generalize(prompt, similar, context)

        # Step 5: Try generalization (legacy fallback if enabled)
        if self._config.enable_generalization:
            similar = self._classifier.get_generalization_candidates(
                prompt,
                min_similarity=self._config.generalization_threshold,
                max_candidates=3,
            )
            if similar:
                return self._generalize(prompt, similar, context)

        # No match found
        return MatchResult(match_type="none", confidence_level="NONE")

    def _match_by_pattern(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]],
    ) -> Optional[str]:
        """Match by detected geometry pattern.

        Args:
            prompt: User prompt.
            context: Scene context with potential pattern info.

        Returns:
            Matched workflow name or None.
        """
        if not context:
            return None

        # Check if pattern was detected by analyzer
        detected_pattern = context.get("detected_pattern")
        if detected_pattern and self._registry:
            return self._registry.find_by_pattern(detected_pattern)

        return None

    def _generalize(
        self,
        prompt: str,
        similar_workflows: List[Tuple[str, float]],
        context: Optional[Dict[str, Any]],
    ) -> MatchResult:
        """Generalize from similar workflows.

        Creates a hybrid approach by combining rules from
        similar workflows weighted by similarity.

        Args:
            prompt: User prompt.
            similar_workflows: List of (workflow_name, similarity) tuples.
            context: Scene context.

        Returns:
            MatchResult with generalized workflow.
        """
        # Use the most similar workflow as base
        base_workflow, base_score = similar_workflows[0]

        # Collect rules from all similar workflows
        applied_rules = []
        for name, score in similar_workflows:
            workflow = self._registry.get_workflow(name) if self._registry else None
            if workflow:
                applied_rules.append(f"proportions_from:{name}:{score:.2f}")

        # Reduce confidence for generalized matches
        # (they're less certain than direct matches)
        generalized_confidence = base_score * 0.8

        # Determine confidence level for generalized result (TASK-051)
        confidence_level = self._classifier.get_confidence_level(generalized_confidence)

        return MatchResult(
            workflow_name=base_workflow,
            confidence=generalized_confidence,
            match_type="generalized",
            confidence_level=confidence_level,
            requires_adaptation=True,  # Generalized matches always need adaptation
            similar_workflows=similar_workflows,
            applied_rules=applied_rules,
            metadata={
                "base_workflow": base_workflow,
                "generalized_from": [w for w, _ in similar_workflows],
                "original_prompt": prompt,
            },
        )

    def find_similar(
        self,
        prompt: str,
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        """Find workflows similar to prompt.

        Public API for exploring workflow similarities.

        Args:
            prompt: User prompt.
            top_k: Number of results.

        Returns:
            List of (workflow_name, similarity) tuples.
        """
        if not self._is_initialized:
            return []
        return self._classifier.find_similar(prompt, top_k=top_k)

    def get_match_explanation(self, result: MatchResult) -> str:
        """Get human-readable explanation of match result.

        Args:
            result: Match result to explain.

        Returns:
            Explanation string.
        """
        if result.match_type == "exact":
            return f"Exact match: '{result.workflow_name}' (keyword match)"

        elif result.match_type == "semantic":
            return (
                f"Semantic match: '{result.workflow_name}' "
                f"(similarity: {result.confidence:.1%})"
            )

        elif result.match_type == "generalized":
            sources = ", ".join(
                f"{w}({s:.0%})" for w, s in result.similar_workflows[:3]
            )
            return (
                f"Generalized match: '{result.workflow_name}' "
                f"(confidence: {result.confidence:.1%}, based on: {sources})"
            )

        elif result.match_type == "error":
            error = result.metadata.get("error", "Unknown error")
            return f"Error: {error}"

        else:
            return "No matching workflow found"

    def get_info(self) -> Dict[str, Any]:
        """Get matcher information.

        Returns:
            Dictionary with matcher status.
        """
        return {
            "is_initialized": self._is_initialized,
            "classifier_info": self._classifier.get_info(),
            "config": {
                "workflow_similarity_threshold": self._config.workflow_similarity_threshold,
                "generalization_threshold": self._config.generalization_threshold,
                "enable_generalization": self._config.enable_generalization,
            },
        }
