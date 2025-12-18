# TASK-050: Multi-Embedding Workflow System

**Priority:** 🔴 High (blocking accurate semantic matching)
**Category:** Router / Vector Store / Semantic Search
**Estimated Effort:** Medium (4-6 hours)
**Dependencies:** TASK-047 (LanceDB Migration), TASK-048 (Shared LaBSE)
**Status:** ✅ Done

---

> **Note (2025-12-17):** The public MCP admin tool `vector_db_manage` referenced in some examples was removed and replaced by `workflow_catalog` (read-only workflow browsing/search/inspection). The multi-embedding strategy still applies via `WorkflowIntentClassifier` and `IVectorStore`.

## Overview

The current workflow embedding system combines all sample prompts, keywords, and descriptions into a single embedding per workflow. This "averaging" effect dilutes semantic similarity scores, resulting in poor matching (e.g., 0.68 for exact phrase match instead of ~1.0).

**Problem Demonstrated:**
```python
# Query: "create a picnic table"
# Combined embedding text: "create a picnic table make an outdoor table..."
# Result: 0.68 similarity (should be ~1.0)

# Individual comparison:
# "create a picnic table" vs "create a picnic table" = 1.0 ✅
# "create a picnic table" vs combined_text = 0.68 ❌
```

**Solution:** Store multiple embeddings per workflow (one per sample_prompt) and use max-score matching.

---

## Architecture

### Current Flow (❌ Problem)
```
Workflow YAML
    ↓
Extract all texts (prompts + keywords + description)
    ↓
Join into single string: " ".join(texts)
    ↓
Single embedding per workflow
    ↓
Query matches against diluted embedding → Low scores
```

### New Flow (✅ Solution)
```
Workflow YAML
    ↓
Extract texts with source types
    ↓
Create separate embedding for EACH text
    ↓
Store with metadata: {workflow_id, source_type, weight}
    ↓
Query matches against ALL embeddings
    ↓
Return best match (max score) with weighted scoring
```

---

## Sub-Tasks

### TASK-050-1: Update LanceDB Schema for Multi-Embeddings

**Status:** ✅ Done

Update vector store schema to support multiple embeddings per workflow with source metadata.

**Current Schema:**
```python
# server/router/infrastructure/vector_store/lance_store.py
{
    "id": str,           # "workflow_name" or "tool_name"
    "namespace": str,    # "workflows" or "tools"
    "text": str,         # Combined text (truncated)
    "vector": list[float]  # 768-dim LaBSE embedding
}
```

**New Schema:**
```python
{
    "id": str,              # Unique ID: "{workflow_name}_{index}"
    "workflow_id": str,     # Parent workflow name
    "namespace": str,       # "workflows" or "tools"
    "source_type": str,     # "sample_prompt" | "trigger_keyword" | "description" | "name"
    "source_weight": float, # 1.0 for prompt, 0.8 for keyword, 0.6 for description
    "language": str,        # Detected language code: "en", "pl", "de", "fr"
    "text": str,            # Original text (NOT combined)
    "vector": list[float]   # 768-dim LaBSE embedding
}
```

**Files to Modify:**

| File | Changes |
|------|---------|
| `server/router/infrastructure/vector_store/lance_store.py` | Update schema, add new fields |
| `server/router/infrastructure/vector_store/base.py` | Update `WorkflowEmbedding` dataclass |

**Implementation:**

```python
# server/router/infrastructure/vector_store/base.py

@dataclass
class WorkflowEmbedding:
    """Single embedding record for a workflow text."""
    id: str                    # Unique: "{workflow_id}_{index}"
    workflow_id: str           # Parent workflow
    namespace: str = "workflows"
    source_type: str = "sample_prompt"  # sample_prompt|trigger_keyword|description|name
    source_weight: float = 1.0
    language: str = "en"
    text: str = ""
    vector: Optional[List[float]] = None
```

```python
# server/router/infrastructure/vector_store/lance_store.py

WORKFLOW_SCHEMA = pa.schema([
    pa.field("id", pa.string()),
    pa.field("workflow_id", pa.string()),
    pa.field("namespace", pa.string()),
    pa.field("source_type", pa.string()),
    pa.field("source_weight", pa.float32()),
    pa.field("language", pa.string()),
    pa.field("text", pa.string()),
    pa.field("vector", pa.list_(pa.float32(), 768)),
])
```

**Checklist:**

