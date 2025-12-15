# TASK-048: Proper DI for Classifiers + Shared LaBSE Model

| Field | Value |
|-------|-------|
| Status | ✅ Done |
| Created | 2024-12-07 |
| Completed | 2024-12-07 |
| Priority | High |
| Category | Performance / Architecture |

## Problem

Currently `SemanticWorkflowMatcher` creates its **own instance** of `WorkflowIntentClassifier` instead of using a shared one via DI:

```
SupervisorRouter
├── self.classifier = IntentClassifier()           # LaBSE model #1
└── self._semantic_matcher = SemanticWorkflowMatcher()
    └── self._classifier = WorkflowIntentClassifier()  # LaBSE model #2
```

Consequences:
- 2x loading LaBSE (~1.8GB RAM each = 3.6GB!)
- 2x connection to LanceDB
- Pre-computed embeddings are not used (the new instance does not know about the cache)

## Solution

All classifiers, the vector store and the LaBSE model via the DI container.

### Changes in files

#### 1. `server/infrastructure/di.py`

Add providers:
```python
_labse_model_instance = None
_vector_store_instance = None
_intent_classifier_instance = None
_workflow_classifier_instance = None

def get_labse_model():
    """Singleton LaBSE model (~1.8GB RAM) - shared between classifiers."""
    global _labse_model_instance
    if _labse_model_instance is None:
        from sentence_transformers import SentenceTransformer
        _labse_model_instance = SentenceTransformer("sentence-transformers/LaBSE")
    return _labse_model_instance

def get_vector_store() -> IVectorStore:
    """Singleton LanceVectorStore."""
    global _vector_store_instance
    if _vector_store_instance is None:
        from server.router.infrastructure.vector_store.lance_store import LanceVectorStore
        _vector_store_instance = LanceVectorStore()
    return _vector_store_instance

def get_intent_classifier() -> IntentClassifier:
    """Singleton IntentClassifier (tools)."""
    global _intent_classifier_instance
    if _intent_classifier_instance is None:
        from server.router.application.classifier.intent_classifier import IntentClassifier
        _intent_classifier_instance = IntentClassifier(
            config=get_router_config(),
            vector_store=get_vector_store(),
            model=get_labse_model(),  # shared model
        )
    return _intent_classifier_instance

def get_workflow_classifier() -> WorkflowIntentClassifier:
    """Singleton WorkflowIntentClassifier (workflows)."""
    global _workflow_classifier_instance
    if _workflow_classifier_instance is None:
        from server.router.application.classifier.workflow_intent_classifier import WorkflowIntentClassifier
        _workflow_classifier_instance = WorkflowIntentClassifier(
            config=get_router_config(),
            vector_store=get_vector_store(),
            model=get_labse_model(),  # shared model
        )
    return _workflow_classifier_instance
```

Update `get_router()`:
```python
def get_router():
    # ... existing code ...
    _router_instance = SupervisorRouter(
        config=router_config,
        rpc_client=get_rpc_client(),
        classifier=get_intent_classifier(),  # ADD
        workflow_classifier=get_workflow_classifier(),  # ADD
    )
```

#### 2. `server/router/application/router.py`

Change the `SupervisorRouter` constructor:
```python
def __init__(
    self,
    config: Optional[RouterConfig] = None,
    rpc_client: Optional[Any] = None,
    classifier: Optional[IntentClassifier] = None,
    workflow_classifier: Optional[WorkflowIntentClassifier] = None,  # ADD
):
    # ...
    self.classifier = classifier or IntentClassifier(config=self.config)

    # Pass workflow_classifier to SemanticWorkflowMatcher
    self._semantic_matcher = SemanticWorkflowMatcher(
        config=self.config,
        classifier=workflow_classifier,  # ADD
    )
```

#### 3. `server/router/application/matcher/semantic_workflow_matcher.py`

Change the constructor to accept a classifier:
```python
def __init__(
    self,
    config: Optional[RouterConfig] = None,
    registry: Optional["WorkflowRegistry"] = None,
    classifier: Optional[WorkflowIntentClassifier] = None,  # ADD
):
    self._config = config or RouterConfig()
    self._registry = registry
    # Use injected or create a new one (fallback for tests)
    self._classifier = classifier or WorkflowIntentClassifier(config=self._config)
    self._is_initialized = False
```

