# MCP Server Documentation

Dokumentacja serwera MCP (Client Side).

## 📚 Indeks Tematyczny

- **[Clean Architecture](./clean_architecture.md)**
  - Szczegółowy opis warstw: Domain, Application, Adapters, Infrastructure.
  - Zasady separacji zależności wdrożone w wersji 0.1.3.

## 🛠 Dostępne Narzędzia (Tools)

Poniższe narzędzia są wystawiane dla modelu AI przez `FastMCP`.

### Scene Tools
Zarządzanie obiektami na poziomie sceny.

| Nazwa Narzędzia | Argumenty | Opis |
|-----------------|-----------|------|
| `list_objects` | *brak* | Zwraca listę wszystkich obiektów na scenie wraz z ich typem i pozycją. |
| `delete_object` | `name` (str) | Usuwa wskazany obiekt. Zwraca błąd jeśli obiekt nie istnieje. |
| `clean_scene` | `keep_lights_and_cameras` (bool, domyślnie True) | Usuwa obiekty ze sceny. Jeśli `True`, zachowuje kamery i światła. Jeśli `False`, czyści projekt całkowicie ("hard reset"). |

## 🛠 Kluczowe Komponenty

### Composition Root (`server/main.py`)
Punkt wejścia aplikacji. Odpowiada za:
1. Inicjalizację Adapterów (`RpcClient`).
2. Inicjalizację Aplikacji (`SceneToolHandler`).
3. Wstrzyknięcie zależności.
4. Uruchomienie serwera FastMCP.

### Application Handlers (`server/application/tool_handlers/`)
Konkretne implementacje logiki narzędzi, niezależne od frameworka MCP.
- `scene_handler.py`: Obsługa operacji na scenie.

### Interfaces (`server/domain/`)
Abstrakcje definiujące kontrakty systemowe.
- `interfaces/rpc.py`: Kontrakt dla klienta RPC.
- `tools/scene.py`: Kontrakt dla narzędzi sceny.