- [ ] Update `WorkflowEmbedding` dataclass in `base.py`
- [ ] Update LanceDB schema in `lance_store.py`
- [ ] Add migration for existing data (or rebuild)
- [ ] Update `store_workflow_embedding()` method
- [ ] Update `search_workflows()` to return `workflow_id` grouping
- [ ] Unit tests for new schema

---

### TASK-050-2: Implement Language Detection

**Status:** ✅ Done

Add lightweight language detection for query and embedding texts to enable language-aware boosting.

**New File:** `server/router/infrastructure/language_detector.py`

```python
"""
Lightweight language detection for semantic matching.

Uses simple heuristics + optional langdetect for accuracy.
"""

from typing import Optional
import re

# Language-specific character patterns
LANGUAGE_PATTERNS = {
    "pl": r"[ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]",  # Polish diacritics
    "de": r"[äöüßÄÖÜ]",              # German umlauts
    "fr": r"[àâçéèêëîïôùûüÿœæ]",    # French accents
    "es": r"[áéíóúñü¿¡]",            # Spanish
    "ru": r"[а-яА-ЯёЁ]",             # Russian Cyrillic
}

# Common words per language
LANGUAGE_MARKERS = {
    "en": {"the", "a", "an", "is", "are", "create", "make", "build"},
    "pl": {"stworz", "zrob", "utworz", "jest", "sa", "stol", "krzeslo"},
    "de": {"erstelle", "mache", "baue", "ist", "sind", "der", "die", "das"},
    "fr": {"creer", "faire", "construire", "est", "sont", "le", "la", "les"},
}


def detect_language(text: str) -> str:
    """Detect language of text.

    Args:
        text: Input text to analyze.

    Returns:
        ISO 639-1 language code (e.g., "en", "pl", "de").
    """
    text_lower = text.lower()

    # Check character patterns first (most reliable for non-English)
    for lang, pattern in LANGUAGE_PATTERNS.items():
        if re.search(pattern, text):
            return lang

    # Check word markers
    words = set(re.findall(r'\b\w+\b', text_lower))

    best_lang = "en"
    best_score = 0

    for lang, markers in LANGUAGE_MARKERS.items():
        score = len(words & markers)
        if score > best_score:
            best_score = score
            best_lang = lang

    return best_lang
```

**Files to Create:**

| File | Content |
|------|---------|
| `server/router/infrastructure/language_detector.py` | Language detection utility |

**Files to Modify:**

| File | Changes |
|------|---------|
| `server/router/application/classifier/workflow_intent_classifier.py` | Use language detector when storing embeddings |

**Checklist:**

- [ ] Create `language_detector.py` with `detect_language()` function
- [ ] Add language detection to embedding creation
- [ ] Add language detection to query processing
- [ ] Unit tests for language detection

---

### TASK-050-3: Refactor Embedding Creation (Multi-Embedding)

**Status:** ✅ Done

Refactor `WorkflowIntentClassifier` to create multiple embeddings per workflow instead of one combined embedding.

**Current Code (❌):**
```python
# server/router/application/classifier/workflow_intent_classifier.py line 226-231

for name, texts in self._workflow_texts.items():
    try:
        # Combine all texts and encode
        combined = " ".join(texts)  # ← PROBLEM: Dilutes embedding
        embedding = self._model.encode(combined, convert_to_numpy=True)
```

