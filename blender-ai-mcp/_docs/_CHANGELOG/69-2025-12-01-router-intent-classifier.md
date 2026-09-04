# Changelog 69: Router Intent Classifier

**Date:** 2025-12-01
**Type:** Feature
**Task:** TASK-039-15

## Summary

Implemented the Intent Classifier for the Router Supervisor, providing offline intent classification using LaBSE embeddings with TF-IDF fallback.

## Changes

### New Files

- `server/router/application/classifier/intent_classifier.py` - Main classifier
- `server/router/application/classifier/embedding_cache.py` - Embedding caching
- `tests/unit/router/application/test_intent_classifier.py` - 35 unit tests

### Features

1. **LaBSE Embeddings**
   - Language-agnostic BERT Sentence Embedding
   - 768-dimensional vectors
   - 109 languages supported
   - ~10ms inference time

2. **TF-IDF Fallback**
   - Automatic fallback when sentence-transformers unavailable
   - Uses scikit-learn TF-IDF vectorizer
   - Reasonable accuracy for English prompts

3. **Embedding Cache**
   - Persists embeddings to disk
   - Hash-based validation for cache freshness
   - Automatic reload on metadata change

4. **Multilingual Support**

```python
classifier.predict("extrude the face")      # English
classifier.predict("wyciągnij ścianę")      # Polish
classifier.predict("extruir la cara")       # Spanish
```

### API

```python
classifier = IntentClassifier(config=RouterConfig())
classifier.load_tool_embeddings(metadata)

tool, confidence = classifier.predict("bevel the edges")
results = classifier.predict_top_k("smooth the mesh", k=5)
```

## Dependencies

Requires `sentence-transformers` for full functionality (optional):

```toml
dependencies = [
    "sentence-transformers>=2.0.0,<4.0.0",
]
```

## Related

- Part of Phase 3: Tool Processing Engines
- Implements `IIntentClassifier` interface
