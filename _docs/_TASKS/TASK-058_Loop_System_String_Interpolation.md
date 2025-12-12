# TASK-058: Loop System & String Interpolation for Workflows

## Overview

Rozszerzenie systemu workflow o **loop parameter** i **string interpolation** aby upraszczać złożone YAML definicje (jak `simple_table.yaml` z 15 powtarzającymi się plankami).

## Architektura Obecnie

### Pipeline Przetwarzania Workflow

```
YAML File
    ↓
WorkflowLoader._parse_step()          # Parsuje YAML → WorkflowStep
    ↓
WorkflowRegistry.expand_workflow()    # Główna metoda ekspansji
    ├── _build_variables()            # defaults + modifiers
    ├── resolve_computed_parameters() # TASK-056-5 (computed params)
    ├── _resolve_definition_params()  # $variable, $CALCULATE substitution
    └── _steps_to_calls()             # Walidacja condition, → CorrectedToolCall[]
```

### Kluczowe Pliki

| Plik | Rola |
|------|------|
| `base.py` | `WorkflowStep` dataclass (pola: tool, params, condition, loop?) |
| `workflow_loader.py:300-350` | `_parse_step()` - parsowanie YAML → WorkflowStep |
| `expression_evaluator.py` | `$CALCULATE`, 13 funkcji math, context variables |
| `registry.py:202-297` | `expand_workflow()` - główna ekspansja |
| `registry.py:539-578` | `_resolve_definition_params()` - substitution |
| `workflow_adapter.py` | Filtrowanie optional steps |

---

## Propozycja Implementacji

### FAZA 1: Loop Expansion (P0 - Critical)

#### 1.1 Nowy `loop` Parameter w WorkflowStep

**Plik**: `server/router/application/workflows/base.py`

```python
@dataclass
class WorkflowStep:
    # ... existing fields ...

    # TASK-057: Loop parameter for step repetition
    loop: Optional[Dict[str, Any]] = None  # NEW
```

**Loop Schema**:
```yaml
loop:
  variable: "i"                    # Loop variable name
  range: "1..plank_count"          # Range expression (computed at runtime)
  # LUB:
  range: [1, 15]                   # Static range [start, end]
```

#### 1.2 LoopExpander w workflow_loader.py

**Plik**: `server/router/infrastructure/workflow_loader.py`

Nowa klasa/metoda do ekspansji loop steps:

```python
class LoopExpander:
    """Expands loop steps into multiple concrete steps."""

    def __init__(self, evaluator: ExpressionEvaluator):
        self._evaluator = evaluator

    def expand_loops(
        self,
        steps: List[WorkflowStep],
        context: Dict[str, Any]
    ) -> List[WorkflowStep]:
        """Expand all loop steps into concrete steps."""
        expanded = []
        for step in steps:
            if step.loop:
                expanded.extend(self._expand_single_loop(step, context))
            else:
                expanded.append(step)
        return expanded

    def _expand_single_loop(
        self,
        step: WorkflowStep,
        context: Dict[str, Any]
    ) -> List[WorkflowStep]:
        """Expand single loop step."""
        loop_config = step.loop
        var_name = loop_config["variable"]

        # Resolve range
        range_spec = loop_config["range"]
        if isinstance(range_spec, str):
            # "1..plank_count" or "0..15"
            start, end = self._parse_range_expression(range_spec, context)
        else:
            # [1, 15]
            start, end = range_spec[0], range_spec[1]

        # Generate steps
        expanded = []
        for i in range(int(start), int(end) + 1):
            # Clone step with loop variable injected
            loop_context = {**context, var_name: i}
            new_step = self._clone_step_with_context(step, loop_context, var_name, i)
            expanded.append(new_step)

        return expanded
```

#### 1.3 String Interpolation: `$FORMAT(...)`

**Plik**: `server/router/application/evaluator/expression_evaluator.py`

Dodać nowy pattern i metodę:

```python
# New pattern
FORMAT_PATTERN = re.compile(r"^\$FORMAT\((.+)\)$")

def resolve_format(self, template: str) -> str:
    """Resolve $FORMAT(Plank_{i}) to concrete string."""
    match = self.FORMAT_PATTERN.match(template)
    if not match:
        return template

    format_str = match.group(1)
    # Replace {var} with context values
    result = format_str
    for var_name, value in self._context.items():
        result = result.replace(f"{{{var_name}}}", str(value))

    return result
```

