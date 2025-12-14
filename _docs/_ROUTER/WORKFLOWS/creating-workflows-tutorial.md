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
6b. [Loops i interpolacja stringow (TASK-058)](#6b-loops-i-interpolacja-stringow-task-058)
7. [Krok 6: Opcjonalne Kroki i Adaptacja](#7-krok-6-opcjonalne-kroki-i-adaptacja)
8. [Krok 7: Testowanie](#8-krok-7-testowanie)
9. [Kompletny Przykład](#9-kompletny-przykład)
10. [Najczęstsze Błędy](#10-najczęstsze-błędy)

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
    offset: 0.05
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

# Funkcje matematyczne w warunkach - TASK-060
condition: "floor(table_width / plank_width) > 5"

# Operatory logiczne
condition: "current_mode == 'EDIT' and has_selection"
condition: "current_mode == 'OBJECT' or not has_selection"

# Nawiasy (grupowanie) - TASK-056-2
condition: "(leg_angle > 0.5 and has_selection) or (object_count >= 3)"
condition: "not (leg_style == 'straight' or leg_angle == 0)"
```

### 5.2a Złożone Wyrażenia Logiczne (TASK-056-2)

System warunków wspiera **nawiasy** do grupowania i prawidłową **kolejność operatorów**:

**Kolejność operatorów** (od najwyższego do najniższego priorytetu):
1. `()` - Nawiasy (grupowanie)
2. `not` - Logiczne NIE
3. `and` - Logiczne I
4. `or` - Logiczne LUB

**Przykłady:**

```yaml
# Zagnieżdżone nawiasy
condition: "(leg_angle > 0.5 and has_selection) or (object_count >= 3 and current_mode == 'EDIT')"

# NOT z nawiasami
condition: "not (leg_style == 'straight' or (leg_angle < 0.1 and leg_angle > -0.1))"

# Kolejność bez nawiasów (NOT > AND > OR)
condition: "width > 1.0 and length > 1.0 and height > 0.5 or is_tall"
# Ewaluuje się jako: ((width > 1.0 and length > 1.0) and height > 0.5) or is_tall

# Wiele operacji AND/OR
condition: "A and B or C and D"
# Ewaluuje się jako: (A and B) or (C and D)

# Złożone zagnieżdżone warunki
condition: "((A or B) and (C or D)) or (E and not F)"
```

**Dobre praktyki:**

```yaml
# ✅ DOBRZE - nawiasy dla czytelności
condition: "(leg_angle_left > 0.5) or (leg_angle_left < -0.5)"

# ⚠️ Działa ale mniej czytelne - opiera się na kolejności
condition: "leg_angle_left > 0.5 or leg_angle_left < -0.5"

# ✅ DOBRZE - zagnieżdżone warunki z jasnym grupowaniem
condition: "(current_mode == 'EDIT' and has_selection) or (current_mode == 'OBJECT' and object_count > 0)"
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
  offset: 0.05
```

### 6.2 Rozwiązanie 1: $CALCULATE

Oblicz wartość matematycznie:

```yaml
params:
  # 5% najmniejszego wymiaru
  offset: "$CALCULATE(min_dim * 0.05)"

  # Średnia szerokości i wysokości
  size: "$CALCULATE((width + height) / 2)"

  # Zaokrąglone
  count: "$CALCULATE(round(depth * 10))"
```

**Nowe w TASK-060:** `$CALCULATE(...)` wspiera też operatory porównania, logiczne i wyrażenia ternarne.
Porównania/warunki w `$CALCULATE(...)` zwracają `1.0` (true) / `0.0` (false):

```yaml
params:
  # Flaga liczbowa z warunku
  has_objects: "$CALCULATE(object_count > 0)"

  # Wyrażenie ternarne
  bevel: "$CALCULATE(0.05 if width > 1.0 else 0.02)"

  # Logika + ternary
  detail: "$CALCULATE(2 if (object_count > 0 and has_selection) else 1)"
```

**Dostępne zmienne:**
- `width`, `height`, `depth` - wymiary obiektu
- `min_dim`, `max_dim` - min/max wymiarów
- Wszystkie parametry z `defaults` i `modifiers`

**Dostępne funkcje matematyczne** (TASK-056-1):

| Kategoria | Funkcje | Opis |
|-----------|---------|------|
| **Podstawowe** | `abs()`, `min()`, `max()` | Wartość bezwzględna, minimum, maksimum |
| **Zaokrąglanie** | `round()`, `floor()`, `ceil()`, `trunc()` | Zaokrąglenie, podłoga, sufit, obcięcie |
| **Potęga/Pierwiastek** | `sqrt()`, `pow()`, `**` | Pierwiastek kwadratowy, potęga |
| **Trygonometryczne** | `sin()`, `cos()`, `tan()` | Sinus, cosinus, tangens (radiany) |
| **Odwrotne Tryg.** | `asin()`, `acos()`, `atan()`, `atan2()` | Arcus sinus, arcus cosinus, arcus tangens |
| **Konwersja Kątów** | `degrees()`, `radians()` | Konwersja radiany↔stopnie |
| **Logarytmiczne** | `log()`, `log10()`, `exp()` | Logarytm naturalny, logarytm dziesiętny, e^x |
| **Zaawansowane** | `hypot()` | Przeciwprostokątna: sqrt(x² + y²) |

**Przykłady użycia:**

```yaml
# Obliczenie kąta z wymiarów
rotation: ["$CALCULATE(atan2(height, width))", 0, 0]

# Skalowanie logarytmiczne
scale: "$CALCULATE(log10(100))"  # = 2.0

# Zanik wykładniczy
alpha: "$CALCULATE(exp(-distance / falloff_radius))"

# Przekątna (odległość po skosie)
diagonal: "$CALCULATE(hypot(width, height))"

# Konwersja stopni na radiany
angle_rad: "$CALCULATE(radians(45))"  # = 0.785...

# Tangens dla nachylenia
slope: "$CALCULATE(tan(leg_angle))"
```

### 6.3 Rozwiązanie 2: $AUTO_*

Gotowe predefiniowane wartości:

```yaml
params:
  # Automatyczny bevel (5% min wymiaru)
  offset: "$AUTO_BEVEL"

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
  mode: "$mode"        # Aktualny tryb
  move: [0, 0, "$depth"]  # Z użyciem wymiarów obiektu
```

### 6.5 Kolejność Rozwiązywania

0. `{var}` - interpolacja stringów (TASK-058; tylko w stringach)
1. `$CALCULATE(...)` - najpierw wyrażenia matematyczne
2. `$AUTO_*` - potem predefiniowane wartości
3. `$zmienna` - na końcu proste zmienne

---

## 6b. Loops i interpolacja stringow (TASK-058)

Gdy workflow ma wiele powtarzalnych elementów (np. deski blatu, okna w elewacji, przyciski w telefonie), ręczne kopiowanie kroków szybko robi się nieczytelne. Rozwiązaniem są **loops** + **string interpolation**.

### 6b.1 Interpolacja `{var}`

W stringach możesz używać placeholderów `{var}` (np. `{i}`, `{row}`, `{col}`), które zostaną podstawione przed obliczeniami `$CALCULATE(...)` i przed ewaluacją `condition`:

```yaml
params:
  name: "TablePlank_{i}"
condition: "{i} <= plank_count"
description: "Create plank {i} of {plank_count}"
```

Escaping: `{{` i `}}` oznaczają literalne `{` i `}`.

### 6b.2 Loop na kroku

Najprostsza pętla (inclusive range):
```yaml
loop:
  variable: i
  range: "1..plank_count"
```

Nested loops (grid):
```yaml
loop:
  variables: [row, col]
  ranges: ["0..(rows - 1)", "0..(cols - 1)"]
```

### 6b.3 Kolejnosc krokow: `loop.group` (interleaving)

Jeśli chcesz wykonać kroki “per iteracja” (np. `create_i → transform_i`), ustaw to samo `loop.group` na kolejnych krokach:

```yaml
- tool: modeling_create_primitive
  params: { primitive_type: CUBE, name: "TablePlank_{i}" }
  loop: { group: planks, variable: i, range: "1..plank_count" }

- tool: modeling_transform_object
  params:
    name: "TablePlank_{i}"
    location: ["$CALCULATE(-table_width/2 + plank_actual_width * ({i} - 0.5))", 0, 0]
  loop: { group: planks, variable: i, range: "1..plank_count" }
```

Tip: dla krótszego YAML używaj anchorów i `<<` merge (PyYAML `safe_load` to wspiera).

## 7. Krok 6: Opcjonalne Kroki i Adaptacja

> **English deep dive:** For a precise explanation of how adaptation (TASK-051) and `condition` interact (two filters),
> plus the full expansion order (computed params → loops/interpolation → `$CALCULATE/$AUTO_/$variable` → `condition`),
> see: [workflow-execution-pipeline.md](./workflow-execution-pipeline.md).

### 7.1 Problem: Zbyt Szczegółowe Workflow

Wyobraź sobie workflow `picnic_table` z 49 krokami, który tworzy stół piknikowy z ławkami i ramą A-frame. Gdy użytkownik powie "prosty stół z 4 nogami", wykonanie pełnego workflow jest nadmierne.

### 7.2 Rozwiązanie: Confidence-Based Adaptation (TASK-051)

Router automatycznie adaptuje workflow na podstawie poziomu dopasowania:

| Confidence | Strategia | Zachowanie |
|------------|-----------|------------|
| **HIGH** (≥0.90) | `FULL` | Wykonaj WSZYSTKIE kroki |
| **MEDIUM** (≥0.75) | `FILTERED` | Core + pasujące optional |
| **LOW** (≥0.60) | `CORE_ONLY` | Tylko CORE kroki |
| **NONE** (<0.60) | `CORE_ONLY` | Tylko CORE (fallback) |

### 7.3 Jak Działa Intent Classifier

**WorkflowIntentClassifier** oblicza confidence na podstawie:

1. **Semantic Similarity (LaBSE embeddings)** - porównuje prompt użytkownika z:
   - `sample_prompts` z workflow YAML
   - `description` workflow
   - `trigger_keywords`

2. **Thresholds dla poziomów confidence:**
   ```python
   HIGH_THRESHOLD = 0.90   # Bardzo wysoka pewność
   MEDIUM_THRESHOLD = 0.75  # Umiarkowana pewność
   LOW_THRESHOLD = 0.60     # Minimalna wymagana pewność
   ```

3. **Przykłady klasyfikacji:**
   ```
   "create a picnic table"           → 0.95 (HIGH)   - bezpośrednie dopasowanie
   "make outdoor table with benches" → 0.82 (MEDIUM) - semantycznie podobne
   "rectangular table with 4 legs"   → 0.65 (LOW)    - częściowe dopasowanie
   "build a shelf"                   → 0.35 (NONE)   - brak dopasowania
   ```

### 7.4 Oznaczanie Kroków jako Opcjonalne

Użyj `optional: true` i `tags` aby oznaczyć kroki, które mogą być pominięte:

```yaml
steps:
  # Krok podstawowy - zawsze wykonywany
  - tool: modeling_create_primitive
    params:
      primitive_type: CUBE
      name: "TableTop"
    description: Stwórz blat stołu
    # optional: false  # Domyślna wartość, nie trzeba pisać

  # Krok opcjonalny - może być pominięty przy niskim confidence
  - tool: modeling_create_primitive
    params:
      primitive_type: CUBE
      name: "BenchLeft"
    description: Stwórz lewą ławkę
    optional: true
    tags: ["bench", "seating", "side"]
```

### 7.5 Jak Działają Tagi przy MEDIUM Confidence?

**WorkflowAdapter** filtruje opcjonalne kroki na podstawie tagów:

```python
# Algorytm filtrowania (pseudokod):
for step in optional_steps:
    # 1. Tag matching (fast, keyword-based)
    if any(tag.lower() in user_prompt.lower() for tag in step.tags):
        include_step(step)
        continue

    # 2. Semantic similarity fallback (dla kroków bez tagów)
    if step.description and similarity(prompt, description) >= 0.6:
        include_step(step)
```

**Przykłady filtrowania:**

```yaml
# Prompt: "table with benches"
# Step tags: ["bench", "seating"]
# Wynik: Krok WŁĄCZONY (tag "bench" pasuje do "benches")

# Prompt: "simple table with 4 legs"
# Step tags: ["bench", "seating"]
# Wynik: Krok POMINIĘTY (żaden tag nie pasuje)

# Prompt: "table with A-frame legs"
# Step tags: ["a-frame", "structural"]
# Wynik: Krok WŁĄCZONY (tag "a-frame" pasuje)
```

### 7.6 Dobre Praktyki dla Tagów

```yaml
# DOBRZE - konkretne, przeszukiwalne tagi
tags: ["bench", "seating", "side", "left"]
tags: ["a-frame", "structural", "cross-support"]
tags: ["handle", "grip", "ergonomic"]
tags: ["decoration", "detail", "ornament"]

# ŹLE - zbyt ogólne
tags: ["extra", "optional"]  # Niespecyficzne
tags: ["part"]               # Wszystko jest "part"
```

**Kategorie tagów rekomendowane:**

| Kategoria | Przykładowe tagi | Zastosowanie |
|-----------|------------------|--------------|
| **Komponenty** | `bench`, `leg`, `shelf`, `drawer` | Główne części |
| **Struktura** | `a-frame`, `cross-support`, `diagonal`, `brace` | Elementy konstrukcyjne |
| **Pozycja** | `left`, `right`, `front`, `back`, `top`, `bottom` | Lokalizacja |
| **Funkcja** | `seating`, `storage`, `decoration` | Przeznaczenie |
| **Styl** | `ornate`, `minimal`, `modern`, `rustic` | Estetyka |

### 7.7 Grupy Opcjonalnych Kroków

Dla złożonych workflow, grupuj powiązane opcjonalne kroki za pomocą wspólnych tagów:

```yaml
steps:
  # === CORE: Zawsze wykonywane ===
  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "TableTop" }
    description: Blat stołu

  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "Leg_FL" }
    description: Noga przednia lewa

  # ... pozostałe nogi ...

  # === OPTIONAL GROUP 1: A-Frame supports ===
  # Wspólne tagi: ["a-frame", "structural"]

  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "CrossBeam_Front" }
    description: Przednia poprzeczka A-frame
    optional: true
    tags: ["a-frame", "cross-support", "structural"]

  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "CrossBeam_Back" }
    description: Tylna poprzeczka A-frame
    optional: true
    tags: ["a-frame", "cross-support", "structural"]

  # === OPTIONAL GROUP 2: Benches ===
  # Wspólne tagi: ["bench", "seating"]

  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "BenchLeft" }
    description: Lewa ławka
    optional: true
    tags: ["bench", "seating", "left"]

  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "BenchRight" }
    description: Prawa ławka
    optional: true
    tags: ["bench", "seating", "right"]
