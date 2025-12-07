# TASK-053: Ensemble Matcher System

**Priority:** 🔴 High
**Category:** Router Supervisor Enhancement
**Estimated Effort:** Large
**Dependencies:** TASK-046 (Semantic Generalization), TASK-051 (Confidence-Based Adaptation), TASK-052 (Parametric Variables)
**Status:** 🚨 **TO DO**

---

## Overview

Replace the current fallback-based matching system with an **Ensemble Matcher** that runs all matchers in parallel and aggregates results using weighted consensus. This fixes the critical bug where parametric modifiers (e.g., "proste nogi") are not applied when semantic matcher wins over keyword matcher.

**Current Problem:**
```
User: "prosty stół z prostymi nogami"
→ Semantic match (84.3%) wins
→ Modifiers from keyword matcher NOT extracted
→ Legs are angled instead of straight (0°)
```

**Solution:**
All matchers run in parallel, results are aggregated, and modifiers are ALWAYS extracted regardless of which matcher "wins" the workflow selection.

---

## Architecture

### Current System (Fallback/OR Logic)

```
Keyword Match? ─Yes→ Return workflow
      │
      No
      ↓
Semantic Match? ─Yes→ Return workflow
      │
      No
      ↓
Pattern Match? ─Yes→ Return workflow
      │
      No
      ↓
No match
```

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
│         │    TAG/MODIFIER        │                         │
│         │    MATCHER (0.05)      │                         │
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

## Matcher Weights

| Matcher | Weight | Rationale |
|---------|--------|-----------|
| **Keyword** | 0.40 | Most precise, low false positive rate |
| **Semantic** | 0.40 | Most flexible, context-aware |
| **Pattern** | 0.15 | Geometry-aware, very confident when triggered |
| **Tag/Modifier** | 0.05 | Doesn't select workflow, only modifies parameters |

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
User: "prosty stół z prostymi nogami"

Matcher Results:
  keyword:  picnic_table_workflow (0.0)  - no exact keyword match
  semantic: picnic_table_workflow (0.84)
  pattern:  None (0.0)
  modifier: ["prosty", "proste nogi"] extracted

Aggregation:
  picnic_table_workflow = 0.0×0.40 + 0.84×0.40 + 0.0×0.15 = 0.336

Final Result:
  workflow: picnic_table_workflow
  modifiers: {leg_angle_left: 0, leg_angle_right: 0}  ← ALWAYS APPLIED
```

---

## Sub-Tasks

### TASK-053-1: Domain Entities

**Status:** 🚨 To Do

Create domain entities for ensemble matching.

```python
# server/router/domain/entities/ensemble.py

@dataclass
class MatcherResult:
    """Result from a single matcher."""
    matcher_name: str
    workflow_name: Optional[str]
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ModifierResult:
    """Extracted modifiers from user prompt."""
    modifiers: Dict[str, Any]
    matched_keywords: List[str]
    confidence_map: Dict[str, float]

@dataclass
class EnsembleResult:
    """Aggregated result from all matchers."""
    workflow_name: Optional[str]
    final_score: float
    confidence_level: str  # HIGH, MEDIUM, LOW, NONE
    modifiers: Dict[str, Any]
    matcher_contributions: Dict[str, float]
    requires_adaptation: bool
    composition_mode: bool = False
    extra_workflows: List[str] = field(default_factory=list)
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/router/domain/entities/ensemble.py` | `MatcherResult`, `ModifierResult`, `EnsembleResult` dataclasses |
| Domain | `server/router/domain/entities/__init__.py` | Export new entities |

---

### TASK-053-2: Matcher Interface

**Status:** 🚨 To Do

Define abstract interface for all matchers.

```python
# server/router/domain/interfaces/matcher.py

from abc import ABC, abstractmethod

class IMatcher(ABC):
    """Abstract interface for workflow matchers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Matcher name for logging."""
        pass

    @property
    @abstractmethod
    def weight(self) -> float:
        """Weight for score aggregation (0.0-1.0)."""
        pass

    @abstractmethod
    def match(self, prompt: str, context: Optional[Dict] = None) -> MatcherResult:
        """Match prompt to workflow.

        Args:
            prompt: User prompt/goal.
            context: Optional scene context.

        Returns:
            MatcherResult with workflow and confidence.
        """
        pass

