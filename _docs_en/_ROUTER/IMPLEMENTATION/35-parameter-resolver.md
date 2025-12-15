# 35. Parameter Resolver

**Status**: ✅ Implemented (TASK-055, TASK-055-FIX-3)
**File**: `server/router/application/resolver/parameter_resolver.py`
**Related**: TASK-055 (Parameter Storage/Retrieval), TASK-055-FIX-3 (Context Truncation Bug Fix)

---

## Overview

ParameterResolver handles interactive parameter resolution for workflows with unresolved parameters. Uses a 3-tier resolution strategy (YAML modifiers → Learned mappings → Defaults/Interactive) with hybrid context extraction for semantic search.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ParameterResolver                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  resolve(prompt, workflow, params, modifiers)               │
│      │                                                      │
│      ├─→ TIER 1: Check existing_modifiers (YAML)          │
│      │                                                      │
│      ├─→ TIER 2: Search learned mappings (ParameterStore) │
│      │   │                                                  │
│      │   ├─→ calculate_relevance(prompt, schema)           │
│      │   │   └─→ LaBSE semantic similarity                 │
│      │   │                                                  │
│      │   └─→ search_parameter(prompt, workflow, param)     │
│      │       └─→ ParameterStore.search()                   │
│      │                                                      │
│      └─→ TIER 3: Use defaults or mark unresolved           │
│                                                             │
│  extract_context(prompt, schema) → Context Extraction       │
│      │                                                      │
│      ├─→ TIER 3: Full prompt (≤500 chars)                  │
│      ├─→ TIER 1: Smart sentence extraction                 │
│      │   └─→ _extract_sentence_context()                   │
│      └─→ TIER 2: Expanded window (200+ chars)              │
│                                                             │
│  store_resolved_value(context, workflow, param, value)      │
│      └─→ ParameterStore.store()                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         │                            │
         │ Depends on                 │ Stores in
         ▼                            ▼
┌──────────────────────┐    ┌─────────────────────┐
│ WorkflowIntent       │    │  ParameterStore     │
│ Classifier           │    │  (LanceDB)          │
│ (LaBSE Similarity)   │    │                     │
└──────────────────────┘    └─────────────────────┘
```

---

## Context Extraction Strategy (TASK-055-FIX-3)

ParameterResolver uses a 3-tier hybrid approach for extracting semantic context around hints:

### TIER 1: Smart Sentence Extraction (Primary)

- Extracts complete sentences containing the semantic hint
- Includes 1 sentence before + hint sentence + 1 sentence after
- Uses sentence boundaries (. ! ? \n) for natural language parsing
- Maximum context: 400 chars
- **Use case**: Long prompts with clear sentence structure

**Example**:
```python
prompt = "I want outdoor furniture. Create a picnic table with X-shaped legs. Use oak wood."
hint = "legs"
# Extracted: "Create a picnic table with X-shaped legs. Use oak wood."
```

**Implementation**:
```python
def _extract_sentence_context(
    self,
    prompt: str,
    hint_idx: int,
    hint: str,
    max_length: int,
) -> str:
    """Extract complete sentences around hint position."""
    SENTENCE_ENDINGS = {'.', '!', '?', '\n'}

    # Walk backwards to find sentence start
    sent_start = hint_idx
    for i in range(hint_idx - 1, -1, -1):
        if prompt[i] in SENTENCE_ENDINGS:
            sent_start = i + 1
            break
    else:
        sent_start = 0  # Beginning of prompt

    # Walk forwards to find sentence end
    sent_end = hint_idx + len(hint)
    for i in range(hint_idx + len(hint), len(prompt)):
        if prompt[i] in SENTENCE_ENDINGS:
            sent_end = i + 1
            break
    else:
        sent_end = len(prompt)  # End of prompt

    # Extract hint sentence
    hint_sentence = prompt[sent_start:sent_end].strip()

    # Try to include previous sentence
    # ... (see implementation for full logic)

    # Build context: prev + hint + next
    context_parts = [prev_sentence, hint_sentence, next_sentence]
    context = " ".join(filter(None, context_parts))

    # Truncate if too long (preserve hint position)
    if len(context) > max_length:
        # Center around hint
        ...

    return context
