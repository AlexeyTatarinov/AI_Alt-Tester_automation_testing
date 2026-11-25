# AltTester: что умеет, чего не умеет, что проверить пробой (25.11.2026)

Автор: Opus. Источники: (1) установленный SDK `scripts\sdk_smoke\.venv\Lib\site-packages\alttester` (AltTester-Driver 2.4.1, список методов прочитан из `altdriver.py`, `altobject.py`); (2) документация https://alttester.com/docs/sdk/latest/ (страницы commands, known-issues, advanced-usage, faq-troubleshooting; версия на страницах 2.4.1); (3) наши прогоны 1–7b. Не прочитаны в документации: раздел про селекторы By (полный список и фильтры @component/@tag), страницы Python и AltTester Editor, GetVisualElementProperty.

Обозначения: ✅ проверено у нас на живой игре; 📄 только по документации; ❓ неизвестно, проверить пробой (задание `prompts\modules_stage1_20261125.md`, этап B).

## 1. Команды SDK 2.4.1 (Python)

| Группа | Команды | Статус у нас |
|---|---|---|
| Сцены | `get_current_scene`, `get_all_loaded_scenes`, `load_scene`, `unload_scene`, `wait_for_current_scene_to_be` | ✅ список сцен; ❓ `load_scene` (LOAD-00 ни разу) — не нужен |
| Время | `get_time_scale`, `set_time_scale` | ✅ чтение (через Time) |
| Поиск | `find_object(s)`, `find_object(s)_which_contain`, `wait_for_object`, `wait_for_object_to_not_be_present`, `get_all_elements`, `find_object_at_coordinates`; у объекта `find_object_from_object`, `get_parent`, `get_all_components` | ✅ NAME, COMPONENT, PATH, всегда `enabled=False`; ❓ `get_all_components`, фильтр `[@component=…]` в PATH |
| Свойства | `obj.get_component_property(comp, prop, asm, max_depth=2)`, `obj.set_component_property`, `obj.wait_for_component_property`, `driver.get_static_property(…, max_depth=2)`, `driver.set_static_property` | ✅ простые поля и статические (в т.ч. `UnityEditor.LogEntries.consoleFlags`, `EditorApplication.isPlaying`); ❓ вложенные пути через ScriptableObject, списки |
| Методы | `obj.call_component_method(comp, method, asm, parameters, type_of_parameters)`, `driver.call_static_method(…)` | ✅ `Damageable.Kill`, `ReceiveAnAttack(System.Int32)`; ❌ Vector3 в параметрах (Physics.Raycast не вызвать) |
| Текст UI | `obj.get_text`, `obj.set_text` | ✅ TMP и UI.Text |
| Клики UI | `obj.click`, `obj.tap`, `pointer_down/up/enter/exit` | ✅ кнопки меню, выбор Yes/No |
| Клавиши | `press_key(key, power, duration)`, `press_keys`, `key_down/up`, `keys_down/up`, `reset_input` | ✅ с удержанием; ⚠ тап 0,05 с и удержание 0,1 с дают разный результат в диалоге (причина не выяснена) |
| Мышь/тач | `move_mouse`, `click(coords)`, `scroll`, `swipe`, `hold_button`, `tap`, `begin/move/end_touch`, `tilt` | ⚠ эмулированная мышь вращает камеру без правой кнопки (Confluence 327707) |
| Скриншот | `get_png_screenshot(path)` | ✅ |
| Уведомления | `add_notification_listener(NotificationType.LOADSCENE/UNLOADSCENE/LOG/APPLICATION_PAUSED, callback, overwrite)`, `remove_notification_listener` | ❓ не пробовали ни разу. 📄 LOG даёт `message`, `stack_trace`, `level` — может заменить разбор Editor.log |
| Настройки драйвера | `set_command_response_timeout`, `set_delay_after_command`, `set_implicit_timeout` (по умолчанию 20 с), `set_server_logging` | ✅ timeout |
| PlayerPrefs | `get/set/delete_player_pref_key` | не нужно (игра хранит в save.chop) |

## 2. Что сказано в документации (главное для нас)

