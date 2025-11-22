# MCP Server Documentation

Dokumentacja serwera MCP (Client Side).

## 📚 Indeks Tematyczny

- **[Clean Architecture](./clean_architecture.md)**
  - Opis warstw: Domain, Application, Adapters, Infrastructure.
  - Zasady separacji zależności.

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
- `server/main.py`: Punkt wejścia serwera. Rejestracja narzędzi.
- `RpcClient` (`server/adapters/rpc/client.py`): Odpowiada za niskopoziomową komunikację z Blenderem.
