# Changelog Entry 99: Router Semantic Matching Improvements (TASK-055-FIX-2)

**Date**: 2025-12-09
**Component**: Router / ModifierExtractor
**Type**: Critical Bug Fix
**Related**: TASK-055 Interactive Parameter Resolution

---

## Problem

"stół z nogami X" (table with X-shaped legs) incorrectly matched "straight legs" YAML modifier, returning `yaml_modifier` with `leg_angle=0` instead of triggering `needs_input` for LLM interaction.

### Root Cause

N-gram matching in `ModifierExtractor` was too lenient - it only required **1 word** to match for multi-word modifiers:

```
Prompt: "stół z nogami X"
YAML modifier: "straight legs"

Current behavior:
- N-gram "nogami" → "straight legs" = 0.739 similarity (> 0.70 threshold)
- MATCH ✅ (WRONG!)
- Only "legs" matched, "straight" ignored
- Result: leg_angle=0 (yaml_modifier)

Expected behavior:
- "nogami" matches "legs" ✅
- "X" does NOT match "straight" ❌
- Only 1/2 words match → REJECT
- Result: status="needs_input"
```

---

## Solution

Implemented two complementary improvements in `ModifierExtractor`:

### 1. Multi-word Matching Requirement

**Rule**: If modifier has N words, require **min(N, 2)** words from prompt to match.

**Algorithm**:
```python
keyword_words = "straight legs".split()  # 2 words

# For each keyword word, find best n-gram match
for kw_word in keyword_words:
    best_ngram = find_best_ngram(kw_word, prompt_ngrams)
    if similarity(kw_word, best_ngram) >= 0.65:
        matched_words.append((kw_word, best_ngram, sim))

# Require min(2, len(keyword_words)) matches
if len(matched_words) >= 2:
    accept_match()
else:
    reject_match()
```

**Per-word threshold**: `0.65` (allows multilingual fuzzy matching while maintaining precision)

**Examples**:
- ✅ **"prosty stół z prostymi nogami"** + `"straight legs"`:
  - "prosty" ↔ "straight" = 0.85 ✅
  - "nogami" ↔ "legs" = 0.92 ✅
  - 2/2 words match → **ACCEPTED**

- ❌ **"stół z nogami X"** + `"straight legs"`:
  - "nogami" ↔ "legs" = 0.92 ✅
  - No match for "straight" (best: "X" = 0.35 < 0.65)
  - 1/2 words match → **REJECTED** (needs 2)

### 2. Negative Signals Detection

**Rule**: Reject match if prompt contains words that contradict the modifier.

**YAML Structure**:
```yaml
modifiers:
  "straight legs":
    leg_angle_left: 0
    leg_angle_right: 0
    negative_signals: ["X", "crossed", "angled", "diagonal", "skośne", "skrzyżowane"]
```

**Implementation**:
```python
def _has_negative_signals(self, prompt: str, negative_signals: list) -> bool:
    """Check if prompt contains contradictory terms."""
    prompt_lower = prompt.lower()
    prompt_words = set(prompt_lower.split())

    for neg_word in negative_signals:
        if neg_word.lower() in prompt_words or neg_word.lower() in prompt_lower:
            return True  # Contradiction found

    return False
```

**Examples**:
- ❌ **"stół z nogami X"** + `"straight legs"`:
  - "X" is in `negative_signals` → **REJECTED**

- ✅ **"prosty stół"** + `"straight legs"`:
  - No negative signals present → **ACCEPTED**

---

## Changes Made

### 1. `picnic_table.yaml` (lines 63-68)

Added `negative_signals` to modifiers:

```yaml
modifiers:
  "straight legs":
    leg_angle_left: 0
    leg_angle_right: 0
    negative_signals: ["X", "crossed", "angled", "diagonal", "skośne", "skrzyżowane"]
```

### 2. `modifier_extractor.py` (lines 86-243)

**Added helper method** (lines 86-118):
```python
def _has_negative_signals(self, prompt: str, negative_signals: list) -> bool:
    """Check if prompt contains negative signals.

    TASK-055-FIX-2: Negative signals detection for semantic matching.
    Rejects modifier match if prompt contains contradictory terms.
    """
    # ... implementation ...
```

