# 32. Workflow Adapter

> **Task:** TASK-051 | **Status:** ✅ Done | **Date:** 2025-12-07

---

## Overview

`WorkflowAdapter` adapts workflow execution based on semantic match confidence level. When a workflow is triggered but the match confidence is not HIGH, the adapter filters optional steps to create a more appropriate execution plan.

**Problem:** Router has confidence levels but doesn't use them. A "simple table with 4 legs" prompt triggers `picnic_table_workflow` with all 49 steps including benches.

**Solution:** Adapt workflow steps based on confidence:
- **HIGH** → Execute all steps
- **MEDIUM** → Execute core + tag-matching optional steps
- **LOW/NONE** → Execute only core steps

---

## Interface

```python
# server/router/domain/interfaces/i_workflow_adapter.py

from abc import ABC, abstractmethod
from typing import List, Tuple
from server.router.application.workflows.base import WorkflowStep, WorkflowDefinition

class IWorkflowAdapter(ABC):
    """Interface for workflow adaptation based on confidence."""

    @abstractmethod
    def adapt(
        self,
        definition: WorkflowDefinition,
        confidence_level: str,
        user_prompt: str,
    ) -> Tuple[List[WorkflowStep], "AdaptationResult"]:
        """Adapt workflow steps based on confidence level."""
        pass

    @abstractmethod
    def should_adapt(
        self,
        definition: WorkflowDefinition,
        confidence_level: str,
    ) -> bool:
        """Check if workflow needs adaptation."""
        pass
```

---

## Implementation

### WorkflowStep Extensions

```python
# server/router/application/workflows/base.py

@dataclass
class WorkflowStep:
    tool: str
    params: Dict[str, Any]
    description: Optional[str] = None
    condition: Optional[str] = None
    optional: bool = False          # NEW: Can be skipped
    tags: List[str] = field(default_factory=list)  # NEW: For filtering
```

### WorkflowAdapter Engine

```python
# server/router/application/engines/workflow_adapter.py

@dataclass
class AdaptationResult:
    """Result of workflow adaptation."""
    original_step_count: int
    adapted_step_count: int
    skipped_steps: List[str]
    confidence_level: str
    strategy: str  # "FULL", "FILTERED", "CORE_ONLY"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_step_count": self.original_step_count,
            "adapted_step_count": self.adapted_step_count,
            "skipped_count": len(self.skipped_steps),
            "skipped_steps": self.skipped_steps,
            "confidence_level": self.confidence_level,
            "strategy": self.strategy,
        }


class WorkflowAdapter:
    """Adapts workflows based on match confidence."""

    def __init__(
        self,
        classifier: Optional[WorkflowIntentClassifier] = None,
        semantic_threshold: float = 0.6,
    ):
        self._classifier = classifier
        self._semantic_threshold = semantic_threshold

    def adapt(
        self,
        definition: WorkflowDefinition,
        confidence_level: str,
        user_prompt: str,
    ) -> Tuple[List[WorkflowStep], AdaptationResult]:
        """Adapt workflow steps based on confidence level."""
        all_steps = definition.steps

        # HIGH confidence = execute everything
        if confidence_level == "HIGH":
            return self._full_execution(all_steps, confidence_level)

        # Separate core and optional steps
        core_steps = [s for s in all_steps if not s.optional]
        optional_steps = [s for s in all_steps if s.optional]

        # LOW/NONE = core only
        if confidence_level in ("LOW", "NONE"):
            return self._core_only(core_steps, optional_steps, confidence_level)

        # MEDIUM = core + filtered optional
        if confidence_level == "MEDIUM":
            relevant = self._filter_by_relevance(optional_steps, user_prompt)
            return self._filtered_execution(
                core_steps, relevant, optional_steps, confidence_level
            )

        # Fallback
        return self._full_execution(all_steps, confidence_level)

    def _filter_by_relevance(
        self,
        steps: List[WorkflowStep],
        prompt: str
    ) -> List[WorkflowStep]:
        """Filter optional steps by tag matching or semantic similarity."""
        relevant = []
        prompt_lower = prompt.lower()

        for step in steps:
            # 1. Tag matching (fast)
            if step.tags and any(tag.lower() in prompt_lower for tag in step.tags):
                relevant.append(step)
                continue

            # 2. Semantic similarity (fallback for steps without tags)
            if step.description and self._classifier:
                similarity = self._classifier.similarity(prompt, step.description)
                if similarity >= self._semantic_threshold:
                    relevant.append(step)

        return relevant

    def should_adapt(
        self,
        definition: WorkflowDefinition,
        confidence_level: str,
    ) -> bool:
        """Check if workflow needs adaptation."""
        if confidence_level == "HIGH":
            return False

        # Check if there are optional steps to filter
        has_optional = any(s.optional for s in definition.steps)
        return has_optional
```

