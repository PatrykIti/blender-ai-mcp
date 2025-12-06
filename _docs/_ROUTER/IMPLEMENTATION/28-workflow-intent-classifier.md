# 28 - Workflow Intent Classifier

> **Task:** TASK-046-2 | **Status:** 📋 Planned

---

## Overview

Classifies user prompts to workflows using LaBSE embeddings. Unlike the existing `IntentClassifier` (for tools), this classifier works with workflow definitions and enables semantic matching across workflows.

## Interface

```python
class WorkflowIntentClassifier:
    """Classifies user prompts to workflows using LaBSE embeddings."""

    def load_workflow_embeddings(self, workflows: Dict[str, Any]) -> None:
        """Load and cache workflow embeddings."""

    def find_similar(self, prompt: str, top_k: int = 3, threshold: float = 0.0) -> List[Tuple[str, float]]:
        """Find workflows semantically similar to prompt."""

    def find_best_match(self, prompt: str, min_confidence: float = 0.5) -> Optional[Tuple[str, float]]:
        """Find the best matching workflow."""

    def get_generalization_candidates(self, prompt: str, min_similarity: float = 0.3) -> List[Tuple[str, float]]:
        """Get workflows that could be generalized for this prompt."""
```

## Implementation

**File:** `server/router/application/classifier/workflow_intent_classifier.py`

### Key Components

1. **LaBSE Model Loading** - Same model as IntentClassifier
2. **Workflow Text Collection** - Collects `sample_prompts`, `trigger_keywords`, name, description
3. **Embedding Computation** - Computes normalized embeddings for each workflow
4. **Similarity Search** - Cosine similarity using dot product (normalized vectors)

### Embedding Strategy

```python
# For each workflow, combine:
texts = []
texts.extend(workflow.sample_prompts)     # Primary: user prompt examples
texts.extend(workflow.trigger_keywords)    # Secondary: keywords
texts.append(name.replace("_", " "))       # Tertiary: workflow name
texts.append(workflow.description)         # Quaternary: description

# Encode combined text
embedding = model.encode(" ".join(texts), normalize_embeddings=True)
```

## Configuration

```python
# server/router/infrastructure/config.py

@dataclass
class RouterConfig:
    # Semantic matching thresholds
    workflow_similarity_threshold: float = 0.5  # Min for semantic match
    generalization_threshold: float = 0.3       # Min for generalization
```

## Dependencies

- TASK-046-1: Workflow Sample Prompts (must add `sample_prompts` to workflows first)

## Tests

```python
# tests/unit/router/application/classifier/test_workflow_intent_classifier.py

def test_find_similar_returns_ranked_workflows():
    classifier = WorkflowIntentClassifier()
    classifier.load_workflow_embeddings(mock_workflows)

    results = classifier.find_similar("create a mobile phone", top_k=3)

    assert len(results) == 3
    assert results[0][0] == "phone_workflow"
    assert results[0][1] > 0.7  # High similarity

def test_multilingual_matching():
    """LaBSE supports 109 languages."""
    classifier = WorkflowIntentClassifier()
    classifier.load_workflow_embeddings(mock_workflows)

    # Polish prompt
    results = classifier.find_similar("zrób telefon", top_k=1)
    assert results[0][0] == "phone_workflow"

    # German prompt
    results = classifier.find_similar("erstelle ein Handy", top_k=1)
    assert results[0][0] == "phone_workflow"
```

## Usage

```python
from server.router.application.classifier import WorkflowIntentClassifier
from server.router.application.workflows import get_workflow_registry

classifier = WorkflowIntentClassifier()
registry = get_workflow_registry()

# Load embeddings from registry
workflows = {name: registry.get_workflow(name) for name in registry.get_all_workflows()}
classifier.load_workflow_embeddings(workflows)

# Find similar workflows
results = classifier.find_similar("comfortable office chair")
# → [("table_workflow", 0.72), ("tower_workflow", 0.45), ...]
```

## See Also

- [14-intent-classifier.md](./14-intent-classifier.md) - Tool intent classifier (similar pattern)
- [29-semantic-workflow-matcher.md](./29-semantic-workflow-matcher.md) - Uses this classifier