class IModifierExtractor(ABC):
    """Interface for modifier/tag extraction."""

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
| Domain | `server/router/domain/interfaces/__init__.py` | Export new interfaces |

---

### TASK-053-3: Keyword Matcher Refactor

**Status:** 🚨 To Do

Refactor existing keyword matching to implement `IMatcher`.

```python
# server/router/application/matcher/keyword_matcher.py

class KeywordMatcher(IMatcher):
    """Matches workflows by trigger keywords."""

    def __init__(self, registry: WorkflowRegistry):
        self._registry = registry

    @property
    def name(self) -> str:
        return "keyword"

    @property
    def weight(self) -> float:
        return 0.40

    def match(self, prompt: str, context: Optional[Dict] = None) -> MatcherResult:
        workflow_name = self._registry.find_by_keywords(prompt)

        if workflow_name:
            return MatcherResult(
                matcher_name=self.name,
                workflow_name=workflow_name,
                confidence=1.0,
                metadata={"matched_by": "keyword"}
            )

        return MatcherResult(
            matcher_name=self.name,
            workflow_name=None,
            confidence=0.0
        )
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Application | `server/router/application/matcher/keyword_matcher.py` | `KeywordMatcher` implementing `IMatcher` |
| Unit Tests | `tests/unit/router/matcher/test_keyword_matcher.py` | Matcher tests |

---

### TASK-053-4: Semantic Matcher Refactor

**Status:** 🚨 To Do

Refactor `SemanticWorkflowMatcher` to implement `IMatcher`.

```python
# server/router/application/matcher/semantic_matcher.py

class SemanticMatcher(IMatcher):
    """Matches workflows using LaBSE embeddings."""

    def __init__(self, classifier: IntentClassifier, registry: WorkflowRegistry):
        self._classifier = classifier
        self._registry = registry
        self._is_initialized = False

    @property
    def name(self) -> str:
        return "semantic"

    @property
    def weight(self) -> float:
        return 0.40

    def initialize(self) -> None:
        """Initialize embeddings for all workflows."""
        # Existing initialization logic
        pass

    def match(self, prompt: str, context: Optional[Dict] = None) -> MatcherResult:
        if not self._is_initialized:
            self.initialize()

        result = self._classifier.find_best_match_with_confidence(prompt)

        return MatcherResult(
            matcher_name=self.name,
            workflow_name=result.get("workflow_id"),
            confidence=result.get("score", 0.0),
            metadata={
                "confidence_level": result.get("confidence_level"),
                "source_type": result.get("source_type")
            }
        )
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Application | `server/router/application/matcher/semantic_matcher.py` | Refactor to implement `IMatcher` |
| Unit Tests | `tests/unit/router/matcher/test_semantic_matcher.py` | Matcher tests |

---

### TASK-053-5: Pattern Matcher Refactor

**Status:** 🚨 To Do

Refactor pattern matching to implement `IMatcher`.

```python
# server/router/application/matcher/pattern_matcher.py

class PatternMatcher(IMatcher):
    """Matches workflows by geometry patterns in scene."""

    def __init__(self, analyzer: SceneAnalyzer, registry: WorkflowRegistry):
        self._analyzer = analyzer
        self._registry = registry

    @property
    def name(self) -> str:
        return "pattern"

    @property
    def weight(self) -> float:
        return 0.15

    def match(self, prompt: str, context: Optional[Dict] = None) -> MatcherResult:
        if not context or not context.get("has_objects"):
            return MatcherResult(
                matcher_name=self.name,
                workflow_name=None,
                confidence=0.0
            )

        # Analyze scene geometry for patterns
        patterns = self._analyzer.detect_patterns(context)

        for pattern in patterns:
            workflow = self._registry.find_by_pattern(pattern)
            if workflow:
                return MatcherResult(
                    matcher_name=self.name,
                    workflow_name=workflow,
                    confidence=0.95,
                    metadata={"pattern": pattern}
                )

        return MatcherResult(
            matcher_name=self.name,
            workflow_name=None,
            confidence=0.0
        )
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Application | `server/router/application/matcher/pattern_matcher.py` | `PatternMatcher` implementing `IMatcher` |
| Unit Tests | `tests/unit/router/matcher/test_pattern_matcher.py` | Matcher tests |

---

### TASK-053-6: Tag/Modifier Extractor

**Status:** 🚨 To Do

Create modifier extractor that ALWAYS runs to extract parametric variables.

```python
# server/router/application/matcher/modifier_extractor.py

