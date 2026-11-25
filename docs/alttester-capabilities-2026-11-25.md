# AltTester: что умеет, чего не умеет, что проверить пробой (25.11.2026)

Автор: Opus. Источники: (1) установленный SDK `scripts\sdk_smoke\.venv\Lib\site-packages\alttester` (AltTester-Driver 2.4.1, список методов прочитан из `altdriver.py`, `altobject.py`); (2) документация https://alttester.com/docs/sdk/latest/ (страницы commands, known-issues, advanced-usage, faq-troubleshooting; версия на страницах 2.4.1); (3) наши прогоны 1–7b. Не прочитаны в документации: раздел про селекторы By (полный список и фильтры @component/@tag), страницы Python и AltTester Editor, GetVisualElementProperty.

Обозначения: ✅ проверено у нас на живой игре; 📄 только по документации; ❓ неизвестно, проверить пробой (задание `prompts\modules_stage1_20261125.md`, этап B).

## 1. Команды SDK 2.4.1 (Python)

| Группа | Команды | Статус у нас |
|---|---|---|
| Сцены | `get_current_scene`, `get_all_loaded_scenes`, `load_scene`, `unload_scene`, `wait_for_current_scene_to_be` | ✅ список сцен; ❓ `load_scene` (LOAD-00 ни разу) — не нужен |
| Время | `get_time_scale`, `set_time_scale` | ✅ чтение (через Time) |
| Поиск | `find_object(s)`, `find_object(s)_which_contain`, `wait_for_object`, `wait_for_object_to_not_be_present`, `get_all_elements`, `find_object_at_coordinates`; у объекта `find_object_from_object`, `get_parent`, `get_all_components` | ✅ NAME, COMPONENT, PATH, всегда `enabled=False`; ✅ 25.11 `get_all_components` (список словарей `componentName`), ✅ 25.11 фильтр `//*[@component=Critter]` в PATH (6 = 6 с By.COMPONENT) |
| Свойства | `obj.get_component_property(comp, prop, asm, max_depth=2)`, `obj.set_component_property`, `obj.wait_for_component_property`, `driver.get_static_property(…, max_depth=2)`, `driver.set_static_property` | ✅ простые поля и статические (в т.ч. `UnityEditor.LogEntries.consoleFlags`, `EditorApplication.isPlaying`); ✅ 25.11 вложенные пути через ScriptableObject и списки `[i]` (см. раздел 3; `max_depth=4` по спискам с префабами ❌ падает) |
| Методы | `obj.call_component_method(comp, method, asm, parameters, type_of_parameters)`, `driver.call_static_method(…)` | ✅ `Damageable.Kill`, `ReceiveAnAttack(System.Int32)`; ❌ Vector3 в параметрах (Physics.Raycast не вызвать) |
| Текст UI | `obj.get_text`, `obj.set_text` | ✅ TMP и UI.Text |
| Клики UI | `obj.click`, `obj.tap`, `pointer_down/up/enter/exit` | ✅ кнопки меню, выбор Yes/No |
| Клавиши | `press_key(key, power, duration)`, `press_keys`, `key_down/up`, `keys_down/up`, `reset_input` | ✅ с удержанием; ⚠ тап 0,05 с и удержание 0,1 с дают разный результат в диалоге (причина не выяснена) |
| Мышь/тач | `move_mouse`, `click(coords)`, `scroll`, `swipe`, `hold_button`, `tap`, `begin/move/end_touch`, `tilt` | ⚠ эмулированная мышь вращает камеру без правой кнопки (Confluence 327707) |
| Скриншот | `get_png_screenshot(path)` | ✅ |
| Уведомления | `add_notification_listener(NotificationType.LOADSCENE/UNLOADSCENE/LOG/APPLICATION_PAUSED, callback, overwrite)`, `remove_notification_listener` | ✅ 25.11 LOADSCENE/UNLOADSCENE/LOG работают (probe.json P11–P12). 📄 LOG даёт `message`, `stack_trace`, `level` — может заменить разбор Editor.log |
| Настройки драйвера | `set_command_response_timeout`, `set_delay_after_command`, `set_implicit_timeout` (по умолчанию 20 с), `set_server_logging` | ✅ timeout |
| PlayerPrefs | `get/set/delete_player_pref_key` | не нужно (игра хранит в save.chop) |

