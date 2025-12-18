# 14. Intent Classifier

## Overview

The Intent Classifier (`IntentClassifier`) classifies user prompts to tool names using semantic embeddings (LaBSE) with TF-IDF fallback.

## File Locations

```
server/router/application/classifier/intent_classifier.py
server/router/application/classifier/embedding_cache.py
```

## Core Functionality

### LaBSE Embeddings

Uses Language-agnostic BERT Sentence Embedding for multilingual semantic similarity:

- Model: `sentence-transformers/LaBSE`
- Embedding dimension: 768
- RAM usage: ~1.8GB
- Inference time: ~10ms per query
- Supports 109 languages

### TF-IDF Fallback

When sentence-transformers is not installed, falls back to scikit-learn TF-IDF:

```python
# Falls back automatically if sentence-transformers unavailable
classifier = IntentClassifier()
classifier.load_tool_embeddings(metadata)
```

## API

### IntentClassifier

```python
# Initialize
classifier = IntentClassifier(config=RouterConfig(), cache_dir=Path)

# Load tool embeddings from metadata
classifier.load_tool_embeddings(metadata)

# Predict best matching tool
tool, confidence = classifier.predict("extrude the top face")
# → ("mesh_extrude_region", 0.87)

# Predict top K matches
results = classifier.predict_top_k("bevel the edges", k=5)
# → [("mesh_bevel", 0.92), ("mesh_smooth", 0.65), ...]

# Check if loaded
classifier.is_loaded()  # True

# Get model info
info = classifier.get_model_info()
```

### EmbeddingCache

```python
cache = EmbeddingCache(cache_dir=Path)

# Save embeddings
cache.save(embeddings_dict, metadata_hash)

# Load embeddings
embeddings = cache.load()

# Check validity
cache.is_valid(metadata_hash)

# Clear cache
cache.clear()

# Get cache info
cache.get_cache_path()
cache.get_cache_size()  # bytes

# Compute metadata hash
hash = EmbeddingCache.compute_metadata_hash(metadata)
```

## Multilingual Support

LaBSE supports 109 languages:

```python
classifier.predict("extrude the top face")      # English
classifier.predict("wyciągnij górną ścianę")    # Polish
classifier.predict("extruir la cara superior")  # Spanish
```

## Configuration

Controlled via `RouterConfig`:

```python
RouterConfig(
    embedding_threshold=0.40,  # Minimum confidence score
)
```

## Dependencies

Add to `pyproject.toml`:

```toml
[project]
dependencies = [
    "sentence-transformers>=2.0.0,<4.0.0",
]
```

## Test Coverage

- `tests/unit/router/application/test_intent_classifier.py`
- 35 tests covering classification and caching
- Some tests skipped when numpy not available
