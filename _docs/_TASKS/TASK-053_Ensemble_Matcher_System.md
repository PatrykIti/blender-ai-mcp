# TASK-053: Ensemble Matcher System

**Priority:** 🔴 High
**Category:** Router Supervisor Enhancement
**Estimated Effort:** Large
**Dependencies:** TASK-046 (Semantic Generalization), TASK-051 (Confidence-Based Adaptation), TASK-052 (Parametric Variables)
**Status:** ✅ **DONE**
**Completed:** 2025-12-11

---

## Overview

Replace the current fallback-based matching system with an **Ensemble Matcher** that runs all matchers in parallel and aggregates results using weighted consensus. This fixes the critical bug where parametric modifiers (e.g., "straight legs") are not applied when semantic matcher wins over keyword matcher.

**Current Problem:**
```
User: "simple table with straight legs"
→ Semantic match (84.3%) wins
→ Modifiers from keyword matcher NOT extracted
→ Legs are angled instead of straight (0°)
```

**Solution:**
All matchers run in parallel, results are aggregated, and modifiers are ALWAYS extracted regardless of which matcher "wins" the workflow selection.

---

## Architecture

### Current System (Fallback/OR Logic)

**Location:** `server/router/application/matcher/semantic_workflow_matcher.py`

```
Keyword Match? ─Yes→ Return workflow (early return line 191-199)
      │
      No
      ↓
Pattern Match? ─Yes→ Return workflow (early return line 203-211)
      │
      No
      ↓
Semantic Match? ─Yes→ Return workflow (line 214-233)
      │
      No
      ↓
Generalization? ─Yes→ Return workflow (line 236-256)
      │
      No
      ↓
No match
```

**Problem:** Each matcher returns early, so:
- If semantic wins → keyword modifiers are NOT checked
- If keyword wins → other matchers never run (no fallback data)

### New System (Ensemble/Parallel)

```
┌─────────────────────────────────────────────────────────────┐
│                    ENSEMBLE MATCHER                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   KEYWORD    │  │   SEMANTIC   │  │   PATTERN    │      │
│  │   MATCHER    │  │   MATCHER    │  │   MATCHER    │      │
│  │   (0.40)     │  │   (0.40)     │  │   (0.15)     │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │               │
│         └────────────┬────┴────────────────┘               │
│                      ↓                                      │
│         ┌────────────────────────┐                         │
│         │    MODIFIER            │                         │
│         │    EXTRACTOR           │                         │
│         │ Always extracts mods   │                         │
│         └────────────┬───────────┘                         │
│                      ↓                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              WEIGHTED AGGREGATOR                     │   │
│  │  final_score = Σ(matcher_confidence × weight)        │   │
│  └─────────────────────────────────────────────────────┘   │
│                      ↓                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              ENSEMBLE RESULT                         │   │
│  │  workflow: picnic_table_workflow                     │   │
│  │  final_score: 0.768                                  │   │
│  │  modifiers: {leg_angle_left: 0, leg_angle_right: 0}  │   │
│  │  confidence_level: HIGH                              │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Current Code Analysis

### Existing Components (to be refactored/replaced)

| Component | Current Location | Current State |
|-----------|------------------|---------------|
| `MatchResult` | `semantic_workflow_matcher.py:29-83` | Dataclass - **KEEP & EXTEND** |
| `SemanticWorkflowMatcher` | `semantic_workflow_matcher.py:86-404` | Class - **REFACTOR** |
| `_build_variables()` | `router.py:601-630` | Method - **EXTRACT TO ModifierExtractor** |
| `_extract_modifiers()` | `registry.py:283-308` | Method - **MIGRATE TO ModifierExtractor** |
| `WorkflowAdapter` | `workflow_adapter.py` | Class - **UPDATE FOR EnsembleResult** |

### Existing Tests (to be updated)

| Test File | What to Update |
|-----------|----------------|
| `tests/unit/router/application/matcher/test_semantic_workflow_matcher.py` | Update imports, add ensemble tests |
| `tests/unit/router/application/test_supervisor_router.py` | Update `set_current_goal` tests |
| `tests/unit/router/application/test_workflow_adapter.py` | Add `EnsembleResult` tests |

---

## Matcher Weights

| Matcher | Weight | Rationale |
|---------|--------|-----------|
| **Keyword** | 0.40 | Most precise, low false positive rate |
| **Semantic** | 0.40 | Most flexible, context-aware |
| **Pattern** | 0.15 | Geometry-aware, very confident when triggered |

### Score Calculation

```python
final_score = (
    keyword_confidence × 0.40 +
    semantic_confidence × 0.40 +
    pattern_confidence × 0.15
)

# Pattern bonus: if pattern matcher fires, boost by 1.3×
if pattern_confidence > 0:
    final_score *= 1.3
```

### Example

```
User: "simple table with straight legs"

Matcher Results:
  keyword:  picnic_table_workflow (0.0)  - no exact keyword match
  semantic: picnic_table_workflow (0.84)
  pattern:  None (0.0)
  modifier: ["simple", "straight legs"] extracted

Aggregation:
  picnic_table_workflow = 0.0×0.40 + 0.84×0.40 + 0.0×0.15 = 0.336

Final Result:
  workflow: picnic_table_workflow
  modifiers: {leg_angle_left: 0, leg_angle_right: 0}  ← ALWAYS APPLIED
```

---

## Sub-Tasks

### TASK-053-1: Domain Entities

**Status:** ✅ Done

Create domain entities for ensemble matching. **Note:** `MatchResult` already exists - we extend it and create new entities.

```python
# server/router/domain/entities/ensemble.py

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class MatcherResult:
    """Result from a single matcher (individual matcher output).

    NOTE: This is different from existing MatchResult in semantic_workflow_matcher.py.
    MatchResult = final result from SemanticWorkflowMatcher
    MatcherResult = intermediate result from individual IMatcher
    """
    matcher_name: str
    workflow_name: Optional[str]
    confidence: float
    weight: float  # Matcher's weight for aggregation
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModifierResult:
    """Extracted modifiers from user prompt."""
    modifiers: Dict[str, Any]
    matched_keywords: List[str]
    confidence_map: Dict[str, float]


