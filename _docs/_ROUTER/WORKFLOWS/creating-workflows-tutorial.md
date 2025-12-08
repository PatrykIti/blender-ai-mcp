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

## 7. Krok 6: Opcjonalne Kroki i Adaptacja

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

### 7.10 Ograniczenia Obecnego Systemu

**Co system MOŻE:**
- Pomijać opcjonalne kroki na podstawie confidence
- Filtrować kroki przez dopasowanie tagów
- Wykonywać różne warianty finalizacji

**Czego system NIE MOŻE (planowane w TASK-052):**
- Dynamicznie zmieniać parametry (np. kąt nóg z 33° na 0°)
- Generować nowe kroki na podstawie intencji
- Adaptować geometrię do opisu użytkownika

Obecnie workflow definiuje **statyczne parametry**. Jeśli użytkownik chce "proste nogi" zamiast "skośnych", system może tylko:
1. Pominąć kroki związane z elementami A-frame
2. Ale NIE może zmienić kąta obrotu nóg z 0.32 rad na 0

To ograniczenie jest rozwiązane w TASK-055 przez **interaktywną rezolucję parametrów** (sekcja poniżej).

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
  "angled legs":
    leg_angle_left: 0.32
    leg_angle_right: -0.32

# Schematy parametrów dla interaktywnej rezolucji (priorytet 3)
parameters:
  leg_angle_left:
    name: leg_angle_left           # Wymagane
    type: float                     # Typ: float, int, string, bool
    range: [-1.57, 1.57]           # Zakres wartości (opcjonalne)
    default: 0.32                   # Wartość domyślna
    description: "Kąt obrotu lewych nóg stołu"
    semantic_hints:                 # Słowa kluczowe do wykrywania
      - angle
      - rotation
      - legs
      - kąt         # Polish
      - nogi        # Polish
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
   "stół z nogami pod kątem" zawiera "kąt" → relevance = 0.8
   ```

3. **Semantic word matching (TASK-055)** - czy JAKIEKOLWIEK słowo w prompt jest semantycznie podobne do hint
   ```
   "Tisch mit Beinen" → "Beinen" ↔ "nogi" = 0.679 → relevance = 0.75
   ```

### 7b.5 Automatyczne Wsparcie Wielojęzyczne

**Nie musisz dodawać hint'ów dla każdego języka!**

Dzięki **semantic word matching** z LaBSE, system automatycznie rozpoznaje powiązania między językami:

| Język | Słowo w prompt | Dopasowanie do hint | Similarity |
|-------|----------------|---------------------|------------|
| German | "Beinen" | "nogi" (Polish) | 0.679 |
| French | "pieds" | "legs" (English) | 0.939 |
| Spanish | "piernas" | "legs" (English) | ~0.85 |

**Wystarczy dodać hinty w 2-3 językach** (np. English + Polish), a LaBSE automatycznie dopasuje inne języki.

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

parameters:
  leg_angle_left:
    name: leg_angle_left
    type: float
    range: [-1.57, 1.57]
    default: 0.32
    description: "Rotation angle for left table legs"
    semantic_hints:
      - angle
      - rotation
      - legs
      - kąt
      - nogi
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
# DOBRZE - konkretne, wielojęzyczne
semantic_hints:
  - angle           # English
  - rotation        # English
  - legs            # English (LaBSE dopasuje French "pieds", German "Beine")
  - kąt             # Polish (literal match)
  - nogi            # Polish (LaBSE dopasuje German "Beinen")

# ŹLE - zbyt ogólne
semantic_hints:
  - table           # Zbyt ogólne, zawsze pasuje
  - create          # Nie dotyczy parametru
```

**Wskazówki:**
1. Dodaj 3-5 konkretnych hint'ów per parametr
2. Użyj English + jeden język słowiański (Polish) - LaBSE dobrze łączy rodziny językowe
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

## 10. Najczęstsze Błędy

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