**New Code (✅):**
```python
# server/router/application/classifier/workflow_intent_classifier.py

def _compute_and_store_embeddings(self, workflows: Dict[str, Any]) -> None:
    """Compute embeddings and store in LanceDB.

    Creates MULTIPLE embeddings per workflow:
    - One for each sample_prompt (weight: 1.0)
    - One for each trigger_keyword (weight: 0.8)
    - One for description (weight: 0.6)
    - One for workflow name (weight: 0.5)
    """
    if self._model is None:
        return

    store = self._ensure_vector_store()
    records = []

    for workflow_name, workflow in workflows.items():
        texts_with_metadata = self._extract_texts_with_metadata(workflow_name, workflow)

        for idx, (text, source_type, weight) in enumerate(texts_with_metadata):
            try:
                # Detect language
                language = detect_language(text)

                # Create embedding for this specific text
                embedding = self._model.encode(text, convert_to_numpy=True)

                record = {
                    "id": f"{workflow_name}_{idx}",
                    "workflow_id": workflow_name,
                    "namespace": "workflows",
                    "source_type": source_type,
                    "source_weight": weight,
                    "language": language,
                    "text": text[:500],
                    "vector": embedding.tolist(),
                }
                records.append(record)

            except Exception as e:
                logger.warning(f"Failed to embed '{text[:50]}...': {e}")

    # Store all records
    if records:
        store.store_workflow_embeddings_batch(records)
        logger.info(f"Stored {len(records)} workflow embeddings in LanceDB")


def _extract_texts_with_metadata(
    self,
    workflow_name: str,
    workflow: Any,
) -> List[Tuple[str, str, float]]:
    """Extract texts with source type and weight.

    Returns:
        List of (text, source_type, weight) tuples.
    """
    results = []

    # Sample prompts - highest weight (1.0)
    prompts = []
    if hasattr(workflow, "sample_prompts"):
        prompts = workflow.sample_prompts
    elif isinstance(workflow, dict) and "sample_prompts" in workflow:
        prompts = workflow["sample_prompts"]

    for prompt in prompts:
        results.append((prompt, "sample_prompt", 1.0))

    # Trigger keywords - high weight (0.8)
    keywords = []
    if hasattr(workflow, "trigger_keywords"):
        keywords = workflow.trigger_keywords
    elif isinstance(workflow, dict) and "trigger_keywords" in workflow:
        keywords = workflow["trigger_keywords"]

    for keyword in keywords:
        results.append((keyword, "trigger_keyword", 0.8))

    # Description - medium weight (0.6)
    description = None
    if hasattr(workflow, "description"):
        description = workflow.description
    elif isinstance(workflow, dict) and "description" in workflow:
        description = workflow["description"]

    if description:
        results.append((description, "description", 0.6))

    # Workflow name - low weight (0.5)
    name_text = workflow_name.replace("_", " ")
    results.append((name_text, "name", 0.5))

    return results
```

**Files to Modify:**

| File | Changes |
|------|---------|
| `server/router/application/classifier/workflow_intent_classifier.py` | Refactor `_compute_and_store_embeddings()`, add `_extract_texts_with_metadata()` |

**Checklist:**

- [ ] Rename `_extract_workflow_texts()` to `_extract_texts_with_metadata()`
- [ ] Return tuples of (text, source_type, weight)
- [ ] Update `_compute_and_store_embeddings()` to create multiple records
- [ ] Add language detection call
- [ ] Update embedding count logging
- [ ] Unit tests for multi-embedding creation

---

### TASK-050-4: Implement Weighted Max-Score Matching

**Status:** ✅ Done

Update search/matching logic to find best match across all embeddings for a workflow and apply weighted scoring.

**Current Search (❌):**
```python
# Returns single score per workflow
results = store.search_workflows(query_embedding, top_k=5)
# [{"workflow_id": "picnic_table_workflow", "score": 0.68}]
```

**New Search (✅):**
```python
# Returns best match per workflow with weighted score
results = store.search_workflows_weighted(query_embedding, query_language="en", top_k=5)
# [
#     {
#         "workflow_id": "picnic_table_workflow",
#         "raw_score": 1.0,           # Cosine similarity
#         "source_weight": 1.0,       # sample_prompt weight
#         "language_boost": 1.0,      # Same language as query
#         "final_score": 1.0,         # Combined score
#         "matched_text": "create a picnic table",
#         "source_type": "sample_prompt"
#     }
# ]
```

**Scoring Formula:**
```python
final_score = raw_cosine_score * source_weight * language_boost

where:
- raw_cosine_score: 0.0 to 1.0 (LaBSE cosine similarity)
- source_weight: 1.0 (prompt), 0.8 (keyword), 0.6 (description), 0.5 (name)
- language_boost: 1.0 (same language) or 0.9 (different language)
```

**Files to Modify:**

| File | Changes |
|------|---------|
| `server/router/infrastructure/vector_store/lance_store.py` | Add `search_workflows_weighted()` method |
| `server/router/infrastructure/vector_store/base.py` | Add `IVectorStore.search_workflows_weighted()` interface |
| `server/router/application/classifier/workflow_intent_classifier.py` | Update `classify()` to use weighted search |

**Implementation:**