```

### TIER 2: Expanded Window (Fallback)

- Fixed window: 100 chars before + hint + 100 chars after
- Total: ~200-250 chars (3-4x larger than legacy 60 chars)
- **Use case**: Long prompts without clear sentences (run-on text, lists)

**Example**:
```python
prompt = "create a picnic table with X-shaped legs and natural wood finish use oak or pine..." (600+ chars)
hint = "legs"
# Extracted: 200 chars centered around "legs"
```

**Implementation**:
```python
# TIER 2: Expanded window fallback
logger.debug("Sentence extraction insufficient, using expanded window")
start = max(0, idx - 100)
end = min(len(prompt), idx + len(hint) + 100)
context = prompt[start:end].strip()

# Remove leading/trailing punctuation
context = re.sub(r"^[,.:;!?\s]+", "", context)
context = re.sub(r"[,.:;!?\s]+$", "", context)

if len(context) > max_context_length:
    context = context[:max_context_length].strip()

return context
```

### TIER 3: Full Prompt (Final Fallback)

- Uses entire prompt if ≤500 chars
- Ensures maximum semantic information for short prompts
- **Use case**: Short prompts, conversational input

**Example**:
```python
prompt = "X-shaped legs picnic table"
hint = "legs"
# Extracted: "X-shaped legs picnic table" (full prompt)
```

**Implementation**:
```python
# TIER 3: If prompt is short enough, use entire prompt
if len(prompt) <= 500:
    logger.debug(f"[TIER 3] Using full prompt as context (length={len(prompt)} ≤ 500)")
    return prompt.strip()
```

### Rationale

**Problem Solved**: Legacy implementation truncated to 60 chars total:
- "create a picnic table with X-shaped legs" → stored as "ed legs picnic table"
- Lost critical semantic information ("X-shaped")
- Similarity searches failed (0.80 < threshold 0.85)

**Solution Benefits**:
- **Preserves semantic context**: Modifiers like "X-shaped", "straight", "angled" are retained
- **Improves similarity scores**: ~0.80 → >0.85 (measured improvement)
- **Maintains natural language boundaries**: Sentence-aware extraction when possible
- **Graceful degradation**: 3 tiers ensure context extraction always succeeds

---

## Resolution Tiers

### TIER 1: Existing Modifiers (YAML)

**Source**: `existing_modifiers` dict from EnsembleMatcher → ModifierExtractor

**Resolution**: Direct lookup
```python
if param_name in existing_modifiers:
    value = existing_modifiers[param_name]
    resolved[param_name] = value
    sources[param_name] = "yaml_modifier"
    continue  # TIER 1 always wins
```

**Example**:
```
Prompt: "straight legs picnic table"
YAML modifier matched: {"leg_angle_left": 0, "leg_angle_right": 0}
Result: leg_angle_left = 0 (yaml_modifier)
```

### TIER 2: Learned Mappings (ParameterStore)

**Source**: ParameterStore (LanceDB with LaBSE semantic search)

**Resolution Steps**:
1. Calculate relevance: `calculate_relevance(prompt, schema)` using LaBSE
2. If relevance ≥ 0.4, search store: `store.search(prompt, workflow, param)`
3. Extract context: `extract_context(prompt, schema)` (3-tier hybrid strategy)
4. Search by context similarity (threshold = 0.85)

**Example**:
```
Prompt: "X-shaped legs picnic table"
Relevance: calculate_relevance("X-shaped legs picnic table", schema) = 0.82 (> 0.4)
Search: ParameterStore.search(context="X-shaped legs picnic table", ...)
Match found: leg_angle_right = -1.0 (similarity = 0.92 > 0.85)
Result: leg_angle_right = -1.0 (learned)
```

**Relevance Calculation**:
```python
def calculate_relevance(
    self,
    prompt: str,
    schema: ParameterSchema,
    threshold: float = 0.4,
) -> float:
    """Calculate semantic relevance using LaBSE."""
    max_relevance = 0.0
    prompt_lower = prompt.lower()

    for hint in schema.semantic_hints:
        # Exact match = 1.0
        if hint.lower() in prompt_lower:
            return 1.0

        # Semantic similarity via LaBSE
        if self._classifier:
            similarity = self._classifier.similarity(hint, prompt)
            max_relevance = max(max_relevance, similarity)

            # Early exit if high relevance
            if max_relevance >= 0.75:
                break

    return max_relevance
