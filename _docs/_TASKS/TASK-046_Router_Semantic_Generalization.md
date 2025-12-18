# TASK-046: Router Semantic Generalization (LaBSE Workflow Matching)

**Priority:** 🔴 High
**Category:** Router Enhancement
**Estimated Effort:** Large
**Dependencies:** TASK-039 (Router Supervisor Implementation), TASK-041 (YAML Workflow Integration)
**Status:** ✅ Done

---

## Overview

Extension of the Router Supervisor with semantic generalization using LaBSE. Currently LaBSE is used only for matching **tools** - this task extends it to **workflows**, enabling:

1. Semantic matching of workflows (not just keyword matching)
2. Generalization between workflows (e.g., "chair" → "table_workflow" when chair_workflow is missing)
3. Combining knowledge from multiple workflows for unknown objects
4. Learning from user feedback

**Problem:**
```python
# NOW - simple keyword matching
def find_by_keywords(self, text: str) -> Optional[str]:
    text_lower = text.lower()
    for name, workflow in self._workflows.items():
        if workflow.matches_keywords(text_lower):  # ← hardcoded "in" check
            return name
    return None

# User: "make a chair"
# Result: None (no "chair" in keywords of any workflow)
```

**Goal:**
```python
# AFTER IMPLEMENTATION - semantic similarity
def find_by_similarity(self, text: str, threshold: float = 0.5) -> List[Tuple[str, float]]:
    # LaBSE understands semantics
    return [
        ("table_workflow", 0.72),   # chair has legs like table
        ("tower_workflow", 0.45),   # vertical structure
    ]
```

---

## Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                     ROUTER SEMANTIC LAYER (NEW)                             │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ WorkflowIntentClassifier (NEW)                                       │   │
│  │   - load_workflow_embeddings(workflows)                              │   │
│  │   - find_similar(text, top_k) → [(workflow_name, score), ...]        │   │
│  │   - get_combined_rules(similar_workflows) → unified rules            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ SemanticWorkflowMatcher (NEW)                                        │   │
│  │   - match(prompt, context) → best workflow + confidence              │   │
│  │   - generalize(prompt, similar_workflows) → hybrid workflow          │   │
│  │   - learn_from_feedback(prompt, correct_workflow)                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ ProportionInheritance (NEW)                                          │   │
│  │   - inherit_proportions(source_workflows) → merged rules             │   │
│  │   - apply_proportions(target_object, rules) → corrected params       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                     EXISTING ROUTER COMPONENTS                              │
│  IntentClassifier (tools) ─► WorkflowRegistry ─► SupervisorRouter          │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Sub-Tasks

### TASK-046-1: Workflow Sample Prompts

**Status:** ✅ Done

Add `sample_prompts` to workflows (analogous to tools).

**Change in BaseWorkflow:**

```python
# server/router/application/workflows/base.py

class BaseWorkflow(ABC):
    # EXISTING
    @property
    @abstractmethod
    def trigger_keywords(self) -> List[str]:
        pass

    # NEW - sample prompts for LaBSE
    @property
    def sample_prompts(self) -> List[str]:
        """Sample prompts for semantic matching.

        These prompts are embedded by LaBSE for semantic similarity.
        Include variations in multiple languages if needed.
        """
        return []
```

**Change in PhoneWorkflow:**

```python
# server/router/application/workflows/phone_workflow.py

class PhoneWorkflow(BaseWorkflow):
    # EXISTING
    @property
    def trigger_keywords(self) -> List[str]:
        return ["phone", "smartphone", "tablet", ...]

    # NEW
    @property
    def sample_prompts(self) -> List[str]:
        return [
            # English
            "create a phone",
            "make a smartphone",
            "model a mobile device",
            "build a tablet",
            "design a cellphone",

            # Polish (LaBSE supports 109 languages)
            "make a phone",
            "create a smartphone",
            "design a tablet",

            # German
            "erstelle ein Handy",

            # Spanish
            "crear un teléfono móvil",
        ]
```

**Change in TowerWorkflow:**

```python
# server/router/application/workflows/tower_workflow.py

class TowerWorkflow(BaseWorkflow):
    @property
    def sample_prompts(self) -> List[str]:
        return [
            "create a tower",
            "build a tall pillar",
            "make a column",
            "model an obelisk",
            "design a skyscraper",

            # Polish
            "make a tower",
            "create a column",
            "design a pillar",
        ]
```

**Change in WorkflowDefinition (YAML):**

```python
# server/router/application/workflows/base.py

@dataclass
class WorkflowDefinition:
    name: str
    steps: List[WorkflowStep]
    description: str = ""
    category: str = "custom"
    trigger_pattern: Optional[str] = None
    trigger_keywords: List[str] = field(default_factory=list)
    sample_prompts: List[str] = field(default_factory=list)  # NEW
    # ...
```

**Change in WorkflowLoader (YAML parsing):**

```python
# server/router/infrastructure/workflow_loader.py

def _parse_workflow(self, data: Dict) -> WorkflowDefinition:
    return WorkflowDefinition(
        name=data["name"],
        # ... existing fields ...
        sample_prompts=data.get("sample_prompts", []),  # NEW
    )
```

**Example YAML workflow:**

```yaml
# server/router/application/workflows/custom/example_chair.yaml
name: chair_workflow
description: "Chair modeling workflow"
category: furniture
trigger_pattern: chair_like
trigger_keywords:
  - chair
  - seat
  - stool

# NEW - sample prompts for LaBSE
sample_prompts:
  - "create a chair"
  - "make a seat"
  - "model a stool"
  - "make a chair"
  - "create an armchair"

steps:
  - tool: modeling_create_primitive
    params:
      type: CUBE
  # ...
```