## 2. Что сказано в документации (главное для нас)

- 📄 Вложенный путь в имени свойства: `property.property2` (пример `position.x`), элемент массива `property[index]`. `max_depth` — глубина сериализации результата (по умолчанию 2). Приватные поля читаются (пример `privateStaticVariable`). Тип результата не описан (видели: строки, числа, bool, списки, словари x/y/z/w).
- 📄 Запись вложенного пути не описана. Нам и не нужна (правило: сеттеры только для телепорта T1 и статических настроек runInBackground/autoSync).
- 📄 Параметры методов передаются строками с явными типами (`System.Int32`, `System.Single`, `System.Boolean`); out/ref, enum, Vector3, массивы не описаны.
- 📄 ScriptableObject напрямую найти нельзя (это не объект сцены). Путь к ним — через поле MonoBehaviour, который на них ссылается (наш вариант, ✅ 25.11 работает) или через статические члены.
- 📄 «Only one test can run on one app simultaneously»: два драйвера одновременно не поддерживаются (у нас это и было `NoAppConnected`).
- 📄 Известная проблема: PressKey не срабатывает, если код читает `wasPressedThisFrame`. В Chop Chop ввод идёт через колбэки Input System (`InputReader`, фаза `Performed`), поэтому к нам, вероятно, не относится.
- 📄 Известная проблема 2.2.x: после модификаторов (Ctrl, Shift) и смены фокуса приложения ввод может перестать отвечать. Это довод против отправки Ctrl+P/Ctrl+Shift+P во время прогона.
- 📄 Про паузу редактора, переподключение после загрузки сцены и `NoAppConnected` документация молчит. Наши данные: после загрузки сцены команды до десятков секунд отвечают `NoAppConnected`; на паузе редактора команда приходит, ответа нет (`guard.py`).

## 3. Что нужно модулям и как это читать (кандидаты, проверить пробой)

Ключевая идея: состояние игры хранится в ScriptableObject-ах, а на них ссылаются компоненты сцены. Читаем через компонент вложенным путём.