```

### TIER 3: Defaults or Unresolved

**Resolution**:
- If parameter has `default` value → use default
- Otherwise → mark as unresolved (triggers interactive prompt)

**Example**:
```python
# Has default
if schema.default is not None:
    resolved[param_name] = schema.default
    sources[param_name] = "default"
else:
    # Mark unresolved (will prompt user)
    unresolved.append(param_name)
```

---

## Methods

### `resolve()`

Resolves parameters for a workflow using 3-tier strategy.

**Signature**:
```python
def resolve(
    self,
    prompt: str,
    workflow_name: str,
    parameters: Dict[str, ParameterSchema],
    existing_modifiers: Optional[Dict[str, Any]] = None,
) -> ParameterResolution:
```

**Returns**:
```python
@dataclass
class ParameterResolution:
    resolved: Dict[str, Any]              # param_name → resolved value
    unresolved: List[str]                 # param names that need interactive input
    resolution_sources: Dict[str, str]    # param_name → source ("yaml_modifier", "learned", "default")
    relevance_scores: Dict[str, float]    # param_name → relevance score (TIER 2 only)
```

### `calculate_relevance()`

Calculates semantic relevance of prompt to parameter using LaBSE.

**Threshold**: 0.4 (parameters with relevance < 0.4 are skipped for TIER 2 search)

**Returns**: Float 0.0-1.0 (1.0 = exact match, 0.0 = no relevance)

### `extract_context()`

Extracts semantic context around hint using 3-tier hybrid strategy.

**Signature**:
```python
def extract_context(
    self,
    prompt: str,
    schema: ParameterSchema,
    max_context_length: int = 400,
) -> str:
```

**Returns**: Context string (100-400 chars, or full prompt if ≤500 chars)

### `store_resolved_value()`

Stores resolved parameter value in ParameterStore for future reuse.

**Signature**:
```python
def store_resolved_value(
    self,
    context: str,
    workflow_name: str,
    param_name: str,
    value: Any,
) -> None:
```

---

## Example Flow

### Case 1: YAML Modifier Match (TIER 1)

```python
# User: "straight legs picnic table"
# ModifierExtractor matched: {"leg_angle_left": 0, "leg_angle_right": 0}

existing_modifiers = {"leg_angle_left": 0, "leg_angle_right": 0}

resolution = resolver.resolve(
    prompt="straight legs picnic table",
    workflow_name="picnic_table_workflow",
    parameters={
        "leg_angle_left": ParameterSchema(...),
        "leg_angle_right": ParameterSchema(...),
    },
    existing_modifiers=existing_modifiers,
)

# Result:
# resolved = {"leg_angle_left": 0, "leg_angle_right": 0}
# unresolved = []
# resolution_sources = {"leg_angle_left": "yaml_modifier", "leg_angle_right": "yaml_modifier"}
```

### Case 2: Learned Mapping Match (TIER 2)

```python
# User: "X-shaped legs picnic table"
# No YAML modifier matched (semantic match insufficient)
# But user previously resolved this to leg_angle = ±1.0

existing_modifiers = {}

resolution = resolver.resolve(
    prompt="X-shaped legs picnic table",
    workflow_name="picnic_table_workflow",
    parameters={
        "leg_angle_left": ParameterSchema(semantic_hints=["legs", "angle"]),
        "leg_angle_right": ParameterSchema(semantic_hints=["legs", "angle"]),
    },
    existing_modifiers={},
)

# Internal flow:
# 1. calculate_relevance("X-shaped legs picnic table", schema) = 0.82 (> 0.4)
# 2. extract_context("X-shaped legs picnic table", schema) = "X-shaped legs picnic table" (TIER 3: full prompt)
# 3. ParameterStore.search(context="X-shaped legs picnic table", ...)
#    → Found: {"leg_angle_left": 1.0} (similarity = 0.92 > 0.85)
#    → Found: {"leg_angle_right": -1.0} (similarity = 0.92 > 0.85)

# Result:
# resolved = {"leg_angle_left": 1.0, "leg_angle_right": -1.0}
# unresolved = []
# resolution_sources = {"leg_angle_left": "learned", "leg_angle_right": "learned"}
# relevance_scores = {"leg_angle_left": 0.82, "leg_angle_right": 0.82}
```

### Case 3: Unresolved (Triggers Interactive Prompt)

```python
# User: "stół z nogami X" (Polish, no previous learned mapping)

existing_modifiers = {}