**Implementation Checklist:**

| Layer | File | What to Change |
|-------|------|----------------|
| Base | `server/router/application/workflows/base.py` | Add `sample_prompts` property to `BaseWorkflow`, add field to `WorkflowDefinition` |
| Phone | `server/router/application/workflows/phone_workflow.py` | Add `sample_prompts` property |
| Tower | `server/router/application/workflows/tower_workflow.py` | Add `sample_prompts` property |
| Screen | `server/router/application/workflows/screen_cutout_workflow.py` | Add `sample_prompts` property |
| Loader | `server/router/infrastructure/workflow_loader.py` | Parse `sample_prompts` from YAML/JSON |
| Tests | `tests/unit/router/application/workflows/test_sample_prompts.py` | Test sample prompts loading |

---

### TASK-046-2: WorkflowIntentClassifier

**Status:** ✅ Done

New component classifying prompts to workflows using LaBSE.

**New file:**

```python
# server/router/application/classifier/workflow_intent_classifier.py

"""
Workflow Intent Classifier.

Classifies user prompts to workflows using LaBSE embeddings.
Enables semantic matching and generalization across workflows.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

from server.router.infrastructure.config import RouterConfig
from server.router.application.classifier.embedding_cache import EmbeddingCache

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False

MODEL_NAME = "sentence-transformers/LaBSE"


class WorkflowIntentClassifier:
    """Classifies user prompts to workflows using LaBSE embeddings.

    Unlike IntentClassifier (for tools), this classifier:
    - Works with workflow definitions
    - Supports generalization (finding similar workflows)
    - Can combine knowledge from multiple workflows
    """

    def __init__(
        self,
        config: Optional[RouterConfig] = None,
        cache_dir: Optional[Path] = None,
    ):
        """Initialize workflow classifier.

        Args:
            config: Router configuration.
            cache_dir: Directory for embedding cache.
        """
        self._config = config or RouterConfig()
        self._cache = EmbeddingCache(cache_dir, prefix="workflow_")
        self._model: Optional[Any] = None
        self._workflow_embeddings: Dict[str, Any] = {}
        self._workflow_texts: Dict[str, List[str]] = {}
        self._is_loaded = False

    def _load_model(self) -> bool:
        """Load the sentence transformer model."""
        if not EMBEDDINGS_AVAILABLE:
            return False

        if self._model is not None:
            return True

        try:
            logger.info(f"Loading LaBSE model for workflow classification")
            self._model = SentenceTransformer(MODEL_NAME)
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False

    def load_workflow_embeddings(
        self,
        workflows: Dict[str, Any],  # name -> workflow or definition
    ) -> None:
        """Load and cache workflow embeddings.

        Args:
            workflows: Dictionary of workflow name -> workflow object.
        """
        if not workflows:
            return

        # Collect texts for each workflow
        self._workflow_texts = {}
        for name, workflow in workflows.items():
            texts = []

            # Get sample prompts
            if hasattr(workflow, 'sample_prompts'):
                texts.extend(workflow.sample_prompts)
            elif hasattr(workflow, 'get') and 'sample_prompts' in workflow:
                texts.extend(workflow['sample_prompts'])

            # Get keywords
            if hasattr(workflow, 'trigger_keywords'):
                texts.extend(workflow.trigger_keywords)
            elif hasattr(workflow, 'get') and 'trigger_keywords' in workflow:
                texts.extend(workflow['trigger_keywords'])

            # Add workflow name and description
            texts.append(name.replace("_", " "))
            if hasattr(workflow, 'description'):
                texts.append(workflow.description)

            if texts:
                self._workflow_texts[name] = texts

        # Compute embeddings
        if EMBEDDINGS_AVAILABLE and self._load_model():
            self._compute_embeddings()
            self._is_loaded = True

    def _compute_embeddings(self) -> None:
        """Compute embeddings for all workflows."""
        if self._model is None:
            return

        logger.info(f"Computing embeddings for {len(self._workflow_texts)} workflows")

        for name, texts in self._workflow_texts.items():
            try:
                # Combine all texts and encode
                combined = " ".join(texts)
                embedding = self._model.encode(
                    combined,
                    convert_to_numpy=True,
                    normalize_embeddings=True,
                )
                self._workflow_embeddings[name] = embedding
            except Exception as e:
                logger.error(f"Failed to compute embedding for {name}: {e}")

        logger.info(f"Computed {len(self._workflow_embeddings)} workflow embeddings")

    def find_similar(
        self,
        prompt: str,
        top_k: int = 3,
        threshold: float = 0.0,
    ) -> List[Tuple[str, float]]:
        """Find workflows semantically similar to prompt.

        Args:
            prompt: User prompt or intent.
            top_k: Number of results to return.
            threshold: Minimum similarity score.

        Returns:
            List of (workflow_name, similarity_score) tuples.
        """
        if not self._is_loaded or not EMBEDDINGS_AVAILABLE:
            return []

        if self._model is None:
            return []

        try:
            # Get prompt embedding
            prompt_embedding = self._model.encode(
                prompt,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )

            # Calculate similarities
            similarities = []
            for name, workflow_embedding in self._workflow_embeddings.items():
                sim = float(np.dot(prompt_embedding, workflow_embedding))
                if sim >= threshold:
                    similarities.append((name, sim))

            # Sort by similarity
            similarities.sort(key=lambda x: x[1], reverse=True)

            return similarities[:top_k]

        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []

    def find_best_match(
        self,
        prompt: str,
        min_confidence: float = 0.5,
    ) -> Optional[Tuple[str, float]]:
        """Find the best matching workflow.

        Args:
            prompt: User prompt.
            min_confidence: Minimum confidence score.

        Returns:
            (workflow_name, confidence) or None.
        """
        results = self.find_similar(prompt, top_k=1, threshold=min_confidence)
        return results[0] if results else None

    def get_generalization_candidates(
        self,
        prompt: str,
        min_similarity: float = 0.3,
        max_candidates: int = 3,
    ) -> List[Tuple[str, float]]:
        """Get workflows that could be generalized for this prompt.

        Used when no exact match exists. Returns workflows that
        share semantic concepts with the prompt.

        Args:
            prompt: User prompt.
            min_similarity: Minimum similarity to consider.
            max_candidates: Maximum workflows to return.

        Returns:
            List of (workflow_name, similarity) tuples.
        """
        return self.find_similar(
            prompt,
            top_k=max_candidates,
            threshold=min_similarity,
        )

    def similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts.

        Args:
            text1: First text.
            text2: Second text.

        Returns:
            Similarity score (0.0 to 1.0).
        """
        if not EMBEDDINGS_AVAILABLE or self._model is None:
            return 0.0

        try:
            embeddings = self._model.encode(
                [text1, text2],
                convert_to_numpy=True,
                normalize_embeddings=True,
            )
            return float(np.dot(embeddings[0], embeddings[1]))
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return 0.0

    def is_loaded(self) -> bool:
        """Check if classifier is loaded."""
        return self._is_loaded

    def get_info(self) -> Dict[str, Any]:
        """Get classifier information."""
        return {
            "embeddings_available": EMBEDDINGS_AVAILABLE,
            "model_loaded": self._model is not None,
            "num_workflows": len(self._workflow_embeddings),
            "is_loaded": self._is_loaded,
        }
```