#### 1.4 Integracja w WorkflowRegistry

**Plik**: `server/router/application/workflows/registry.py`

W `expand_workflow()` przed `_steps_to_calls()`:

```python
def expand_workflow(self, ...):
    # ... existing code ...

    # TASK-057: Expand loop steps BEFORE other processing
    if definition:
        loop_expander = LoopExpander(self._evaluator)
        expanded_steps = loop_expander.expand_loops(
            definition.steps,
            all_params  # Contains plank_count, etc.
        )
        steps = self._resolve_definition_params(expanded_steps, all_params)
        return self._steps_to_calls(steps, workflow_name, workflow_params=all_params)
```

---

### FAZA 2: Conditional Functions (P1 - High)

#### 2.1 Piecewise Expression w $CALCULATE

Rozszerzyć `expression_evaluator.py` o obsługę `if...else`:

```python
# Expression: "0.10 if i <= plank_full_count else plank_remainder_width"
def _eval_node(self, node: ast.AST) -> float:
    # ... existing cases ...

    # NEW: IfExp (ternary)
    if isinstance(node, ast.IfExp):
        test = self._eval_node(node.test)
        if test:
            return self._eval_node(node.body)
        else:
            return self._eval_node(node.orelse)

    # NEW: Compare (for boolean expressions in IfExp)
    if isinstance(node, ast.Compare):
        left = self._eval_node(node.left)
        for op, comparator in zip(node.ops, node.comparators):
            right = self._eval_node(comparator)
            if not self._compare(left, op, right):
                return 0.0  # False
            left = right
        return 1.0  # True
```

---

### FAZA 3: Nested Loops (P2 - Medium)

Dla 2D grids (telefon z przyciskami 3x4):

```yaml
loop:
  variables: ["row", "col"]
  ranges: ["0..3", "0..4"]
```

---

## Przykład Po Implementacji

### simple_table.yaml (BEFORE - 200+ linii)

```yaml
steps:
  # Plank 1
  - tool: modeling_create_primitive
    params:
      name: "TablePlank_1"
  - tool: modeling_transform_object
    params:
      name: "TablePlank_1"
      location: ["$CALCULATE(-table_width/2 + plank_actual_width * 0.5)", ...]

  # Plank 2 (condition: plank_count >= 2)
  - tool: modeling_create_primitive
    params:
      name: "TablePlank_2"
    condition: "plank_count >= 2"
  # ... repeat for 15 planks ...
```

### simple_table.yaml (AFTER - ~30 linii)

```yaml
steps:
  # All planks via loop
  - tool: modeling_create_primitive
    params:
      name: "$FORMAT(TablePlank_{i})"
    loop:
      variable: "i"
      range: "1..plank_count"
    description: "Create table plank {i}"

  - tool: modeling_transform_object
    params:
      name: "$FORMAT(TablePlank_{i})"
      scale: ["$CALCULATE(plank_actual_width / 2)", "$CALCULATE(table_length / 2)", 0.0114]
      location: ["$CALCULATE(-table_width/2 + plank_actual_width * (i - 0.5))", 0, "$CALCULATE(leg_length + 0.0114)"]
    loop:
      variable: "i"
      range: "1..plank_count"
    description: "Position plank {i}"
```

---

## Pliki Do Modyfikacji

### Faza 1 (Loop + String Interpolation)

| Plik | Zmiana | Priorytet |
|------|--------|-----------|
| `base.py:18-58` | Dodać `loop: Optional[Dict]` do WorkflowStep | P0 |
| `workflow_loader.py` | Dodać obsługę `loop` w `_parse_step()` | P0 |
| `workflow_loader.py` | NOWY: `LoopExpander` class | P0 |
| `expression_evaluator.py` | Dodać `$FORMAT()` pattern i metodę | P0 |
| `registry.py:202-297` | Integracja `LoopExpander` w `expand_workflow()` | P0 |
| `simple_table.yaml` | Przepisać na loop syntax | P0 |

### Faza 2 (Conditional Functions)

| Plik | Zmiana | Priorytet |
|------|--------|-----------|
| `expression_evaluator.py:262-336` | Dodać `ast.IfExp` i `ast.Compare` w `_eval_node()` | P1 |

---

## Testy