| Модуль | Что нужно знать | Кандидат вызова (assembly `Assembly-CSharp`, если не сказано) | Запасной путь | Итог пробы 25.11 |
|---|---|---|---|---|
| M03 состояние | текущее состояние игры | объект с `UIManager`: `get_component_property("UIManager", "_gameStateManager._currentGameState")` (или `.CurrentGameState`) | косвенно: активные панели UI | **МОЖНО** (✅ 25.11). `UIManager` → `get_component_property("UIManager","_gameStateManager._currentGameState","Assembly-CSharp")` приходит ЧИСЛОМ (int); то же через публичное `"_gameStateManager.CurrentGameState"`. Наблюдали: 0 Gameplay, 1 Pause (Esc), 2 Inventory (Tab). По enum `GameState`: 3 Dialogue, 4 Cutscene, 5 LocationTransition, 6 Combat (не наблюдали в пробе). |
| M03 ввод | какие карты ввода включены | объект с `Protagonist`: `"_inputReader._gameInput.Gameplay.enabled"`, `.Dialogues.enabled`, `.Menus.enabled` | реакция на клавишу (сдвиг, открытие панели) | **МОЖНО** (✅ 25.11). `Protagonist` → `"_inputReader._gameInput.Gameplay.enabled"` / `.Menus.enabled` / `.Dialogues.enabled` → bool. Gameplay: G=True M=False D=False; Esc и Tab: G=False M=True D=False. |
| M09 здоровье | текущее/макс. здоровье | `PigChef(Clone)` → `Damageable`: `"_currentHealthSO._currentHealth"`, `"_currentHealthSO._maxHealth"` | уже работало (DTH-02), уточнить путь | **МОЖНО** (✅ 25.11). `PigChef(Clone)` `Damageable`: `"_currentHealthSO._currentHealth"`=50, `".CurrentHealth"`=50, `"_maxHealth"`=50. |
| M12 инвентарь | список предметов и количества | объект с `InventoryManager`: `"_currentInventory._items"` (max_depth 3–4), `"_currentInventory._items[0]._amount"`, `"…[0]._item.name"` | экран инвентаря (как раньше) и `save.chop` | **ОБХОД** (✅ 25.11). `_currentInventory._items` с max_depth 2 читается (список словарей `Amount`/`Item{…}`), с max_depth 4 ❌ `UnknownErrorException … 'transform' on GameObject` (сериализация префаба). Рабочий обход: `"_currentInventory._items.Count"` (=6), `"_currentInventory._items[i].Item.name"`, `"_currentInventory._items[i].Amount"`. `[0]._item.name` тоже работает, `[0]._amount` ❌ (поле зовётся иначе). Совпало с экраном Tab (6 = 6, имена и числа). |
| M15 квест | текущий квестлайн/шаг | объект с `GameManager`: `"_questManager._currentQuestlineIndex"`, `"_currentStepIndex"`, `"_currentStep.name"` | `save.chop` `_finishedQuestlineItemsGUIds` | **МОЖНО** (✅ 25.11, до разговоров). `GameManager` → `"_questManager._currentQuestlineIndex"`=0, `"_questManager._currentStepIndex"`=0, `"_questManager._currentStep.name"`=None (шаг ещё не взят). Имя шага после разговора ещё не проверено. |
| M04 сохранение | данные сохранения в памяти | объект с `StartGame` (MainMenu): `"_saveSystem.saveData._locationId"`, `"…_finishedQuestlineItemsGUIds"` | файл `save.chop` (надёжно) | **МОЖНО** (✅ 25.11, только MainMenu). Объект называется `StartGameController`, компонент `StartGame`: `"_saveSystem.saveData._locationId"`, `"…_finishedQuestlineItemsGUIds"` (5 шт.), `"…_itemStacks"` (max_depth 4) совпали с файлом save.chop. В Gameplay-сценах `StartGame` нет. |
| M18 звук | громкость микшера | объект с `AudioManager`: `call_component_method("AudioManager", "GetGroupVolume", parameters=["MasterVolume"], type_of_parameters=["System.String"])`; поля `_masterVolume` | значения в save.chop | **МОЖНО** (✅ 25.11). `call_component_method("AudioManager","GetGroupVolume","Assembly-CSharp",["MasterVolume"],["System.String"])` → 1.0 (так же Music, SFX; 0,02 с); поля `_masterVolume`, `_musicVolume`, `_sfxVolume` тоже читаются. |
| M16 катсцены | идёт ли катсцена | объект с `CutsceneManager`: `"_activePlayableDirector"` (не null), `"_activePlayableDirector.state"`, `".time"` | состояние Cutscene из M03 | **МОЖНО читать**, значение пока пустое (✅ 25.11). `CutsceneManager` → `"_activePlayableDirector"` = None и через 0 с, и через 30 с после New Game (интро-директор в эти моменты не активен). Что даёт катсцена, смотреть в M16-01. |
| M10 враги | тревога, навигация | `Critter.isPlayerInAlertZone` ✅; `NavMeshAgent` (assembly `UnityEngine.AIModule`): `"isStopped"`, `"remainingDistance"` | позиция врага по времени | `isPlayerInAlertZone` ✅. **НЕЛЬЗЯ** (❌ 25.11) `NavMeshAgent`: у PlantCritter такого компонента нет (список: Transform, 2×CapsuleCollider, Animator, StateMachine, Critter, Attacker, Damageable, CritterAudio, BoneRenderer), в Field_Hill 0 NavMeshAgent. **ОБХОД**: позиция врага по времени + `Critter.isPlayerInAlertZone`. Имя объекта `PlantCritter`, компонент `Critter` (компонента `PlantCritter` нет). |
| M14 диалог | открыт ли диалог, текущая реплика, есть ли выбор | ✅ `UIDialogueManager` активен, `DialogueLine` TMP `text`, `UIDialogueChoicesManager` | — | ✅ (прогоны 1–8, не пробовали заново). |
| M01 загрузки | события загрузки сцен | уведомление `LOADSCENE`/`UNLOADSCENE` | опрос `get_all_loaded_scenes` ✅ | **МОЖНО** (✅ 25.11). LOADSCENE/UNLOADSCENE: при Field_Hill→Beach UNLOAD `Field_Hill` через 0,67 с после клика, LOAD `Beach` (`LoadSceneMode.Additive`) через 0,87 с; имя в поле `scene_name`. Опрос `get_all_loaded_scenes` каждые 0,5 с: **0 ошибок** (`NoAppConnected` не было) при загрузке 5,2 и 5,4 с. |
| Все | ошибки игры | уведомление `LOG` (уровень Error/Exception) | разбор Editor.log ✅ | **МОЖНО с оговоркой** (✅ 25.11). `add_notification_listener(NotificationType.LOG, cb, True)` (импорт `alttester.commands.Notifications.notification_type`) получает `message`, `stack_trace`, `type`. Поле `type` во всех 81 сообщениях = 1 (уровень не отличить) — различать по тексту. В канал попадают и строки самого AltTester (`AltTester|DEBUG…`). За переход 60 сообщений игры, все «There are 2/no audio listeners in the scene» (51 и 9). |

