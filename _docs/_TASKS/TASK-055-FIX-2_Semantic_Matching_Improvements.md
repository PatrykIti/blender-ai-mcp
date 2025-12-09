# TASK-055-FIX-2: Semantic Matching Improvements for ModifierExtractor

**Status**: 🔧 In Progress
**Priority**: P0 (Critical)
**Parent**: TASK-055 Interactive Parameter Resolution
**Created**: 2025-12-09
**Related**: TASK-055-FIX (Defaults removal - ✅ DONE)

---

## Problem Statement

After FIX-1 (removing defaults from ModifierExtractor), "stół z nogami X" still incorrectly matches "straight legs" YAML modifier instead of triggering `needs_input`.

### Root Cause

**N-gram matching is too lenient**: Only requires 1 word to match instead of requiring multi-word alignment.

**Example failure**:
```
Prompt: "stół z nogami X"
YAML modifier: "straight legs"

Current behavior:
- N-gram "nogami" → "straight legs" = 0.739 similarity (> 0.70 threshold)
- MATCH ✅ (WRONG!)
- Result: leg_angle=0 (yaml_modifier)

Expected behavior:
- "nogami" matches "legs" ✅
- "X" does NOT match "straight" ❌
- Only 1/2 words match → REJECT
- Result: status="needs_input"
```

---

## Solution Design

### 1. Multi-word Matching Requirement

**Rule**: If modifier has N words, require **min(N, 2)** words from prompt to match.

**Implementation**:
- Split modifier into words: `"straight legs"` → `["straight", "legs"]`
- For each word, find best n-gram match with similarity >= 0.65
- Count matched words
- Require min(2, N) words to match before accepting

**Examples**:
- ✅ "prosty stół z prostymi nogami" + "straight legs":
  - "prosty" ↔ "straight" = 0.85 ✅
  - "nogami" ↔ "legs" = 0.92 ✅
  - 2/2 words match → **PASS**

- ❌ "stół z nogami X" + "straight legs":
  - "nogami" ↔ "legs" = 0.92 ✅
  - No match for "straight" (best: "X" = 0.35 < 0.65)
  - 1/2 words match → **FAIL**

### 2. Negative Signals Detection

**Rule**: Reject match if prompt contains words that contradict the modifier.

**Implementation**:
- YAML defines `negative_signals` list per modifier
- Python checks if any negative signal appears in prompt
- If found, reject match even if similarity is high

**YAML Structure**:
```yaml
modifiers:
  "straight legs":
    leg_angle_left: 0
    leg_angle_right: 0
    negative_signals: ["X", "crossed", "angled", "diagonal", "skośne", "skrzyżowane"]
```

**Examples**:
- ❌ "stół z nogami X" + "straight legs":
  - "X" is in `negative_signals` → **REJECTED**

- ✅ "prosty stół" + "straight legs":
  - No negative signals present → **ACCEPTED**

---

## Architecture Decisions

### Why YAML for negative_signals?

**Rationale**:
1. **Domain-specific knowledge**: Each workflow has unique contradictions
   - "straight" vs "X" is furniture-specific
   - "phone" vs "tablet" is device-specific
2. **Easy modification**: No code changes required
3. **Workflow isolation**: Each workflow defines its own negative signals
4. **Python stays generic**: ModifierExtractor only checks if signal exists in prompt

### Why Python for multi-word logic?

**Rationale**:
1. **Universal algorithm**: Works for all workflows
2. **No configuration needed**: Logic is deterministic
3. **Maintainability**: Single implementation in ModifierExtractor

---

## Implementation Plan

### Files to Modify

1. **picnic_table.yaml** (lines 63-67)
   - Add `negative_signals` list to "straight legs" modifier

2. **modifier_extractor.py** (lines 64-172)
   - Add `_has_negative_signals()` helper method
   - Replace current matching loop with multi-word logic
   - Add comprehensive DEBUG logging