```

### 7.8 Finalizacja z Adaptacją

Sekcja finalizacji (join, rename, material) musi obsługiwać różne warianty:

```yaml
steps:
  # ... kroki tworzące geometrię ...

  # === FINALIZE: Wariant minimalny (CORE) ===
  - tool: modeling_join_objects
    params:
      object_names:
        - "TableTop"
        - "Leg_FL"
        - "Leg_FR"
        - "Leg_BL"
        - "Leg_BR"
    description: Join 5 podstawowych części stołu

  - tool: scene_rename_object
    params:
      old_name: "Leg_BR"
      new_name: "Table"
    description: Nazwij obiekt "Table"

  # === FINALIZE: Wariant z A-frame (dodaj gdy mamy a-frame) ===
  - tool: modeling_join_objects
    params:
      object_names:
        - "Table"
        - "CrossBeam_Front"
        - "CrossBeam_Back"
    description: Dołącz elementy A-frame do stołu
    optional: true
    tags: ["a-frame", "structural"]

  # === FINALIZE: Wariant z ławkami (dodaj gdy mamy benches) ===
  - tool: modeling_join_objects
    params:
      object_names:
        - "Table"
        - "BenchLeft"
        - "BenchRight"
    description: Dołącz ławki do stołu
    optional: true
    tags: ["bench", "seating"]

  - tool: scene_rename_object
    params:
      old_name: "BenchRight"
      new_name: "Picnic_Table"
    description: Nazwij pełny stół piknikowy
    optional: true
    tags: ["bench", "seating"]