**Implementation Checklist:**

| Layer | File | What to Create |
|-------|------|----------------|
| Classifier | `server/router/application/classifier/workflow_intent_classifier.py` | Full implementation above |
| Init | `server/router/application/classifier/__init__.py` | Export `WorkflowIntentClassifier` |
| Tests | `tests/unit/router/application/classifier/test_workflow_intent_classifier.py` | Unit tests (30+) |

---

### TASK-046-3: SemanticWorkflowMatcher

**Status:** ✅ Done

Component combining workflow matching with generalization.

**New file:**

```python
# server/router/application/matcher/semantic_workflow_matcher.py

"""
Semantic Workflow Matcher.

Combines workflow matching with generalization capabilities.
When no exact workflow match exists, it can:
1. Find similar workflows by semantic similarity
2. Combine rules from multiple workflows
3. Generate hybrid workflows for unknown objects
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple, Optional

from server.router.application.classifier.workflow_intent_classifier import (
    WorkflowIntentClassifier,
)
from server.router.application.workflows.registry import WorkflowRegistry
from server.router.infrastructure.config import RouterConfig

logger = logging.getLogger(__name__)


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
    """Matches prompts to workflows using semantic understanding.

    Matching hierarchy:
    1. Exact keyword match (fastest, highest confidence)
    2. Semantic similarity match (LaBSE embeddings)
    3. Generalization from similar workflows (combines knowledge)
    """

    def __init__(
        self,
        config: Optional[RouterConfig] = None,
        registry: Optional[WorkflowRegistry] = None,
    ):
        """Initialize matcher.

        Args:
            config: Router configuration.
            registry: Workflow registry.
        """
        self._config = config or RouterConfig()
        self._registry = registry
        self._classifier = WorkflowIntentClassifier(config=self._config)
        self._is_initialized = False

    def initialize(self, registry: WorkflowRegistry) -> None:
        """Initialize with workflow registry.

        Args:
            registry: Workflow registry to use.
        """
        self._registry = registry

        # Build workflow dict for classifier
        workflows = {}
        for name in registry.get_all_workflows():
            workflow = registry.get_workflow(name)
            if workflow:
                workflows[name] = workflow
            else:
                definition = registry.get_definition(name)
                if definition:
                    workflows[name] = definition

        # Load embeddings
        self._classifier.load_workflow_embeddings(workflows)
        self._is_initialized = True

        logger.info(f"SemanticWorkflowMatcher initialized with {len(workflows)} workflows")

    def match(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> MatchResult:
        """Match prompt to workflow.

        Tries matching in order:
        1. Exact keyword match
        2. Semantic similarity match
        3. Generalization from similar workflows

        Args:
            prompt: User prompt or intent.
            context: Optional scene context.

        Returns:
            MatchResult with workflow and confidence.
        """
        if not self._is_initialized or not self._registry:
            return MatchResult(match_type="error", metadata={"error": "not initialized"})

        # Step 1: Try exact keyword match
        keyword_match = self._registry.find_by_keywords(prompt)
        if keyword_match:
            return MatchResult(
                workflow_name=keyword_match,
                confidence=1.0,
                match_type="exact",
            )

        # Step 2: Try semantic similarity
        semantic_result = self._classifier.find_best_match(
            prompt,
            min_confidence=self._config.workflow_similarity_threshold,
        )
        if semantic_result:
            name, score = semantic_result
            return MatchResult(
                workflow_name=name,
                confidence=score,
                match_type="semantic",
            )

        # Step 3: Try generalization
        similar = self._classifier.get_generalization_candidates(
            prompt,
            min_similarity=self._config.generalization_threshold,
            max_candidates=3,
        )
        if similar:
            return self._generalize(prompt, similar, context)

        # No match found
        return MatchResult(match_type="none")

    def _generalize(
        self,
        prompt: str,
        similar_workflows: List[Tuple[str, float]],
        context: Optional[Dict[str, Any]],
    ) -> MatchResult:
        """Generalize from similar workflows.

        Creates a hybrid approach by combining rules from
        similar workflows weighted by similarity.

        Args:
            prompt: User prompt.
            similar_workflows: List of (workflow_name, similarity) tuples.
            context: Scene context.

        Returns:
            MatchResult with generalized workflow.
        """
        # Use the most similar workflow as base
        base_workflow, base_score = similar_workflows[0]

        # Collect rules from all similar workflows
        applied_rules = []
        for name, score in similar_workflows:
            workflow = self._registry.get_workflow(name)
            if workflow:
                applied_rules.append(f"proportions_from:{name}:{score:.2f}")

        return MatchResult(
            workflow_name=base_workflow,
            confidence=base_score * 0.8,  # Reduce confidence for generalized
            match_type="generalized",
            similar_workflows=similar_workflows,
            applied_rules=applied_rules,
            metadata={
                "base_workflow": base_workflow,
                "generalized_from": [w for w, _ in similar_workflows],
            }
        )

    def find_similar(
        self,
        prompt: str,
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        """Find workflows similar to prompt.

        Args:
            prompt: User prompt.
            top_k: Number of results.

        Returns:
            List of (workflow_name, similarity) tuples.
        """
        return self._classifier.find_similar(prompt, top_k=top_k)
```

