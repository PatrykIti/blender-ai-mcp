# 102 - Ensemble Matching & Modifier Extraction Fixes (TASK-055 Bugfixes)

**Date:** 2025-12-08

## Summary

Fixed five critical bugs in Router workflow execution discovered during Polish and German prompt testing.

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

### Bug 4: SemanticMatcher No-Match for Prompts with Numbers

**Problem:** Prompt `"stol z nogami pod katem 45 stopni"` returned `no_match` even though workflow exists.

**Root Cause:** `SemanticMatcher` filtered results before they reached `EnsembleAggregator`:

```
Flow (before fix):
                                     Bug 4 HERE
                                         ↓
Prompt → Classifier.find_best_match_with_confidence() → score 0.587 < 0.60 → workflow_id=None
              ↓
         SemanticMatcher.match() → checks workflow_id → None → returns confidence=0.0
              ↓
         EnsembleAggregator → receives 0.0 → no normalization possible!
                                 Bug 3 fix never sees the original score
```

Test results:
```
"stol z nogami pod katem 45 stopni" → score=0.587 (< 0.60 threshold → NONE → workflow_id=None)
"stol z nogami pod katem" (no "45 stopni") → score=0.702 (>= 0.60 → LOW → matched!)
```

Adding numbers like "45 stopni" reduces LaBSE semantic similarity (adds "noise").

**Fix:** Modified `SemanticMatcher.match()` to return RAW scores without filtering by `confidence_level`. Uses `fallback_candidates` when `workflow_id` is `None`:

```python
# TASK-055-FIX (Bug 4): Return result regardless of confidence_level
# If classifier set workflow_id to None due to threshold,
# get it from fallback_candidates
if workflow_id is None and score > 0 and result.get("fallback_candidates"):
    best_fallback = result["fallback_candidates"][0]
    workflow_id = best_fallback.get("workflow_id")

# Return match if we have a workflow (regardless of confidence_level)
if workflow_id and score > 0:
    return MatcherResult(
        workflow_name=workflow_id,
        confidence=score,  # Raw score, let aggregator normalize
        ...
    )
```

**Result:**

| Prompt | Before Fix | After Fix |
|--------|------------|-----------|
| "stol z nogami pod katem 45 stopni" | `no_match` | `picnic_table_workflow` (MEDIUM) |
| "stol z nogami pod katem" | `picnic_table_workflow` (HIGH) | `picnic_table_workflow` (HIGH) |

**File:** `server/router/application/matcher/semantic_matcher.py` (lines 156-181)

### Bug 5: Floating Point Precision Error (confidence > 1.0)

**Problem:** Prompt `"erstelle einen Picknicktisch"` (German) threw validation error because confidence score was `1.0000000000000002`.

**Root Cause:** IEEE 754 floating point precision causes scores like `1.0000000000000002` which fail strict `<= 1.0` validation in `MatcherResult.__post_init__()`.

**Fix:** Added clamping for floating point precision issues before validation:

```python
def __post_init__(self):
    """Validate field values and clamp for floating point precision."""
    # Clamp confidence to handle floating point precision issues
    if self.confidence > 1.0 and self.confidence < 1.0 + 1e-9:
        object.__setattr__(self, 'confidence', 1.0)
    elif self.confidence < 0.0 and self.confidence > -1e-9:
        object.__setattr__(self, 'confidence', 0.0)

    if not 0.0 <= self.confidence <= 1.0:
        raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
```

**Result:**

| Prompt | Before Fix | After Fix |
|--------|------------|-----------|
| "erstelle einen Picknicktisch" | Error: `confidence > 1.0` | `picnic_table_workflow` (HIGH, 100%) |

**File:** `server/router/domain/entities/ensemble.py` (lines 37-48)

### Bug 6: Cross-Language Parameter Detection Not Working

**Problem:** German prompt `"Tisch mit Beinen im 45 Grad Winkel"` should trigger interactive parameter input (X-legs) but used defaults instead.

