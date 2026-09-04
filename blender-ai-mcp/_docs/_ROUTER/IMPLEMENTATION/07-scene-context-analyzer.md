# Scene Context Analyzer

**Task:** TASK-039-7
**Layer:** Application
**Status:** ✅ Done

## Overview

Analyzes Blender scene state via RPC for router decision making.

## File

- `server/router/application/analyzers/scene_context_analyzer.py`

## Implementation

```python
class SceneContextAnalyzer(ISceneAnalyzer):
    def analyze(self, object_name: str = None) -> SceneContext
    def get_cached() -> Optional[SceneContext]
    def invalidate_cache() -> None
    def get_mode() -> str
    def has_selection() -> bool
    def analyze_from_data(data: Dict) -> SceneContext  # For testing
```

## Features

- Queries scene via RPC client
- Caches results with configurable TTL
- Extracts: mode, active object, selection, topology, proportions
- Calculates proportions automatically from dimensions
- Graceful fallback on RPC errors

## Data Collected

```python
SceneContext:
    mode: str                    # OBJECT, EDIT, SCULPT
    active_object: str           # Name of active object
    selected_objects: List[str]  # Selected object names
    objects: List[ObjectInfo]    # Detailed object info
    topology: TopologyInfo       # Vertices, edges, faces, selection
    proportions: ProportionInfo  # Calculated proportions
    materials: List[str]         # Material names
    modifiers: List[str]         # Modifier names
```

## Usage

```python
analyzer = SceneContextAnalyzer(rpc_client=rpc, cache_ttl=1.0)

# Analyze current scene
context = analyzer.analyze()
print(f"Mode: {context.mode}")
print(f"Active: {context.active_object}")
print(f"Has selection: {context.has_selection}")

# Use cached result
cached = analyzer.get_cached()
```

## Tests

- `tests/unit/router/application/test_scene_context_analyzer.py` - 20 tests