**Configuration:**

```python
# server/router/infrastructure/config.py

@dataclass
class RouterConfig:
    # ... existing fields ...

    # NEW - Semantic matching thresholds
    workflow_similarity_threshold: float = 0.5  # Min for semantic match
    generalization_threshold: float = 0.3       # Min for generalization
    enable_generalization: bool = True          # Enable workflow generalization
```

**Implementation Checklist:**

| Layer | File | What to Create/Change |
|-------|------|----------------------|
| Matcher | `server/router/application/matcher/semantic_workflow_matcher.py` | Full implementation above |
| Matcher | `server/router/application/matcher/__init__.py` | Create with exports |
| Config | `server/router/infrastructure/config.py` | Add new thresholds |
| Tests | `tests/unit/router/application/matcher/test_semantic_workflow_matcher.py` | Unit tests (25+) |

---

### TASK-046-4: ProportionInheritance

**Status:** ✅ Done

Proportion inheritance between similar workflows.

**New file:**

```python
# server/router/application/inheritance/proportion_inheritance.py

"""
Proportion Inheritance.

Enables workflows to inherit and combine proportion rules from similar workflows.
When modeling an unknown object (e.g., "chair"), this module can:
1. Find similar workflows (table, tower)
2. Extract proportion rules from each
3. Combine rules with weighted inheritance
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class ProportionRule:
    """A single proportion rule."""
    name: str                    # e.g., "bevel_ratio", "inset_ratio"
    value: float                 # The proportion value
    source_workflow: str         # Which workflow this came from
    weight: float = 1.0          # Weight for combining (from similarity)
    description: str = ""


@dataclass
class InheritedProportions:
    """Collection of inherited proportion rules."""
    rules: Dict[str, ProportionRule] = field(default_factory=dict)
    sources: List[str] = field(default_factory=list)
    total_weight: float = 0.0

    def get(self, name: str, default: float = 0.0) -> float:
        """Get proportion value by name."""
        if name in self.rules:
            return self.rules[name].value
        return default

    def to_dict(self) -> Dict[str, float]:
        """Convert to simple dict for parameter substitution."""
        return {name: rule.value for name, rule in self.rules.items()}
```

(continued)