- 📄 Вложенный путь в имени свойства: `property.property2` (пример `position.x`), элемент массива `property[index]`. `max_depth` — глубина сериализации результата (по умолчанию 2). Приватные поля читаются (пример `privateStaticVariable`). Тип результата не описан (видели: строки, числа, bool, списки, словари x/y/z/w).
- 📄 Запись вложенного пути не описана. Нам и не нужна (правило: сеттеры только для телепорта T1 и статических настроек runInBackground/autoSync).
- 📄 Параметры методов передаются строками с явными типами (`System.Int32`, `System.Single`, `System.Boolean`); out/ref, enum, Vector3, массивы не описаны.
- 📄 ScriptableObject напрямую найти нельзя (это не объект сцены). Путь к ним — через поле MonoBehaviour, который на них ссылается (наш вариант, ❓) или через статические члены.
- 📄 «Only one test can run on one app simultaneously»: два драйвера одновременно не поддерживаются (у нас это и было `NoAppConnected`).
- 📄 Известная проблема: PressKey не срабатывает, если код читает `wasPressedThisFrame`. В Chop Chop ввод идёт через колбэки Input System (`InputReader`, фаза `Performed`), поэтому к нам, вероятно, не относится.
- 📄 Известная проблема 2.2.x: после модификаторов (Ctrl, Shift) и смены фокуса приложения ввод может перестать отвечать. Это довод против отправки Ctrl+P/Ctrl+Shift+P во время прогона.
- 📄 Про паузу редактора, переподключение после загрузки сцены и `NoAppConnected` документация молчит. Наши данные: после загрузки сцены команды до десятков секунд отвечают `NoAppConnected`; на паузе редактора команда приходит, ответа нет (`guard.py`).

## 3. Что нужно модулям и как это читать (кандидаты, проверить пробой)

Ключевая идея: состояние игры хранится в ScriptableObject-ах, а на них ссылаются компоненты сцены. Читаем через компонент вложенным путём.

| Модуль | Что нужно знать | Кандидат вызова (assembly `Assembly-CSharp`, если не сказано) | Запасной путь |
|---|---|---|---|
| M03 состояние | текущее состояние игры | объект с `UIManager`: `get_component_property("UIManager", "_gameStateManager._currentGameState")` (или `.CurrentGameState`) | косвенно: активные панели UI |
| M03 ввод | какие карты ввода включены | объект с `Protagonist`: `"_inputReader._gameInput.Gameplay.enabled"`, `.Dialogues.enabled`, `.Menus.enabled` | реакция на клавишу (сдвиг, открытие панели) |
| M09 здоровье | текущее/макс. здоровье | `PigChef(Clone)` → `Damageable`: `"_currentHealthSO._currentHealth"`, `"_currentHealthSO._maxHealth"` | уже работало (DTH-02), уточнить путь |
| M12 инвентарь | список предметов и количества | объект с `InventoryManager`: `"_currentInventory._items"` (max_depth 3–4), `"_currentInventory._items[0]._amount"`, `"…[0]._item.name"` | экран инвентаря (как раньше) и `save.chop` |
| M15 квест | текущий квестлайн/шаг | объект с `GameManager`: `"_questManager._currentQuestlineIndex"`, `"_currentStepIndex"`, `"_currentStep.name"` | `save.chop` `_finishedQuestlineItemsGUIds` |
| M04 сохранение | данные сохранения в памяти | объект с `StartGame` (MainMenu): `"_saveSystem.saveData._locationId"`, `"…_finishedQuestlineItemsGUIds"` | файл `save.chop` (надёжно) |
| M18 звук | громкость микшера | объект с `AudioManager`: `call_component_method("AudioManager", "GetGroupVolume", parameters=["MasterVolume"], type_of_parameters=["System.String"])`; поля `_masterVolume` | значения в save.chop |
| M16 катсцены | идёт ли катсцена | объект с `CutsceneManager`: `"_activePlayableDirector"` (не null), `"_activePlayableDirector.state"`, `".time"` | состояние Cutscene из M03 |
| M10 враги | тревога, навигация | `Critter.isPlayerInAlertZone` ✅; `NavMeshAgent` (assembly `UnityEngine.AIModule`): `"isStopped"`, `"remainingDistance"` | позиция врага по времени |
| M14 диалог | открыт ли диалог, текущая реплика, есть ли выбор | ✅ `UIDialogueManager` активен, `DialogueLine` TMP `text`, `UIDialogueChoicesManager` | — |
| M01 загрузки | события загрузки сцен | уведомление `LOADSCENE`/`UNLOADSCENE` | опрос `get_all_loaded_scenes` ✅ |
| Все | ошибки игры | уведомление `LOG` (уровень Error/Exception) | разбор Editor.log ✅ |

## 4. Чего AltTester точно не сделает (обходы уже есть)

| Нельзя | Обход |
|---|---|
| Подписаться на канал событий игры | смотреть следствие: поле, объект, save.chop, лог |
| Передать Vector3 в метод (Raycast) | границы коллайдеров, зонд падением |
| Работать на паузе редактора / при Error Pause / свёрнутом окне | `guard.preflight` (consoleFlags 7683), `restore_window`, runInBackground |
| Запустить Play после Stop | клавиша Ctrl+P извне (`scripts\play_control`, не проверено) или владелец |
| Два драйвера одновременно | одна сессия на игру; очередь по одному заданию |
| Настоящая мышь (камера) | CAM-03 только человеком |
