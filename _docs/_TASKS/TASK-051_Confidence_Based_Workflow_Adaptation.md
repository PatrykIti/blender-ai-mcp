# TASK-051: Confidence-Based Workflow Adaptation

| Status | Priority | Complexity | Completion Date |
|--------|----------|------------|-----------------|
| ✅ Done | 🔴 High | Medium | 2025-12-07 |

---

## Problem
Router ma zbudowane komponenty (confidence levels, `find_best_match_with_confidence()`, feedback learning), ale **nie są połączone**:
1. `find_best_match_with_confidence()` istnieje ale nigdy nie jest wywoływane
2. Confidence levels (HIGH≥0.90, MEDIUM≥0.75, LOW≥0.60) zdefiniowane ale nieużywane
3. "simple table with 4 legs" → wykonuje PEŁNY picnic_table_workflow z ławkami
4. Feedback learning zbiera dane ale ich nie używa

## Rozwiązanie: Workflow Adaptation Engine

### Koncepcja
```
Confidence Level → Adaptation Strategy
─────────────────────────────────────────
HIGH (≥0.90)   → Wykonaj WSZYSTKIE kroki
MEDIUM (≥0.75) → Core + semantycznie pasujące optional
LOW (≥0.60)    → Tylko CORE steps (skip optional)
NONE (<0.60)   → Tylko CORE steps (fallback)
```

### Zmiany w plikach

#### 1. `server/router/application/workflows/base.py`
Dodaj pola `optional` i `tags` do `WorkflowStep`:
```python
@dataclass
class WorkflowStep:
    tool: str
    params: Dict[str, Any]
    description: Optional[str] = None
    condition: Optional[str] = None
    optional: bool = False  # NEW
    tags: List[str] = field(default_factory=list)  # NEW
```

#### 2. `server/router/infrastructure/workflow_loader.py`
Update `_parse_step()` aby parsować nowe pola z YAML.

#### 3. `server/router/application/workflows/custom/picnic_table.yaml`
Oznacz 16 kroków bench-related jako `optional: true, tags: ["bench", "seating"]`:
- BenchLeft_Inner/Outer (4 kroki)
- BenchRight_Inner/Outer (4 kroki)
- BenchBack_Inner/Outer (4 kroki)
- BenchFront_Inner/Outer (4 kroki)

#### 4. `server/router/application/matcher/semantic_workflow_matcher.py`
Update `MatchResult` dataclass:
```python
@dataclass
class MatchResult:
    # ... existing ...
    confidence_level: str = "NONE"  # NEW
    requires_adaptation: bool = False  # NEW
```

W `match()` zamień `find_best_match()` na `find_best_match_with_confidence()`.

#### 5. NEW: `server/router/application/engines/workflow_adapter.py`
Nowy engine (~230 linii):
```python
class WorkflowAdapter:
    def adapt(
        self,
        definition: WorkflowDefinition,
        confidence_level: str,
        user_prompt: str,
    ) -> Tuple[List[WorkflowStep], AdaptationResult]:
        if confidence_level == "HIGH":
            return all_steps

        core_steps = [s for s in steps if not s.optional]
        optional_steps = [s for s in steps if s.optional]

        if confidence_level in ("LOW", "NONE"):
            return core_steps  # Skip all optional

        if confidence_level == "MEDIUM":
            relevant = self._filter_by_relevance(optional_steps, user_prompt)
            return core_steps + relevant

    def _filter_by_relevance(self, steps, prompt) -> List[WorkflowStep]:
        """Fallback: najpierw tag matching, potem semantic similarity."""
        relevant = []
        for step in steps:
            # 1. Tag matching (szybkie)
            if step.tags and any(tag.lower() in prompt.lower() for tag in step.tags):
                relevant.append(step)
                continue
            # 2. Semantic similarity (fallback dla kroków bez tagów)
            if step.description and self._classifier:
                sim = self._classifier.similarity(prompt, step.description)
                if sim >= self._semantic_threshold:
                    relevant.append(step)
        return relevant
```

#### 6. `server/router/application/router.py`
W `_expand_triggered_workflow()` dodaj:
```python
if self.config.enable_workflow_adaptation and match_result.requires_adaptation:
    adapted_steps, result = self._workflow_adapter.adapt(
        definition, confidence_level, user_prompt
    )
```

#### 7. `server/router/infrastructure/config.py`
```python
enable_workflow_adaptation: bool = True
adaptation_semantic_threshold: float = 0.6
```

### Kolejność implementacji
1. ✅ `base.py` - dodaj pola do WorkflowStep
2. ✅ `workflow_loader.py` - parsuj nowe pola
3. ✅ `picnic_table.yaml` - oznacz optional steps
4. ✅ `semantic_workflow_matcher.py` - użyj find_best_match_with_confidence
5. ✅ `workflow_adapter.py` - nowy engine
6. ✅ `config.py` - nowe opcje
7. ✅ `router.py` - integracja adaptera
8. ✅ Testy
9. ✅ Dokumentacja
10. ✅ Rebuild Docker image

