# TASK-051: Confidence-Based Workflow Adaptation

| Status | Priority | Complexity |
|--------|----------|------------|
| 🚧 In Progress | 🔴 High | Medium |

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
Nowy engine (~120 linii):
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
1. `base.py` - dodaj pola do WorkflowStep
2. `workflow_loader.py` - parsuj nowe pola
3. `picnic_table.yaml` - oznacz optional steps
4. `semantic_workflow_matcher.py` - użyj find_best_match_with_confidence
5. `workflow_adapter.py` - nowy engine
6. `config.py` - nowe opcje
7. `router.py` - integracja adaptera
8. Testy

### Oczekiwany rezultat
```
"create a picnic table" → HIGH (0.92) → 49 kroków (pełny workflow)
"simple table with 4 legs" → LOW (0.72) → ~28 kroków (bez ławek)
"table with benches" → MEDIUM (0.78) → ~40 kroków (core + bench)
```

---

## Testy do dodania/aktualizacji

### Nowe testy jednostkowe

| Plik | Opis |
|------|------|
| `tests/unit/router/application/engines/test_workflow_adapter.py` | **NOWY** - testy WorkflowAdapter |

**Testy dla `test_workflow_adapter.py`:**
```python
- test_high_confidence_returns_all_steps()
- test_low_confidence_skips_all_optional()
- test_none_confidence_skips_all_optional()
- test_medium_confidence_filters_by_tags()
- test_medium_confidence_uses_semantic_fallback()
- test_simple_table_prompt_skips_benches()
- test_table_with_benches_includes_bench_steps()
- test_empty_optional_steps_returns_core_only()
- test_adaptation_result_contains_skipped_info()
```

### Aktualizacja istniejących testów

| Plik | Zmiany |
|------|--------|
| `tests/unit/router/application/matcher/test_semantic_workflow_matcher.py` | Dodaj testy dla `confidence_level` i `requires_adaptation` w `MatchResult` |
| `tests/unit/router/application/test_supervisor_router.py` | Dodaj test integracji adaptera w `_expand_triggered_workflow()` |
| `tests/unit/router/application/workflows/test_workflow_definition.py` | Dodaj testy dla pól `optional` i `tags` w `WorkflowStep` |
| `tests/unit/router/infrastructure/test_workflow_loader.py` | Dodaj testy parsowania `optional` i `tags` z YAML |

---

## Dokumentacja do aktualizacji

### Router Documentation

| Plik | Zmiany |
|------|--------|
| `_docs/_ROUTER/README.md` | Dodaj sekcję "Workflow Adaptation" do listy komponentów |
| `_docs/_ROUTER/IMPLEMENTATION/README.md` | Dodaj `33-workflow-adapter.md` do listy |
| `_docs/_ROUTER/IMPLEMENTATION/33-workflow-adapter.md` | **NOWY** - dokumentacja WorkflowAdapter |
| `_docs/_ROUTER/IMPLEMENTATION/12-workflow-expansion-engine.md` | Zaktualizuj o integrację z adapterem |
| `_docs/_ROUTER/IMPLEMENTATION/28-workflow-intent-classifier.md` | Zaktualizuj - metoda `find_best_match_with_confidence()` teraz używana |
| `_docs/_ROUTER/IMPLEMENTATION/29-semantic-workflow-matcher.md` | Zaktualizuj - nowe pola w MatchResult |

### Workflow Documentation

| Plik | Zmiany |
|------|--------|
| `_docs/_ROUTER/WORKFLOWS/README.md` | Dodaj sekcję o `optional` i `tags` w definicjach workflow |
| `_docs/_ROUTER/WORKFLOWS/picnic-table-workflow.md` | Zaktualizuj z informacją o optional steps |

### Changelog

| Plik | Zmiany |
|------|--------|
| `_docs/_CHANGELOG/README.md` | Dodaj wpis dla TASK-051 |
| `_docs/_CHANGELOG/51-YYYY-MM-DD-confidence-workflow-adaptation.md` | **NOWY** - changelog entry |

---

## Checklist

- [ ] 1. `base.py` - dodaj pola `optional` i `tags` do WorkflowStep
- [ ] 2. `workflow_loader.py` - parsuj nowe pola z YAML
- [ ] 3. `picnic_table.yaml` - oznacz 16 bench steps jako optional
- [ ] 4. `semantic_workflow_matcher.py` - użyj `find_best_match_with_confidence()`
- [ ] 5. `workflow_adapter.py` - nowy engine
- [ ] 6. `config.py` - nowe opcje konfiguracyjne
- [ ] 7. `router.py` - integracja adaptera
- [ ] 8. Testy jednostkowe
- [ ] 9. Dokumentacja
- [ ] 10. Rebuild Docker image