```

### 7.9 Przykład: Stół Piknikowy z Pełną Adaptacją

```yaml
# picnic_table.yaml (uproszczony)
name: picnic_table_workflow
description: Stół piknikowy z opcjonalnymi ławkami i ramą A-frame

sample_prompts:
  - "create a picnic table"
  - "make outdoor table with benches"
  - "build a park table"

steps:
  # === CORE STEPS (zawsze wykonywane) ===
  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "TableTop" }
    description: Blat stołu

  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "Leg_FL" }
    description: Noga przednia lewa (może być skośna lub prosta)

  # ... więcej nóg ...

  # === OPTIONAL: A-Frame elements ===
  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "CrossBeam" }
    description: Poprzeczka łącząca nogi A-frame
    optional: true
    tags: ["a-frame", "structural", "cross-support"]

  # === OPTIONAL: Bench elements ===
  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "BenchLeft" }
    description: Lewa ławka
    optional: true
    tags: ["bench", "seating", "left"]
```

**Wyniki adaptacji:**

```
"create a picnic table"       → HIGH (0.95)   → 57 kroków (pełny workflow)
"table with A-frame legs"     → MEDIUM (0.78) → 45 kroków (core + a-frame)
"table with benches"          → MEDIUM (0.80) → 48 kroków (core + benches)
"simple table with 4 legs"    → LOW (0.65)    → 25 kroków (tylko core)
```

### 7.10 Per-Step Adaptation Control (TASK-055-FIX-5)

**Problem**: Konflikt między filtrowaniem semantycznym a warunkami matematycznymi.

Dla MEDIUM confidence, WorkflowAdapter filtruje opcjonalne kroki przez dopasowanie tagów. Gdy krok jest kontrolowany przez **warunek matematyczny** (`leg_angle > 0.5`), filtrowanie semantyczne może go pominąć mimo że warunek jest spełniony.

**Przykład**:
- Prompt: `"stół z nogami w X"` (Polski)
- Tags: `["x-shaped", "crossed-legs"]` (Angielski)
- Semantic matching: ❌ FAIL (Polski prompt nie pasuje do angielskich tagów)
- Parametry: `leg_angle_left=1.0` (X-shaped)
- Warunek: `leg_angle_left > 0.5` → **TRUE**
- Wynik BEZ fix: Krok pominięty przez semantic filtering ❌
- Wynik Z fix: Krok wykonany (warunek=True) ✅

**Rozwiązanie**: Flaga `disable_adaptation`

```yaml
steps:
  # Conditional step - controlled by mathematical condition
  - tool: mesh_transform_selected
    params:
      translate: ["$CALCULATE(0.342 * sin(leg_angle_left))", 0, "$CALCULATE(0.342 * cos(leg_angle_left))"]
    description: "Stretch leg top for X-shaped configuration"
    condition: "leg_angle_left > 0.5 or leg_angle_left < -0.5"
    optional: true                # Documents: optional feature
    disable_adaptation: true      # CRITICAL: Skip semantic filtering, use condition
    tags: ["x-shaped", "crossed-legs", "leg-stretch"]