@dataclass
class EnsembleResult:
    """Aggregated result from all matchers.

    This is the NEW primary result type for workflow matching.
    Replaces MatchResult as the output of the matching pipeline.
    """
    workflow_name: Optional[str]
    final_score: float
    confidence_level: str  # HIGH, MEDIUM, LOW, NONE
    modifiers: Dict[str, Any]  # ← KEY: Always populated by ModifierExtractor
    matcher_contributions: Dict[str, float]  # matcher_name → weighted_score
    requires_adaptation: bool
    composition_mode: bool = False
    extra_workflows: List[str] = field(default_factory=list)

    # Compatibility with existing MatchResult API
    @property
    def confidence(self) -> float:
        """Alias for final_score (backward compatibility)."""
        return self.final_score

    def is_match(self) -> bool:
        """Check if a match was found."""
        return self.workflow_name is not None and self.final_score > 0

    def needs_adaptation(self) -> bool:
        """Check if workflow needs adaptation based on confidence."""
        return self.requires_adaptation and self.confidence_level != "HIGH"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "workflow_name": self.workflow_name,
            "final_score": self.final_score,
            "confidence_level": self.confidence_level,
            "modifiers": self.modifiers,
            "matcher_contributions": self.matcher_contributions,
            "requires_adaptation": self.requires_adaptation,
            "composition_mode": self.composition_mode,
            "extra_workflows": self.extra_workflows,
        }
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/router/domain/entities/ensemble.py` | `MatcherResult`, `ModifierResult`, `EnsembleResult` dataclasses |
| Domain | `server/router/domain/entities/__init__.py` | Export: `MatcherResult`, `ModifierResult`, `EnsembleResult` |
| Tests | `tests/unit/router/domain/test_entities.py` | Add tests for new entities |

---

### TASK-053-2: Matcher Interface

**Status:** ✅ Done

Define abstract interface for all matchers.

```python
# server/router/domain/interfaces/matcher.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from server.router.domain.entities.ensemble import MatcherResult, ModifierResult