```python
class ProportionInheritance:
    """Inherits and combines proportion rules from workflows.

    Proportion rules define relative sizes for modeling operations:
    - bevel_ratio: Edge bevel as % of smallest dimension
    - inset_ratio: Face inset as % of face size
    - extrude_ratio: Extrusion depth as % of object height
    - taper_ratio: Taper amount for tall objects
    """

    # Standard proportion rules per workflow type
    WORKFLOW_PROPORTIONS: Dict[str, Dict[str, float]] = {
        "phone_workflow": {
            "bevel_ratio": 0.04,      # Subtle edge bevel
            "inset_ratio": 0.05,      # Screen border
            "extrude_ratio": 0.40,    # Screen depth
            "corner_radius": 0.02,    # Rounded corners
        },
        "tower_workflow": {
            "bevel_ratio": 0.02,      # Light bevel
            "taper_ratio": 0.15,      # Top narrower than base
            "segment_ratio": 0.25,    # Floor/level height
            "base_ratio": 1.2,        # Base wider than body
        },
        "table_workflow": {
            "bevel_ratio": 0.03,      # Edge bevel
            "leg_ratio": 0.08,        # Leg width vs top
            "top_thickness": 0.05,    # Top thickness ratio
            "leg_inset": 0.10,        # Leg distance from edge
        },
        "screen_cutout_workflow": {
            "inset_ratio": 0.03,      # Border width
            "extrude_ratio": 0.50,    # Screen depth
            "bevel_ratio": 0.005,     # Very subtle bevel
        },
    }

    def __init__(self):
        """Initialize proportion inheritance."""
        self._custom_proportions: Dict[str, Dict[str, float]] = {}

    def register_proportions(
        self,
        workflow_name: str,
        proportions: Dict[str, float],
    ) -> None:
        """Register custom proportions for a workflow.

        Args:
            workflow_name: Workflow name.
            proportions: Proportion rules.
        """
        self._custom_proportions[workflow_name] = proportions

    def get_workflow_proportions(
        self,
        workflow_name: str,
    ) -> Dict[str, float]:
        """Get proportions for a specific workflow.

        Args:
            workflow_name: Workflow name.

        Returns:
            Proportion rules dict.
        """
        # Check custom first
        if workflow_name in self._custom_proportions:
            return self._custom_proportions[workflow_name]

        # Check built-in
        if workflow_name in self.WORKFLOW_PROPORTIONS:
            return self.WORKFLOW_PROPORTIONS[workflow_name]

        return {}

    def inherit_proportions(
        self,
        similar_workflows: List[Tuple[str, float]],
    ) -> InheritedProportions:
        """Inherit proportions from similar workflows.

        Combines proportion rules weighted by workflow similarity.
        Higher similarity = more weight in the combined result.

        Args:
            similar_workflows: List of (workflow_name, similarity) tuples.

        Returns:
            InheritedProportions with combined rules.
        """
        result = InheritedProportions()

        # Collect all rules with weights
        weighted_rules: Dict[str, List[Tuple[float, float, str]]] = {}

        for workflow_name, similarity in similar_workflows:
            proportions = self.get_workflow_proportions(workflow_name)
            result.sources.append(workflow_name)
            result.total_weight += similarity

            for rule_name, value in proportions.items():
                if rule_name not in weighted_rules:
                    weighted_rules[rule_name] = []
                weighted_rules[rule_name].append((value, similarity, workflow_name))

        # Calculate weighted average for each rule
        for rule_name, values in weighted_rules.items():
            total_weight = sum(w for _, w, _ in values)
            if total_weight > 0:
                weighted_value = sum(v * w for v, w, _ in values) / total_weight

                # Use the highest-weight source as the main source
                main_source = max(values, key=lambda x: x[1])[2]

                result.rules[rule_name] = ProportionRule(
                    name=rule_name,
                    value=weighted_value,
                    source_workflow=main_source,
                    weight=total_weight / result.total_weight if result.total_weight > 0 else 0,
                )

        return result

    def apply_to_dimensions(
        self,
        proportions: InheritedProportions,
        dimensions: List[float],
    ) -> Dict[str, float]:
        """Apply proportions to object dimensions.

        Converts relative proportions to absolute values based on dimensions.

        Args:
            proportions: Inherited proportions.
            dimensions: Object dimensions [x, y, z].

        Returns:
            Dict of parameter name -> absolute value.
        """
        if len(dimensions) < 3:
            return {}

        x, y, z = dimensions[:3]
        min_dim = min(x, y, z)
        min_xy = min(x, y)

        result = {}

        for name, rule in proportions.rules.items():
            if "bevel" in name or "corner" in name:
                result[name] = rule.value * min_dim
            elif "inset" in name or "border" in name:
                result[name] = rule.value * min_xy
            elif "extrude" in name or "depth" in name:
                result[name] = rule.value * z
            elif "taper" in name:
                result[name] = rule.value  # Keep as ratio
            elif "leg" in name:
                result[name] = rule.value * min_xy
            else:
                result[name] = rule.value * min_dim  # Default

        return result
```

**Implementation Checklist:**

| Layer | File | What to Create |
|-------|------|----------------|
| Inheritance | `server/router/application/inheritance/proportion_inheritance.py` | Full implementation above |
| Inheritance | `server/router/application/inheritance/__init__.py` | Create with exports |
| Tests | `tests/unit/router/application/inheritance/test_proportion_inheritance.py` | Unit tests (20+) |

---

### TASK-046-5: Integration with SupervisorRouter

**Status:** ✅ Done

Integration of all new components with the main router.

**Changes in SupervisorRouter:**