```

**Semantyka flag**:

| Flaga | Znaczenie | Cel |
|-------|-----------|-----|
| `optional: true` | Krok jest opcjonalną funkcją | Dokumentacja/czytelność |
| `disable_adaptation: true` | Pomiń filtrowanie semantyczne | Traktuj jako core step |
| `condition` | Wyrażenie matematyczne | Kontrola wykonania w runtime |

**Kiedy użyć `disable_adaptation: true`**:

✅ **Użyj gdy**:
- Krok kontrolowany przez warunek matematyczny (`leg_angle > 0.5`)
- Workflow wielojęzyczny (tag matching zawodny)
- Chcesz precyzyjnej kontroli przez condition, nie przez semantic matching

❌ **Nie używaj gdy**:
- Krok bazuje na tagach (benches, decorations) → użyj semantic filtering
- Krok jest core → po prostu usuń `optional: true`

**Przepływ adaptacji z `disable_adaptation`**:

```
MEDIUM confidence:
1. Ensemble matcher sets requires_adaptation=True
2. WorkflowAdapter separates:
   - Core: not optional OR disable_adaptation=True → ALWAYS included
   - Optional: optional=True AND disable_adaptation=False → Semantic filtering
3. All steps with disable_adaptation=True passed to registry
4. ConditionEvaluator evaluates conditions at runtime
5. Only steps with condition=True execute
```

**Korzyści**:
1. ✅ Matematyczna precyzja (condition) > semantyczna aproksymacja (tags)
2. ✅ Wsparcie wielojęzyczne (brak zależności od tag matching)
3. ✅ Jasna intencja w YAML
4. ✅ Zachowana semantyka `optional` do dokumentacji

### 7.11 Niestandardowe Parametry Semantyczne (TASK-055-FIX-6 Phase 2)

**Problem**: Jak dodać własne filtry semantyczne specyficzne dla workflow bez modyfikowania kodu Router?

**Rozwiązanie**: Parametry semantyczne - niestandardowe pola boolean w YAML, które automatycznie działają jako filtry.

#### 7.11.1 Co To Są Parametry Semantyczne?

**Parametry semantyczne** to dowolne pola boolean dodane do kroku workflow, które:
1. Nie są jawnie udokumentowane w `WorkflowStep` (jak `disable_adaptation`, `optional`)
2. Automatycznie wykrywane przez `WorkflowLoader`
3. Mapowane na słowa kluczowe przez `WorkflowAdapter`
4. Porównywane z prompt użytkownika

**Przykład:**

```yaml
steps:
  # Podstawowa struktura stołu (zawsze)
  - tool: modeling_create_primitive
    params: { primitive_type: CUBE }
    description: "Stwórz blat stołu"

  # Ławka (parametr semantyczny)
  - tool: modeling_create_primitive
    params: { primitive_type: CUBE }
    description: "Stwórz ławkę"
    optional: true
    add_bench: true  # PARAMETR SEMANTYCZNY - wykrywa "bench"/"ławka" w prompt
    tags: ["bench", "seating"]
```

#### 7.11.2 Jak To Działa

1. **WorkflowLoader** wykrywa `add_bench` jako nieznane pole
2. Dodaje je jako dynamiczny atrybut do `WorkflowStep` (via `setattr()`)
3. **WorkflowAdapter** wyodrębnia parametry semantyczne:
   - `add_bench` → słowo kluczowe: `"bench"`
4. Sprawdza czy `"bench"` występuje w prompt użytkownika
5. Jeśli TAK → krok włączony, jeśli NIE → krok pominięty

**Konwersja nazw:**

| Nazwa parametru | Wyodrębnione słowo | Dopasowanie |
|-----------------|-------------------|-------------|
| `add_bench` | `"bench"` | bench, ławka, банка |
| `include_stretchers` | `"stretchers"` | stretchers, rozpórki |
| `decorative` | `"decorative"` | decorative, ozdobny |
| `add_handles` | `"handles"` | handles, uchwyty |

System usuwa prefiksy `add_`, `include_` i zastępuje `_` spacjami.

#### 7.11.3 Dopasowanie Pozytywne vs Negatywne

**Pozytywne** (`true`) - Włącz krok jeśli słowo kluczowe **występuje** w prompt:

```yaml
- tool: modeling_create_primitive
  params: { primitive_type: CUBE }
  description: "Stwórz ławkę"
  optional: true
  add_bench: true  # Włącz TYLKO gdy "bench" w prompt
  tags: ["bench"]
```

**Negatywne** (`false`) - Włącz krok jeśli słowo kluczowe **NIE występuje** w prompt:

```yaml
- tool: modeling_create_primitive
  params: { primitive_type: CUBE }
  description: "Prosty stół bez ozdób"
  optional: true
  decorative: false  # Włącz TYLKO gdy "decorative" NIE w prompt
```

**Po co `true`/`false`? Warianty Wzajemnie Wykluczające Się**

Wartość boolean określa **kierunek dopasowania**, umożliwiając warianty wzajemnie wykluczające się w jednym workflow:

```yaml
steps:
  # Core: zawsze wykonywane
  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "TableTop" }
    description: "Stwórz blat"

  # Wariant A: Z ławką (gdy użytkownik chce)
  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "Bench" }
    description: "Stwórz ławkę"
    optional: true
    add_bench: true  # Włącz gdy "bench" JEST w prompt

  # Wariant B: Dodatkowe wsparcie (gdy BRAK ławki)
  - tool: modeling_create_primitive
    params: { primitive_type: CYLINDER, name: "ExtraSupport" }
    description: "Dodaj dodatkowe wsparcie (bo nie ma ławki dla stabilności)"
    optional: true
    add_bench: false  # Włącz gdy "bench" NIE w prompt
