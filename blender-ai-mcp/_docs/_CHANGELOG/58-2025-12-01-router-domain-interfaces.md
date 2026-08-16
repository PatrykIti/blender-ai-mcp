# Changelog: Router Domain Interfaces

**Date:** 2025-12-01
**Task:** TASK-039-3
**Type:** Feature

---

## Summary

Defined abstract interfaces for all Router Supervisor components following the Dependency Inversion Principle.

---

## New Files

| File | Interface | Purpose |
|------|-----------|---------|
| `i_interceptor.py` | `IToolInterceptor` | Capture LLM tool calls |
| `i_scene_analyzer.py` | `ISceneAnalyzer` | Analyze Blender scene state |
| `i_pattern_detector.py` | `IPatternDetector` | Detect geometry patterns |
| `i_correction_engine.py` | `ICorrectionEngine` | Fix parameters and context |
| `i_override_engine.py` | `IOverrideEngine` | Replace tools with alternatives |
| `i_expansion_engine.py` | `IExpansionEngine` | Expand to workflows |
| `i_firewall.py` | `IFirewall` | Validate operations |
| `i_intent_classifier.py` | `IIntentClassifier` | Classify user intent |

---

## Interface Summary

| Interface | Methods | Purpose |
|-----------|---------|---------|
| `IToolInterceptor` | 4 | intercept, get_history, clear_history, get_session_calls |
| `ISceneAnalyzer` | 5 | analyze, get_cached, invalidate_cache, get_mode, has_selection |
| `IPatternDetector` | 4 | detect, detect_pattern, get_best_match, get_supported_patterns |
| `ICorrectionEngine` | 6 | correct, clamp_parameters, get_required_mode, requires_selection, get_mode_switch_call, get_selection_call |
| `IOverrideEngine` | 4 | check_override, get_override_rules, register_rule, remove_rule |
| `IExpansionEngine` | 5 | expand, get_workflow, register_workflow, get_available_workflows, expand_workflow |
| `IFirewall` | 7 | validate, validate_sequence, can_auto_fix, get_firewall_rules, register_rule, enable_rule, disable_rule |
| `IIntentClassifier` | 6 | predict, predict_top_k, load_tool_embeddings, is_loaded, get_embedding, similarity |

---

## Tests

24 unit tests covering:
- Interface is abstract (ABC)
- Required methods exist
- Interface can be properly implemented

---

## Next Steps

- TASK-039-4: Metadata Loader
- TASK-039-5: Router Configuration
