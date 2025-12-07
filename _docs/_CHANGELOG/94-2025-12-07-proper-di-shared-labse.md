# Changelog 94 - Proper DI for Classifiers + Shared LaBSE Model

**Date:** 2025-12-07
**Task:** [TASK-048](../_TASKS/TASK-048_Proper_DI_For_Classifiers_Shared_LaBSE_model.md)
**Category:** Performance / Architecture

## Summary

Fixed DI architecture to share a single LaBSE model (~1.8GB RAM) between `IntentClassifier` and `WorkflowIntentClassifier`. Previously each classifier loaded its own model instance, doubling RAM usage.

## Problem

```
SupervisorRouter
├── self.classifier = IntentClassifier()           # model LaBSE #1
└── self._semantic_matcher = SemanticWorkflowMatcher()
    └── self._classifier = WorkflowIntentClassifier()  # model LaBSE #2
```

**Issues:**
- 2x LaBSE loading (~1.8GB RAM each = 3.6GB!)
- 2x LanceDB connections
- Pre-computed embeddings not shared

## Solution

All classifiers, vector store, and LaBSE model provided through DI container:

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

## Changes

### Files Modified

| File | Change |
|------|--------|
| `server/infrastructure/di.py` | Added 4 providers: `get_labse_model()`, `get_vector_store()`, `get_intent_classifier()`, `get_workflow_classifier()`. Updated `get_router()`. |
| `server/router/application/router.py` | Added `workflow_classifier` param to constructor. |
| `server/router/application/matcher/semantic_workflow_matcher.py` | Added `classifier` param to accept via DI. |
| `server/scripts/precompute_embeddings.py` | Updated to use DI providers. |

## Verification

```python
>>> from server.infrastructure.di import *
>>> model1 = get_labse_model()
>>> model2 = get_labse_model()
>>> model1 is model2
True
>>> c1 = get_intent_classifier()
>>> c2 = get_workflow_classifier()
>>> c1._model is c2._model
True
```

## Performance Impact

- **RAM savings: ~1.8GB** (one LaBSE model instead of two)
- **Startup time**: Faster (single model load)
- **Pre-computed embeddings**: Properly shared across all components