```

**Wyniki:**

| Prompt użytkownika | `add_bench: true` (Ławka) | `add_bench: false` (Dodatkowe wsparcie) |
|--------------------|---------------------------|------------------------------------------|
| `"stół"` | ❌ Pominięty | ✅ Włączony (brak ławki → potrzebne wsparcie) |
| `"stół z ławką"` | ✅ Włączony | ❌ Pominięty (jest ławka → nie trzeba wsparcia) |

**Więcej Przykładów:**

```yaml
# Ozdobny vs Prosty
- tool: mesh_bevel
  params: { offset: 0.1 }
  description: "Duże zaokrąglenia (ozdobne)"
  optional: true
  decorative: true  # Włącz gdy "decorative"/"ozdobny" w prompt

- tool: mesh_bevel
  params: { offset: 0.01 }
  description: "Małe zaokrąglenia (minimalistyczne)"
  optional: true
  decorative: false  # Włącz gdy "decorative" NIE w prompt

# Z Uchwytami vs Bez
- tool: modeling_create_primitive
  params: { primitive_type: CYLINDER, name: "Handle" }
  description: "Stwórz uchwyt"
  optional: true
  add_handles: true  # Włącz gdy "handles"/"uchwyty" w prompt

- tool: mesh_bevel
  params: { offset: 0.05 }
  description: "Zaokrągl krawędzie (zamiast uchwytów)"
  optional: true
  add_handles: false  # Włącz gdy "handles" NIE w prompt
```

**Kluczowe Zrozumienie:**

Bez wartości `true`/`false` system nie wiedziałby czy:
- Włączyć krok gdy słowo **występuje** (dopasowanie pozytywne)
- Włączyć krok gdy słowo **NIE występuje** (dopasowanie negatywne)

Dzięki `true`/`false`:
- `true` = "Użytkownik chce tę funkcję" → włącz gdy słowo w prompt
- `false` = "Użytkownik NIE chce tej funkcji" → włącz gdy słowa BRAK w prompt

To umożliwia **warianty wzajemnie wykluczające się** (albo ławka, albo wsparcie, ale nie oba naraz) w ramach jednego workflow!

#### 7.11.4 Przykłady Użycia

**Przykład 1: Stół Piknikowy z Ławką**

```yaml
name: picnic_table_workflow
description: Stół piknikowy z opcjonalną ławką

defaults:
  leg_angle: 0.32

steps:
  # === CORE (zawsze) ===
  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "TableTop" }
    description: "Blat stołu"

  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "Leg_FL" }
    description: "Noga stołu"

  # === OPTIONAL: Bench (parametr semantyczny) ===
  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "BenchSeat" }
    description: "Siedzisko ławki"
    optional: true
    add_bench: true  # Filtr semantyczny
    tags: ["bench", "seating"]

  - tool: modeling_create_primitive
    params: { primitive_type: CUBE, name: "BenchLeg" }
    description: "Noga ławki"
    optional: true
    add_bench: true  # Filtr semantyczny
    tags: ["bench"]

  # === OPTIONAL: Rozpórki (parametr semantyczny) ===
  - tool: modeling_create_primitive
    params: { primitive_type: CYLINDER, name: "Stretcher" }
    description: "Rozpórka między nogami"
    optional: true
    include_stretchers: true  # Filtr semantyczny
    tags: ["stretchers", "support", "structural"]
```

**Wyniki dopasowania:**

| Prompt użytkownika | Ławka włączona? | Rozpórki włączone? |
|--------------------|-----------------|--------------------|
| `"stół piknikowy"` | ❌ Nie | ❌ Nie |
| `"stół piknikowy z ławką"` | ✅ Tak (`"ławką"`) | ❌ Nie |
| `"picnic table with bench"` | ✅ Tak (`"bench"`) | ❌ Nie |
| `"table with stretchers"` | ❌ Nie | ✅ Tak (`"stretchers"`) |
| `"stół z ławką i rozpórkami"` | ✅ Tak (`"ławką"`) | ✅ Tak (`"rozpórkami"`) |

#### 7.11.5 Strategia Filtrowania (3 Poziomy)

WorkflowAdapter używa strategii wielopoziomowej dla MEDIUM confidence:

```
1. Tag matching (szybkie)
   → Sprawdź czy któryś tag występuje w prompt

2. Parametry semantyczne (Phase 2)
   → Sprawdź niestandardowe pola boolean

3. Semantic similarity (wolne, fallback)
   → LaBSE embeddings dla description
```

**Przykład działania:**

```yaml
- tool: modeling_create_primitive
  params: { primitive_type: CUBE }
  description: "Stwórz ławkę do siedzenia"
  optional: true
  add_bench: true
  tags: ["bench", "seating"]
```

**Prompt**: `"stół z ławką"`

1. ✅ **Tag matching**: `"ławką"` nie pasuje do `"bench"` → SKIP
2. ✅ **Parametr semantyczny**: `add_bench` → `"bench"` → mapuje `"ławką"` (LaBSE) → MATCH!
3. ❌ **Semantic similarity**: NIE sprawdzone (już znaleziono match)

#### 7.11.6 Dobre Praktyki

**✅ DOBRZE - Kombinuj parametry semantyczne z tagami:**

```yaml
- tool: modeling_create_primitive
  params: { primitive_type: CUBE }
  description: "Stwórz ławkę"
  optional: true
  add_bench: true        # Parametr semantyczny (wielojęzyczny)
  tags: ["bench"]        # Fallback tag matching
```

**❌ ŹLE - Tylko parametr semantyczny, bez tagów:**

```yaml
- tool: modeling_create_primitive
  params: { primitive_type: CUBE }
  description: "Stwórz ławkę"
  optional: true
  add_bench: true        # Co jeśli zmienię nazwę parametru?
  # Brak tagów - mniej niezawodne
