# 102 - Ensemble Matching & Modifier Extraction Fixes (TASK-055 Bugfixes)

**Date:** 2025-12-08

## Summary

Fixed three critical bugs in Router workflow execution discovered during Polish prompt testing.

## Bugs Fixed

### Bug 1: Step Count Mismatch (25 vs 55)

**Problem:** WorkflowAdapter correctly calculated 25 core steps (skipping 30 optional), but `expand_workflow()` was still executing all 55 steps.

**Root Cause:** `execute_pending_workflow()` called `registry.expand_workflow()` which ignores `steps_to_execute` and expands the full `definition.steps`.

**Fix:** Bypassed `expand_workflow()` and directly called:
```python
resolved_steps = registry._resolve_definition_params(steps_to_execute, final_variables)
calls = registry._steps_to_calls(resolved_steps, workflow_name)
```

**File:** `server/router/application/router.py` (lines 1385-1400)

### Bug 2: Polish Modifier Not Matching (0.32 vs 0)

**Problem:** Prompt `"prosty stół z 4 prostymi nogami"` should apply `"straight legs"` modifier (`leg_angle=0`) but got default values (`leg_angle=0.32`).

**Root Cause (2a):** LaBSE model not injected into `WorkflowIntentClassifier`:
```python
# Before (model=None)
self._workflow_classifier = WorkflowIntentClassifier(config=self.config)

# After (model from DI singleton)
from server.infrastructure.di import get_labse_model
self._workflow_classifier = WorkflowIntentClassifier(
    config=self.config,
    model=get_labse_model(),
)
```

**Root Cause (2b):** ModifierExtractor applied ALL modifiers above threshold instead of selecting the best one:
```
"prostymi nogami" ↔ "straight legs" = 0.877 ← Should win!
"prostymi nogami" ↔ "vertical legs" = 0.811
"prostymi nogami" ↔ "angled legs"   = 0.798 ← Was winning (last applied)
```

**Fix:** Modified `ModifierExtractor.extract()` to:
1. Collect all matches above threshold
2. Sort by similarity descending
3. Apply ONLY the best match

**Files:**
- `server/router/application/router.py` (lines 685-692)
- `server/router/application/matcher/modifier_extractor.py` (lines 127-176)

### Bug 3: Confidence Level Always LOW for Polish Prompts

**Problem:** Prompt `"utworz stol piknikowy"` executed only 25 core steps (no benches) despite being a clear picnic table request.

**Root Cause:** Absolute confidence thresholds didn't account for single-matcher scenarios:

```
Prompt: "utworz stol piknikowy" (Polish)

KeywordMatcher:  0.0   (no English keywords in Polish prompt)
SemanticMatcher: 0.336 (0.84 similarity × 0.40 weight)
PatternMatcher:  0.0   (empty scene)
─────────────────────────
TOTAL:           0.336

Old thresholds:
  score >= 0.7 → HIGH    # 0.336 < 0.7 → NO
  score >= 0.4 → MEDIUM  # 0.336 < 0.4 → NO
  else → LOW             # ← This won! → CORE_ONLY (no benches)
```

**Fix:** Normalize score relative to maximum possible from contributing matchers:

```python
def _calculate_max_possible_score(self, contributions: Dict[str, float]) -> float:
    """When only semantic matcher contributes, max is 0.40 (not 0.95)."""
    WEIGHTS = {"keyword": 0.40, "semantic": 0.40, "pattern": 0.195}
    return sum(WEIGHTS[name] for name in contributions.keys())

def _determine_confidence_level(self, score, prompt, max_possible_score):
    normalized_score = score / max_possible_score  # 0.336 / 0.40 = 0.84 (84%)

    if normalized_score >= 0.70: return "HIGH"   # 0.84 >= 0.70 → YES!
    elif normalized_score >= 0.50: return "MEDIUM"
    else: return "LOW"
```

**Result:**

| Prompt | Matchers | Raw | Max | Normalized | Old | New |
|--------|----------|-----|-----|------------|-----|-----|
| "utworz stol piknikowy" | semantic | 0.336 | 0.40 | 84% | LOW | **HIGH** |
| "create picnic table" | keyword+semantic | 0.74 | 0.80 | 92% | HIGH | **HIGH** |
| "prosty stol" | semantic | 0.30 | 0.40 | 75% | LOW | **LOW** (forced) |

**File:** `server/router/application/matcher/ensemble_aggregator.py` (lines 173-262)

## Architecture Clarification

### Ensemble Matching Flow (TASK-053)

```
User Prompt
    │
    ▼
┌─────────────────────────────────────────────────┐
│  EnsembleMatcher.match() - WHICH workflow?      │
│  ├─ KeywordMatcher  → workflow (0.40 weight)    │
│  ├─ SemanticMatcher → workflow (0.40 weight)    │
│  └─ PatternMatcher  → workflow (0.15 weight)    │
│                                                 │
│  EnsembleAggregator.aggregate()                 │
│  → Weighted consensus → best_workflow           │
└─────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────┐
│  ModifierExtractor.extract() - WHICH params?    │
│  ├─ Extract n-grams from prompt                 │
│  ├─ LaBSE similarity vs YAML modifier keywords  │
│  └─ Select BEST match (highest similarity)      │
│                                                 │
│  → modifiers = {leg_angle_left: 0, ...}         │
└─────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────┐
│  router._pending_modifiers = result.modifiers   │
│  (stored, waiting for execute)                  │
└─────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────┐
│  execute_pending_workflow()                     │
│  ├─ final_variables = _pending_modifiers        │
│  ├─ WorkflowAdapter filters steps (confidence)  │
│  └─ Expand steps with final_variables           │
│                                                 │
│  → Blender executes 25 tool calls               │
└─────────────────────────────────────────────────┘
```

### Key Components

| Component | Purpose | Location |
|-----------|---------|----------|
| **EnsembleMatcher** | Orchestrates 3 matchers | `matcher/ensemble_matcher.py` |
| **EnsembleAggregator** | Weighted consensus + calls ModifierExtractor | `matcher/ensemble_aggregator.py` |
| **ModifierExtractor** | LaBSE semantic modifier matching | `matcher/modifier_extractor.py` |
| **KeywordMatcher** | Trigger keyword matching | `matcher/keyword_matcher.py` |
| **SemanticMatcher** | LaBSE workflow similarity | `matcher/semantic_matcher.py` |
| **PatternMatcher** | Geometry pattern detection | `matcher/pattern_matcher.py` |

## Test Results

```python
# Local test with Polish prompt
prompt = "prosty stół z 4 prostymi nogami"
result = extractor.extract(prompt, "picnic_table_workflow")

# Before fix:
# leg_angle_left = 0.32 (wrong - angled legs)
# Matched: ['straight legs', 'vertical legs', 'angled legs']

# After fix:
# leg_angle_left = 0 (correct - straight legs)
# Matched: ['straight legs']
# Confidence: {'straight legs': 0.877}
```

## Files Changed

| File | Changes |
|------|---------|
| `server/router/application/router.py` | Use DI for LaBSE model, bypass expand_workflow() |
| `server/router/application/matcher/modifier_extractor.py` | Select only best semantic match |
| `server/router/application/matcher/ensemble_aggregator.py` | Normalize confidence score relative to contributing matchers |

## Related Tasks

- **TASK-053:** Ensemble Matching System (original implementation)
- **TASK-055:** Interactive Parameter Resolution (where bugs were discovered)
- **TASK-048:** Shared LaBSE via DI (singleton pattern used in fix)