```python
# server/router/infrastructure/vector_store/lance_store.py

def search_workflows_weighted(
    self,
    query_embedding: List[float],
    query_language: str = "en",
    top_k: int = 5,
    min_score: float = 0.5,
) -> List[Dict[str, Any]]:
    """Search workflows with weighted scoring.

    Returns best match per workflow with combined scoring.

    Args:
        query_embedding: Query vector (768-dim).
        query_language: Detected language of query.
        top_k: Number of workflows to return.
        min_score: Minimum final score threshold.

    Returns:
        List of workflow matches with scores.
    """
    if self._table is None:
        return []

    # Search with higher limit to get multiple embeddings per workflow
    raw_results = (
        self._table.search(query_embedding)
        .where(f"namespace = 'workflows'")
        .limit(top_k * 10)  # Get more results for grouping
        .to_pandas()
    )

    # Group by workflow_id, keep best match per workflow
    workflow_matches = {}

    for _, row in raw_results.iterrows():
        workflow_id = row["workflow_id"]
        raw_score = 1 - row["_distance"]  # Convert distance to similarity
        source_weight = row.get("source_weight", 1.0)
        text_language = row.get("language", "en")

        # Language boost
        language_boost = 1.0 if text_language == query_language else 0.9

        # Calculate final score
        final_score = raw_score * source_weight * language_boost

        # Keep best match per workflow
        if workflow_id not in workflow_matches or final_score > workflow_matches[workflow_id]["final_score"]:
            workflow_matches[workflow_id] = {
                "workflow_id": workflow_id,
                "raw_score": raw_score,
                "source_weight": source_weight,
                "language_boost": language_boost,
                "final_score": final_score,
                "matched_text": row["text"],
                "source_type": row.get("source_type", "unknown"),
            }

    # Sort by final score and filter
    results = sorted(
        workflow_matches.values(),
        key=lambda x: x["final_score"],
        reverse=True
    )

    # Apply minimum score filter
    results = [r for r in results if r["final_score"] >= min_score]

    return results[:top_k]
```

**Checklist:**

- [ ] Add `search_workflows_weighted()` to `LanceVectorStore`
- [ ] Add interface method to `IVectorStore`
- [ ] Update `WorkflowIntentClassifier.classify()` to use new method
- [ ] Add query language detection before search
- [ ] Unit tests for weighted search
- [ ] E2E tests for improved matching

---

### TASK-050-5: Confidence Threshold and Fallback

**Status:** ✅ Done

Add confidence threshold to trigger fallback to atomic tools when match quality is low.

**Configuration:**
```python
# server/router/infrastructure/config.py

class RouterConfig:
    # Semantic matching thresholds
    WORKFLOW_MATCH_THRESHOLD: float = 0.75      # Minimum score to trigger workflow
    WORKFLOW_CONFIDENT_THRESHOLD: float = 0.90  # High-confidence automatic trigger
    WORKFLOW_FALLBACK_THRESHOLD: float = 0.60   # Below this → atomic tools only
```

**Logic:**
```python
def classify(self, prompt: str) -> ClassificationResult:
    """Classify prompt to workflow with confidence handling.

    Returns:
        ClassificationResult with confidence level:
        - HIGH (>0.90): Auto-trigger workflow
        - MEDIUM (0.75-0.90): Suggest workflow, allow override
        - LOW (0.60-0.75): Weak match, prefer atomic tools
        - NONE (<0.60): No workflow match, atomic tools only
    """
    query_language = detect_language(prompt)
    query_embedding = self._model.encode(prompt, convert_to_numpy=True)

    results = self._store.search_workflows_weighted(
        query_embedding.tolist(),
        query_language=query_language,
        top_k=3,
        min_score=0.5,
    )

    if not results:
        return ClassificationResult(
            workflow_id=None,
            confidence=ConfidenceLevel.NONE,
            score=0.0,
            fallback_to_atomic=True,
        )

    best = results[0]
    score = best["final_score"]

    if score >= self.config.WORKFLOW_CONFIDENT_THRESHOLD:
        confidence = ConfidenceLevel.HIGH
        fallback = False
    elif score >= self.config.WORKFLOW_MATCH_THRESHOLD:
        confidence = ConfidenceLevel.MEDIUM
        fallback = False
    elif score >= self.config.WORKFLOW_FALLBACK_THRESHOLD:
        confidence = ConfidenceLevel.LOW
        fallback = True  # Suggest atomic tools
    else:
        confidence = ConfidenceLevel.NONE
        fallback = True

    return ClassificationResult(
        workflow_id=best["workflow_id"],
        confidence=confidence,
        score=score,
        matched_text=best["matched_text"],
        source_type=best["source_type"],
        fallback_to_atomic=fallback,
    )
```

**Files to Modify:**