```

**✅ DOBRZE - Opisowe nazwy parametrów:**

```yaml
add_bench: true           # Jasne: szuka "bench"
include_handles: true     # Jasne: szuka "handles"
decorative: true          # Jasne: szuka "decorative"
```

**❌ ŹLE - Niejasne nazwy:**

```yaml
feature_1: true           # Niejasne: jakiego słowa szukać?
enable_extra: true        # Niejasne: co to "extra"?
has_option: true          # Niejasne: jaka opcja?
```

#### 7.11.7 Kiedy Użyć Parametrów Semantycznych

| Feature | Użyj | Przykład |
|---------|------|----------|
| **Jawne pola** | Udokumentowane zachowanie z logiką w kodzie | `disable_adaptation`, `optional`, `condition` |
| **Parametry semantyczne** | Filtry specyficzne dla workflow | `add_bench`, `include_stretchers`, `decorative` |
| **Tagi** | Szybkie dopasowanie słów kluczowych | `tags: ["bench", "seating"]` |

**Użyj parametrów semantycznych gdy:**

✅ Chcesz dodać filtr specyficzny dla workflow bez zmiany kodu Router
✅ Potrzebujesz wielojęzycznego dopasowania (LaBSE)
✅ Nazwa parametru naturalnie mapuje na koncept (np. `add_bench` → `"bench"`)

**Użyj tagów gdy:**

✅ Potrzebujesz listy synonimów
✅ Chcesz szybkiego dopasowania (bez LaBSE)
✅ Masz wiele wariantów słów kluczowych (np. `["bench", "seat", "seating"]`)

#### 7.11.8 Elastyczność Systemu

**Automatyczne ładowanie** (TASK-055-FIX-6 Phase 1):
- Wszystkie pola z `WorkflowStep` automatycznie ładowane z YAML
- Nowe pola dodane do `WorkflowStep` → automatycznie wspierane
- Brak ręcznej synchronizacji loader ↔ dataclass

**Dynamiczne atrybuty** (TASK-055-FIX-6 Phase 2):
- Nieznane pola YAML → dynamiczne atrybuty (`setattr()`)
- Automatycznie wykrywane przez `WorkflowAdapter`
- Nie trzeba modyfikować klasy `WorkflowStep`

---

## 7b. Interaktywna Rezolucja Parametrów (TASK-055)

### 7b.1 Przegląd

System parametrów umożliwia **interaktywne pytanie użytkownika** o wartości, gdy prompt wspomina parametr ale nie podaje konkretnej wartości.

**Przykład:**
```
Prompt: "stół z nogami pod kątem 45 stopni"

System rozpoznaje:
  - Workflow: picnic_table_workflow ✅
  - Parametr "leg_angle" wspomniany ale wartość nieznana

Reakcja:
  → Oznacza parametr jako "unresolved"
  → LLM pyta użytkownika: "Jaki kąt nóg? (zakres: -90° do +90°, domyślnie: 18°)"
```

### 7b.2 Trzy Poziomy Rezolucji

System używa **trzech poziomów** do rozwiązywania parametrów:

| Priorytet | Źródło | Opis |
|-----------|--------|------|
| 1. YAML modifiers | Najwyższy | Dopasowanie semantyczne do `modifiers` w workflow |
| 2. Learned mappings | Średni | Zapamiętane mapowania z poprzednich interakcji |
| 3. LLM interaction | Najniższy | Pytanie użytkownika gdy parametr wspomniany ale nieznany |

### 7b.3 Definicja Parametrów w YAML

```yaml
# W pliku workflow.yaml

# Wartości domyślne
defaults:
  leg_angle_left: 0.32
  leg_angle_right: -0.32

# Predefiniowane modyfikatory (priorytet 1)
modifiers:
  "straight legs":
    leg_angle_left: 0
    leg_angle_right: 0
    negative_signals: ["X", "crossed", "angled", "diagonal", "skośne", "skrzyżowane"]  # TASK-055-FIX-2
  "angled legs":
    leg_angle_left: 0.32
    leg_angle_right: -0.32

# Schematy parametrów dla interaktywnej rezolucji (priorytet 3)
parameters:
  leg_angle_left:
    type: float                     # Typ: float, int, string, bool
    range: [-1.57, 1.57]           # Zakres wartości (opcjonalne)
    default: 0.32                   # Wartość domyślna
    description: "Rotation angle for left table legs"
    semantic_hints:                 # English keywords - LaBSE handles other languages
      - angle      # Auto-matches: kąt (PL), Winkel (DE), ángulo (ES)
      - legs       # Auto-matches: nogi (PL), Beinen (DE), pieds (FR)
      - crossed    # Auto-matches: skrzyżowane (PL), croisé (FR)
    group: leg_angles              # Grupa parametrów (opcjonalne)
```

### 7b.4 Jak Działają semantic_hints

`semantic_hints` służą do wykrywania czy prompt **wspomina** dany parametr.

**Trzy mechanizmy wykrywania:**

1. **LaBSE similarity (pełny prompt)** - porównuje cały prompt z hint
   ```
   "table with legs at 45 degrees" ↔ "angle" = 0.42
   ```

2. **Literal matching** - czy hint dosłownie występuje w prompt
   ```
   "table with angle" zawiera "angle" → relevance = 0.8
   ```

3. **Semantic word matching (TASK-055)** - czy JAKIEKOLWIEK słowo w prompt jest semantycznie podobne do hint
   ```
   "Tisch mit Beinen" → "Beinen" ↔ "legs" = 0.757 → relevance = 0.75
   ```

### 7b.5 Automatyczne Wsparcie Wielojęzyczne

**Wystarczą TYLKO angielskie hinty!**

Dzięki **semantic word matching** z LaBSE, system automatycznie rozpoznaje słowa z innych języków:

| Język | Słowo w prompt | Dopasowanie do hint (EN) | Similarity |
|-------|----------------|--------------------------|------------|
| Polish | "kątem" | "angle" | 0.879 |
| German | "Beinen" | "legs" | 0.757 |
| French | "pieds" | "legs" | 0.939 |
| Spanish | "ángulo" | "angle" | 0.959 |
| Italian | "angolo" | "angle" | 0.935 |

**Nie trzeba dodawać hintów dla każdego języka** - LaBSE automatycznie mapuje pojęcia cross-language.

### 7b.6 Thresholds

| Parametr | Wartość | Znaczenie |
|----------|---------|-----------|
| `relevance_threshold` | 0.4 | Min. similarity żeby uznać parametr za "wspomniany" |
| `memory_threshold` | 0.85 | Min. similarity żeby użyć zapamiętanego mapowania |
| Literal match boost | 0.8 | Relevance gdy hint dosłownie w prompt |
| Semantic word threshold | 0.65 | Min. similarity dla pojedynczych słów |
| Semantic word boost | 0.75 | Relevance gdy słowo semantycznie pasuje |

### 7b.7 Przykład: Stół z Nogami pod Kątem X

**Workflow YAML:**
```yaml
defaults:
  leg_angle_left: 0.32

