# 29 - Semantic Workflow Matcher

> **Task:** TASK-046-3 | **Status:** ✅ Done

---

## Overview

Combines workflow matching with generalization capabilities. When no exact workflow match exists, it can find similar workflows and create hybrid approaches.

## Interface

```python
@dataclass
class MatchResult:
    """Result of workflow matching."""
    workflow_name: Optional[str] = None
    confidence: float = 0.0
    match_type: str = "none"  # exact, semantic, generalized, none
    similar_workflows: List[Tuple[str, float]] = field(default_factory=list)
    applied_rules: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SemanticWorkflowMatcher:
    """Matches prompts to workflows using semantic understanding."""

    def initialize(self, registry: WorkflowRegistry) -> None:
        """Initialize with workflow registry."""

    def match(self, prompt: str, context: Optional[Dict] = None) -> MatchResult:
        """Match prompt to workflow with 3-tier fallback."""

    def find_similar(self, prompt: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Find workflows similar to prompt."""
```

## Implementation

**File:** `server/router/application/matcher/semantic_workflow_matcher.py`

### Matching Hierarchy

```
┌─────────────────────────────────────────────────────┐
│ 1. Exact Keyword Match (fastest, confidence=1.0)    │
│    "create a phone" → phone_workflow                │
├─────────────────────────────────────────────────────┤
│ 2. Semantic Similarity (LaBSE, confidence=score)    │
│    "design a mobile device" → phone_workflow (0.85) │
├─────────────────────────────────────────────────────┤
│ 3. Generalization (combine similar workflows)       │
│    "make a chair" → table_workflow (0.72)           │
│    + proportions from tower_workflow (0.45)         │
└─────────────────────────────────────────────────────┘
```

### Match Flow

```python
def match(self, prompt: str, context: Optional[Dict] = None) -> MatchResult:
    # Step 1: Exact keyword match
    keyword_match = self._registry.find_by_keywords(prompt)
    if keyword_match:
        return MatchResult(
            workflow_name=keyword_match,
            confidence=1.0,
            match_type="exact",
        )

    # Step 2: Semantic similarity
    semantic_result = self._classifier.find_best_match(
        prompt,
        min_confidence=self._config.workflow_similarity_threshold,
    )
    if semantic_result:
        return MatchResult(
            workflow_name=semantic_result[0],
            confidence=semantic_result[1],
            match_type="semantic",
        )

    # Step 3: Generalization
    similar = self._classifier.get_generalization_candidates(prompt)
    if similar:
        return self._generalize(prompt, similar, context)

    return MatchResult(match_type="none")
```

## Configuration

```python
@dataclass
class RouterConfig:
    workflow_similarity_threshold: float = 0.5  # Min for semantic match
    generalization_threshold: float = 0.3       # Min for generalization
    enable_generalization: bool = True          # Enable/disable generalization
```

## Dependencies

- TASK-046-2: WorkflowIntentClassifier

## Tests

```python
# tests/unit/router/application/matcher/test_semantic_workflow_matcher.py

def test_exact_match_takes_priority():
    matcher = SemanticWorkflowMatcher()
    matcher.initialize(registry)

    result = matcher.match("create a phone")

    assert result.match_type == "exact"
    assert result.confidence == 1.0
    assert result.workflow_name == "phone_workflow"

def test_semantic_match_when_no_exact():
    matcher = SemanticWorkflowMatcher()
    matcher.initialize(registry)

    result = matcher.match("design a mobile device")

    assert result.match_type == "semantic"
    assert result.confidence > 0.5
    assert result.workflow_name == "phone_workflow"

def test_generalization_when_no_direct_match():
    matcher = SemanticWorkflowMatcher()
    matcher.initialize(registry)

    result = matcher.match("create a chair")  # No chair_workflow exists

    assert result.match_type == "generalized"
    assert len(result.similar_workflows) > 0
    assert "table_workflow" in [w for w, _ in result.similar_workflows]
```

## Usage

```python
from server.router.application.matcher import SemanticWorkflowMatcher
from server.router.application.workflows import get_workflow_registry

matcher = SemanticWorkflowMatcher()
matcher.initialize(get_workflow_registry())

# Match with fallback
result = matcher.match("comfortable office chair")

if result.match_type == "exact":
    print(f"Exact match: {result.workflow_name}")
elif result.match_type == "semantic":
    print(f"Semantic match: {result.workflow_name} ({result.confidence:.2f})")
elif result.match_type == "generalized":
    print(f"Generalized from: {result.similar_workflows}")
```

## See Also

- [28-workflow-intent-classifier.md](./28-workflow-intent-classifier.md) - Underlying classifier
- [30-proportion-inheritance.md](./30-proportion-inheritance.md) - Used for generalization