**Root Cause:** `ParameterResolver.calculate_relevance()` used two mechanisms:
1. **LaBSE similarity** (threshold 0.5) - but cross-language scores were ~0.4
2. **Literal matching** - only worked if exact hint word appeared in prompt

Polish worked accidentally because "kąt" was in hints AND in prompt. German "Winkel" wasn't in hints.

```
German: "Tisch mit Beinen im 45 Grad Winkel"
  LaBSE("Winkel", "angle") = 0.426 < 0.5 threshold → NOT relevant
  Literal match: "angle" not in prompt → no boost
  → Uses defaults, no interactive input ❌

Polish: "stół z nogami pod kątem 45 stopni"
  LaBSE("kąt", "angle") = 0.414 < 0.5 threshold → NOT relevant
  Literal match: "kąt" IS in prompt AND in hints → boost to 0.8 ✅
```

**Fix:** Two changes to `ParameterResolver`:

1. **Lowered `relevance_threshold`** from 0.5 to 0.4
2. **Added semantic word matching** - checks if ANY word in prompt is semantically similar to ANY hint:

```python
# Semantic word matching (cross-language support)
prompt_words = [w for w in prompt_lower.split() if len(w) > 2]
for hint in schema.semantic_hints:
    for word in prompt_words:
        word_sim = self._classifier.similarity(word, hint)
        if word_sim > 0.65:  # Higher threshold for single words
            max_relevance = max(max_relevance, 0.75)
            break
```

**Result:**

| Language | Prompt | Before | After | Method |
|----------|--------|--------|-------|--------|
| German | "Tisch mit Beinen im 45 Grad Winkel" | 0.42 ❌ | **0.75 ✅** | "beinen" ↔ "nogi" = 0.679 |
| French | "table avec pieds à 45 degrés" | 0.38 ❌ | **0.75 ✅** | "pieds" ↔ "legs" = 0.939 |
| Polish | "stół z nogami pod kątem 45 stopni" | 0.80 ✅ | 0.80 ✅ | literal match |
| English | "table with legs at 45 degree angle" | 0.80 ✅ | 0.80 ✅ | literal match |

**Key insight:** No need to add hints for every language! LaBSE automatically matches:
- German "Beinen" → Polish "nogi" (0.679)
- French "pieds" → English "legs" (0.939)

**File:** `server/router/application/resolver/parameter_resolver.py` (lines 49, 174-239)

## German Language Test Results

After all fixes, German prompts work correctly:

| Prompt (German) | Translation | Workflow | Normalized | Confidence | Modifiers |
|-----------------|-------------|----------|------------|------------|-----------|
| `Picknicktisch` | picnic table | ✅ picnic_table_workflow | 72.91% | **HIGH** | default |
| `erstelle einen Picknicktisch` | create a picnic table | ✅ picnic_table_workflow | 100.00% | **HIGH** | default |
| `Tisch mit geraden Beinen` | table with straight legs | ✅ picnic_table_workflow | 67.31% | **MEDIUM** | **straight** ✅ |
| `Tisch mit schrägen Beinen` | table with angled legs | ✅ picnic_table_workflow | 65.27% | **MEDIUM** | **angled** ✅ |
| `Tisch mit Beinen im 45 Grad Winkel` | table with legs at 45° | ✅ picnic_table_workflow | 49.61% | **LOW** | default |
| `einfacher Tisch` | simple table | ✅ picnic_table_workflow | 67.82% | **LOW** (forced) | default |

**Key observations:**
- LaBSE cross-language matching works: `"geraden Beinen"` (DE) → `"straight legs"` (EN)
- `"einfacher"` (German for "simple") correctly triggers LOW confidence via SIMPLE_KEYWORDS

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
| `server/router/application/matcher/semantic_matcher.py` | Return raw scores, use fallback_candidates |
| `server/router/domain/entities/ensemble.py` | Clamp floating point precision in MatcherResult |

## Related Tasks

- **TASK-053:** Ensemble Matching System (original implementation)
- **TASK-055:** Interactive Parameter Resolution (where bugs were discovered)
- **TASK-048:** Shared LaBSE via DI (singleton pattern used in fix)