modifiers:
  "straight legs":
    leg_angle_left: 0
    leg_angle_right: 0
    negative_signals: ["X", "crossed", "angled", "diagonal", "skośne", "skrzyżowane"]  # TASK-055-FIX-2

parameters:
  leg_angle_left:
    type: float
    range: [-1.57, 1.57]
    default: 0.32
    description: "Rotation angle for left table legs"
    semantic_hints:
      - angle      # LaBSE matches: kątem (PL)=0.879, ángulo (ES)=0.959, angolo (IT)=0.935
      - legs       # LaBSE matches: Beinen (DE)=0.757, pieds (FR)=0.939, nogi (PL)=0.967
      - crossed    # LaBSE matches: skrzyżowane (PL)=0.855, croisés (FR)=0.887
```

**Scenariusze:**

| Prompt | Rozwiązanie | Wynik |
|--------|-------------|-------|
| "create a picnic table" | defaults | leg_angle=0.32 |
| "table with straight legs" | modifier match | leg_angle=0 |
| "stół z prostymi nogami" | modifier match (LaBSE) | leg_angle=0 |
| "table with legs at 45°" | **UNRESOLVED** → pytanie | LLM pyta użytkownika |
| "Tisch mit Beinen im Winkel" | **UNRESOLVED** → pytanie | LLM pyta użytkownika |

### 7b.8 Dobre Praktyki dla semantic_hints

```yaml
# DOBRZE - tylko angielskie, konkretne
semantic_hints:
  - angle      # LaBSE automatycznie dopasuje: kąt, Winkel, ángulo, angolo
  - legs       # LaBSE automatycznie dopasuje: nogi, Beinen, pieds, piernas
  - crossed    # LaBSE automatycznie dopasuje: skrzyżowane, gekreuzt, croisé

# ŹLE - zbyt ogólne
semantic_hints:
  - table      # Zbyt ogólne, zawsze pasuje
  - create     # Nie dotyczy parametru
```

**Wskazówki:**
1. Użyj 2-4 konkretnych angielskich hint'ów per parametr
2. LaBSE automatycznie dopasuje inne języki (nie dodawaj tłumaczeń!)
3. Unikaj zbyt ogólnych słów
4. Hinty powinny być związane z **parametrem**, nie z workflow

---

## 8. Krok 7: Testowanie

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

## 9. Kompletny Przykład

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
      offset: "$AUTO_BEVEL"
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
      offset: 0.0004  # 5% z 8mm
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

## 10. Najczęstsze Błędy

### 9.1 Błędy Składni YAML

```yaml
# ŹLE - brak spacji po dwukropku
params:
  offset:0.05

# DOBRZE
params:
  offset: 0.05
```

```yaml
# ŹLE - nieprawidłowe wcięcie
steps:
- tool: mesh_bevel
params:
  offset: 0.05

# DOBRZE
steps:
  - tool: mesh_bevel
    params:
      offset: 0.05
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
offset: "$CALCULATE(min_dim * 0.05"

# DOBRZE
offset: "$CALCULATE(min_dim * 0.05)"
```

```yaml
# ŹLE - nieistniejąca zmienna
offset: "$CALCULATE(szerokość * 0.05)"

# DOBRZE (użyj angielskich nazw)
offset: "$CALCULATE(width * 0.05)"
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

## 11. Zaawansowane Funkcje Workflow (TASK-056)

### 11.1 Walidacja Enum dla Parametrów (TASK-056-3)

Ogranicz wartości parametrów do dyskretnych opcji:

```yaml
parameters:
  table_style:
    type: string
    enum: ["modern", "rustic", "industrial", "traditional"]
    default: "modern"
    description: Styl konstrukcji stołu
    semantic_hints: ["style", "design", "styl"]

  detail_level:
    type: string
    enum: ["low", "medium", "high", "ultra"]
    default: "medium"
    description: Poziom detali siatki (wpływa na liczbę poligonów)

  leg_count:
    type: int
    enum: [3, 4, 6, 8]
    default: 4
    description: Liczba nóg stołu
```

**Korzyści:**
- Bezpieczeństwo typów: Nieprawidłowe wartości automatycznie odrzucane
- Samodokumentujące: Jasne opcje dla użytkowników
- Wsparcie LLM: LLM widzi prawidłowe opcje w schemacie

**Walidacja:**
- Sprawdzenie enum następuje **przed** walidacją zakresu
- Wartość domyślna musi być w liście enum
- Działa z każdym typem (string, int, float, bool)
- Dla `type: string` router normalizuje input (trim + case-insensitive), np. `"Sides"` → `"sides"`
- Gdy parametr jest `unresolved`, `router_set_goal` zwraca listę `enum` w odpowiedzi (żeby LLM/caller mógł wybrać poprawną wartość)

### 11.2 Parametry Obliczane (TASK-056-5)

Definiuj parametry automatycznie obliczane z innych parametrów:

```yaml
parameters:
  table_width:
    type: float
    default: 1.2
    description: Szerokość stołu w metrach

  plank_max_width:
    type: float
    default: 0.10
    description: Maksymalna szerokość pojedynczej deski

  # Obliczany: Liczba potrzebnych desek
  plank_count:
    type: int
    computed: "ceil(table_width / plank_max_width)"
    depends_on: ["table_width", "plank_max_width"]
    description: Liczba desek potrzebna do pokrycia szerokości stołu

  # Obliczany: Rzeczywista szerokość deski (dopasowana do dokładnego dopasowania)
  plank_actual_width:
    type: float
    computed: "table_width / plank_count"
    depends_on: ["table_width", "plank_count"]
    description: Rzeczywista szerokość każdej deski (dopasowana do dokładnego zmieszczenia)

  # Obliczany: Współczynnik proporcji
  aspect_ratio:
    type: float
    computed: "width / height"
    depends_on: ["width", "height"]
    description: Stosunek szerokości do wysokości

  # Obliczany: Odległość po przekątnej
  diagonal:
    type: float
    computed: "hypot(width, height)"
    depends_on: ["width", "height"]
    description: Odległość po przekątnej blatu stołu
```

