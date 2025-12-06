# Plan: Proper DI for Classifiers + Shared LaBSE Model

## Problem

Obecnie `SemanticWorkflowMatcher` tworzy **własną instancję** `WorkflowIntentClassifier` zamiast używać wspólnej przez DI:

```
SupervisorRouter
├── self.classifier = IntentClassifier()           # model LaBSE #1
└── self._semantic_matcher = SemanticWorkflowMatcher()
    └── self._classifier = WorkflowIntentClassifier()  # model LaBSE #2
```

**Skutki:**
- 2x ładowanie LaBSE (~1.8GB RAM każdy = 3.6GB!)
- 2x połączenie do LanceDB
- Pre-computed embeddings nie są używane (nowa instancja nie wie o cache)

## Rozwiązanie

Wszystkie classifiery, vector store i model LaBSE przez DI container.

### Zmiany w plikach

#### 1. `server/infrastructure/di.py`

Dodać providery:
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

Zaktualizować `get_router()`:
```python
def get_router():
    # ... existing code ...
    _router_instance = SupervisorRouter(
        config=router_config,
        rpc_client=get_rpc_client(),
        classifier=get_intent_classifier(),  # DODAĆ
        workflow_classifier=get_workflow_classifier(),  # DODAĆ
    )
```

#### 2. `server/router/application/router.py`

Zmienić konstruktor `SupervisorRouter`:
```python
def __init__(
    self,
    config: Optional[RouterConfig] = None,
    rpc_client: Optional[Any] = None,
    classifier: Optional[IntentClassifier] = None,
    workflow_classifier: Optional[WorkflowIntentClassifier] = None,  # DODAĆ
):
    # ...
    self.classifier = classifier or IntentClassifier(config=self.config)

    # Przekazać workflow_classifier do SemanticWorkflowMatcher
    self._semantic_matcher = SemanticWorkflowMatcher(
        config=self.config,
        classifier=workflow_classifier,  # DODAĆ
    )
```

#### 3. `server/router/application/matcher/semantic_workflow_matcher.py`

Zmienić konstruktor aby przyjmował classifier:
```python
def __init__(
    self,
    config: Optional[RouterConfig] = None,
    registry: Optional["WorkflowRegistry"] = None,
    classifier: Optional[WorkflowIntentClassifier] = None,  # DODAĆ
):
    self._config = config or RouterConfig()
    self._registry = registry
    # Użyj wstrzykniętego lub stwórz nowy (fallback dla testów)
    self._classifier = classifier or WorkflowIntentClassifier(config=self._config)
    self._is_initialized = False
```

#### 4. `server/scripts/precompute_embeddings.py`

Użyć DI zamiast tworzyć własne instancje:
```python
def main():
    # Użyj DI
    from server.infrastructure.di import get_intent_classifier, get_workflow_classifier

    classifier = get_intent_classifier()
    # ... load tool embeddings ...

    workflow_classifier = get_workflow_classifier()
    # ... load workflow embeddings ...
```

#### 5. `server/router/application/classifier/intent_classifier.py`

Dodać `model` jako opcjonalny parametr:
```python
def __init__(
    self,
    config: Optional[RouterConfig] = None,
    vector_store: Optional[IVectorStore] = None,
    model: Optional[Any] = None,  # DODAĆ - shared LaBSE
):
    self._model = model  # użyj wstrzyknięty lub załaduj później
```

#### 6. `server/router/application/classifier/workflow_intent_classifier.py`

Tak samo - dodać `model` parametr:
```python
def __init__(
    self,
    config: Optional[RouterConfig] = None,
    vector_store: Optional[IVectorStore] = None,
    model: Optional[Any] = None,  # DODAĆ - shared LaBSE
):
    self._model = model
```

### Pliki do modyfikacji

| Plik | Zmiana |
|------|--------|
| `server/infrastructure/di.py` | Dodać 4 providery (model, store, 2x classifier) + update `get_router()` |
| `server/router/application/router.py` | Dodać `workflow_classifier` param |
| `server/router/application/matcher/semantic_workflow_matcher.py` | Dodać `classifier` param |
| `server/router/application/classifier/intent_classifier.py` | Dodać `model` param |
| `server/router/application/classifier/workflow_intent_classifier.py` | Dodać `model` param |
| `server/scripts/precompute_embeddings.py` | Użyć DI |

### Efekt końcowy

```
DI Container (singleton instances)
├── get_labse_model()          # 1x LaBSE ~1.8GB (shared)
├── get_vector_store()         # 1x LanceDB connection
├── get_intent_classifier()    # używa shared model + store
├── get_workflow_classifier()  # używa shared model + store
└── get_router()
    └── SupervisorRouter
        ├── classifier = get_intent_classifier()
        └── _semantic_matcher
            └── _classifier = get_workflow_classifier()
```

**Oszczędność RAM: ~1.8GB** (jeden model zamiast dwóch)

### Kolejność implementacji

1. Dodać `model` param do `intent_classifier.py` i `workflow_intent_classifier.py`
2. Dodać 4 providery do `di.py` (model, store, 2x classifier)
3. Zaktualizować `SemanticWorkflowMatcher` (przyjmuje classifier)
4. Zaktualizować `SupervisorRouter` (przyjmuje workflow_classifier)
5. Zaktualizować `get_router()` w DI
6. Zaktualizować `precompute_embeddings.py` (używa DI)
7. Zbudować Docker i przetestować `router_find_similar_workflows`