#### 4. `server/scripts/precompute_embeddings.py`

Use DI instead of creating your own instances:
```python
def main():
    # Use DI
    from server.infrastructure.di import get_intent_classifier, get_workflow_classifier

    classifier = get_intent_classifier()
    # ... load tool embeddings ...

    workflow_classifier = get_workflow_classifier()
    # ... load workflow embeddings ...
```

#### 5. `server/router/application/classifier/intent_classifier.py`

Add `model` as an optional parameter:
```python
def __init__(
    self,
    config: Optional[RouterConfig] = None,
    vector_store: Optional[IVectorStore] = None,
    model: Optional[Any] = None,  # ADD - shared LaBSE
):
    self._model = model  # use injected or load later
```

#### 6. `server/router/application/classifier/workflow_intent_classifier.py`

Same — add `model` parameter:
```python
def __init__(
    self,
    config: Optional[RouterConfig] = None,
    vector_store: Optional[IVectorStore] = None,
    model: Optional[Any] = None,  # ADD - shared LaBSE
):
    self._model = model
```

### Files to modify

| File | Change |
|------|--------|
| `server/infrastructure/di.py` | Add 4 providers (model, store, 2x classifier) + update `get_router()` |
| `server/router/application/router.py` | Add `workflow_classifier` param |
| `server/router/application/matcher/semantic_workflow_matcher.py` | Add `classifier` param |
| `server/router/application/classifier/intent_classifier.py` | Add `model` param |
| `server/router/application/classifier/workflow_intent_classifier.py` | Add `model` param |
| `server/scripts/precompute_embeddings.py` | Use DI |

### Final result

```
DI Container (singleton instances)
├── get_labse_model()          # 1x LaBSE ~1.8GB (shared)
├── get_vector_store()         # 1x LanceDB connection
├── get_intent_classifier()    # uses shared model + store
├── get_workflow_classifier()  # uses shared model + store
└── get_router()
    └── SupervisorRouter
        ├── classifier = get_intent_classifier()
        └── _semantic_matcher
            └── _classifier = get_workflow_classifier()
```

**RAM savings: ~1.8GB** (one model instead of two)

### Implementation order

1. ✅ Add `model` param to `intent_classifier.py` and `workflow_intent_classifier.py`
2. ✅ Add 4 providers to `di.py` (model, store, 2x classifier)
3. ✅ Update `SemanticWorkflowMatcher` (accepts classifier)
4. ✅ Update `SupervisorRouter` (accepts workflow_classifier)
5. ✅ Update `get_router()` in DI
6. ✅ Update `precompute_embeddings.py` (uses DI)
7. ✅ Build Docker and test `router_find_similar_workflows`

---

## Implementation Summary

### Files Modified

| File | Change |
|------|--------|
| `server/infrastructure/di.py` | Added 4 providers: `get_labse_model()`, `get_vector_store()`, `get_intent_classifier()`, `get_workflow_classifier()`. Updated `get_router()` to inject both classifiers. |
| `server/router/application/router.py` | Added `workflow_classifier` param to constructor. Passes it to `SemanticWorkflowMatcher`. |
| `server/router/application/matcher/semantic_workflow_matcher.py` | Added `classifier` param to accept `WorkflowIntentClassifier` via DI. |
| `server/router/application/classifier/intent_classifier.py` | Already had `model` param (done in TASK-047). |
| `server/router/application/classifier/workflow_intent_classifier.py` | Already had `model` param (done in TASK-047). |
| `server/scripts/precompute_embeddings.py` | Updated to use DI providers instead of creating own instances. |

### Verification

Docker build and runtime tests confirm:

```
LaBSE model is singleton: True
Vector store is singleton: True
Both classifiers use same model: True
Both classifiers use same vector store: True
Router uses DI intent classifier: True
Router semantic matcher uses DI workflow classifier: True
```

### Performance Impact

- **RAM savings: ~1.8GB** (one LaBSE model instead of two)
- **Startup time**: Faster (embeddings loaded once, shared)
- **Pre-computed embeddings**: Now properly used by all components