| File | Changes |
|------|---------|
| `server/router/infrastructure/config.py` | Add threshold constants |
| `server/router/domain/entities/classification.py` | Add `ClassificationResult`, `ConfidenceLevel` |
| `server/router/application/classifier/workflow_intent_classifier.py` | Update `classify()` with confidence logic |
| `server/router/application/router.py` | Handle confidence levels in routing |

**New File:** `server/router/domain/entities/classification.py`

```python
"""Classification result entities."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ConfidenceLevel(Enum):
    """Confidence level for workflow classification."""
    HIGH = "high"       # >0.90 - Auto-trigger
    MEDIUM = "medium"   # 0.75-0.90 - Suggest
    LOW = "low"         # 0.60-0.75 - Weak match
    NONE = "none"       # <0.60 - No match


@dataclass
class ClassificationResult:
    """Result of workflow classification."""
    workflow_id: Optional[str]
    confidence: ConfidenceLevel
    score: float
    matched_text: Optional[str] = None
    source_type: Optional[str] = None
    fallback_to_atomic: bool = False
    alternatives: list = None  # Other possible workflows

    def __post_init__(self):
        if self.alternatives is None:
            self.alternatives = []
```

**Checklist:**

- [ ] Create `classification.py` with entities
- [ ] Add threshold constants to `config.py`
- [ ] Update `classify()` method with confidence logic
- [ ] Update `SupervisorRouter` to handle confidence levels
- [ ] Add logging for confidence decisions
- [ ] Unit tests for confidence thresholds
- [ ] E2E tests for fallback behavior

---

### TASK-050-6: Update Precompute Script

**Status:** ✅ Done

Update the Docker precompute script to generate multi-embeddings.

**File:** `server/scripts/precompute_embeddings.py`

```python
def precompute_workflow_embeddings():
    """Pre-compute workflow embeddings for Docker image."""
    logger.info("Pre-computing workflow embeddings...")

    # Load workflows
    from server.router.application.workflows.workflow_registry import WorkflowRegistry
    registry = WorkflowRegistry()
    workflows = registry.list_workflows()

    if not workflows:
        logger.info("No workflows found to embed")
        return

    # Get classifier with shared model
    classifier = get_workflow_intent_classifier()

    # This now creates MULTIPLE embeddings per workflow
    classifier.load_workflow_embeddings(workflows)

    # Log statistics
    store = classifier._ensure_vector_store()
    stats = store.get_stats()

    workflow_count = len(workflows)
    embedding_count = stats.get("workflows_count", 0)
    avg_per_workflow = embedding_count / workflow_count if workflow_count > 0 else 0

    logger.info(
        f"Stored {embedding_count} embeddings for {workflow_count} workflows "
        f"(avg {avg_per_workflow:.1f} per workflow)"
    )
```

**Files to Modify:**

| File | Changes |
|------|---------|
| `server/scripts/precompute_embeddings.py` | Update logging, verify multi-embedding |

**Checklist:**

- [ ] Update precompute script with new statistics
- [ ] Verify multi-embedding generation
- [ ] Test Docker build with new embeddings

---

### TASK-050-7: Update MCP Tools for Vector DB

**Status:** ✅ Done

Update `vector_db_manage` tool to show multi-embedding statistics.

**File:** `server/adapters/mcp/areas/vector_db.py`

Update `stats` action to show:
```json
{
    "db_path": "/root/.cache/blender-ai-mcp/vector_store",
    "total_records": 150,
    "tools_count": 135,
    "workflows_count": 1,
    "workflow_embeddings_count": 15,
    "avg_embeddings_per_workflow": 15.0,
    "source_type_breakdown": {
        "sample_prompt": 10,
        "trigger_keyword": 3,
        "description": 1,
        "name": 1
    }
}
```

**Files to Modify:**

| File | Changes |
|------|---------|
| `server/adapters/mcp/areas/vector_db.py` | Update `stats` action output |
| `server/router/infrastructure/vector_store/lance_store.py` | Add `get_detailed_stats()` method |

**Checklist:**

- [ ] Add `get_detailed_stats()` to vector store
- [ ] Update `vector_db_manage` stats output
- [ ] Update `search_test` to show weighted scores

---

## Testing Requirements

### Unit Tests

| Test File | What to Test |
|-----------|--------------|
| `tests/unit/router/infrastructure/test_language_detector.py` | Language detection accuracy |
| `tests/unit/router/infrastructure/test_lance_store_multi.py` | Multi-embedding storage/search |
| `tests/unit/router/application/test_classifier_weighted.py` | Weighted scoring logic |
| `tests/unit/router/domain/test_classification_entities.py` | Classification result entities |