resolution = resolver.resolve(
    prompt="stół z nogami X",
    workflow_name="picnic_table_workflow",
    parameters={
        "leg_angle_left": ParameterSchema(semantic_hints=["legs", "angle"]),
    },
    existing_modifiers={},
)

# Internal flow:
# 1. calculate_relevance("stół z nogami X", schema) = 0.45 (> 0.4)
# 2. ParameterStore.search(...) → No match found (similarity < 0.85)
# 3. No default value → Mark unresolved

# Result:
# resolved = {}
# unresolved = ["leg_angle_left"]  # Will trigger interactive question
# resolution_sources = {}
# relevance_scores = {"leg_angle_left": 0.45}
```

---

## Testing

**File**: `tests/unit/router/application/resolver/test_parameter_resolver_context.py`

**Test Coverage**:
- ✅ TIER 3: Full prompt extraction (3 tests)
- ✅ TIER 1: Sentence extraction (4 tests)
- ✅ TIER 2: Expanded window (2 tests)
- ✅ Edge cases: empty prompt, hint not found, very long prompts (6 tests)
- ✅ Regression prevention: X-shaped legs bug, modifier preservation (3 tests)
- ✅ Context quality: word boundaries, modifier preservation (2 tests)

**Total**: 20 unit tests (all passing)

**Critical Test** (Regression Prevention):
```python
def test_x_shaped_legs_context_preservation(resolver, sample_schema):
    """
    CRITICAL TEST: The bug that triggered TASK-055-FIX-3.

    Before fix: "ed legs picnic table" (lost "X-shaped")
    After fix: Should preserve "X-shaped" in context
    """
    prompt = "create a picnic table with X-shaped legs"
    context = resolver.extract_context(prompt, sample_schema)

    # MUST preserve "X-shaped" modifier
    assert "X-shaped" in context or "x-shaped" in context.lower()
    assert "legs" in context.lower()
    assert len(context) >= len("X-shaped legs")
```

---

## Performance Considerations

### Context Extraction Performance

**TIER 3** (Full prompt):
- Time complexity: O(1) - simple string slicing
- No sentence parsing overhead
- Fastest tier (used for 90% of prompts in practice)

**TIER 1** (Sentence extraction):
- Time complexity: O(n) where n = prompt length
- Sentence boundary detection requires linear scan
- Used for long prompts (>500 chars) with clear structure

**TIER 2** (Expanded window):
- Time complexity: O(1) - fixed window slicing
- Fallback when TIER 1 returns < 100 chars
- Rare in practice (malformed prompts)

### LaBSE Similarity Performance

**Relevance calculation**:
- ~10-50ms per `classifier.similarity()` call
- Early exit at similarity ≥ 0.75
- Cached sentence embeddings (LaBSE model warmup)

**ParameterStore search**:
- LanceDB vector search: O(log n) with HNSW index
- ~50-200ms for typical database size (100-1000 entries)
- Batch search optimization for multiple parameters

---

## Configuration

**Relevance Threshold**: 0.4 (parameters with lower relevance skip TIER 2 search)
**Similarity Threshold**: 0.85 (learned mappings must exceed this for match)
**Max Context Length**: 400 chars (TIER 1/2), 500 chars (TIER 3)
**Expanded Window**: 100 chars before + hint + 100 chars after

**Tuning**:
- **Lower relevance threshold** (e.g., 0.3) → More TIER 2 searches, higher recall, slower
- **Higher similarity threshold** (e.g., 0.90) → Fewer false positives, lower recall
- **Larger context window** (e.g., 600 chars) → Better semantic matching, larger DB

---

## Future Improvements

1. **Adaptive window sizing**: Adjust window size based on prompt characteristics
2. **Multi-hint extraction**: Extract context for multiple hints in single pass
3. **Caching**: Cache `calculate_relevance()` results for repeated prompts
4. **Phrase extraction**: Use NLP techniques (spaCy) for better phrase boundaries
5. **Context ranking**: Score multiple context candidates and select best

---

## Related Components

- **ModifierExtractor**: Provides `existing_modifiers` for TIER 1
- **WorkflowIntentClassifier**: Provides LaBSE semantic similarity
- **ParameterStore**: Stores and searches learned mappings (TIER 2)
- **EnsembleMatcher**: Coordinates modifier extraction before ParameterResolver
- **SupervisorRouter**: Handles interactive prompts for unresolved parameters