class ModifierExtractor(IModifierExtractor):
    """Extracts parametric modifiers from user prompt."""

    def __init__(self, registry: WorkflowRegistry):
        self._registry = registry

    def extract(self, prompt: str, workflow_name: str) -> ModifierResult:
        definition = self._registry.get_definition(workflow_name)
        if not definition or not definition.modifiers:
            return ModifierResult(
                modifiers={},
                matched_keywords=[],
                confidence_map={}
            )

        prompt_lower = prompt.lower()
        extracted = {}
        matched = []
        confidence = {}

        for keyword, params in definition.modifiers.items():
            if keyword.lower() in prompt_lower:
                matched.append(keyword)
                confidence[keyword] = 1.0
                extracted.update(params)

        return ModifierResult(
            modifiers=extracted,
            matched_keywords=matched,
            confidence_map=confidence
        )
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Application | `server/router/application/matcher/modifier_extractor.py` | `ModifierExtractor` implementing `IModifierExtractor` |
| Unit Tests | `tests/unit/router/matcher/test_modifier_extractor.py` | Extractor tests |

---

### TASK-053-7: Ensemble Aggregator

**Status:** 🚨 To Do

Create the weighted aggregator that combines all matcher results.

```python
# server/router/application/matcher/ensemble_aggregator.py

class EnsembleAggregator:
    """Aggregates results from multiple matchers using weighted consensus."""

    PATTERN_BOOST = 1.3
    COMPOSITION_THRESHOLD = 0.15

    def __init__(self, modifier_extractor: ModifierExtractor):
        self._modifier_extractor = modifier_extractor

    def aggregate(
        self,
        results: List[MatcherResult],
        prompt: str
    ) -> EnsembleResult:
        """Aggregate matcher results into final decision.

        Args:
            results: Results from all matchers.
            prompt: Original user prompt.

        Returns:
            EnsembleResult with final workflow and modifiers.
        """
        # Group by workflow
        workflow_scores: Dict[str, Dict[str, float]] = defaultdict(dict)

        for result in results:
            if result.workflow_name:
                workflow_scores[result.workflow_name][result.matcher_name] = (
                    result.confidence * result.weight
                )

        if not workflow_scores:
            return EnsembleResult(
                workflow_name=None,
                final_score=0.0,
                confidence_level="NONE",
                modifiers={},
                matcher_contributions={},
                requires_adaptation=False
            )

        # Calculate final scores
        final_scores = {}
        for workflow, contributions in workflow_scores.items():
            score = sum(contributions.values())

            # Pattern boost
            if "pattern" in contributions and contributions["pattern"] > 0:
                score *= self.PATTERN_BOOST

            final_scores[workflow] = score

        # Sort by score
        sorted_workflows = sorted(
            final_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        best_workflow, best_score = sorted_workflows[0]

        # Check for composition mode
        composition_mode = False
        extra_workflows = []
        if len(sorted_workflows) > 1:
            second_workflow, second_score = sorted_workflows[1]
            if abs(best_score - second_score) < self.COMPOSITION_THRESHOLD:
                composition_mode = True
                extra_workflows = [second_workflow]

        # ALWAYS extract modifiers
        modifier_result = self._modifier_extractor.extract(prompt, best_workflow)

        # Determine confidence level
        confidence_level = self._determine_confidence_level(best_score, prompt)

        return EnsembleResult(
            workflow_name=best_workflow,
            final_score=best_score,
            confidence_level=confidence_level,
            modifiers=modifier_result.modifiers,
            matcher_contributions=workflow_scores[best_workflow],
            requires_adaptation=confidence_level != "HIGH",
            composition_mode=composition_mode,
            extra_workflows=extra_workflows
        )

    def _determine_confidence_level(self, score: float, prompt: str) -> str:
        """Determine confidence level from score and prompt analysis."""
        prompt_lower = prompt.lower()

        # Check for "simple" keywords that force LOW confidence
        simple_keywords = [
            "simple", "basic", "minimal", "just", "only", "plain",
            "prosty", "podstawowy", "tylko"  # Polish
        ]
        wants_simple = any(kw in prompt_lower for kw in simple_keywords)

        if wants_simple:
            return "LOW"

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
| Unit Tests | `tests/unit/router/matcher/test_ensemble_aggregator.py` | Aggregator tests |

---

### TASK-053-8: Ensemble Matcher (Main Class)

**Status:** 🚨 To Do

Create the main `EnsembleMatcher` that orchestrates all matchers.

```python
# server/router/application/matcher/ensemble_matcher.py