### Unit Tests

```
tests/unit/router/infrastructure/test_loop_expander.py
- test_expand_static_range
- test_expand_computed_range
- test_format_string_interpolation
- test_nested_loops (FAZA 3)
```

### E2E Tests

```
tests/e2e/router/test_simple_table_with_loops.py
- test_table_with_8_planks_via_loop
- test_table_width_0_73m_fractional_planks
```

---

## Kolejność Implementacji

1. **WorkflowStep.loop field** - base.py
2. **Loop loading** - workflow_loader.py `_parse_step()`
3. **LoopExpander class** - workflow_loader.py (new)
4. **$FORMAT pattern** - expression_evaluator.py
5. **Integration** - registry.py `expand_workflow()`
6. **Tests** - unit + e2e
7. **simple_table.yaml refactor** - use loop syntax
8. **Documentation** - TASK-057 doc update

---

## Decyzje (Bez Pytań - Implementacja Domyślna)

1. **Loop range syntax**: `"1..plank_count"` - spójna z innymi DSL, czytelna
2. **String interpolation**: `$FORMAT(Plank_{i})` - spójna z istniejącym `$CALCULATE()`
3. **Nested loops**: FAZA 1 tylko - podstawowe pętle, rozszerzenie w przyszłości jeśli potrzebne

---

## Kolejność Implementacji (Szczegółowa)

### Krok 1: WorkflowStep.loop field
**Plik**: `server/router/application/workflows/base.py`
```python
@dataclass
class WorkflowStep:
    # ... existing fields ...
    loop: Optional[Dict[str, Any]] = None  # TASK-058: Loop parameter
```

### Krok 2: Loop parsing w workflow_loader.py
**Plik**: `server/router/infrastructure/workflow_loader.py`
- Metoda `_parse_step()` już automatycznie obsłuży nowe pole dzięki TASK-055-FIX-6
- Weryfikacja: pole `loop` będzie parsowane z YAML automatycznie

### Krok 3: LoopExpander class
**Plik**: `server/router/infrastructure/loop_expander.py` (NEW FILE)
```python
class LoopExpander:
    def __init__(self, evaluator: ExpressionEvaluator):
        self._evaluator = evaluator

    def expand_loops(self, steps: List[WorkflowStep], context: Dict) -> List[WorkflowStep]:
        # Expand all loop steps

    def _expand_single_loop(self, step: WorkflowStep, context: Dict) -> List[WorkflowStep]:
        # Parse range, generate steps with loop variable

    def _parse_range_expression(self, range_spec: str, context: Dict) -> Tuple[int, int]:
        # Handle "1..plank_count" or "1..15"
```

### Krok 4: $FORMAT pattern w expression_evaluator.py
**Plik**: `server/router/application/evaluator/expression_evaluator.py`
```python
FORMAT_PATTERN = re.compile(r"^\$FORMAT\((.+)\)$")

def resolve_format(self, template: str, context: Dict) -> str:
    """Resolve $FORMAT(Plank_{i}) with context variables."""
```

### Krok 5: Integracja w registry.py
**Plik**: `server/router/application/workflows/registry.py`
- W `expand_workflow()` dodać `LoopExpander.expand_loops()` PRZED `_steps_to_calls()`

### Krok 6: Unit Tests
**Plik**: `tests/unit/router/infrastructure/test_loop_expander.py` (NEW FILE)
- test_expand_static_range
- test_expand_computed_range
- test_format_string_interpolation
- test_no_loop_passthrough

### Krok 7: Refaktor simple_table.yaml
**Plik**: `server/router/application/workflows/custom/simple_table.yaml`
- Zastąpić 15 powtarzających się kroków jednym krokiem z `loop`

### Krok 8: Dokumentacja TASK-058
**Plik**: `_docs/_TASKS/TASK-058_Loop_System_String_Interpolation.md` (NEW FILE)

---

## Szacowany Czas Implementacji

| Krok | Czas |
|------|------|
| WorkflowStep.loop | 5 min |
| Loop parsing | 0 min (automatyczne) |
| LoopExpander class | 30 min |
| $FORMAT pattern | 15 min |
| Registry integration | 10 min |
| Unit tests | 20 min |
| simple_table.yaml refaktor | 15 min |
| Dokumentacja | 10 min |
| **TOTAL** | ~2h |