### Oczekiwany rezultat
```
"create a picnic table" → HIGH (0.92) → 49 kroków (pełny workflow)
"simple table with 4 legs" → LOW (0.72) → ~33 kroków (bez ławek)
"table with benches" → MEDIUM (0.78) → ~40 kroków (core + bench)
```

---

## Implementacja

### Nowe pliki
- `server/router/application/engines/workflow_adapter.py` (~230 linii)
- `tests/unit/router/application/test_workflow_adapter.py` (~450 linii, 20 testów)

### Zmodyfikowane pliki
- `server/router/application/workflows/base.py`
- `server/router/infrastructure/workflow_loader.py`
- `server/router/application/workflows/custom/picnic_table.yaml`
- `server/router/application/matcher/semantic_workflow_matcher.py`
- `server/router/infrastructure/config.py`
- `server/router/application/router.py`
- `server/router/application/engines/__init__.py`
- `tests/unit/router/application/matcher/test_semantic_workflow_matcher.py`

---

## Testy

### Nowe testy jednostkowe

| Plik | Opis |
|------|------|
| `tests/unit/router/application/test_workflow_adapter.py` | **NOWY** - 20 testów WorkflowAdapter |

**Testy zaimplementowane:**
```python
- test_high_confidence_returns_all_steps() ✅
- test_high_confidence_result_metadata() ✅
- test_low_confidence_skips_all_optional() ✅
- test_low_confidence_preserves_core_steps() ✅
- test_none_confidence_skips_all_optional() ✅
- test_medium_confidence_filters_by_tags() ✅
- test_medium_confidence_without_matching_tags() ✅
- test_medium_confidence_partial_tag_match() ✅
- test_simple_table_prompt_skips_benches() ✅
- test_table_with_benches_includes_bench_steps() ✅
- test_empty_optional_steps_returns_core_only() ✅
- test_all_optional_steps_workflow() ✅
- test_adaptation_result_to_dict() ✅
- test_adaptation_result_contains_skipped_info() ✅
- test_should_adapt_returns_false_for_high() ✅
- test_should_adapt_returns_true_for_low_with_optional() ✅
- test_should_adapt_returns_false_without_optional() ✅
- test_semantic_fallback_when_no_tags() ✅
- test_semantic_fallback_below_threshold() ✅
- test_get_info_returns_config() ✅
```

### Aktualizacja istniejących testów

| Plik | Zmiany |
|------|--------|
| `tests/unit/router/application/matcher/test_semantic_workflow_matcher.py` | Zaktualizowano testy dla `find_best_match_with_confidence()` |

---

## Dokumentacja

### Router Documentation

| Plik | Zmiany |
|------|--------|
| `_docs/_ROUTER/README.md` | Dodano sekcję "WorkflowAdapter" do listy komponentów |
| `_docs/_ROUTER/IMPLEMENTATION/README.md` | Dodano `32-workflow-adapter.md` do listy |
| `_docs/_ROUTER/IMPLEMENTATION/32-workflow-adapter.md` | **NOWY** - dokumentacja WorkflowAdapter |

### Workflow Documentation

| Plik | Zmiany |
|------|--------|
| `_docs/_ROUTER/WORKFLOWS/README.md` | Dodano sekcję o `optional` i `tags` w definicjach workflow |
| `_docs/_ROUTER/WORKFLOWS/creating-workflows-tutorial.md` | Dodano sekcję o optional steps i adaptacji |

### Changelog

| Plik | Zmiany |
|------|--------|
| `_docs/_CHANGELOG/README.md` | Dodano wpis dla TASK-051 |
| `_docs/_CHANGELOG/97-2025-12-07-confidence-based-workflow-adaptation.md` | **NOWY** - changelog entry |

---

## Checklist

- [x] 1. `base.py` - dodaj pola `optional` i `tags` do WorkflowStep
- [x] 2. `workflow_loader.py` - parsuj nowe pola z YAML
- [x] 3. `picnic_table.yaml` - oznacz 16 bench steps jako optional
- [x] 4. `semantic_workflow_matcher.py` - użyj `find_best_match_with_confidence()`
- [x] 5. `workflow_adapter.py` - nowy engine
- [x] 6. `config.py` - nowe opcje konfiguracyjne
- [x] 7. `router.py` - integracja adaptera
- [x] 8. Testy jednostkowe
- [x] 9. Dokumentacja
- [x] 10. Rebuild Docker image

---

## See Also

- [Changelog #97](../_CHANGELOG/97-2025-12-07-confidence-based-workflow-adaptation.md)
- [WorkflowAdapter Implementation](../_ROUTER/IMPLEMENTATION/32-workflow-adapter.md)