## 4. Чего AltTester точно не сделает (обходы уже есть)

| Нельзя | Обход |
|---|---|
| Подписаться на канал событий игры | смотреть следствие: поле, объект, save.chop, лог |
| Передать Vector3 в метод (Raycast) | границы коллайдеров, зонд падением |
| Работать на паузе редактора / при Error Pause / свёрнутом окне | `guard.preflight` (consoleFlags 7683), `restore_window`, runInBackground |
| Запустить Play после Stop | клавиша Ctrl+P извне (`scripts\play_control`, не проверено) или владелец |
| Два драйвера одновременно | одна сессия на игру; очередь по одному заданию |
| Настоящая мышь (камера) | CAM-03 только человеком |


## Дописано 25.11.2026 (этап D, модульное задание, Sonnet)

Источник: `Reports_2026-11-21\results\modules_stage1_20261125\probe.json` и `probe2.json` (P01–P15), отчёт `report.md` там же. Колонка «Итог пробы 25.11» в разделе 3 заполнена; значки ❓ в разделе 1 заменены на ✅/❌ с датой (`load_scene` не пробовали: не нужен, оставлен ❓).

Дополнительные факты пробы:
- P01 `get_all_components(PigChef(Clone))` ✅: Transform, CapsuleCollider, CharacterController, Animator, StateMachine, Attacker, Damageable, BoneRenderer, ProtagonistAudio, Protagonist, RigBuilder …
- P13 ✅ ошибок `NoAppConnected` при переходе по меню читов нет (опрос 0,5 с, 2 перехода).
- P14 ✅ `By.PATH //*[@component=Critter]` и `By.COMPONENT Critter` дают одно число (6 в Field_Hill).
- P15 ✅ `find_objects(By.COMPONENT,"AudioListener",enabled=False)` в Beach: 5 объектов (`Listener` + 4 `AudioListener`), с `enabled=True` — 1. Другие сцены: Field_Hill 2, Town_Market 2, MainMenu 1.
- Параметр `enabled=False` в `find_objects` возвращает все объекты (и неактивные), `enabled=True` — только активные.
