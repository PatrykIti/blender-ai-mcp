# 🔌 Blender Addon Documentation

## 📌 Przegląd
Blender Addon ("Blender AI MCP") pełni rolę serwera wykonawczego dla komend przychodzących z MCP Servera. Działa wewnątrz procesu Blendera, nasłuchując na porcie lokalnym (domyślnie `8765`) i wykonując operacje na API `bpy`.

## 🏗 Struktura
Kod źródłowy znajduje się w katalogu `blender_addon/`.

- `__init__.py`: Punkt wejścia addona. Rejestruje operatorów i uruchamia serwer RPC w tle.
- `rpc_server.py`: Implementacja serwera TCP Socket.
  - Używa `threading` do obsługi połączeń bez blokowania UI Blendera.
  - Używa `bpy.app.timers` do bezpiecznego delegowania zadań do głównego wątku Blendera (Context Safety).

## 🚀 Instalacja i Uruchomienie
1. Uruchom Blendera.
2. Przejdź do `Edit` -> `Preferences` -> `Add-ons`.
3. Zainstaluj addon (wskazując plik ZIP lub katalog).
   *(Dla developmentu można użyć skryptu linkującego lub uruchamiać Blendera ze ścieżką do skryptu).*
4. Po włączeniu, addon automatycznie startuje serwer na `127.0.0.1:8765`.

## 📡 Protokół Komunikacji
Addon akceptuje wiadomości JSON w formacie:

```json
{
  "request_id": "uuid-v4",
  "cmd": "nazwa_komendy",
  "args": { ... }
}
```

Odpowiedzi są zwracane jako:
```json
{
  "request_id": "uuid-v4",
  "status": "ok" | "error",
  "result": { ... },
  "error": "Opcjonalny komunikat błędu"
}
```

## 🛠 Dostępne Komendy (System)
- `ping`: Sprawdza połączenie. Zwraca wersję Blendera.

*(Więcej komend modelowania w trakcie implementacji)*
