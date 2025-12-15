# 34 - Ensemble Matching System (TASK-053)

> **Status:** ✅ Done
> **Task:** TASK-053
> **Related:** TASK-046 (Semantic Generalization), TASK-051 (Workflow Adaptation), TASK-052 (Parametric Variables)

## Overview

The Ensemble Matching System replaces the fallback-based `SemanticWorkflowMatcher.match()` flow with parallel ensemble matching. Multiple matchers run independently and their results are aggregated using weighted consensus.

## Architecture

```
User Prompt: "simple table with 4 straight legs"
                        │
                        ▼
┌───────────────────────────────────────────────────────────────────┐
│                    EnsembleMatcher.match()                        │
│                                                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │ KeywordMatcher  │  │ SemanticMatcher │  │ PatternMatcher  │   │
│  │   weight: 0.40  │  │   weight: 0.40  │  │   weight: 0.15  │   │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘   │
│           │                    │                    │             │
│           ▼                    ▼                    ▼             │
│  MatcherResult         MatcherResult         MatcherResult        │
│  workflow: table       workflow: table       workflow: None       │
│  confidence: 0.85      confidence: 0.90      confidence: 0.0      │
└───────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────────┐
│               EnsembleAggregator.aggregate()                      │
│                                                                   │
│  1. Group scores by workflow:                                     │
│     picnic_table_workflow: {keyword: 0.34, semantic: 0.36}        │
│                                                                   │
│  2. Calculate final score: 0.34 + 0.36 = 0.70                     │
│                                                                   │
│  3. Apply pattern boost (if pattern matched): score × 1.3         │
│                                                                   │
│  4. Select best_workflow = "picnic_table_workflow"                │
│                                                                   │
│  5. CRITICAL: Extract modifiers via ModifierExtractor             │
└───────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────────┐
│            ModifierExtractor.extract(prompt, best_workflow)       │
│                                                                   │
│  1. Extract n-grams from prompt:                                  │
│     ["simple", "table", "straight", "legs", "simple table", ...]  │
│                                                                   │
│  2. For each modifier keyword in YAML:                            │
│     "straight legs" ↔ "straight" = 0.65                           │
│     "straight legs" ↔ "legs"   = 0.42                             │
│     "straight legs" ↔ "straight legs" = 0.877 ← BEST!             │
│                                                                   │
│  3. Collect all matches above threshold (0.70):                   │
│     [("straight legs", 0.877), ("vertical legs", 0.811), ...]     │
│                                                                   │
│  4. Sort by similarity, select ONLY the best match                │
│                                                                   │
│  → modifiers = {leg_angle_left: 0, leg_angle_right: 0}            │
└───────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────────┐
│                      EnsembleResult                               │
│                                                                   │
│  workflow_name: "picnic_table_workflow"                           │
│  final_score: 0.70                                                │
│  confidence_level: "HIGH"                                         │
│  modifiers: {leg_angle_left: 0, leg_angle_right: 0}               │
│  matcher_contributions: {keyword: 0.34, semantic: 0.36}           │
│  requires_adaptation: False                                       │
└───────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────────┐
│              router._pending_modifiers = result.modifiers         │
│              (stored, waiting for execute_pending_workflow)       │
└───────────────────────────────────────────────────────────────────┘
```

## Components

### 1. EnsembleMatcher

**File:** `server/router/application/matcher/ensemble_matcher.py`

Orchestrates parallel matching using multiple matchers:
- KeywordMatcher (weight: 0.40)
- SemanticMatcher (weight: 0.40)
- PatternMatcher (weight: 0.15)

```python
class EnsembleMatcher:
    def match(self, prompt: str, context: Optional[SceneContext] = None) -> EnsembleResult:
        results: List[MatcherResult] = []
        for matcher in self._matchers:
            result = matcher.match(prompt, context_dict)
            results.append(result)

        return self._aggregator.aggregate(results, prompt)
```

### 2. EnsembleAggregator

**File:** `server/router/application/matcher/ensemble_aggregator.py`

Aggregates results from all matchers using weighted consensus:

```python
class EnsembleAggregator:
    PATTERN_BOOST = 1.3  # Multiplier when pattern matcher fires
    COMPOSITION_THRESHOLD = 0.15  # For detecting similar workflows

    def aggregate(self, results: List[MatcherResult], prompt: str) -> EnsembleResult:
        # 1. Group scores by workflow
        # 2. Sum weighted scores
        # 3. Apply pattern boost if applicable
        # 4. Select best workflow
        # 5. CRITICAL: Extract modifiers
        modifier_result = self._modifier_extractor.extract(prompt, best_workflow)

        return EnsembleResult(
            workflow_name=best_workflow,
            modifiers=modifier_result.modifiers,
            ...
        )
```