**Jak to działa:**
1. Router rozwiązuje parametry obliczane w **kolejności zależności** (sortowanie topologiczne)
2. Każdy parametr obliczany ewaluuje swoje wyrażenie `computed`
3. Wynik staje się dostępny dla zależnych parametrów
4. Zależności cykliczne są wykrywane i odrzucane

**Uwaga (interaktywna rezolucja + learned mappings):**
- Parametry z `computed: "..."` są traktowane jako wewnętrzne wyniki i **nie** są pytane jako `unresolved`.
- Computed params są ignorowane przez learned mappings (żeby nie “uczyć się” wartości wyliczanych i uniknąć dryfu).
- Jeśli naprawdę chcesz nadpisać computed value (advanced), przekaż ją jawnie przez `resolved_params` albo YAML `modifiers`.

**Użycie w krokach:**

```yaml
steps:
  # Użyj parametru obliczanego jak każdego innego
  - tool: modeling_create_primitive
    params:
      primitive_type: CUBE
      scale: ["$plank_actual_width", 1, 0.1]
    description: "Stwórz deskę o dokładnej szerokości"

  # Warunkowy krok na podstawie obliczonej wartości
  - tool: modeling_create_primitive
    params:
      primitive_type: CUBE
    description: "Dodaj dodatkowe wsparcie dla szerokich stołów"
    condition: "plank_count >= 12"
```

**Korzyści:**
- Automatyczne obliczenia: Nie trzeba powtarzać formuł w krokach
- Śledzenie zależności: Parametry rozwiązują się we właściwej kolejności
- Dynamiczna adaptacja: Obliczone wartości dopasowują się do wymiarów wejściowych

### 11.3 Zależności Kroków i Kontrola Wykonania (TASK-056-4)

Kontroluj kolejność wykonania kroków i obsługę błędów:

```yaml
steps:
  - id: "create_base"
    tool: modeling_create_primitive
    params:
      primitive_type: CUBE
      name: "Base"
    description: Stwórz bazę stołu
    timeout: 5.0                # Maksymalny czas wykonania (sekundy)
    max_retries: 2              # Próby powtórzenia przy błędzie
    retry_delay: 1.0            # Opóźnienie między próbami (sekundy)

  - id: "scale_base"
    tool: modeling_transform_object
    depends_on: ["create_base"]  # Czekaj na zakończenie create_base
    params:
      name: "Base"
      scale: [1, 2, 0.1]
    description: Przeskaluj bazę do prawidłowych proporcji
    on_failure: "abort"         # "skip", "abort", "continue"
    priority: 10                # Wyższy priorytet = wykonaj wcześniej

  - id: "add_legs"
    tool: modeling_create_primitive
    depends_on: ["scale_base"]  # Czekaj na scale_base
    params:
      primitive_type: CUBE
      name: "Leg_1"
    max_retries: 1
    retry_delay: 0.5
```

**Pola:**

| Pole | Typ | Opis |
|------|-----|------|
| `id` | string | Unikalny identyfikator kroku |
| `depends_on` | list[string] | ID kroków, od których ten krok zależy |
| `timeout` | float | Maksymalny czas wykonania (sekundy) |
| `max_retries` | int | Liczba prób powtórzenia przy błędzie |
| `retry_delay` | float | Opóźnienie między próbami |
| `on_failure` | string | "skip", "abort", "continue" |
| `priority` | int | Wyższy = wykonaj wcześniej |

**Funkcje:**
- **Rozwiązywanie zależności**: Kroki wykonują się we właściwej kolejności (sortowanie topologiczne)
- **Wykrywanie zależności cyklicznych**: Odrzuca nieprawidłowe grafy zależności
- **Wymuszanie timeout**: Zabija długo działające kroki
- **Mechanizm retry**: Automatycznie powtarza nieudane kroki
- **Sortowanie priorytetowe**: Kontrola kolejności wykonania dla niezależnych kroków

**Przykłady użycia:**

```yaml
# Zapewnij utworzenie przed transformacją
- id: "create"
  tool: modeling_create_primitive
  params: {primitive_type: CUBE}

- id: "transform"
  depends_on: ["create"]
  tool: modeling_transform_object
  params: {scale: [1, 2, 1]}

# Retry przy błędzie (np. import z sieci)
- tool: import_fbx
  params: {filepath: "https://example.com/model.fbx"}
  max_retries: 3
  retry_delay: 2.0
  timeout: 30.0
  on_failure: "skip"
```

---

## Podsumowanie

1. **Zaplanuj** - przetestuj ręcznie, zapisz kroki
2. **Utwórz plik** - w `workflows/custom/nazwa.yaml`
3. **Dodaj metadane** - name, description, trigger_keywords
4. **Zdefiniuj kroki** - tool, params, description
5. **Dodaj warunki** - `condition` dla odporności (z nawiasami jeśli potrzeba)
6. **Użyj dynamicznych parametrów** - `$AUTO_*` lub `$CALCULATE`
7. **Rozważ zaawansowane funkcje** - enum, computed params, dependencies (TASK-056)
8. **Przetestuj** - sprawdź ładowanie i rozwijanie

**Nowe w TASK-056:**
- Rozszerzone funkcje matematyczne (tan, atan2, log, exp, hypot, itd.)
- Nawiasy w warunkach z prawidłową kolejnością operatorów
- Walidacja enum dla parametrów
- Parametry obliczane z automatycznym rozwiązywaniem zależności
- Kontrola wykonania kroków (timeout, retry, dependencies)

**Nowe w TASK-060:**
- Funkcje matematyczne w `condition` (np. `floor()`, `sqrt()`)
- Operatory porównania/logiczne i ternary w `$CALCULATE(...)`

**Zobacz też:**
- [yaml-workflow-guide.md](./yaml-workflow-guide.md) - Pełna dokumentacja składni
- [expression-reference.md](./expression-reference.md) - Referencja wyrażeń