**Replaced matching loop** (lines 163-243):
- Multi-word matching with per-word threshold (0.65)
- Negative signals check before accepting match
- Comprehensive DEBUG logging for decisions
- Filter `negative_signals` key when extracting parameter values

---

## Impact

### Correctness Improvements

- ✅ **"stół z nogami X"** now correctly returns `status: "needs_input"` (was: `yaml_modifier`)
- ✅ **"prosty stół z prostymi nogami"** still matches `"straight legs"` (leg_angle=0)
- ✅ **"stół piknikowy"** uses defaults (leg_angle=±0.32) - no match to "straight legs"

### Semantic Precision

- Multi-word requirement ensures semantic coherence
- Negative signals prevent contradictory matches
- Per-word threshold (0.65) balances precision/recall for multilingual matching

### Logging Improvements

New DEBUG logs:
```
DEBUG: Word match: 'nogami' ↔ 'legs' (sim=0.919)
DEBUG: Insufficient word matches for 'straight legs': 1/2 (need 2)
```

```
INFO: Modifier match: 'straight legs' (2/2 words) → {leg_angle_left: 0, leg_angle_right: 0} (avg_sim=0.885)
```

---

## Architecture Decisions

### Why YAML for negative_signals?

1. **Domain-specific knowledge**: Each workflow defines its own contradictions
   - "straight" vs "X" is furniture-specific
   - "phone" vs "tablet" is device-specific
2. **Easy modification**: No code changes required
3. **Workflow isolation**: Each workflow manages its own semantics

### Why Python for multi-word logic?

1. **Universal algorithm**: Works for all workflows
2. **No configuration needed**: Logic is deterministic
3. **Single implementation**: Centralized in ModifierExtractor

---

## Testing

### Manual Tests (via Docker)

**Test 1**: "stół z nogami X" ✅
```json
{
  "status": "needs_input",
  "unresolved": ["leg_angle_left", "leg_angle_right"]
}
```

**Test 2**: "prosty stół z prostymi nogami" ✅
```json
{
  "status": "ready",
  "resolved": {"leg_angle_left": 0, "leg_angle_right": 0},
  "resolution_sources": {"leg_angle_left": "yaml_modifier", "leg_angle_right": "yaml_modifier"}
}
```

**Test 3**: "stół piknikowy" ✅
```json
{
  "status": "ready",
  "resolved": {"leg_angle_left": 0.32, "leg_angle_right": -0.32},
  "resolution_sources": {"leg_angle_left": "default", "leg_angle_right": "default"}
}
```

---

## Related Tasks

- **TASK-055**: Interactive Parameter Resolution via LLM Feedback (parent)
- **TASK-055-FIX**: Defaults Removal from ModifierExtractor (✅ DONE)
- **TASK-053**: Ensemble Matcher Consolidation (architecture foundation)

---

## Files Modified

1. `server/router/application/workflows/custom/picnic_table.yaml` (line 68)
2. `server/router/application/matcher/modifier_extractor.py` (lines 86-243)
3. `_docs/_TASKS/TASK-055_Interactive_Parameter_Resolution.md` (FIX-2 section added)
4. `_docs/_TASKS/TASK-055-FIX-2_Semantic_Matching_Improvements.md` (new task doc)

---

## Migration Notes

None - fully backward compatible. Existing workflows without `negative_signals` continue to work as before.

Workflows can add `negative_signals` to modifiers as needed:

```yaml
modifiers:
  "your modifier":
    param1: value1
    negative_signals: ["contradictory", "terms", "here"]  # Optional
```

---

## Known Limitations

1. **Single-word modifiers**: Multi-word requirement doesn't apply (require only 1 word match for 1-word modifiers)
2. **Negative signals are exact matches**: Case-insensitive substring/word match, no fuzzy matching
3. **Per-workflow configuration**: Each workflow must define its own negative signals

These limitations are acceptable for current use cases and can be addressed in future iterations if needed.

---

**Status**: ✅ Complete
**PR**: (to be added)
**Deployed**: (pending Docker rebuild + testing)