### 3. ModifierExtractor

**File:** `server/router/application/matcher/modifier_extractor.py`

Extracts parametric modifiers from prompts using LaBSE semantic matching:

```python
class ModifierExtractor(IModifierExtractor):
    def extract(self, prompt: str, workflow_name: str) -> ModifierResult:
        # 1. Get workflow definition with modifiers from YAML
        definition = self._registry.get_definition(workflow_name)

        # 2. Extract n-grams from prompt
        ngrams = self._extract_ngrams(prompt)  # 1-3 word phrases

        # 3. Find best semantic match for each modifier keyword
        semantic_matches = []
        for keyword, values in definition.modifiers.items():
            for ngram in ngrams:
                sim = self._classifier.similarity(keyword, ngram)
                if sim >= self._similarity_threshold:
                    semantic_matches.append((keyword, values, sim, ngram))

        # 4. Select ONLY the best match (highest similarity)
        if semantic_matches:
            semantic_matches.sort(key=lambda x: x[2], reverse=True)
            best_keyword, best_values, _, _ = semantic_matches[0]
            modifiers.update(best_values)

        return ModifierResult(modifiers=modifiers, ...)
```

### 4. Individual Matchers

#### KeywordMatcher
**File:** `server/router/application/matcher/keyword_matcher.py`

Matches workflow trigger keywords from YAML definitions:
```yaml
# picnic_table.yaml
trigger_keywords:
  - "table"
  - "picnic"
  - "table"  # Polish
```

#### SemanticMatcher
**File:** `server/router/application/matcher/semantic_matcher.py`

Uses LaBSE embeddings for semantic similarity matching:
- Compares prompt embedding vs workflow sample_prompts embeddings
- Supports 109 languages natively

#### PatternMatcher
**File:** `server/router/application/matcher/pattern_matcher.py`

Matches geometry patterns from scene context:
- `tower_like`: height > width × 3
- `phone_like`: flat, rectangular, thin
- `table_like`: flat horizontal surface

## Data Entities

### MatcherResult

```python
@dataclass
class MatcherResult:
    matcher_name: str      # "keyword", "semantic", "pattern"
    workflow_name: Optional[str]
    confidence: float      # 0.0 - 1.0
    weight: float          # Matcher weight for aggregation
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### EnsembleResult

```python
@dataclass
class EnsembleResult:
    workflow_name: Optional[str]
    final_score: float
    confidence_level: str  # "HIGH", "MEDIUM", "LOW", "NONE"
    modifiers: Dict[str, Any]
    matcher_contributions: Dict[str, float]
    requires_adaptation: bool
    composition_mode: bool = False
    extra_workflows: List[str] = field(default_factory=list)
```

### ModifierResult

```python
@dataclass
class ModifierResult:
    modifiers: Dict[str, Any]       # Variable overrides
    matched_keywords: List[str]     # Which keywords matched
    confidence_map: Dict[str, float]  # Keyword → similarity score
```

## Configuration

### Weights

| Matcher | Weight | Rationale |
|---------|--------|-----------|
| KeywordMatcher | 0.40 | Explicit trigger keywords |
| SemanticMatcher | 0.40 | LaBSE semantic similarity |
| PatternMatcher | 0.15 | Geometry-based detection |

### Thresholds

| Threshold | Value | Purpose |
|-----------|-------|---------|
| `similarity_threshold` | 0.70 | Minimum for modifier match |
| `PATTERN_BOOST` | 1.3 | Score multiplier when pattern matches |
| `COMPOSITION_THRESHOLD` | 0.15 | Detect similar-scoring workflows |

### Confidence Levels

| Level | Score Range | Adaptation |
|-------|-------------|------------|
| HIGH | ≥ 0.70 | Full workflow |
| MEDIUM | ≥ 0.40 | Filtered (core + tag-matching) |
| LOW | < 0.40 | Core only |

## Integration with Router

### Initialization (router.py)

```python
def _ensure_ensemble_initialized(self) -> bool:
    # Use shared LaBSE model from DI (singleton)
    from server.infrastructure.di import get_labse_model
    self._workflow_classifier = WorkflowIntentClassifier(
        config=self.config,
        model=get_labse_model(),
    )

    # Create modifier extractor with LaBSE
    modifier_extractor = ModifierExtractor(
        registry=registry,
        classifier=self._workflow_classifier,
        similarity_threshold=0.70,
    )

    # Create aggregator with modifier extractor
    aggregator = EnsembleAggregator(modifier_extractor, self.config)

    # Create ensemble matcher
    self._ensemble_matcher = EnsembleMatcher(
        keyword_matcher=KeywordMatcher(registry),
        semantic_matcher=SemanticMatcher(classifier, registry, config),
        pattern_matcher=PatternMatcher(registry),
        aggregator=aggregator,
    )