3. **workflow_definition.py** (type hints only, if needed)
   - Update `modifiers` type hint to support nested dicts

### Detailed Changes

#### 1. YAML Update (picnic_table.yaml)

```yaml
modifiers:
  "straight legs":
    leg_angle_left: 0
    leg_angle_right: 0
    negative_signals: ["X", "crossed", "angled", "diagonal", "skośne", "skrzyżowane"]
```

#### 2. ModifierExtractor Update (modifier_extractor.py)

**Add helper method**:
```python
def _has_negative_signals(self, prompt: str, negative_signals: list) -> bool:
    """Check if prompt contains negative signals.

    Args:
        prompt: User prompt (e.g., "stół z nogami X")
        negative_signals: List of contradictory terms from YAML

    Returns:
        True if any negative signal found in prompt.
    """
    if not negative_signals:
        return False

    prompt_lower = prompt.lower()
    prompt_words = set(prompt_lower.split())

    for neg_word in negative_signals:
        neg_lower = neg_word.lower()
        # Check both substring and word boundary match
        if neg_lower in prompt_words or neg_lower in prompt_lower:
            logger.debug(f"Negative signal detected: '{neg_word}' in prompt")
            return True

    return False
```

**Replace matching loop** (around lines 135-172):
```python
if self._classifier is not None:
    ngrams = self._extract_ngrams(prompt)

    for keyword, values in definition.modifiers.items():
        keyword_words = keyword.lower().split()  # ["straight", "legs"]

        # Multi-word matching: count how many keyword words match
        matched_words = []  # [(kw_word, best_ngram, similarity), ...]

        for kw_word in keyword_words:
            best_sim = 0.0
            best_ngram = ""

            for ngram in ngrams:
                sim = self._classifier.similarity(kw_word, ngram)
                if sim > best_sim:
                    best_sim = sim
                    best_ngram = ngram

            if best_sim >= 0.65:  # Per-word threshold
                matched_words.append((kw_word, best_ngram, best_sim))
                logger.debug(
                    f"Word match: '{kw_word}' ↔ '{best_ngram}' (sim={best_sim:.3f})"
                )

        # Require min(N, 2) words to match
        required_matches = min(len(keyword_words), 2)

        if len(matched_words) >= required_matches:
            # Calculate average similarity
            avg_sim = sum(m[2] for m in matched_words) / len(matched_words)

            # Check negative signals from YAML
            negative_signals = values.get("negative_signals", [])
            if self._has_negative_signals(prompt, negative_signals):
                logger.debug(
                    f"Rejected '{keyword}': negative signals detected in prompt"
                )
                continue  # Skip this match

            # Extract actual parameter values (filter out negative_signals key)
            param_values = {k: v for k, v in values.items() if k != "negative_signals"}

            logger.info(
                f"Modifier match: '{keyword}' ({len(matched_words)}/{len(keyword_words)} words) "
                f"→ {param_values} (avg_sim={avg_sim:.3f})"
            )

            semantic_matches.append((keyword, param_values, avg_sim, matched_words))
        else:
            logger.debug(
                f"Insufficient word matches for '{keyword}': "
                f"{len(matched_words)}/{len(keyword_words)} (need {required_matches})"
            )
```

---

## Testing Plan

### Test Case 1: "stół z nogami X" (Should NOT match)

**Expected behavior**:
```
DEBUG: Word match: 'nogami' ↔ 'legs' (sim=0.919)
DEBUG: Insufficient word matches for 'straight legs': 1/2 (need 2)
Result: status="needs_input"
```

### Test Case 2: "prosty stół z prostymi nogami" (Should match)

**Expected behavior**:
```
DEBUG: Word match: 'prosty' ↔ 'straight' (sim=0.850)
DEBUG: Word match: 'nogami' ↔ 'legs' (sim=0.919)
INFO: Modifier match: 'straight legs' (2/2 words) → {leg_angle_left: 0, leg_angle_right: 0} (avg_sim=0.885)
Result: status="ready", leg_angle_left=0, leg_angle_right=0 (yaml_modifier)
```

