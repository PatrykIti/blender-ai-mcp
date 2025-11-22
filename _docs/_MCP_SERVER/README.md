# MCP Server Documentation

Dokumentacja serwera MCP (Client Side).

## 📚 Indeks Tematyczny

- **[Clean Architecture](./clean_architecture.md)**
  - Szczegółowy opis warstw i przepływu sterowania (DI).
  - Zasady separacji zależności wdrożone w wersji 0.1.5.

## 🚀 Uruchamianie (Docker)

Serwer można uruchomić w kontenerze Docker, co izoluje środowisko.

### 1. Budowanie obrazu
```bash
docker build -t blender-ai-mcp .
```

### 2. Uruchamianie
Aby serwer w kontenerze mógł połączyć się z Blenderem na hoście, należy odpowiednio skonfigurować sieć.

**MacOS / Windows:**
```bash
docker run -i --rm -e BLENDER_RPC_HOST=host.docker.internal blender-ai-mcp
```

**Linux:**
```bash
docker run -i --rm --network host -e BLENDER_RPC_HOST=127.0.0.1 blender-ai-mcp
```

*(Flaga `-i` jest kluczowa dla interaktywnej komunikacji stdio używanej przez MCP)*.

## 🛠 Dostępne Narzędzia (Tools)

### Scene Tools
Zarządzanie obiektami na poziomie sceny.

| Nazwa Narzędzia | Argumenty | Opis |
|-----------------|-----------|------|
| `list_objects` | *brak* | Zwraca listę wszystkich obiektów na scenie wraz z ich typem i pozycją. |
| `delete_object` | `name` (str) | Usuwa wskazany obiekt. Zwraca błąd jeśli obiekt nie istnieje. |
| `clean_scene` | `keep_lights_and_cameras` (bool, domyślnie True) | Usuwa obiekty ze sceny. Jeśli `True`, zachowuje kamery i światła. Jeśli `False`, czyści projekt całkowicie ("hard reset"). |

### Modeling Tools
Tworzenie i edycja geometrii.

| Nazwa Narzędzia | Argumenty | Opis |
|-----------------|-----------|------|
| `create_primitive` | `primitive_type` (str), `size` (float), `location` ([x,y,z]), `rotation` ([x,y,z]) | Tworzy prosty obiekt 3D (Cube, Sphere, Cylinder, Plane, Cone, Torus, Monkey). |
| `transform_object` | `name` (str), `location` (opt), `rotation` (opt), `scale` (opt) | Zmienia położenie, rotację lub skalę istniejącego obiektu. |
| `add_modifier` | `name` (str), `modifier_type` (str), `properties` (dict) | Dodaje modyfikator do obiektu (np. `SUBSURF`, `BEVEL`). |

## 🛠 Kluczowe Komponenty

### Entry Point (`server/main.py`)
Minimalistyczny punkt startowy.

### Dependency Injection (`server/infrastructure/di.py`)
Zestaw "Providerów" (funkcji fabrycznych). Wstrzykuje konfigurację z `server/infrastructure/config.py`.

### Configuration (`server/infrastructure/config.py`)
Obsługa zmiennych środowiskowych (np. adres IP Blendera).

### Application Handlers (`server/application/tool_handlers/`)
Konkretne implementacje logiki narzędzi.
- `scene_handler.py`: Obsługa operacji na scenie.
- `modeling_handler.py`: Obsługa modelowania.

### Interfaces (`server/domain/`)
Abstrakcje definiujące kontrakty systemowe.
- `interfaces/rpc.py`: Kontrakt dla klienta RPC.
- `tools/scene.py`: Kontrakt dla narzędzi sceny.
- `tools/modeling.py`: Kontrakt dla narzędzi modelowania.