class EnsembleMatcher:
    """Orchestrates parallel matching using multiple matchers."""

    def __init__(
        self,
        keyword_matcher: KeywordMatcher,
        semantic_matcher: SemanticMatcher,
        pattern_matcher: PatternMatcher,
        aggregator: EnsembleAggregator,
        config: RouterConfig
    ):
        self._matchers: List[IMatcher] = [
            keyword_matcher,
            semantic_matcher,
            pattern_matcher
        ]
        self._aggregator = aggregator
        self._config = config
        self._logger = get_router_logger()

    def match(
        self,
        prompt: str,
        context: Optional[SceneContext] = None
    ) -> EnsembleResult:
        """Run all matchers and aggregate results.

        Args:
            prompt: User prompt/goal.
            context: Optional scene context.

        Returns:
            EnsembleResult with workflow, confidence, and modifiers.
        """
        context_dict = context.to_dict() if context else None

        # Run all matchers
        results = []
        for matcher in self._matchers:
            try:
                result = matcher.match(prompt, context_dict)
                results.append(result)

                self._logger.log_info(
                    f"Matcher '{matcher.name}': "
                    f"{result.workflow_name or 'None'} "
                    f"(confidence: {result.confidence:.2f})"
                )
            except Exception as e:
                self._logger.log_error(matcher.name, str(e))
                results.append(MatcherResult(
                    matcher_name=matcher.name,
                    workflow_name=None,
                    confidence=0.0,
                    metadata={"error": str(e)}
                ))

        # Aggregate results
        ensemble_result = self._aggregator.aggregate(results, prompt)

        self._logger.log_info(
            f"Ensemble result: {ensemble_result.workflow_name} "
            f"(score: {ensemble_result.final_score:.3f}, "
            f"level: {ensemble_result.confidence_level}, "
            f"modifiers: {list(ensemble_result.modifiers.keys())})"
        )

        return ensemble_result
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Application | `server/router/application/matcher/ensemble_matcher.py` | `EnsembleMatcher` class |
| Unit Tests | `tests/unit/router/matcher/test_ensemble_matcher.py` | Integration tests |

---

### TASK-053-9: Router Integration

**Status:** 🚨 To Do

Integrate `EnsembleMatcher` into `SupervisorRouter`.

**Changes to `server/router/application/router.py`:**

