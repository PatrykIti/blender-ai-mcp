# 03 - Domain Interfaces

**Task:** TASK-039-3
**Status:** ✅ Done
**Layer:** Domain

---

## Overview

Domain interfaces define abstract contracts for all router components. They follow the Dependency Inversion Principle - high-level modules depend on abstractions, not concrete implementations.

---

## Interfaces

### IToolInterceptor

Captures LLM tool calls before execution.

```python
class IToolInterceptor(ABC):
    def intercept(self, tool_name, params, prompt=None) -> InterceptedToolCall
    def get_history(self, limit=10) -> List[InterceptedToolCall]
    def clear_history() -> None
    def get_session_calls(self, session_id) -> List[InterceptedToolCall]
```

### ISceneAnalyzer

Analyzes current Blender scene state.

```python
class ISceneAnalyzer(ABC):
    def analyze(self, object_name=None) -> SceneContext
    def get_cached() -> Optional[SceneContext]
    def invalidate_cache() -> None
    def get_mode() -> str
    def has_selection() -> bool
```

### IPatternDetector

Detects geometry patterns (tower_like, phone_like, etc.).

```python
class IPatternDetector(ABC):
    def detect(self, context) -> PatternMatchResult
    def detect_pattern(self, context, pattern_type) -> DetectedPattern
    def get_best_match(self, context, threshold=0.5) -> Optional[DetectedPattern]
    def get_supported_patterns() -> List[PatternType]
```

### ICorrectionEngine

Corrects tool call parameters and context.

```python
class ICorrectionEngine(ABC):
    def correct(self, tool_name, params, context) -> Tuple[CorrectedToolCall, List[CorrectedToolCall]]
    def clamp_parameters(self, tool_name, params, context) -> Tuple[Dict, List[str]]
    def get_required_mode(self, tool_name) -> str
    def requires_selection(self, tool_name) -> bool
    def get_mode_switch_call(self, target_mode) -> CorrectedToolCall
    def get_selection_call(self, selection_type="all") -> CorrectedToolCall
```

### IOverrideEngine

Decides if tools should be replaced with alternatives.

```python
class IOverrideEngine(ABC):
    def check_override(self, tool_name, params, context, pattern=None) -> OverrideDecision
    def get_override_rules() -> List[Dict]
    def register_rule(self, rule_name, trigger_tool, trigger_pattern, replacement_tools) -> None
    def remove_rule(self, rule_name) -> bool
```

### IExpansionEngine

Expands tool calls into workflows.

```python
class IExpansionEngine(ABC):
    def expand(self, tool_name, params, context, pattern=None) -> Optional[List[CorrectedToolCall]]
    def get_workflow(self, workflow_name) -> Optional[List[Dict]]
    def register_workflow(self, name, steps, trigger_pattern=None, trigger_keywords=None) -> None
    def get_available_workflows() -> List[str]
    def expand_workflow(self, workflow_name, params) -> List[CorrectedToolCall]
```

### IFirewall

Validates and blocks invalid operations.

```python
class IFirewall(ABC):
    def validate(self, tool_call, context) -> FirewallResult
    def validate_sequence(self, calls, context) -> List[FirewallResult]
    def can_auto_fix(self, tool_call, context) -> bool
    def get_firewall_rules() -> List[Dict]
    def register_rule(self, rule_name, tool_pattern, condition, action, fix_description="") -> None
    def enable_rule(self, rule_name) -> bool
    def disable_rule(self, rule_name) -> bool
```

### IIntentClassifier

Classifies user intent to tools using embeddings.

```python
class IIntentClassifier(ABC):
    def predict(self, prompt) -> Tuple[str, float]
    def predict_top_k(self, prompt, k=5) -> List[Tuple[str, float]]
    def load_tool_embeddings(self, metadata) -> None
    def is_loaded() -> bool
    def get_embedding(self, text) -> Optional[Any]
    def similarity(self, text1, text2) -> float
```

---

## Design Principles

### Dependency Inversion

```
SupervisorRouter (Application)
        ↓ depends on
    IFirewall (Domain Interface)
        ↑ implements
ErrorFirewall (Application)
```

### Single Responsibility

Each interface has one clear purpose:
- `IToolInterceptor` - capture calls
- `ISceneAnalyzer` - read scene state
- `IPatternDetector` - detect patterns
- `ICorrectionEngine` - fix parameters
- `IOverrideEngine` - replace tools
- `IExpansionEngine` - expand workflows
- `IFirewall` - validate operations
- `IIntentClassifier` - classify intent

---

## Tests

- `tests/unit/router/domain/test_interfaces.py` - 24 tests
  - Verifies each interface is abstract
  - Verifies required methods exist
  - Verifies interface can be implemented

---

## See Also

- [02-domain-entities.md](./02-domain-entities.md)
- [04-metadata-loader.md](./04-metadata-loader.md) (next)