```python
# server/router/application/router.py

from server.router.application.matcher.semantic_workflow_matcher import (
    SemanticWorkflowMatcher,
    MatchResult,
)
from server.router.application.inheritance.proportion_inheritance import (
    ProportionInheritance,
)


class SupervisorRouter:
    def __init__(
        self,
        config: Optional[RouterConfig] = None,
        rpc_client: Optional[Any] = None,
    ):
        # ... existing initialization ...

        # NEW - Semantic matching
        self._semantic_matcher = SemanticWorkflowMatcher(config=self.config)
        self._proportion_inheritance = ProportionInheritance()

        # Initialize semantic matcher when registry is available
        self._semantic_initialized = False

    def _ensure_semantic_initialized(self) -> None:
        """Ensure semantic matcher is initialized."""
        if self._semantic_initialized:
            return

        from server.router.application.workflows import get_workflow_registry
        registry = get_workflow_registry()
        self._semantic_matcher.initialize(registry)
        self._semantic_initialized = True

    def process_llm_tool_call(
        self,
        tool_name: str,
        params: Dict[str, Any],
        prompt: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Process an LLM tool call through the router pipeline."""
        # ... existing steps 1-3 ...

        # Step 4: Try semantic workflow matching (NEW)
        if prompt and self.config.enable_generalization:
            self._ensure_semantic_initialized()
            match_result = self._semantic_matcher.match(prompt, context)

            if match_result.match_type in ("semantic", "generalized"):
                # Apply inherited proportions
                if match_result.similar_workflows:
                    inherited = self._proportion_inheritance.inherit_proportions(
                        match_result.similar_workflows
                    )
                    if context and hasattr(context, 'dimensions'):
                        applied = self._proportion_inheritance.apply_to_dimensions(
                            inherited,
                            context.dimensions,
                        )
                        # Merge into params
                        for key, value in applied.items():
                            if key not in params:
                                params[key] = value

                # Expand matched workflow
                if match_result.workflow_name:
                    expanded = self._expand_semantic_workflow(
                        match_result,
                        params,
                        context,
                    )
                    if expanded:
                        return expanded

        # ... continue with existing steps ...

    def _expand_semantic_workflow(
        self,
        match_result: MatchResult,
        params: Dict[str, Any],
        context: Optional[SceneContext],
    ) -> Optional[List[Dict[str, Any]]]:
        """Expand a semantically matched workflow.

        Args:
            match_result: Semantic match result.
            params: Tool parameters.
            context: Scene context.

        Returns:
            List of tool calls or None.
        """
        from server.router.application.workflows import get_workflow_registry
        registry = get_workflow_registry()

        workflow_name = match_result.workflow_name

        # Build context with inherited proportions
        expand_context = {}
        if context:
            expand_context = {
                "mode": context.mode,
                "dimensions": getattr(context, 'dimensions', None),
            }

        # Add metadata about match
        expand_context["match_type"] = match_result.match_type
        expand_context["match_confidence"] = match_result.confidence

        # Expand workflow
        calls = registry.expand_workflow(
            workflow_name,
            params=params,
            context=expand_context,
        )

        if calls:
            # Add metadata to first call
            calls[0].corrections_applied.append(
                f"semantic_match:{match_result.match_type}:{match_result.confidence:.2f}"
            )

        return [{"tool": c.tool_name, "params": c.params} for c in calls] if calls else None

    def find_similar_workflows(
        self,
        prompt: str,
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        """Find workflows similar to a prompt.

        Public API for debugging and exploration.

        Args:
            prompt: User prompt.
            top_k: Number of results.

        Returns:
            List of (workflow_name, similarity) tuples.
        """
        self._ensure_semantic_initialized()
        return self._semantic_matcher.find_similar(prompt, top_k=top_k)
```

**Implementation Checklist:**

| Layer | File | What to Change |
|-------|------|----------------|
| Router | `server/router/application/router.py` | Add semantic matching integration |
| Tests | `tests/unit/router/application/test_supervisor_router_semantic.py` | Integration tests (15+) |
| E2E | `tests/e2e/router/test_semantic_matching.py` | E2E tests |

---

### TASK-046-6: Learning from Feedback

**Status:** ✅ Done

System for learning from user feedback.

**New file:**

```python
# server/router/application/learning/feedback_collector.py

"""
Feedback Collector.

Collects user feedback to improve workflow matching over time.
Stores:
- Prompt -> Workflow mappings (correct matches)
- Failed matches (for improvement)
- User corrections
"""

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class FeedbackEntry:
    """Single feedback entry."""
    timestamp: str
    prompt: str
    matched_workflow: Optional[str]
    match_confidence: float
    match_type: str  # exact, semantic, generalized, none
    user_correction: Optional[str]  # If user corrected the match
    was_helpful: Optional[bool]
    metadata: Dict[str, Any]


class FeedbackCollector:
    """Collects and stores feedback for learning.

    Feedback is used to:
    1. Add new sample_prompts to workflows
    2. Adjust similarity thresholds
    3. Identify gaps in workflow coverage
    """

    def __init__(
        self,
        storage_path: Optional[Path] = None,
        max_entries: int = 10000,
    ):
        """Initialize collector.

        Args:
            storage_path: Path to feedback storage file.
            max_entries: Maximum entries to keep.
        """
        self._storage_path = storage_path or Path.home() / ".blender-mcp" / "feedback.jsonl"
        self._max_entries = max_entries
        self._entries: List[FeedbackEntry] = []
        self._load()

    def _load(self) -> None:
        """Load existing feedback."""
        if not self._storage_path.exists():
            return

        try:
            with open(self._storage_path, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    self._entries.append(FeedbackEntry(**data))
        except Exception as e:
            logger.warning(f"Failed to load feedback: {e}")

    def _save(self) -> None:
        """Save feedback to storage."""
        try:
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._storage_path, 'w') as f:
                for entry in self._entries[-self._max_entries:]:
                    f.write(json.dumps(asdict(entry)) + '\n')
        except Exception as e:
            logger.warning(f"Failed to save feedback: {e}")

    def record_match(
        self,
        prompt: str,
        matched_workflow: Optional[str],
        confidence: float,
        match_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a workflow match.

        Args:
            prompt: User prompt.
            matched_workflow: Matched workflow name.
            confidence: Match confidence.
            match_type: Type of match.
            metadata: Additional metadata.
        """
        entry = FeedbackEntry(
            timestamp=datetime.utcnow().isoformat(),
            prompt=prompt,
            matched_workflow=matched_workflow,
            match_confidence=confidence,
            match_type=match_type,
            user_correction=None,
            was_helpful=None,
            metadata=metadata or {},
        )
        self._entries.append(entry)
        self._save()

    def record_correction(
        self,
        prompt: str,
        original_match: Optional[str],
        correct_workflow: str,
    ) -> None:
        """Record user correction.

        When user indicates a different workflow should have matched.

        Args:
            prompt: Original prompt.
            original_match: What router matched.
            correct_workflow: What should have matched.
        """
        # Find and update the entry
        for entry in reversed(self._entries):
            if entry.prompt == prompt and entry.matched_workflow == original_match:
                entry.user_correction = correct_workflow
                entry.was_helpful = False
                break
        else:
            # Create new correction entry
            entry = FeedbackEntry(
                timestamp=datetime.utcnow().isoformat(),
                prompt=prompt,
                matched_workflow=original_match,
                match_confidence=0.0,
                match_type="correction",
                user_correction=correct_workflow,
                was_helpful=False,
                metadata={},
            )
            self._entries.append(entry)

        self._save()

    def get_new_sample_prompts(
        self,
        workflow_name: str,
        min_corrections: int = 3,
    ) -> List[str]:
        """Get prompts that should be added as sample_prompts.

        Returns prompts that were corrected to this workflow multiple times.

        Args:
            workflow_name: Workflow to get prompts for.
            min_corrections: Minimum corrections to include prompt.

        Returns:
            List of prompts to add.
        """
        prompt_counts: Dict[str, int] = {}

        for entry in self._entries:
            if entry.user_correction == workflow_name:
                prompt_counts[entry.prompt] = prompt_counts.get(entry.prompt, 0) + 1

        return [
            prompt for prompt, count in prompt_counts.items()
            if count >= min_corrections
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """Get feedback statistics."""
        total = len(self._entries)
        corrections = sum(1 for e in self._entries if e.user_correction)
        by_type = {}
        for e in self._entries:
            by_type[e.match_type] = by_type.get(e.match_type, 0) + 1

        return {
            "total_entries": total,
            "corrections": corrections,
            "correction_rate": corrections / total if total > 0 else 0,
            "by_match_type": by_type,
        }
```