---

## Configuration

```python
# server/router/infrastructure/config.py

@dataclass
class RouterConfig:
    # ... existing config ...

    # Workflow Adaptation (TASK-051)
    enable_workflow_adaptation: bool = True
    adaptation_semantic_threshold: float = 0.6
```

---

## Integration with Router

```python
# server/router/application/router.py

class SupervisorRouter:
    def __init__(self, config: RouterConfig, ...):
        # ... existing init ...

        # Initialize WorkflowAdapter
        self._workflow_adapter = WorkflowAdapter(
            classifier=self._workflow_classifier,
            semantic_threshold=config.adaptation_semantic_threshold,
        )

    def _expand_triggered_workflow(
        self,
        workflow_name: str,
        match_result: MatchResult,
        context: Dict[str, Any],
    ) -> List[InterceptedToolCall]:
        """Expand workflow with optional adaptation."""
        definition = self._workflow_registry.get_definition(workflow_name)

        # Adapt if needed
        if (
            self.config.enable_workflow_adaptation
            and match_result.requires_adaptation
            and self._workflow_adapter.should_adapt(definition, match_result.confidence_level)
        ):
            adapted_steps, result = self._workflow_adapter.adapt(
                definition,
                match_result.confidence_level,
                match_result.user_prompt or "",
            )
            # Use adapted steps for expansion
            definition = WorkflowDefinition(
                name=definition.name,
                description=definition.description,
                steps=adapted_steps,
                # ... other fields ...
            )

        # Continue with normal expansion
        return self._workflow_expansion_engine.expand(definition, context)
```

---

## YAML Workflow Example

```yaml
# picnic_table.yaml
name: picnic_table_workflow
description: Picnic table with optional benches

steps:
  # Core steps (always executed)
  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "TableTop" }
    description: Create table top

  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "Leg1" }
    description: Create first leg

  # Optional steps (filtered by confidence)
  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "BenchLeft" }
    description: Create left bench
    optional: true
    tags: ["bench", "seating", "left"]

  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "BenchRight" }
    description: Create right bench
    optional: true
    tags: ["bench", "seating", "right"]
```

---

## Tests

Located in `tests/unit/router/application/test_workflow_adapter.py`:

```python
def test_high_confidence_returns_all_steps():
    """HIGH confidence executes all steps."""
    adapter = WorkflowAdapter()
    steps, result = adapter.adapt(definition, "HIGH", "prompt")
    assert len(steps) == len(definition.steps)
    assert result.strategy == "FULL"

def test_low_confidence_skips_optional():
    """LOW confidence skips optional steps."""
    adapter = WorkflowAdapter()
    steps, result = adapter.adapt(definition, "LOW", "prompt")
    assert all(not s.optional for s in steps)
    assert result.strategy == "CORE_ONLY"

def test_medium_confidence_filters_by_tags():
    """MEDIUM confidence includes tag-matching optional steps."""
    adapter = WorkflowAdapter()
    steps, result = adapter.adapt(definition, "MEDIUM", "table with benches")
    # "bench" tag matches "benches" in prompt
    assert any("Bench" in s.params.get("name", "") for s in steps)
    assert result.strategy == "FILTERED"
```

**Test Summary:**
- 20 unit tests
- All passing

---

## Adaptation Strategies

| Confidence | Strategy | Behavior |
|------------|----------|----------|
| **HIGH** (≥0.90) | `FULL` | Execute ALL steps |
| **MEDIUM** (≥0.75) | `FILTERED` | Core + tag-matching optional |
| **LOW** (≥0.60) | `CORE_ONLY` | Core steps only |
| **NONE** (<0.60) | `CORE_ONLY` | Core steps only (fallback) |

---

## Expected Results

```
"create a picnic table"       → HIGH (0.92)  → 49 steps (full workflow)
"simple table with 4 legs"    → LOW (0.68)   → ~33 steps (no benches)
"table with benches"          → MEDIUM (0.78) → ~40 steps (core + bench)
```

---

## See Also

- [TASK-051: Confidence-Based Workflow Adaptation](../../_TASKS/TASK-051_Confidence_Based_Workflow_Adaptation.md)
- [Changelog #97](../../_CHANGELOG/97-2025-12-07-confidence-based-workflow-adaptation.md)
- [29-semantic-workflow-matcher.md](./29-semantic-workflow-matcher.md)
- [WORKFLOWS/README.md](../WORKFLOWS/README.md)