### Test Case 3: Edge case with negative signal

**Prompt**: "stół z krzyżowanymi nogami" (table with crossed legs)

**Expected behavior**:
```
DEBUG: Word match: 'nogami' ↔ 'legs' (sim=0.919)
DEBUG: Insufficient word matches for 'straight legs': 1/2 (need 2)
Result: status="needs_input"
```

OR if we add "crossed legs" modifier:
```
DEBUG: Negative signal detected: 'straight' in negative_signals for 'crossed legs'
Result: Match rejected
```

---

## Documentation Updates

### Critical Files to Update

1. **TASK-055_Interactive_Parameter_Resolution.md**
   - Add FIX-2 section with multi-word matching details
   - Update status to reflect semantic matching improvements

2. **_docs/_ROUTER/IMPLEMENTATION/04-modifier-extractor.md** (if exists)
   - Document multi-word matching algorithm
   - Document negative signals feature
   - Add examples and decision tree

3. **_docs/_ROUTER/README.md**
   - Update component status for ModifierExtractor
   - Add reference to FIX-2

4. **_docs/_CHANGELOG/NN-2025-12-09-router-semantic-matching-fix.md**
   - Create new changelog entry for FIX-2
   - Document problem, solution, and impact

5. **_docs/_CHANGELOG/README.md**
   - Add FIX-2 changelog to index

6. **README.md** (optional)
   - Update Router Supervisor roadmap if relevant

### Documentation Template for Changelog

```markdown
# Router Semantic Matching Improvements (FIX-2)

**Date**: 2025-12-09
**Component**: ModifierExtractor
**Impact**: Critical bug fix for TASK-055

## Problem

"stół z nogami X" incorrectly matched "straight legs" YAML modifier because n-gram matching only required 1 word to match instead of requiring multi-word alignment.

## Solution

1. **Multi-word Matching**: Require min(N, 2) words to match for N-word modifiers
2. **Negative Signals**: YAML-defined contradictory terms that reject matches

## Changes

- `modifier_extractor.py`: Rewritten matching logic with multi-word requirement
- `picnic_table.yaml`: Added negative_signals to modifiers
- Per-word threshold: 0.65 (allows multilingual fuzzy matching)

## Impact

- ✅ "stół z nogami X" now correctly returns `needs_input`
- ✅ "prosty stół z prostymi nogami" still matches "straight legs"
- 🎯 Improved semantic precision for TASK-055 Interactive Parameter Resolution
```

---

## Success Criteria

- [ ] "stół z nogami X" returns `status: "needs_input"` ✅
- [ ] "prosty stół z prostymi nogami" returns `yaml_modifier` with leg_angle=0 ✅
- [ ] DEBUG logs show word-level matching details ✅
- [ ] Negative signals correctly reject matches ✅
- [ ] Docker rebuild successful ✅
- [ ] All 3 test prompts work as expected ✅
- [ ] Documentation updated ✅

---

## Related Tasks

- **TASK-055**: Main Interactive Parameter Resolution task
- **TASK-055-FIX**: Defaults removal from ModifierExtractor (✅ DONE)
- **TASK-053**: Ensemble Matcher consolidation (parent system)

---

## Notes

- **Per-word threshold (0.65)**: Chosen based on analysis of LaBSE similarity scores
  - "nogami" → "legs" = 0.85+ (clear match)
  - "straight" → "prosty" = 0.75+ (clear match)
  - "X" → "straight" = 0.35 (clear non-match)
  - 0.65 provides safety margin

- **Negative signals in YAML**: Allows workflow designers to define domain-specific contradictions without code changes

- **Multi-word requirement**: Ensures semantic coherence - all words in modifier must be represented in prompt