**Implementation Checklist:**

| Layer | File | What to Create |
|-------|------|----------------|
| Learning | `server/router/application/learning/feedback_collector.py` | Full implementation above |
| Learning | `server/router/application/learning/__init__.py` | Create with exports |
| Router | `server/router/application/router.py` | Integrate feedback collection |
| Tests | `tests/unit/router/application/learning/test_feedback_collector.py` | Unit tests (15+) |

---

### TASK-046-7: MCP Tools for Semantic Matching

**Status:** ✅ Done

New MCP tools for exploring semantic matching (debugging/development).

**New file:**

```python
# server/adapters/mcp/areas/router_tools.py

"""
Router MCP Tools.

Tools for interacting with and debugging the Router Supervisor.
"""

from typing import List, Tuple
from fastmcp import Context


def register_router_tools(mcp):
    """Register router-related MCP tools."""

    @mcp.tool()
    def router_set_goal(
        ctx: Context,
        goal: str,
    ) -> str:
        """
        [SYSTEM][CRITICAL] Tell the Router what you're building.

        IMPORTANT: Call this FIRST before ANY modeling operation!

        The Router Supervisor uses this to optimize your workflow automatically.
        Without setting a goal, the router cannot help you with smart workflow
        expansion and error prevention.

        Args:
            goal: What you're creating. Be specific!
                  Examples: "smartphone", "wooden table", "medieval tower",
                           "office chair", "sports car", "human face"

        Returns:
            Confirmation with matched workflow (if any).

        Example workflow:
            1. router_set_goal("smartphone")     # <- FIRST!
            2. modeling_create_primitive("CUBE") # Router expands to phone workflow
            3. ... router handles the rest automatically

        Supported goal keywords (trigger workflows):
            - phone, smartphone, tablet, mobile -> phone_workflow
            - tower, pillar, column, obelisk -> tower_workflow
            - table, desk, surface -> table_workflow
            - house, building, home -> house_workflow
            - chair, seat, stool -> chair_workflow
        """
        # Implementation will use SemanticWorkflowMatcher
        pass

    @mcp.tool()
    def router_find_similar_workflows(
        ctx: Context,
        prompt: str,
        top_k: int = 5,
    ) -> str:
        """
        [SYSTEM][SAFE] Find workflows similar to a description.

        Uses LaBSE semantic embeddings to find workflows that match
        the meaning of your prompt, not just keywords.

        Useful for:
        - Exploring available workflows
        - Finding the right workflow for an object
        - Understanding what workflows could apply

        Args:
            prompt: Description of what you want to build.
            top_k: Number of similar workflows to return.

        Returns:
            JSON with similar workflows and similarity scores.

        Example:
            router_find_similar_workflows("comfortable office chair")
            -> [("chair_workflow", 0.85), ("table_workflow", 0.62), ...]
        """
        pass

    @mcp.tool()
    def router_get_inherited_proportions(
        ctx: Context,
        similar_workflows: List[str],
        dimensions: List[float],
    ) -> str:
        """
        [SYSTEM][SAFE] Get inherited proportions from similar workflows.

        Combines proportion rules from multiple workflows weighted by
        relevance. Useful for objects that don't have their own workflow.

        Args:
            similar_workflows: List of workflow names to inherit from.
            dimensions: Object dimensions [x, y, z] in meters.

        Returns:
            JSON with inherited proportion rules and calculated values.

        Example:
            router_get_inherited_proportions(
                ["table_workflow", "tower_workflow"],
                [0.5, 0.5, 0.9]
            )
        """
        pass

    @mcp.tool()
    def router_feedback(
        ctx: Context,
        prompt: str,
        correct_workflow: str,
    ) -> str:
        """
        [SYSTEM][SAFE] Provide feedback to improve workflow matching.

        Call this when the router matched the wrong workflow.
        The feedback is stored and used to improve future matching.

        Args:
            prompt: The original prompt/description.
            correct_workflow: The workflow that should have matched.

        Returns:
            Confirmation message.

        Example:
            # Router matched "phone_workflow" but you wanted "tablet_workflow"
            router_feedback("create a large tablet", "tablet_workflow")
        """
        pass
```