```

### Goal Setting (router.py)

```python
def _set_goal_ensemble(self, goal: str) -> Optional[str]:
    result = self._ensemble_matcher.match(goal, context)

    if result.workflow_name:
        self._pending_workflow = result.workflow_name
        self._pending_modifiers = result.modifiers  # CRITICAL!
        self._last_ensemble_result = result
        return result.workflow_name

    return None
```

### Execution (router.py)

```python
def execute_pending_workflow(self, variables: Optional[Dict] = None):
    # Use modifiers from ensemble result
    final_variables = dict(self._pending_modifiers)
    if variables:
        final_variables.update(variables)

    # WorkflowAdapter filters steps by confidence
    if should_adapt:
        adapted_steps, _ = self._workflow_adapter.adapt(
            definition, self._last_ensemble_result
        )
        steps_to_execute = adapted_steps

    # Expand steps with final_variables
    resolved_steps = registry._resolve_definition_params(steps_to_execute, final_variables)
    calls = registry._steps_to_calls(resolved_steps, workflow_name)
```

## Multilingual Support

LaBSE (Language-Agnostic BERT Sentence Embeddings) supports 109 languages natively. This enables:

- Polish: `"straight legs"` → `"straight legs"` (0.877 similarity)
- German: `"straight legs"` → `"straight legs"`
- No need to add translations to YAML modifiers

### Example

```yaml
# picnic_table.yaml - Only English keywords needed
modifiers:
  "straight legs":
    leg_angle_left: 0
    leg_angle_right: 0
  "angled legs":
    leg_angle_left: 0.32
    leg_angle_right: -0.32
```

```python
# Polish prompt automatically matches English keyword
prompt = "simple table with 4 straight legs"
result = extractor.extract(prompt, "picnic_table_workflow")
# → modifiers = {leg_angle_left: 0, leg_angle_right: 0}
# → matched_keywords = ["straight legs"]
# → confidence_map = {"straight legs": 0.877}
```

## Testing

### Unit Tests

```bash
PYTHONPATH=. poetry run pytest tests/unit/router/application/matcher/ -v
```

### Local Integration Test

```python
from server.router.application.matcher.modifier_extractor import ModifierExtractor
from server.router.application.classifier.workflow_intent_classifier import WorkflowIntentClassifier
from server.infrastructure.di import get_labse_model

# Create classifier with shared model
classifier = WorkflowIntentClassifier(config=config, model=get_labse_model())

# Create extractor
extractor = ModifierExtractor(registry=registry, classifier=classifier)

# Test
result = extractor.extract("simple table with 4 straight legs", "picnic_table_workflow")
assert result.modifiers["leg_angle_left"] == 0
assert "straight legs" in result.matched_keywords
```

## Files

| File | Purpose |
|------|---------|
| `server/router/application/matcher/ensemble_matcher.py` | Main orchestrator |
| `server/router/application/matcher/ensemble_aggregator.py` | Weighted consensus |
| `server/router/application/matcher/modifier_extractor.py` | LaBSE modifier matching |
| `server/router/application/matcher/keyword_matcher.py` | Trigger keyword matching |
| `server/router/application/matcher/semantic_matcher.py` | LaBSE workflow matching |
| `server/router/application/matcher/pattern_matcher.py` | Geometry pattern matching |
| `server/router/domain/entities/ensemble.py` | Data entities |
| `server/router/domain/interfaces/matcher.py` | IMatcher, IModifierExtractor |

## Related Documentation

- [28-workflow-intent-classifier.md](./28-workflow-intent-classifier.md) - LaBSE classifier
- [29-semantic-workflow-matcher.md](./29-semantic-workflow-matcher.md) - Semantic matching
- [32-workflow-adapter.md](./32-workflow-adapter.md) - Confidence-based adaptation
- [33-parametric-variables.md](./33-parametric-variables.md) - YAML variable system