```python
class SupervisorRouter:
    def __init__(self, ...):
        # ...existing init...

        # Replace individual matchers with ensemble
        self._ensemble_matcher = EnsembleMatcher(
            keyword_matcher=KeywordMatcher(registry),
            semantic_matcher=SemanticMatcher(self._classifier, registry),
            pattern_matcher=PatternMatcher(self._analyzer, registry),
            aggregator=EnsembleAggregator(ModifierExtractor(registry)),
            config=self.config
        )

    def set_current_goal(self, goal: str) -> Optional[str]:
        """Set modeling goal using ensemble matching."""
        self._current_goal = goal

        # Get scene context
        context = self._analyzer.get_scene_context()

        # Run ensemble matching
        result = self._ensemble_matcher.match(goal, context)

        if result.workflow_name:
            self._pending_workflow = result.workflow_name
            self._last_ensemble_result = result

            # Store modifiers for workflow expansion
            self._pending_modifiers = result.modifiers

            self.logger.log_info(
                f"Goal '{goal}' matched workflow: {result.workflow_name} "
                f"(ensemble score: {result.final_score:.3f})"
            )

            return result.workflow_name

        self._pending_workflow = None
        self.logger.log_info(f"Goal '{goal}' set (no matching workflow)")
        return None

    def _expand_workflow(self, ...):
        """Expand workflow with modifiers from ensemble result."""
        # Use self._pending_modifiers instead of building from scratch
        # This ensures modifiers are ALWAYS applied regardless of match type
        pass
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Application | `server/router/application/router.py` | Replace fallback matching with `EnsembleMatcher` |
| Application | `server/router/application/router.py` | Store and use `_pending_modifiers` |
| Unit Tests | `tests/unit/router/test_router_ensemble.py` | Router integration tests |
| E2E Tests | `tests/e2e/router/test_ensemble_matching.py` | Full E2E tests |

---

### TASK-053-10: Composition Mode (Optional/Future)

**Status:** 🚨 To Do (Optional)

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
- [ ] `test_semantic_matcher.py` - Semantic matcher tests
- [ ] `test_pattern_matcher.py` - Pattern matcher tests
- [ ] `test_modifier_extractor.py` - Modifier extraction tests
- [ ] `test_ensemble_aggregator.py` - Aggregation logic tests
- [ ] `test_ensemble_matcher.py` - Full ensemble tests
- [ ] `test_router_ensemble.py` - Router integration tests

### E2E Tests

- [ ] `test_ensemble_matching.py` - Full pipeline tests
- [ ] Test: "prosty stół z prostymi nogami" → modifiers applied
- [ ] Test: "simple table with 4 legs" → CORE_ONLY + straight legs
- [ ] Test: "picnic table" → FULL workflow
- [ ] Test: Multi-language prompts (Polish, German, etc.)

---

## Configuration

Add to `RouterConfig`:

```python
@dataclass
class RouterConfig:
    # ...existing fields...

    # Ensemble matching
    keyword_weight: float = 0.40
    semantic_weight: float = 0.40
    pattern_weight: float = 0.15
    pattern_boost_factor: float = 1.3
    composition_threshold: float = 0.15
    enable_composition_mode: bool = False  # Future feature
```

---

## Files to Create

### New Files

```
server/router/domain/entities/ensemble.py
server/router/domain/interfaces/matcher.py
server/router/application/matcher/keyword_matcher.py
server/router/application/matcher/semantic_matcher.py      # Refactor existing
server/router/application/matcher/pattern_matcher.py
server/router/application/matcher/modifier_extractor.py
server/router/application/matcher/ensemble_aggregator.py
server/router/application/matcher/ensemble_matcher.py

tests/unit/router/matcher/test_keyword_matcher.py
tests/unit/router/matcher/test_semantic_matcher.py
tests/unit/router/matcher/test_pattern_matcher.py
tests/unit/router/matcher/test_modifier_extractor.py
tests/unit/router/matcher/test_ensemble_aggregator.py
tests/unit/router/matcher/test_ensemble_matcher.py
tests/unit/router/test_router_ensemble.py
tests/e2e/router/test_ensemble_matching.py
```

### Files to Modify

```
server/router/application/router.py                        # Use EnsembleMatcher
server/router/application/matcher/__init__.py              # Export new classes
server/router/domain/entities/__init__.py                  # Export new entities
server/router/domain/interfaces/__init__.py                # Export new interfaces
server/router/infrastructure/config.py                     # Add ensemble config
```

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

## Implementation Order

1. **TASK-053-1**: Domain entities (foundation)
2. **TASK-053-2**: Matcher interface (contracts)
3. **TASK-053-6**: Modifier extractor (critical for bug fix)
4. **TASK-053-3**: Keyword matcher refactor
5. **TASK-053-4**: Semantic matcher refactor
6. **TASK-053-5**: Pattern matcher refactor
7. **TASK-053-7**: Ensemble aggregator
8. **TASK-053-8**: Ensemble matcher (orchestrator)
9. **TASK-053-9**: Router integration
10. **TASK-053-10**: Composition mode (optional/future)

---

## Success Criteria

1. **Bug Fixed**: "prosty stół z prostymi nogami" produces straight legs (0°)
2. **Modifiers Always Applied**: Regardless of which matcher wins
3. **Weighted Scoring**: All matchers contribute to final decision
4. **Backward Compatible**: Existing workflows work unchanged
5. **Performance**: No significant latency increase (<50ms)
6. **Logging**: Clear visibility into matcher contributions

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