### E2E Tests

| Test File | What to Test |
|-----------|--------------|
| `tests/e2e/router/test_semantic_matching_accuracy.py` | Exact phrase → ~1.0 score |
| `tests/e2e/router/test_language_aware_matching.py` | Polish prompt → Polish workflow text boost |
| `tests/e2e/router/test_confidence_fallback.py` | Low confidence → atomic tools |

### Verification Script

```python
# Run after implementation to verify improvements

from server.router.infrastructure.di import get_workflow_intent_classifier

classifier = get_workflow_intent_classifier()

test_cases = [
    ("create a picnic table", "picnic_table_workflow", 0.95),
    ("zrob stol piknikowy", "picnic_table_workflow", 0.90),
    ("make an outdoor table with benches", "picnic_table_workflow", 0.85),
    ("random unrelated query", None, 0.0),
]

print("Multi-Embedding Verification:")
print("=" * 60)

for query, expected_workflow, min_score in test_cases:
    result = classifier.classify(query)
    status = "✅" if (
        result.workflow_id == expected_workflow and
        result.score >= min_score
    ) else "❌"

    print(f"{status} Query: '{query}'")
    print(f"   Expected: {expected_workflow} (>={min_score})")
    print(f"   Got: {result.workflow_id} ({result.score:.3f})")
    print(f"   Confidence: {result.confidence.value}")
    print()
```

---

## Files Summary

### New Files to Create

| File | Purpose |
|------|---------|
| `server/router/infrastructure/language_detector.py` | Language detection utility |
| `server/router/domain/entities/classification.py` | Classification result entities |
| `tests/unit/router/infrastructure/test_language_detector.py` | Language detector tests |
| `tests/unit/router/infrastructure/test_lance_store_multi.py` | Multi-embedding tests |
| `tests/unit/router/application/test_classifier_weighted.py` | Weighted scoring tests |
| `tests/e2e/router/test_semantic_matching_accuracy.py` | Accuracy E2E tests |

### Files to Modify

| File | Changes |
|------|---------|
| `server/router/infrastructure/vector_store/base.py` | Update schema, add interfaces |
| `server/router/infrastructure/vector_store/lance_store.py` | Multi-embedding storage/search |
| `server/router/application/classifier/workflow_intent_classifier.py` | Refactor embedding creation, weighted matching |
| `server/router/infrastructure/config.py` | Add threshold constants |
| `server/router/application/router.py` | Handle confidence levels |
| `server/adapters/mcp/areas/vector_db.py` | Update stats output |
| `server/scripts/precompute_embeddings.py` | Update for multi-embedding |

---

## Implementation Order

1. **TASK-050-1:** Update LanceDB schema (foundation)
2. **TASK-050-2:** Implement language detection (dependency for 050-3)
3. **TASK-050-3:** Refactor embedding creation (core fix)
4. **TASK-050-4:** Implement weighted matching (core fix)
5. **TASK-050-5:** Confidence threshold and fallback (polish)
6. **TASK-050-6:** Update precompute script (Docker)
7. **TASK-050-7:** Update MCP tools (visibility)

---

## Expected Results

### Before (Current)
```
Query: "create a picnic table"
Score: 0.68 ❌
Confidence: Low
```

### After (Fixed)
```
Query: "create a picnic table"
Score: 1.00 ✅
Matched: "create a picnic table" (sample_prompt)
Confidence: HIGH
Language: en → en (boost: 1.0)
```

---

## Documentation Updates Required

After implementing this task, update:

| File | What to Update |
|------|----------------|
| `_docs/_TASKS/TASK-050_Multi_Embedding_Workflow_System.md` | Mark sub-tasks as ✅ Done |
| `_docs/_TASKS/README.md` | Add TASK-050, update statistics |
| `_docs/_CHANGELOG/{NN}-{date}-multi-embedding-system.md` | Create changelog entry |
| `_docs/_ROUTER/README.md` | Update semantic matching documentation |
| `_docs/_ROUTER/IMPLEMENTATION/XX-multi-embedding-system.md` | Implementation details |

---

## Relation to Other Tasks

```
TASK-047 (LanceDB Migration)
    ↓
TASK-048 (Shared LaBSE)
    ↓
TASK-050 (Multi-Embedding System) ← THIS TASK
    ↓
Accurate semantic workflow matching
```

This task directly addresses the root cause of poor semantic matching discovered during testing of the picnic table workflow.
