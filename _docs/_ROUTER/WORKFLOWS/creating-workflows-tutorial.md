# Tutorial: Tworzenie Workflow od Podstaw

Kompletny przewodnik krok po kroku do tworzenia własnych workflow YAML.

---

## Spis Treści

1. [Przegląd](#1-przegląd)
2. [Krok 1: Planowanie Workflow](#2-krok-1-planowanie-workflow)
3. [Krok 2: Tworzenie Pliku YAML](#3-krok-2-tworzenie-pliku-yaml)
4. [Krok 3: Definiowanie Kroków](#4-krok-3-definiowanie-kroków)
5. [Krok 4: Dodawanie Warunków](#5-krok-4-dodawanie-warunków)
6. [Krok 5: Dynamiczne Parametry](#6-krok-5-dynamiczne-parametry)
7. [Krok 6: Testowanie](#7-krok-6-testowanie)
8. [Kompletny Przykład](#8-kompletny-przykład)
9. [Najczęstsze Błędy](#9-najczęstsze-błędy)

---

## 1. Przegląd

Workflow to sekwencja operacji Blendera zapisana w pliku YAML/JSON, która wykonuje się automatycznie. Zamiast ręcznie wywoływać 10+ narzędzi, użytkownik mówi "stwórz telefon" i workflow robi resztę.

**Co workflow może zawierać:**
- Sekwencję kroków (tool calls)
- Warunki wykonania kroków (`condition`)
- Dynamiczne parametry (`$CALCULATE`, `$AUTO_*`)
- Triggery (słowa kluczowe, wzorce geometrii)

---

## 2. Krok 1: Planowanie Workflow

### 2.1 Zdefiniuj Cel

Zanim napiszesz kod, odpowiedz:
1. **Co ma powstać?** - np. "telefon z ekranem"
2. **Jakie kroki są potrzebne?** - lista operacji w Blenderze
3. **Co powinno być konfigurowalne?** - rozmiary, proporcje

### 2.2 Przetestuj Ręcznie

Wykonaj workflow ręcznie w Blenderze i zapisz:
- Jakie narzędzia użyłeś
- W jakiej kolejności
- Jakie parametry ustawiłeś

### 2.3 Przykład: Telefon

```
Cel: Telefon z zaokrąglonymi krawędziami i wgłębionym ekranem

Kroki:
1. Stwórz kostkę
2. Przejdź do trybu Edit
3. Zaznacz wszystko
4. Bevel na krawędziach (zaokrąglenie rogów)
5. Zaznacz górną ścianę
6. Inset (ramka ekranu)
7. Extrude w dół (wgłębienie ekranu)
8. Wróć do trybu Object
```

---

## 3. Krok 2: Tworzenie Pliku YAML

### 3.1 Lokalizacja

Utwórz plik w:
```
server/router/application/workflows/custom/moj_workflow.yaml
```

### 3.2 Podstawowa Struktura

```yaml
# moj_workflow.yaml

# === METADANE (wymagane) ===
name: moj_workflow                    # Unikalna nazwa (snake_case)
description: Opis co robi workflow    # Co workflow tworzy

# === METADANE (opcjonalne) ===
category: moja_kategoria              # Kategoria (np. furniture, electronics)
author: Twoje Imię                    # Autor
version: "1.0"                        # Wersja

# === TRIGGERY (opcjonalne) ===
trigger_pattern: box_pattern          # Wzorzec geometrii do wykrycia
trigger_keywords:                     # Słowa kluczowe aktywujące workflow
  - telefon
  - smartphone
  - komórka

# === KROKI (wymagane) ===
steps:
  - tool: nazwa_narzedzia
    params:
      parametr1: wartosc1
    description: Co robi ten krok
```

### 3.3 Nazewnictwo

| Element | Konwencja | Przykład |
|---------|-----------|----------|
| name | snake_case | `phone_workflow` |
| tool | snake_case | `modeling_create_primitive` |
| params | snake_case | `number_cuts` |

---

## 4. Krok 3: Definiowanie Kroków

### 4.1 Struktura Kroku

```yaml
- tool: mesh_bevel              # Nazwa narzędzia (wymagane)
  params:                       # Parametry (wymagane)
    width: 0.05
    segments: 3
  description: Zaokrąglij krawędzie  # Opis (opcjonalne)
  condition: "has_selection"    # Warunek (opcjonalne)
```

### 4.2 Znajdowanie Nazw Narzędzi

Sprawdź `_docs/AVAILABLE_TOOLS_SUMMARY.md` lub użyj:

```bash
grep -r "def " server/adapters/mcp/areas/ | grep "@mcp.tool"
```

### 4.3 Typowe Narzędzia

| Kategoria | Narzędzie | Co robi |
|-----------|-----------|---------|
| **Tworzenie** | `modeling_create_primitive` | Tworzy kostkę, kulę, itp. |
| **Transformacja** | `modeling_transform_object` | Skaluje, przesuwa, obraca |
| **Tryb** | `system_set_mode` | Zmienia tryb (OBJECT/EDIT) |
| **Zaznaczanie** | `mesh_select` | Zaznacza geometrię |
| **Zaznaczanie** | `mesh_select_targeted` | Zaznacza po indeksie |
| **Edycja** | `mesh_bevel` | Zaokrągla krawędzie |
| **Edycja** | `mesh_inset` | Wstawia ścianę w ścianę |
| **Edycja** | `mesh_extrude_region` | Wyciąga geometrię |

### 4.4 Przykład: Pierwsze 3 Kroki Telefonu

```yaml
steps:
  # Krok 1: Stwórz kostkę
  - tool: modeling_create_primitive
    params:
      type: CUBE
    description: Stwórz bazową kostkę

  # Krok 2: Przejdź do trybu Edit
  - tool: system_set_mode
    params:
      mode: EDIT
    description: Wejdź w tryb edycji

  # Krok 3: Zaznacz wszystko
  - tool: mesh_select
    params:
      action: all
    description: Zaznacz całą geometrię
```

---

## 5. Krok 4: Dodawanie Warunków

Warunki (`condition`) pozwalają pomijać kroki, gdy nie są potrzebne.

### 5.1 Po co Warunki?

```yaml
# BEZ warunku - błąd jeśli już w trybie EDIT
- tool: system_set_mode
  params: { mode: EDIT }

# Z warunkiem - pomija jeśli już w EDIT
- tool: system_set_mode
  params: { mode: EDIT }
  condition: "current_mode != 'EDIT'"
```

### 5.2 Składnia Warunków

```yaml
# Porównania stringów
condition: "current_mode == 'EDIT'"
condition: "current_mode != 'OBJECT'"
condition: "active_object == 'Cube'"

# Zmienne boolean
condition: "has_selection"
condition: "not has_selection"

# Porównania liczbowe
condition: "object_count > 0"
condition: "selected_verts >= 4"

# Operatory logiczne
condition: "current_mode == 'EDIT' and has_selection"
condition: "current_mode == 'OBJECT' or not has_selection"
```

### 5.3 Dostępne Zmienne

| Zmienna | Typ | Przykład |
|---------|-----|----------|
| `current_mode` | str | `'OBJECT'`, `'EDIT'`, `'SCULPT'` |
| `has_selection` | bool | `True`, `False` |
| `object_count` | int | `0`, `5`, `10` |
| `selected_verts` | int | `0`, `8`, `100` |
| `selected_edges` | int | `0`, `12` |
| `selected_faces` | int | `0`, `6` |
| `active_object` | str | `'Cube'`, `'Sphere'` |

### 5.4 Symulacja Kontekstu

Router symuluje zmiany kontekstu podczas rozwijania workflow:

```yaml
steps:
  # Krok 1: Zmień tryb (wykona się)
  - tool: system_set_mode
    params: { mode: EDIT }
    condition: "current_mode != 'EDIT'"

  # Krok 2: Zaznacz (wykona się)
  - tool: mesh_select
    params: { action: all }
    condition: "not has_selection"

  # Krok 3: Kolejna zmiana trybu (POMINIE - symulacja mówi, że już EDIT)
  - tool: system_set_mode
    params: { mode: EDIT }
    condition: "current_mode != 'EDIT'"
```

---

## 6. Krok 5: Dynamiczne Parametry

### 6.1 Problem ze Statycznymi Wartościami

```yaml
# ŹLE - 0.05 działa dla 1m kostki, ale nie dla 10m lub 1cm
params:
  width: 0.05
```

### 6.2 Rozwiązanie 1: $CALCULATE

Oblicz wartość matematycznie:

```yaml
params:
  # 5% najmniejszego wymiaru
  width: "$CALCULATE(min_dim * 0.05)"

  # Średnia szerokości i wysokości
  size: "$CALCULATE((width + height) / 2)"

  # Zaokrąglone
  count: "$CALCULATE(round(depth * 10))"
```

**Dostępne zmienne:**
- `width`, `height`, `depth` - wymiary obiektu
- `min_dim`, `max_dim` - min/max wymiarów

**Dostępne funkcje:**
- `min()`, `max()`, `abs()`
- `round()`, `floor()`, `ceil()`
- `sqrt()`

### 6.3 Rozwiązanie 2: $AUTO_*

Gotowe predefiniowane wartości:

```yaml
params:
  # Automatyczny bevel (5% min wymiaru)
  width: "$AUTO_BEVEL"

  # Automatyczny inset (3% min XY)
  thickness: "$AUTO_INSET"

  # Automatyczne wgłębienie (10% głębokości w dół)
  move: [0, 0, "$AUTO_EXTRUDE_NEG"]
```

**Pełna lista $AUTO_*:**

| Parametr | Wzór | Opis |
|----------|------|------|
| `$AUTO_BEVEL` | `min * 5%` | Standardowy bevel |
| `$AUTO_BEVEL_SMALL` | `min * 2%` | Mały bevel |
| `$AUTO_BEVEL_LARGE` | `min * 10%` | Duży bevel |
| `$AUTO_INSET` | `XY_min * 3%` | Standardowy inset |
| `$AUTO_INSET_THICK` | `XY_min * 5%` | Gruby inset |
| `$AUTO_EXTRUDE` | `Z * 10%` | Extrude w górę |
| `$AUTO_EXTRUDE_NEG` | `Z * -10%` | Extrude w dół |
| `$AUTO_EXTRUDE_DEEP` | `Z * 20%` | Głęboki extrude |
| `$AUTO_SCREEN_DEPTH` | `Z * 50%` | Głębokość ekranu |
| `$AUTO_SCREEN_DEPTH_NEG` | `Z * -50%` | Wgłębienie ekranu |
| `$AUTO_SCALE_SMALL` | `[80%, 80%, 80%]` | Zmniejsz do 80% |

### 6.4 Rozwiązanie 3: Proste Zmienne

Odwołanie do wartości z kontekstu:

```yaml
params:
  depth: "$depth"      # Głębokość obiektu
  mode: "$mode"        # Aktualny tryb
```

### 6.5 Kolejność Rozwiązywania

1. `$CALCULATE(...)` - najpierw wyrażenia matematyczne
2. `$AUTO_*` - potem predefiniowane wartości
3. `$zmienna` - na końcu proste zmienne

---

## 7. Krok 6: Testowanie

### 7.1 Walidacja Składni YAML

```bash
# Sprawdź składnię YAML
python -c "import yaml; yaml.safe_load(open('server/router/application/workflows/custom/moj_workflow.yaml'))"
```

### 7.2 Test Ładowania

```python
from server.router.application.workflows.registry import WorkflowRegistry

registry = WorkflowRegistry()
registry.load_custom_workflows()

# Sprawdź czy workflow się załadował
print(registry.get_all_workflows())

# Pobierz definicję
definition = registry.get_definition("moj_workflow")
print(definition)
```

### 7.3 Test Rozwijania

```python
# Rozwiń workflow z kontekstem
calls = registry.expand_workflow(
    "moj_workflow",
    context={
        "dimensions": [2.0, 4.0, 0.5],
        "mode": "OBJECT",
        "has_selection": False,
    }
)

# Sprawdź wynik
for call in calls:
    print(f"{call.tool_name}: {call.params}")
```

### 7.4 Test Triggerów

```python
# Test dopasowania słów kluczowych
workflow = registry.find_by_keywords("stwórz telefon")
print(f"Znaleziono: {workflow}")
```

---

## 8. Kompletny Przykład

### 8.1 Workflow: Telefon z Ekranem

```yaml
# server/router/application/workflows/custom/phone_complete.yaml

name: phone_complete
description: Telefon z zaokrąglonymi rogami i wgłębionym ekranem
category: electronics
author: BlenderAI
version: "2.0"

trigger_keywords:
  - telefon
  - smartphone
  - komórka
  - iphone
  - android

steps:
  # === FAZA 1: Tworzenie bazowej geometrii ===

  - tool: modeling_create_primitive
    params:
      type: CUBE
    description: Stwórz bazową kostkę dla telefonu

  # === FAZA 2: Przejście do trybu Edit ===

  - tool: system_set_mode
    params:
      mode: EDIT
    description: Wejdź w tryb edycji
    condition: "current_mode != 'EDIT'"

  # === FAZA 3: Zaznaczanie i edycja ===

  - tool: mesh_select
    params:
      action: all
    description: Zaznacz całą geometrię
    condition: "not has_selection"

  - tool: mesh_bevel
    params:
      width: "$AUTO_BEVEL"
      segments: 3
    description: Zaokrąglij wszystkie krawędzie

  # === FAZA 4: Tworzenie ekranu ===

  - tool: mesh_select
    params:
      action: none
    description: Odznacz wszystko

  - tool: mesh_select_targeted
    params:
      mode: FACE
      indices: [5]
    description: Zaznacz górną ścianę (ekran)

  - tool: mesh_inset
    params:
      thickness: "$AUTO_INSET"
    description: Stwórz ramkę ekranu

  - tool: mesh_extrude_region
    params:
      move:
        - 0
        - 0
        - "$AUTO_SCREEN_DEPTH_NEG"
    description: Wgłęb ekran

  # === FAZA 5: Finalizacja ===

  - tool: system_set_mode
    params:
      mode: OBJECT
    description: Wróć do trybu Object
    condition: "current_mode != 'OBJECT'"
```

### 8.2 Test Workflow

```python
from server.router.application.workflows.registry import WorkflowRegistry

registry = WorkflowRegistry()
registry.load_custom_workflows()

# Rozwiń z wymiarami telefonu (7cm x 15cm x 8mm)
calls = registry.expand_workflow(
    "phone_complete",
    context={
        "dimensions": [0.07, 0.15, 0.008],
        "mode": "OBJECT",
        "has_selection": False,
    }
)

print(f"Workflow rozwinięty do {len(calls)} kroków:")
for i, call in enumerate(calls, 1):
    print(f"  {i}. {call.tool_name}")
    for k, v in call.params.items():
        print(f"      {k}: {v}")
```

**Oczekiwany wynik:**
```
Workflow rozwinięty do 9 kroków:
  1. modeling_create_primitive
      type: CUBE
  2. system_set_mode
      mode: EDIT
  3. mesh_select
      action: all
  4. mesh_bevel
      width: 0.0004  # 5% z 8mm
      segments: 3
  5. mesh_select
      action: none
  6. mesh_select_targeted
      mode: FACE
      indices: [5]
  7. mesh_inset
      thickness: 0.0021  # 3% z 7cm
  8. mesh_extrude_region
      move: [0, 0, -0.004]  # 50% z 8mm w dół
  9. system_set_mode
      mode: OBJECT
```

---

## 9. Najczęstsze Błędy

### 9.1 Błędy Składni YAML

```yaml
# ŹLE - brak spacji po dwukropku
params:
  width:0.05

# DOBRZE
params:
  width: 0.05
```

```yaml
# ŹLE - nieprawidłowe wcięcie
steps:
- tool: mesh_bevel
params:
  width: 0.05

# DOBRZE
steps:
  - tool: mesh_bevel
    params:
      width: 0.05
```

### 9.2 Błędy Warunków

```yaml
# ŹLE - brak cudzysłowów w stringu
condition: current_mode != EDIT

# DOBRZE
condition: "current_mode != 'EDIT'"
```

```yaml
# ŹLE - literówka w nazwie zmiennej
condition: "curent_mode != 'EDIT'"

# DOBRZE
condition: "current_mode != 'EDIT'"
```

### 9.3 Błędy $CALCULATE

```yaml
# ŹLE - brak zamknięcia nawiasu
width: "$CALCULATE(min_dim * 0.05"

# DOBRZE
width: "$CALCULATE(min_dim * 0.05)"
```

```yaml
# ŹLE - nieistniejąca zmienna
width: "$CALCULATE(szerokość * 0.05)"

# DOBRZE (użyj angielskich nazw)
width: "$CALCULATE(width * 0.05)"
```

### 9.4 Błędy Logiczne

```yaml
# ŹLE - extrude bez zaznaczenia
- tool: mesh_extrude_region
  params:
    move: [0, 0, 1]

# DOBRZE - najpierw zaznacz
- tool: mesh_select
  params:
    action: all
  condition: "not has_selection"

- tool: mesh_extrude_region
  params:
    move: [0, 0, 1]
```

---

## Podsumowanie

1. **Zaplanuj** - przetestuj ręcznie, zapisz kroki
2. **Utwórz plik** - w `workflows/custom/nazwa.yaml`
3. **Dodaj metadane** - name, description, trigger_keywords
4. **Zdefiniuj kroki** - tool, params, description
5. **Dodaj warunki** - `condition` dla odporności
6. **Użyj dynamicznych parametrów** - `$AUTO_*` lub `$CALCULATE`
7. **Przetestuj** - sprawdź ładowanie i rozwijanie

**Zobacz też:**
- [yaml-workflow-guide.md](./yaml-workflow-guide.md) - Pełna dokumentacja składni
- [expression-reference.md](./expression-reference.md) - Referencja wyrażeń
