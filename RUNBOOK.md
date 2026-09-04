# Blender Agent Runbook

Практическая инструкция для агента, который управляет Blender через `blender-ai-mcp`.

## Рабочие пути

- Рабочая папка: `D:\03_3D`
- Репозиторий MCP: `D:\03_3D\blender-ai-mcp`
- Основная сцена: `D:\03_3D\Untitled.blend`
- Рендеры: `D:\03_3D\vase_render.png`
- Blender RPC: `127.0.0.1:8765`

## Запуск Blender

1. Запустить Blender 4.0 или новее. Рекомендуемая версия проекта: Blender 5.0.
2. Открыть `Edit > Preferences > Add-ons`.
3. Нажать `Install...` и выбрать архив аддона `blender_ai_mcp.zip`.
4. Включить аддон `Blender AI MCP`.
5. Проверить доступность RPC-порта:

```powershell
Test-NetConnection 127.0.0.1 -Port 8765 -InformationLevel Quiet
```

Ожидаемый результат: `True`.

Если архива аддона нет, собрать его из репозитория:

```powershell
Set-Location -LiteralPath 'D:\03_3D\blender-ai-mcp'
python scripts/build_addon.py
```

После сборки установить полученный zip через настройки Blender.

## Запуск MCP-сервера

Аддон Blender должен быть включён до запуска MCP-сервера.

```powershell
Set-Location -LiteralPath 'D:\03_3D\blender-ai-mcp'
poetry run python server/main.py
```

Для локальной конфигурации сервера используются значения:

```text
BLENDER_RPC_HOST=127.0.0.1
BLENDER_RPC_PORT=8765
ROUTER_ENABLED=true
MCP_SURFACE_PROFILE=llm-guided
```

Не запускать второй экземпляр MCP-сервера без необходимости.

## Рабочий цикл агента

1. Проверить, что Blender открыт и RPC-порт отвечает.
2. Проверить текущую сцену перед изменениями.
3. Перед разрушительной операцией явно определить область очистки.
4. Для полной очистки использовать `scene.clean_scene` с `keep_lights_and_cameras=false`.
5. Создать геометрию через инструменты MCP, а не изменять `.blend` вручную.
6. Назначить материал и проверить материал через инспекцию сцены.
7. Сохранить сцену через `system.save_file` в `D:\03_3D\Untitled.blend`.
8. Настроить разрешение рендера `1920×1080`.
9. Выполнить рендер и проверить существование итогового файла.
10. В конце сообщить пользователю путь к `.blend` и изображению.

## Часто используемые операции

Очистка сцены:

```text
scene.clean_scene({"keep_lights_and_cameras": false})
```

Создание примитива:

```text
modeling.create_primitive({
  "primitive_type": "Cylinder",
  "radius": 1.0,
  "size": 2.0,
  "location": [0, 0, 1],
  "name": "Object_Name"
})
```

Создание белого материала:

```text
material.create({
  "name": "Porcelain_White",
  "base_color": [0.97, 0.97, 0.97, 1.0],
  "metallic": 0.0,
  "roughness": 0.28
})
```

Настройка рендера:

```text
scene.configure_render_settings({
  "settings": {
    "resolution": {"x": 1920, "y": 1080, "percentage": 100},
    "image_settings": {"file_format": "PNG"},
    "filepath": "D:\\03_3D\\vase_render.png",
    "film_transparent": false
  }
})
```

Сохранение сцены:

```text
system.save_file({
  "filepath": "D:\\03_3D\\Untitled.blend",
  "compress": true
})
```

## Правила безопасности

- Не удалять сцену без явного указания пользователя или подтверждённого задания.
- Не использовать `system.new_file`, если нужно сохранить текущую сцену.
- После каждого существенного изменения сохранять `.blend`.
- Не перезаписывать существующий рендер без необходимости.
- После мутации проверять список объектов и активный материал.
- При недоступном порте сначала восстановить соединение с Blender, а не повторять мутацию вслепую.
- Не считать успешным ответ MCP доказательством результата без проверки сцены или файла.

## Диагностика

Порт `8765` недоступен:

- проверить, что Blender запущен;
- проверить, что аддон включён;
- отключить и снова включить аддон;
- повторить проверку `Test-NetConnection`.

MCP-сервер не подключается:

- проверить, что запущен только один сервер;
- проверить `BLENDER_RPC_HOST` и `BLENDER_RPC_PORT`;
- запускать сервер из `D:\03_3D\blender-ai-mcp`.

Результат не виден:

- проверить `scene.list_objects`;
- проверить `scene.inspect_render_settings`;
- проверить наличие файла через `Test-Path`;
- повторно сохранить сцену и выполнить рендер.