class IMatcher(ABC):
    """Abstract interface for workflow matchers.

    All matchers implement this interface to enable ensemble matching.
    Each matcher runs independently and returns a MatcherResult.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Matcher name for logging and aggregation."""
        pass

    @property
    @abstractmethod
    def weight(self) -> float:
        """Weight for score aggregation (0.0-1.0).

        Higher weight = more influence on final decision.
        Sum of all weights should be ~1.0 for normalized scores.
        """
        pass

    @abstractmethod
    def match(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> MatcherResult:
        """Match prompt to workflow.

        Args:
            prompt: User prompt/goal.
            context: Optional scene context dict.

        Returns:
            MatcherResult with workflow and confidence.
        """
        pass


class IModifierExtractor(ABC):
    """Interface for modifier/tag extraction.

    Extracts parametric modifiers from user prompt for a given workflow.
    Always runs regardless of which matcher "wins" the workflow selection.
    """

    @abstractmethod
    def extract(self, prompt: str, workflow_name: str) -> ModifierResult:
        """Extract modifiers from prompt for given workflow.

        Args:
            prompt: User prompt.
            workflow_name: Target workflow to check modifiers for.

        Returns:
            ModifierResult with extracted parameters.
        """
        pass
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/router/domain/interfaces/matcher.py` | `IMatcher`, `IModifierExtractor` ABCs |
| Domain | `server/router/domain/interfaces/__init__.py` | Export: `IMatcher`, `IModifierExtractor` |
| Tests | `tests/unit/router/domain/test_interfaces.py` | Add interface contract tests |

---

### TASK-053-3: Keyword Matcher Refactor

**Status:** ✅ Done

Extract keyword matching logic from `SemanticWorkflowMatcher` into standalone `KeywordMatcher` implementing `IMatcher`.

```python
# server/router/application/matcher/keyword_matcher.py

from typing import Dict, Any, Optional, TYPE_CHECKING

from server.router.domain.interfaces.matcher import IMatcher
from server.router.domain.entities.ensemble import MatcherResult

if TYPE_CHECKING:
    from server.router.application.workflows.registry import WorkflowRegistry


class KeywordMatcher(IMatcher):
    """Matches workflows by trigger keywords.

    Extracts keyword matching logic from SemanticWorkflowMatcher.
    Uses WorkflowRegistry.find_by_keywords() for matching.
    """

    def __init__(self, registry: "WorkflowRegistry", weight: float = 0.40):
        """Initialize matcher.

        Args:
            registry: Workflow registry for keyword lookup.
            weight: Weight for ensemble aggregation (default 0.40).
        """
        self._registry = registry
        self._weight = weight

    @property
    def name(self) -> str:
        return "keyword"

    @property
    def weight(self) -> float:
        return self._weight

    def match(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> MatcherResult:
        """Match prompt by keywords.

        Delegates to WorkflowRegistry.find_by_keywords().
        Returns confidence 1.0 for exact keyword matches.
        """
        workflow_name = self._registry.find_by_keywords(prompt)

        if workflow_name:
            return MatcherResult(
                matcher_name=self.name,
                workflow_name=workflow_name,
                confidence=1.0,
                weight=self.weight,
                metadata={"matched_by": "keyword"}
            )

        return MatcherResult(
            matcher_name=self.name,
            workflow_name=None,
            confidence=0.0,
            weight=self.weight
        )
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Application | `server/router/application/matcher/keyword_matcher.py` | `KeywordMatcher` implementing `IMatcher` |
| Tests | `tests/unit/router/application/matcher/test_keyword_matcher.py` | Matcher tests |

---

### TASK-053-4: Semantic Matcher Refactor

**Status:** ✅ Done

**IMPORTANT:** This is a refactor, NOT a replacement. Keep existing `SemanticWorkflowMatcher` for backward compatibility, create new `SemanticMatcher` implementing `IMatcher`.

```python
# server/router/application/matcher/semantic_matcher.py

from typing import Dict, Any, Optional, TYPE_CHECKING
import logging

from server.router.domain.interfaces.matcher import IMatcher
from server.router.domain.entities.ensemble import MatcherResult
from server.router.infrastructure.config import RouterConfig

if TYPE_CHECKING:
    from server.router.application.classifier.workflow_intent_classifier import (
        WorkflowIntentClassifier,
    )
    from server.router.application.workflows.registry import WorkflowRegistry

logger = logging.getLogger(__name__)


class SemanticMatcher(IMatcher):
    """Matches workflows using LaBSE embeddings.

    Wrapper around WorkflowIntentClassifier for IMatcher interface.
    Does NOT include keyword matching (that's KeywordMatcher's job).
    """

    def __init__(
        self,
        classifier: "WorkflowIntentClassifier",
        registry: "WorkflowRegistry",
        config: Optional[RouterConfig] = None,
        weight: float = 0.40,
    ):
        """Initialize matcher.

        Args:
            classifier: WorkflowIntentClassifier for semantic matching.
            registry: Workflow registry for workflow info.
            config: Router configuration.
            weight: Weight for ensemble aggregation (default 0.40).
        """
        self._classifier = classifier
        self._registry = registry
        self._config = config or RouterConfig()
        self._weight = weight
        self._is_initialized = False

    @property
    def name(self) -> str:
        return "semantic"

    @property
    def weight(self) -> float:
        return self._weight

    def initialize(self, registry: "WorkflowRegistry") -> None:
        """Initialize embeddings for all workflows.

        Must be called before matching.
        """
        workflows = {}
        for name in registry.get_all_workflows():
            workflow = registry.get_workflow(name)
            if workflow:
                workflows[name] = workflow
            else:
                definition = registry.get_definition(name)
                if definition:
                    workflows[name] = definition

        self._classifier.load_workflow_embeddings(workflows)
        self._is_initialized = True
        logger.info(f"SemanticMatcher initialized with {len(workflows)} workflows")

    def is_initialized(self) -> bool:
        """Check if matcher is initialized."""
        return self._is_initialized

    def match(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> MatcherResult:
        """Match prompt using semantic similarity.

        Uses LaBSE embeddings via WorkflowIntentClassifier.
        Does NOT check keywords (that's KeywordMatcher's responsibility).
        """
        if not self._is_initialized:
            logger.warning("SemanticMatcher not initialized, returning no match")
            return MatcherResult(
                matcher_name=self.name,
                workflow_name=None,
                confidence=0.0,
                weight=self.weight,
                metadata={"error": "Not initialized"}
            )

        # Use classifier's find_best_match_with_confidence
        result = self._classifier.find_best_match_with_confidence(prompt)

        workflow_id = result.get("workflow_id")
        score = result.get("score", 0.0)
        confidence_level = result.get("confidence_level", "NONE")

        # Only return match if above threshold and not NONE
        if workflow_id and confidence_level != "NONE":
            return MatcherResult(
                matcher_name=self.name,
                workflow_name=workflow_id,
                confidence=score,
                weight=self.weight,
                metadata={
                    "confidence_level": confidence_level,
                    "source_type": result.get("source_type"),
                    "matched_text": result.get("matched_text"),
                    "language_detected": result.get("language_detected"),
                }
            )

        return MatcherResult(
            matcher_name=self.name,
            workflow_name=None,
            confidence=0.0,
            weight=self.weight,
            metadata={"confidence_level": confidence_level}
        )
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Application | `server/router/application/matcher/semantic_matcher.py` | `SemanticMatcher` implementing `IMatcher` |
| Tests | `tests/unit/router/application/matcher/test_semantic_matcher.py` | Matcher tests (NEW file, separate from existing) |

---

### TASK-053-5: Pattern Matcher Refactor

**Status:** ✅ Done

Extract pattern matching logic from `SemanticWorkflowMatcher._match_by_pattern()` into standalone `PatternMatcher`.

```python
# server/router/application/matcher/pattern_matcher.py

from typing import Dict, Any, Optional, TYPE_CHECKING
import logging

from server.router.domain.interfaces.matcher import IMatcher
from server.router.domain.entities.ensemble import MatcherResult

if TYPE_CHECKING:
    from server.router.application.workflows.registry import WorkflowRegistry

logger = logging.getLogger(__name__)


class PatternMatcher(IMatcher):
    """Matches workflows by geometry patterns in scene.

    Extracts pattern matching from SemanticWorkflowMatcher._match_by_pattern().
    Checks context for detected_pattern and matches to workflow.
    """

    def __init__(self, registry: "WorkflowRegistry", weight: float = 0.15):
        """Initialize matcher.

        Args:
            registry: Workflow registry for pattern lookup.
            weight: Weight for ensemble aggregation (default 0.15).
        """
        self._registry = registry
        self._weight = weight

    @property
    def name(self) -> str:
        return "pattern"

    @property
    def weight(self) -> float:
        return self._weight

    def match(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> MatcherResult:
        """Match by detected geometry pattern.

        Requires context with 'detected_pattern' key.
        Returns high confidence (0.95) for pattern matches.
        """
        if not context:
            return MatcherResult(
                matcher_name=self.name,
                workflow_name=None,
                confidence=0.0,
                weight=self.weight
            )

        # Check if pattern was detected by GeometryPatternDetector
        detected_pattern = context.get("detected_pattern")
        if not detected_pattern:
            return MatcherResult(
                matcher_name=self.name,
                workflow_name=None,
                confidence=0.0,
                weight=self.weight
            )

        # Lookup workflow by pattern
        workflow_name = self._registry.find_by_pattern(detected_pattern)

        if workflow_name:
            logger.debug(f"Pattern match: {detected_pattern} → {workflow_name}")
            return MatcherResult(
                matcher_name=self.name,
                workflow_name=workflow_name,
                confidence=0.95,
                weight=self.weight,
                metadata={
                    "matched_by": "pattern",
                    "pattern": detected_pattern
                }
            )

        return MatcherResult(
            matcher_name=self.name,
            workflow_name=None,
            confidence=0.0,
            weight=self.weight,
            metadata={"pattern_detected": detected_pattern, "no_matching_workflow": True}
        )
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Application | `server/router/application/matcher/pattern_matcher.py` | `PatternMatcher` implementing `IMatcher` |
| Tests | `tests/unit/router/application/matcher/test_pattern_matcher.py` | Matcher tests |

---

### TASK-053-6: Modifier Extractor (REFACTOR)

**Status:** ✅ Done

**CRITICAL:** This extracts and consolidates existing logic from TWO places:
1. `SupervisorRouter._build_variables()` (router.py:601-630)
2. `WorkflowRegistry._extract_modifiers()` (registry.py:283-308)

```python
# server/router/application/matcher/modifier_extractor.py

from typing import Dict, Any, List, TYPE_CHECKING
import logging

from server.router.domain.interfaces.matcher import IModifierExtractor
from server.router.domain.entities.ensemble import ModifierResult

if TYPE_CHECKING:
    from server.router.application.workflows.registry import WorkflowRegistry

logger = logging.getLogger(__name__)


class ModifierExtractor(IModifierExtractor):
    """Extracts parametric modifiers from user prompt.

    CONSOLIDATES logic from:
    - SupervisorRouter._build_variables()
    - WorkflowRegistry._extract_modifiers()

    This extractor ALWAYS runs, regardless of which matcher wins.
    Ensures modifiers like "straight legs" are always applied.
    """

    def __init__(self, registry: "WorkflowRegistry"):
        """Initialize extractor.

        Args:
            registry: Workflow registry for workflow definitions.
        """
        self._registry = registry

    def extract(self, prompt: str, workflow_name: str) -> ModifierResult:
        """Extract modifiers from prompt for given workflow.

        Scans prompt for modifier keywords defined in workflow definition.
        Returns all matching variable overrides.

        Args:
            prompt: User prompt (e.g., "simple table with straight legs").
            workflow_name: Target workflow to check modifiers for.

        Returns:
            ModifierResult with extracted parameters.
        """
        definition = self._registry.get_definition(workflow_name)

        if not definition:
            logger.debug(f"No definition found for workflow: {workflow_name}")
            return ModifierResult(
                modifiers={},
                matched_keywords=[],
                confidence_map={}
            )

        if not definition.modifiers:
            logger.debug(f"Workflow '{workflow_name}' has no modifiers defined")
            return ModifierResult(
                modifiers={},
                matched_keywords=[],
                confidence_map={}
            )

        prompt_lower = prompt.lower()
        extracted: Dict[str, Any] = {}
        matched: List[str] = []
        confidence: Dict[str, float] = {}

        # Also include defaults as base
        if definition.defaults:
            extracted.update(definition.defaults)

        # Apply modifiers from user prompt (override defaults)
        for keyword, params in definition.modifiers.items():
            if keyword.lower() in prompt_lower:
                matched.append(keyword)
                confidence[keyword] = 1.0
                extracted.update(params)
                logger.info(f"Modifier matched: '{keyword}' → {params}")

        return ModifierResult(
            modifiers=extracted,
            matched_keywords=matched,
            confidence_map=confidence
        )

    def extract_with_defaults(
        self,
        prompt: str,
        workflow_name: str,
    ) -> Dict[str, Any]:
        """Extract modifiers and merge with defaults.

        Convenience method that returns just the variables dict.
        Equivalent to what _build_variables() currently does.

        Args:
            prompt: User prompt.
            workflow_name: Target workflow.

        Returns:
            Dictionary of variable values (defaults + modifiers).
        """
        result = self.extract(prompt, workflow_name)
        return result.modifiers
```

**Migration Notes:**

After implementing, update these files to use `ModifierExtractor`:

1. **`router.py`:** Replace `_build_variables()` with `ModifierExtractor.extract_with_defaults()`
2. **`registry.py`:** Replace `_extract_modifiers()` with call to `ModifierExtractor.extract()`

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Application | `server/router/application/matcher/modifier_extractor.py` | `ModifierExtractor` implementing `IModifierExtractor` |
| Tests | `tests/unit/router/application/matcher/test_modifier_extractor.py` | Extractor tests |

---

### TASK-053-7: Ensemble Aggregator

**Status:** ✅ Done

Create the weighted aggregator that combines all matcher results.

```python
# server/router/application/matcher/ensemble_aggregator.py

from collections import defaultdict
from typing import Dict, List, Optional
import logging

from server.router.domain.entities.ensemble import MatcherResult, EnsembleResult
from server.router.application.matcher.modifier_extractor import ModifierExtractor
from server.router.infrastructure.config import RouterConfig

logger = logging.getLogger(__name__)


class EnsembleAggregator:
    """Aggregates results from multiple matchers using weighted consensus.

    Takes MatcherResult from each matcher and produces a single EnsembleResult.
    ALWAYS runs ModifierExtractor to ensure modifiers are applied.
    """

    # Score multiplier when pattern matcher fires
    PATTERN_BOOST = 1.3

    # Threshold for activating composition mode (two workflows with similar scores)
    COMPOSITION_THRESHOLD = 0.15

    # Keywords that force LOW confidence (simple workflow)
    SIMPLE_KEYWORDS = [
        "simple", "basic", "minimal", "just", "only", "plain",
        "prosty", "podstawowy", "tylko", "zwykły",  # Polish
        "einfach", "nur", "schlicht",  # German
    ]

    def __init__(
        self,
        modifier_extractor: ModifierExtractor,
        config: Optional[RouterConfig] = None,
    ):
        """Initialize aggregator.

        Args:
            modifier_extractor: Extractor for modifiers.
            config: Router configuration for thresholds.
        """
        self._modifier_extractor = modifier_extractor
        self._config = config or RouterConfig()

    def aggregate(
        self,
        results: List[MatcherResult],
        prompt: str,
    ) -> EnsembleResult:
        """Aggregate matcher results into final decision.

        Args:
            results: Results from all matchers (KeywordMatcher, SemanticMatcher, PatternMatcher).
            prompt: Original user prompt.

        Returns:
            EnsembleResult with final workflow, score, and modifiers.
        """
        # Group scores by workflow
        workflow_scores: Dict[str, Dict[str, float]] = defaultdict(dict)

        for result in results:
            if result.workflow_name:
                # Store weighted score per matcher
                weighted_score = result.confidence * result.weight
                workflow_scores[result.workflow_name][result.matcher_name] = weighted_score

        # No matches from any matcher
        if not workflow_scores:
            return EnsembleResult(
                workflow_name=None,
                final_score=0.0,
                confidence_level="NONE",
                modifiers={},
                matcher_contributions={},
                requires_adaptation=False
            )

        # Calculate final scores for each workflow
        final_scores: Dict[str, float] = {}
        for workflow, contributions in workflow_scores.items():
            score = sum(contributions.values())

            # Pattern boost: if pattern matcher contributed, multiply by boost factor
            if "pattern" in contributions and contributions["pattern"] > 0:
                score *= self.PATTERN_BOOST
                logger.debug(f"Applied pattern boost to {workflow}: {score:.3f}")

            final_scores[workflow] = score

        # Sort workflows by score (descending)
        sorted_workflows = sorted(
            final_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        best_workflow, best_score = sorted_workflows[0]
        best_contributions = workflow_scores[best_workflow]

        # Check for composition mode (two workflows with similar scores)
        composition_mode = False
        extra_workflows: List[str] = []
        if len(sorted_workflows) > 1:
            second_workflow, second_score = sorted_workflows[1]
            if abs(best_score - second_score) < self.COMPOSITION_THRESHOLD:
                composition_mode = True
                extra_workflows = [second_workflow]
                logger.info(
                    f"Composition mode activated: {best_workflow} ({best_score:.3f}) "
                    f"≈ {second_workflow} ({second_score:.3f})"
                )

        # CRITICAL: ALWAYS extract modifiers (this is the bug fix!)
        modifier_result = self._modifier_extractor.extract(prompt, best_workflow)

        # Determine confidence level
        confidence_level = self._determine_confidence_level(best_score, prompt)

        logger.info(
            f"Ensemble aggregation: {best_workflow} "
            f"(score: {best_score:.3f}, level: {confidence_level}, "
            f"modifiers: {list(modifier_result.modifiers.keys())})"
        )

        return EnsembleResult(
            workflow_name=best_workflow,
            final_score=best_score,
            confidence_level=confidence_level,
            modifiers=modifier_result.modifiers,
            matcher_contributions=best_contributions,
            requires_adaptation=confidence_level != "HIGH",
            composition_mode=composition_mode,
            extra_workflows=extra_workflows
        )

    def _determine_confidence_level(self, score: float, prompt: str) -> str:
        """Determine confidence level from score and prompt analysis.

        Args:
            score: Aggregated final score.
            prompt: User prompt to check for "simple" keywords.

        Returns:
            Confidence level: HIGH, MEDIUM, LOW, or NONE.
        """
        prompt_lower = prompt.lower()

        # Check for "simple" keywords that force LOW confidence
        wants_simple = any(kw in prompt_lower for kw in self.SIMPLE_KEYWORDS)

        if wants_simple:
            logger.debug(f"User wants simple version → forcing LOW confidence")
            return "LOW"

        # Use configured thresholds from RouterConfig
        # HIGH: score >= 0.7 (normalized), MEDIUM: >= 0.4, LOW: < 0.4
        if score >= 0.7:
            return "HIGH"
        elif score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Application | `server/router/application/matcher/ensemble_aggregator.py` | `EnsembleAggregator` class |
| Tests | `tests/unit/router/application/matcher/test_ensemble_aggregator.py` | Aggregator tests |

---

### TASK-053-8: Ensemble Matcher (Main Class)

**Status:** ✅ Done

Create the main `EnsembleMatcher` that orchestrates all matchers.

```python
# server/router/application/matcher/ensemble_matcher.py

from typing import List, Optional, Dict, Any, TYPE_CHECKING
import logging

from server.router.domain.interfaces.matcher import IMatcher
from server.router.domain.entities.ensemble import MatcherResult, EnsembleResult
from server.router.domain.entities.scene_context import SceneContext
from server.router.application.matcher.keyword_matcher import KeywordMatcher
from server.router.application.matcher.semantic_matcher import SemanticMatcher
from server.router.application.matcher.pattern_matcher import PatternMatcher
from server.router.application.matcher.ensemble_aggregator import EnsembleAggregator
from server.router.infrastructure.config import RouterConfig
from server.router.infrastructure.logger import RouterLogger

if TYPE_CHECKING:
    from server.router.application.workflows.registry import WorkflowRegistry

logger = logging.getLogger(__name__)


class EnsembleMatcher:
    """Orchestrates parallel matching using multiple matchers.

    Runs all matchers (keyword, semantic, pattern) and aggregates
    results using EnsembleAggregator for weighted consensus.

    This replaces the fallback-based SemanticWorkflowMatcher.match() flow.
    """

    def __init__(
        self,
        keyword_matcher: KeywordMatcher,
        semantic_matcher: SemanticMatcher,
        pattern_matcher: PatternMatcher,
        aggregator: EnsembleAggregator,
        config: Optional[RouterConfig] = None,
    ):
        """Initialize ensemble matcher.

        Args:
            keyword_matcher: Matcher for keyword-based matching.
            semantic_matcher: Matcher for LaBSE semantic matching.
            pattern_matcher: Matcher for geometry pattern matching.
            aggregator: Aggregator for combining results.
            config: Router configuration.
        """
        self._matchers: List[IMatcher] = [
            keyword_matcher,
            semantic_matcher,
            pattern_matcher
        ]
        self._aggregator = aggregator
        self._config = config or RouterConfig()
        self._router_logger = RouterLogger()
        self._is_initialized = False

    def initialize(self, registry: "WorkflowRegistry") -> None:
        """Initialize all matchers that need initialization.

        Args:
            registry: Workflow registry for initializing semantic matcher.
        """
        for matcher in self._matchers:
            if hasattr(matcher, 'initialize') and callable(matcher.initialize):
                if hasattr(matcher, 'is_initialized') and not matcher.is_initialized():
                    matcher.initialize(registry)

        self._is_initialized = True
        logger.info("EnsembleMatcher initialized")

    def is_initialized(self) -> bool:
        """Check if ensemble matcher is initialized."""
        return self._is_initialized

    def match(
        self,
        prompt: str,
        context: Optional[SceneContext] = None,
    ) -> EnsembleResult:
        """Run all matchers and aggregate results.

        Args:
            prompt: User prompt/goal.
            context: Optional scene context.

        Returns:
            EnsembleResult with workflow, confidence, and modifiers.
        """
        # Convert context to dict for matchers
        context_dict: Optional[Dict[str, Any]] = None
        if context:
            context_dict = context.to_dict()
            # Add detected pattern if available from GeometryPatternDetector
            # This is passed in from SupervisorRouter._detect_pattern()

        # Run all matchers
        results: List[MatcherResult] = []
        for matcher in self._matchers:
            try:
                result = matcher.match(prompt, context_dict)
                results.append(result)

                self._router_logger.log_info(
                    f"Matcher '{matcher.name}': "
                    f"{result.workflow_name or 'None'} "
                    f"(confidence: {result.confidence:.2f}, "
                    f"weighted: {result.confidence * result.weight:.3f})"
                )
            except Exception as e:
                logger.exception(f"Matcher '{matcher.name}' failed: {e}")
                self._router_logger.log_error(matcher.name, str(e))
                # Add failed result with zero confidence
                results.append(MatcherResult(
                    matcher_name=matcher.name,
                    workflow_name=None,
                    confidence=0.0,
                    weight=matcher.weight,
                    metadata={"error": str(e)}
                ))

        # Aggregate results
        ensemble_result = self._aggregator.aggregate(results, prompt)

        self._router_logger.log_info(
            f"Ensemble result: {ensemble_result.workflow_name} "
            f"(score: {ensemble_result.final_score:.3f}, "
            f"level: {ensemble_result.confidence_level}, "
            f"modifiers: {list(ensemble_result.modifiers.keys())})"
        )

        return ensemble_result

    def get_info(self) -> Dict[str, Any]:
        """Get ensemble matcher information.

        Returns:
            Dictionary with matcher status and configuration.
        """
        return {
            "is_initialized": self._is_initialized,
            "matchers": [
                {
                    "name": m.name,
                    "weight": m.weight,
                    "initialized": getattr(m, 'is_initialized', lambda: True)()
                }
                for m in self._matchers
            ],
            "config": {
                "pattern_boost": EnsembleAggregator.PATTERN_BOOST,
                "composition_threshold": EnsembleAggregator.COMPOSITION_THRESHOLD,
            }
        }
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Application | `server/router/application/matcher/ensemble_matcher.py` | `EnsembleMatcher` class |
| Application | `server/router/application/matcher/__init__.py` | Export all new classes |
| Tests | `tests/unit/router/application/matcher/test_ensemble_matcher.py` | Integration tests |

---

### TASK-053-9: Router Integration - New Fields

**Status:** ✅ Done

Add new fields to `SupervisorRouter` for ensemble matching.

**Changes to `server/router/application/router.py`:**

```python
# Add to __init__:

class SupervisorRouter:
    def __init__(self, ...):
        # ... existing init ...

        # Semantic workflow matching (TASK-046) - KEEP for backward compatibility
        self._semantic_matcher = SemanticWorkflowMatcher(...)

        # NEW: Ensemble matching (TASK-053)
        self._ensemble_matcher: Optional[EnsembleMatcher] = None
        self._last_ensemble_result: Optional[EnsembleResult] = None
        self._pending_modifiers: Dict[str, Any] = {}  # NEW FIELD
        self._use_ensemble_matching: bool = True  # NEW: Feature flag

    def _ensure_ensemble_initialized(self) -> bool:
        """Ensure ensemble matcher is initialized.

        Lazily initializes the ensemble matcher with all components.
        """
        if self._ensemble_matcher is not None:
            return True

        try:
            from server.router.application.workflows.registry import get_workflow_registry
            from server.router.application.matcher.keyword_matcher import KeywordMatcher
            from server.router.application.matcher.semantic_matcher import SemanticMatcher
            from server.router.application.matcher.pattern_matcher import PatternMatcher
            from server.router.application.matcher.modifier_extractor import ModifierExtractor
            from server.router.application.matcher.ensemble_aggregator import EnsembleAggregator
            from server.router.application.matcher.ensemble_matcher import EnsembleMatcher

            registry = get_workflow_registry()
            registry.ensure_custom_loaded()

            # Create modifier extractor
            modifier_extractor = ModifierExtractor(registry)

            # Create matchers
            keyword_matcher = KeywordMatcher(registry)
            semantic_matcher = SemanticMatcher(
                classifier=self._workflow_classifier,  # Reuse existing classifier
                registry=registry,
                config=self.config,
            )
            pattern_matcher = PatternMatcher(registry)

            # Create aggregator
            aggregator = EnsembleAggregator(modifier_extractor, self.config)

            # Create ensemble matcher
            self._ensemble_matcher = EnsembleMatcher(
                keyword_matcher=keyword_matcher,
                semantic_matcher=semantic_matcher,
                pattern_matcher=pattern_matcher,
                aggregator=aggregator,
                config=self.config,
            )

            # Initialize semantic matcher with registry
            self._ensemble_matcher.initialize(registry)

            self.logger.log_info("Ensemble matcher initialized")
            return True

        except Exception as e:
            self.logger.log_error("ensemble_init", str(e))
            return False
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Application | `server/router/application/router.py` | Add `_ensemble_matcher`, `_last_ensemble_result`, `_pending_modifiers` fields |
| Application | `server/router/application/router.py` | Add `_ensure_ensemble_initialized()` method |

---

### TASK-053-10: Router Integration - set_current_goal Refactor

**Status:** ✅ Done

Refactor `set_current_goal()` to use `EnsembleMatcher` while maintaining backward compatibility.

**Changes to `server/router/application/router.py`:**

```python
def set_current_goal(self, goal: str) -> Optional[str]:
    """Set current modeling goal and find matching workflow.

    Uses ensemble matching (TASK-053) if enabled, falls back to
    legacy SemanticWorkflowMatcher for backward compatibility.

    Args:
        goal: User's modeling goal (e.g., "smartphone", "table")

    Returns:
        Name of matched workflow, or None.
    """
    self._current_goal = goal

    # Try ensemble matching first (TASK-053)
    if self._use_ensemble_matching and self._ensure_ensemble_initialized():
        return self._set_goal_ensemble(goal)

    # Fallback to legacy matching
    return self._set_goal_legacy(goal)


def _set_goal_ensemble(self, goal: str) -> Optional[str]:
    """Set goal using ensemble matching (TASK-053).

    Args:
        goal: User's modeling goal.

    Returns:
        Name of matched workflow, or None.
    """
    # Get scene context for pattern matching
    context = None
    if self._rpc_client:
        context = self._analyze_scene()
        # Add detected pattern to context
        pattern = self._detect_pattern(context)
        if pattern:
            # Convert pattern to dict format expected by PatternMatcher
            context_with_pattern = context.to_dict() if context else {}
            context_with_pattern["detected_pattern"] = pattern.pattern_type.value

    # Run ensemble matching
    result = self._ensemble_matcher.match(goal, context)

    if result.workflow_name:
        self._pending_workflow = result.workflow_name
        self._last_ensemble_result = result
        self._pending_modifiers = result.modifiers  # CRITICAL: Store modifiers

        # Also store as MatchResult for WorkflowAdapter compatibility
        self._last_match_result = MatchResult(
            workflow_name=result.workflow_name,
            confidence=result.final_score,
            match_type="ensemble",
            confidence_level=result.confidence_level,
            requires_adaptation=result.requires_adaptation,
            metadata={"matcher_contributions": result.matcher_contributions}
        )

        self.logger.log_info(
            f"Goal '{goal}' matched workflow (ensemble): {result.workflow_name} "
            f"(score: {result.final_score:.3f}, level: {result.confidence_level}, "
            f"modifiers: {list(result.modifiers.keys())})"
        )

        # Record feedback for learning
        self._feedback_collector.record_match(
            prompt=goal,
            matched_workflow=result.workflow_name,
            confidence=result.final_score,
            match_type="ensemble",
            metadata={
                "matcher_contributions": result.matcher_contributions,
                "modifiers_applied": list(result.modifiers.keys()),
            },
        )

        return result.workflow_name

    # No match found
    self._feedback_collector.record_match(
        prompt=goal,
        matched_workflow=None,
        confidence=0.0,
        match_type="none",
    )

    self._pending_workflow = None
    self._pending_modifiers = {}
    self.logger.log_info(f"Goal '{goal}' set (no matching workflow)")
    return None


def _set_goal_legacy(self, goal: str) -> Optional[str]:
    """Set goal using legacy matching (backward compatibility).

    This is the original set_current_goal logic before TASK-053.
    Kept for fallback if ensemble matching is disabled.
    """
    # ... move existing set_current_goal logic here ...
    pass
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Application | `server/router/application/router.py` | Refactor `set_current_goal()` to use ensemble |
| Application | `server/router/application/router.py` | Add `_set_goal_ensemble()` method |
| Application | `server/router/application/router.py` | Add `_set_goal_legacy()` method (existing code) |

---

### TASK-053-11: Router Integration - _expand_triggered_workflow Update

**Status:** ✅ Done

Update `_expand_triggered_workflow()` to use `_pending_modifiers` from ensemble result.

**Changes to `server/router/application/router.py`:**

```python
def _expand_triggered_workflow(
    self,
    workflow_name: str,
    params: Dict[str, Any],
    context: SceneContext,
) -> Optional[List[CorrectedToolCall]]:
    """Expand a triggered workflow by name.

    TASK-053: Uses _pending_modifiers from ensemble result instead of
    building modifiers from scratch. This ensures modifiers are ALWAYS
    applied regardless of which matcher won.
    """
    from server.router.application.workflows.registry import get_workflow_registry

    registry = get_workflow_registry()
    registry.ensure_custom_loaded()

    # Build evaluation context for $CALCULATE expressions
    eval_context = self._build_eval_context(context, params)

    # TASK-053: Use modifiers from ensemble result if available
    if self._pending_modifiers:
        variables = dict(self._pending_modifiers)
        self.logger.log_info(
            f"Using modifiers from ensemble result: {list(variables.keys())}"
        )
    else:
        # Fallback: build variables from definition (legacy path)
        definition = registry.get_definition(workflow_name)
        if definition:
            variables = self._build_variables(definition, self._current_goal or "")
        else:
            variables = {}

    # ... rest of existing _expand_triggered_workflow logic ...
    # Use 'variables' instead of calling _build_variables again
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Application | `server/router/application/router.py` | Update `_expand_triggered_workflow()` to use `_pending_modifiers` |

---

### TASK-053-12: Configuration Updates

**Status:** ✅ Done

Add ensemble matching configuration to `RouterConfig`.

**Changes to `server/router/infrastructure/config.py`:**

```python
@dataclass
class RouterConfig:
    # ... existing fields ...

    # Ensemble matching (TASK-053)
    use_ensemble_matching: bool = True  # Enable ensemble matching
    keyword_weight: float = 0.40  # Weight for keyword matcher
    semantic_weight: float = 0.40  # Weight for semantic matcher
    pattern_weight: float = 0.15  # Weight for pattern matcher
    pattern_boost_factor: float = 1.3  # Boost when pattern matcher fires
    composition_threshold: float = 0.15  # Threshold for multi-workflow mode
    enable_composition_mode: bool = False  # Future feature

    # Confidence level thresholds
    ensemble_high_threshold: float = 0.7  # Score >= this → HIGH confidence
    ensemble_medium_threshold: float = 0.4  # Score >= this → MEDIUM confidence
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Infrastructure | `server/router/infrastructure/config.py` | Add ensemble config fields |
| Tests | `tests/unit/router/infrastructure/test_config.py` | Test new config fields |

---

### TASK-053-13: WorkflowAdapter Compatibility

**Status:** ✅ Done

Update `WorkflowAdapter` to work with `EnsembleResult` in addition to `MatchResult`.

**Changes to `server/router/application/engines/workflow_adapter.py`:**

```python
# Add to imports:
from server.router.domain.entities.ensemble import EnsembleResult

# Update adapt() method to accept both MatchResult and EnsembleResult confidence levels:

def adapt(
    self,
    definition: WorkflowDefinition,
    confidence_level: str,  # Can come from MatchResult or EnsembleResult
    user_prompt: str,
) -> Tuple[List[WorkflowStep], AdaptationResult]:
    """Adapt workflow steps based on confidence level.

    TASK-053: Now works with both MatchResult (legacy) and
    EnsembleResult (new ensemble matching).

    Args:
        definition: Full workflow definition.
        confidence_level: Match confidence level (HIGH, MEDIUM, LOW, NONE).
                         Can come from MatchResult.confidence_level or
                         EnsembleResult.confidence_level.
        user_prompt: Original user prompt for relevance filtering.

    Returns:
        Tuple of (adapted_steps, adaptation_result).
    """
    # ... existing logic works unchanged since it uses confidence_level string
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Application | `server/router/application/engines/workflow_adapter.py` | Update docstring, add import |
| Tests | `tests/unit/router/application/test_workflow_adapter.py` | Add tests with EnsembleResult |

---

### TASK-053-14: Update Existing Tests

**Status:** ✅ Done

Update existing tests to work with ensemble matching.

**Files to Update:**

| Test File | What to Update |
|-----------|----------------|
| `tests/unit/router/application/matcher/test_semantic_workflow_matcher.py` | Keep existing tests (backward compat), add ensemble imports |
| `tests/unit/router/application/test_supervisor_router.py` | Add ensemble matching tests, update `set_current_goal` tests |
| `tests/unit/router/application/test_workflow_adapter.py` | Add tests with `EnsembleResult` |
| `tests/unit/router/application/workflows/test_registry.py` | Add tests for modifier extraction migration |

**New Test Files to Create:**

| Test File | Content |
|-----------|---------|
| `tests/unit/router/application/matcher/test_keyword_matcher.py` | KeywordMatcher unit tests |
| `tests/unit/router/application/matcher/test_semantic_matcher.py` | SemanticMatcher unit tests (new file) |
| `tests/unit/router/application/matcher/test_pattern_matcher.py` | PatternMatcher unit tests |
| `tests/unit/router/application/matcher/test_modifier_extractor.py` | ModifierExtractor unit tests |
| `tests/unit/router/application/matcher/test_ensemble_aggregator.py` | EnsembleAggregator unit tests |
| `tests/unit/router/application/matcher/test_ensemble_matcher.py` | EnsembleMatcher integration tests |
| `tests/unit/router/test_router_ensemble.py` | Router ensemble integration tests |
| `tests/e2e/router/test_ensemble_matching.py` | Full E2E tests |

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Tests | All test files above | Create/update tests |

---

### TASK-053-15: Cleanup Legacy Code (Optional)

**Status:** ✅ Done (After Verification)

After ensemble matching is working and tested, optionally clean up legacy code.

**Files to Review:**

1. **`SemanticWorkflowMatcher`**: Can be deprecated in favor of `EnsembleMatcher`, but keep for backward compatibility
2. **`SupervisorRouter._build_variables()`**: Can delegate to `ModifierExtractor`
3. **`WorkflowRegistry._extract_modifiers()`**: Can delegate to `ModifierExtractor`

**NOTE:** Do NOT remove legacy code until ensemble matching is fully tested and stable.

---

### TASK-053-16: Composition Mode (Optional/Future)

**Status:** ✅ Done (Optional)

Implement composition mode for multi-workflow scenarios.

```python
# Example: "picnic table with 4 chairs"
# → main: picnic_table_workflow
# → extras: [chair_workflow × 4]
# → spatial_arrangement: True
```

This is an advanced feature for future implementation.

---

## Conflict Resolution Rules

### Rule 1: Highest Score Wins

Default behavior - workflow with highest `final_score` is selected.

### Rule 2: Composition Mode

If `abs(score_A - score_B) < 0.15`, activate composition mode:
- Create compound goal
- Execute multiple workflows
- Handle spatial arrangement

### Rule 3: Pattern Boost

If pattern matcher fires (confidence > 0), multiply final score by 1.3.

### Rule 4: Simple Keyword Override

If prompt contains "simple", "basic", "minimal", etc., force `confidence_level = LOW` regardless of score.

---

## Testing Requirements

### Unit Tests

- [ ] `test_keyword_matcher.py` - Keyword matcher tests
- [ ] `test_semantic_matcher.py` - Semantic matcher tests (NEW)
- [ ] `test_pattern_matcher.py` - Pattern matcher tests
- [ ] `test_modifier_extractor.py` - Modifier extraction tests
- [ ] `test_ensemble_aggregator.py` - Aggregation logic tests
- [ ] `test_ensemble_matcher.py` - Full ensemble tests
- [ ] `test_router_ensemble.py` - Router integration tests

### E2E Tests

- [ ] `test_ensemble_matching.py` - Full pipeline tests
- [ ] Test: "simple table with straight legs" → modifiers applied
- [ ] Test: "simple table with 4 legs" → CORE_ONLY + straight legs
- [ ] Test: "picnic table" → FULL workflow
- [ ] Test: Multi-language prompts (Polish, German, etc.)

---

## Files to Create

### New Files

```
server/router/domain/entities/ensemble.py
server/router/domain/interfaces/matcher.py
server/router/application/matcher/keyword_matcher.py
server/router/application/matcher/semantic_matcher.py
server/router/application/matcher/pattern_matcher.py
server/router/application/matcher/modifier_extractor.py
server/router/application/matcher/ensemble_aggregator.py
server/router/application/matcher/ensemble_matcher.py

tests/unit/router/application/matcher/test_keyword_matcher.py
tests/unit/router/application/matcher/test_semantic_matcher.py
tests/unit/router/application/matcher/test_pattern_matcher.py
tests/unit/router/application/matcher/test_modifier_extractor.py
tests/unit/router/application/matcher/test_ensemble_aggregator.py
tests/unit/router/application/matcher/test_ensemble_matcher.py
tests/unit/router/test_router_ensemble.py
tests/e2e/router/test_ensemble_matching.py
```

### Files to Modify

```
server/router/application/router.py                        # Use EnsembleMatcher
server/router/application/matcher/__init__.py              # Export new classes
server/router/application/engines/workflow_adapter.py      # EnsembleResult compat
server/router/domain/entities/__init__.py                  # Export new entities
server/router/domain/interfaces/__init__.py                # Export new interfaces
server/router/infrastructure/config.py                     # Add ensemble config

tests/unit/router/application/matcher/test_semantic_workflow_matcher.py  # Update
tests/unit/router/application/test_supervisor_router.py                  # Update
tests/unit/router/application/test_workflow_adapter.py                   # Update
tests/unit/router/domain/test_entities.py                                # Add tests
tests/unit/router/domain/test_interfaces.py                              # Add tests
```

---

## Implementation Order

1. **TASK-053-1**: Domain entities (foundation)
2. **TASK-053-2**: Matcher interface (contracts)
3. **TASK-053-6**: Modifier extractor (critical for bug fix)
4. **TASK-053-3**: Keyword matcher refactor
5. **TASK-053-4**: Semantic matcher refactor
6. **TASK-053-5**: Pattern matcher refactor
7. **TASK-053-7**: Ensemble aggregator
8. **TASK-053-8**: Ensemble matcher (orchestrator)
9. **TASK-053-12**: Configuration updates
10. **TASK-053-9**: Router integration - new fields
11. **TASK-053-10**: Router integration - set_current_goal
12. **TASK-053-11**: Router integration - _expand_triggered_workflow
13. **TASK-053-13**: WorkflowAdapter compatibility
14. **TASK-053-14**: Update existing tests
15. **TASK-053-15**: Cleanup legacy code (optional)
16. **TASK-053-16**: Composition mode (optional/future)

---

## Migration Strategy

### Phase 1: Add New Components (Non-Breaking)
- Create all new files (entities, interfaces, matchers, aggregator)
- No changes to existing code yet
- All new code has tests

### Phase 2: Add Feature Flag
- Add `use_ensemble_matching` config flag (default: True)
- Add `_ensure_ensemble_initialized()` method
- No changes to existing `set_current_goal()` yet

### Phase 3: Integrate with Feature Flag
- Update `set_current_goal()` to use ensemble when flag is True
- Keep legacy `_set_goal_legacy()` as fallback
- Update `_expand_triggered_workflow()` to use `_pending_modifiers`

### Phase 4: Testing & Verification
- Run all existing tests (should pass)
- Run new ensemble tests
- Verify bug fix: "simple table with straight legs" → modifiers applied

### Phase 5: Cleanup (After Verification)
- Optional: Deprecate `SemanticWorkflowMatcher` methods
- Optional: Remove legacy code paths

---

## Success Criteria

1. **Bug Fixed**: "simple table with straight legs" produces straight legs (0°)
2. **Modifiers Always Applied**: Regardless of which matcher wins
3. **Weighted Scoring**: All matchers contribute to final decision
4. **Backward Compatible**: Existing workflows work unchanged
5. **Feature Flag**: Can disable ensemble matching if needed
6. **Performance**: No significant latency increase (<50ms)
7. **Logging**: Clear visibility into matcher contributions
8. **Tests**: All existing tests pass, new tests cover ensemble logic

---

## Documentation Updates Required

After implementing, update:

| File | What to Update |
|------|----------------|
| `_docs/_TASKS/TASK-053_Ensemble_Matcher_System.md` | Mark sub-tasks as Done |
| `_docs/_TASKS/README.md` | Move to Done, update statistics |
| `_docs/_CHANGELOG/{NN}-{date}-ensemble-matcher.md` | Create changelog entry |
| `_docs/_ROUTER/README.md` | Update component status, add ensemble section |
| `_docs/_ROUTER/ROUTER_ARCHITECTURE.md` | Add ensemble architecture diagram |
| `_docs/_ROUTER/IMPLEMENTATION/34-ensemble-matcher.md` | Create implementation doc |
| `_docs/_ROUTER/WORKFLOWS/yaml-workflow-guide.md` | Update matching section |
| `_docs/_ROUTER/WORKFLOWS/expression-reference.md` | Update modifier resolution docs |
| `README.md` | Update Router Supervisor section |

---

## Related Tasks

- [TASK-046](./TASK-046_Router_Semantic_Generalization.md) - Semantic matching foundation
- [TASK-051](./TASK-051_Confidence_Based_Workflow_Adaptation.md) - Confidence levels
- [TASK-052](./TASK-052_Intelligent_Parametric_Adaptation.md) - Parametric variables

---

## References

- Ensemble methods in ML: Weighted voting classifiers
- RAG systems: Multi-retriever fusion
- LLM routers: Mixture of experts