**Implementation Checklist:**

| Layer | File | What to Create/Change |
|-------|------|----------------------|
| Adapter | `server/adapters/mcp/areas/router_tools.py` | Full implementation above |
| Server | `server/adapters/mcp/server.py` | Import and register router_tools |
| Metadata | `server/router/infrastructure/tools_metadata/router/` | Create metadata for new tools |
| Tests | `tests/unit/adapters/mcp/test_router_tools.py` | Unit tests |

---

## Testing Requirements

- [x] Unit tests for WorkflowIntentClassifier (30+ tests)
- [x] Unit tests for SemanticWorkflowMatcher (25+ tests)
- [x] Unit tests for ProportionInheritance (20+ tests)
- [x] Unit tests for FeedbackCollector (15+ tests)
- [x] Integration tests for SupervisorRouter semantic matching (15+ tests)
- [x] E2E tests for full semantic pipeline
- [x] Test with multilingual prompts (PL, EN, DE, ES)

---

## Implementation Order

1. **TASK-046-1** - Sample prompts (foundation)
2. **TASK-046-2** - WorkflowIntentClassifier (core classifier)
3. **TASK-046-3** - SemanticWorkflowMatcher (matching logic)
4. **TASK-046-4** - ProportionInheritance (rule inheritance)
5. **TASK-046-5** - SupervisorRouter integration
6. **TASK-046-6** - Feedback learning
7. **TASK-046-7** - MCP tools

---

## New Files to Create

### Server Side

```
server/router/application/classifier/workflow_intent_classifier.py
server/router/application/matcher/__init__.py
server/router/application/matcher/semantic_workflow_matcher.py
server/router/application/inheritance/__init__.py
server/router/application/inheritance/proportion_inheritance.py
server/router/application/learning/__init__.py
server/router/application/learning/feedback_collector.py
server/adapters/mcp/areas/router_tools.py
server/router/infrastructure/tools_metadata/router/
  ├── router_set_goal.json
  ├── router_find_similar_workflows.json
  ├── router_get_inherited_proportions.json
  └── router_feedback.json
```

### Tests

```
tests/unit/router/application/classifier/test_workflow_intent_classifier.py
tests/unit/router/application/matcher/__init__.py
tests/unit/router/application/matcher/test_semantic_workflow_matcher.py
tests/unit/router/application/inheritance/__init__.py
tests/unit/router/application/inheritance/test_proportion_inheritance.py
tests/unit/router/application/learning/__init__.py
tests/unit/router/application/learning/test_feedback_collector.py
tests/unit/router/application/workflows/test_sample_prompts.py
tests/unit/router/application/test_supervisor_router_semantic.py
tests/e2e/router/test_semantic_matching.py
```

---

## Files to Modify

| File | What to Change |
|------|----------------|
| `server/router/application/workflows/base.py` | Add `sample_prompts` property |
| `server/router/application/workflows/phone_workflow.py` | Add `sample_prompts` |
| `server/router/application/workflows/tower_workflow.py` | Add `sample_prompts` |
| `server/router/application/workflows/screen_cutout_workflow.py` | Add `sample_prompts` |
| `server/router/infrastructure/workflow_loader.py` | Parse `sample_prompts` |
| `server/router/infrastructure/config.py` | Add semantic thresholds |
| `server/router/application/router.py` | Integrate semantic matching |
| `server/router/application/classifier/__init__.py` | Export new classifier |
| `server/adapters/mcp/server.py` | Register router_tools |

---

## Documentation Updates Required

| File | What to Update |
|------|----------------|
| `_docs/_TASKS/TASK-046_Router_Semantic_Generalization.md` | This file |
| `_docs/_TASKS/README.md` | Add TASK-046 |
| `_docs/_ROUTER/README.md` | Add semantic matching section |
| `_docs/_ROUTER/IMPLEMENTATION/28-workflow-intent-classifier.md` | Create |
| `_docs/_ROUTER/IMPLEMENTATION/29-semantic-workflow-matcher.md` | Create |
| `_docs/_ROUTER/IMPLEMENTATION/30-proportion-inheritance.md` | Create |
| `_docs/_ROUTER/IMPLEMENTATION/31-feedback-learning.md` | Create |
| `_docs/_CHANGELOG/{NN}-semantic-generalization.md` | Create |
| `README.md` | Update Router section |

---

## Expected Results

After implementation:

```python
# User: "make a chair" (no chair_workflow exists)
matcher.match("make a chair")
# → MatchResult(
#     workflow_name="table_workflow",
#     confidence=0.72,
#     match_type="generalized",
#     similar_workflows=[
#         ("table_workflow", 0.72),
#         ("tower_workflow", 0.45),
#     ],
#     applied_rules=["proportions_from:table_workflow:0.72", ...]
# )

# Router automatically applies:
# - Leg proportions from table_workflow
# - Vertical proportions from tower_workflow (weighted less)
# - Combined bevel/inset ratios
```

---

## Dependencies

- `sentence-transformers>=2.0.0` (LaBSE model)
- `numpy` (for embeddings)
- TASK-039 Router Supervisor (base infrastructure)
- TASK-041 YAML Workflow Integration (workflow definitions)
