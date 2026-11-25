# Задание для Claude Code (Sonnet): модули Chop Chop, этап 1 — проба AltTester, снимок модулей, модульные проверки в обычном Play (25.11.2026)

Ты тестировщик-автоматизатор. Работаешь через AltTester Python SDK с игрой Chop Chop, запущенной в Unity Editor (Play). Отчёты пишешь на русском простыми словами. Задание длинное: иди по этапам строго по порядку, после каждого этапа обновляй файлы результатов (если прервёшься, следующий запуск продолжит с места остановки).

## 0. Прочитай перед началом (обязательно, целиком)
1. `C:\Users\Aotat\Desktop\Test_Ai\modules-decomposition-2026-11-25.md` — модули M01…M19, цепочки IT-xx, уровни L1/L2/L3.
2. `C:\Users\Aotat\Desktop\Test_Ai\alttester-capabilities-2026-11-25.md` — что умеет AltTester и кандидаты вызовов для каждого модуля.
3. `C:\Users\Aotat\Desktop\Test_Ai\game_behaviors.md` — известное поведение игры (раздел «Обновление 24.11» главнее старых строк).
4. `C:\Users\Aotat\Desktop\Test_Ai\Reports_2026-11-21\results\opus_review_20261124\cases_state.json` — ведомость: что уже проверено. **Кейсы с вердиктом PASS / NOT_IMPLEMENTED / SUPERSEDED не повторять.** Поле `do_not_repeat_until` обязательно.
5. Скрипты-основа: `scripts\fast_run7\` (`fastlib.py`, `guard.py`, `r4lib.py`: connect, preflight, teleport T1, key, scenes, save_hashes, restore, log_mark, exc_summary). Новые скрипты класть в `scripts\modules\`. Python: `scripts\sdk_smoke\.venv\Scripts\python.exe`.

## 1. Правила (действуют всегда, нарушение = остановка)
- Игру и проект Unity (`C:\Games\ChopChop`) НЕ менять. Сцену Initialization не загружать. Второй Unity.exe не запускать. Окно Unity не закрывать и не сворачивать.
- **Мышь и computer use не использовать.** Ctrl+Shift+P и Ctrl+P не нажимать. Stop/Play не трогать.
- Работать только в `C:\Users\Aotat\Desktop\Test_Ai`. Ключи и пароли не печатать. Jira и Confluence не трогать.
- Через AltTester только чтение. Разрешённые записи: `Physics.autoSyncTransforms` (True на время телепорта T1, в конце False), `Application.runInBackground = True`, позиция игрока (телепорт T1). Вызовы методов игры: только `Damageable.Kill` и `Damageable.ReceiveAnAttack` (как в DTH-01/02) и `AudioManager.GetGroupVolume` (чтение). Никаких других сеттеров и методов.
- Перед КАЖДЫМ этапом и перед каждой сценой: `guard.preflight` (consoleFlags 7683 = Error Pause выключена; если 7686 — СТОП, записать, ждать владельца), проба «живости» (frameCount растёт), окно не свёрнуто (иначе `guard.restore_window`, до 5 раз за запуск, записывать).
- Одно подключение драйвера на всё время (`connect()` один раз). Если другой прогон уже идёт (порт занят, ответы `NoAppConnected` дольше 90 с без загрузки сцены) — СТОП.
- `save.chop`: перед первым изменением сверить хеши с копией `Reports_2026-11-21\evidence\save_backup\20261122_122526`; в конце вернуть из копии и сверить (`r4lib.restore()`).
- **С BardHare не разговаривать вообще** (E рядом с зайцем запрещено): это делает Play «грязным» (CC-90), а чистый Play нужен для следующего этапа. Q в диалоге не нажимать.
- Esc-меню после проверки всегда закрывать (оно блокирует загрузку локаций).
- Не больше 2 попыток на одну проверку. Ошибка скрипта ≠ баг игры: в отчёте разделять.
- Вердикты только по критериям из задания: PASS / FAIL / OBSERVATION (описать, вердикт за владельцем) / BLOCKED (с причиной) / CANNOT (AltTester не может). Не выдумывать.

## 2. Этап A (без игры, 10 мин): ведомость
В `cases_state.json` каждой записи добавить поля `module` (M01…M19 или T01) и `level` (L1/L2/L3) по таблице из раздела 2 и 5 `modules-decomposition-2026-11-25.md` (например INT-03 → M14, L2; INV-10 → M12, L1; LOC-01 → M08, L1; DTH-01 → M09, L1; ENM-03 → M10, L2 (IT-05)). Остальные поля не менять. В `_meta` добавить описание полей. Проверить, что JSON читается.

## 3. Этап B (≈15 мин): проба возможностей AltTester
Сцена: MainMenu → New Game (Beach) → меню читов C → Field_Hill. Скрипт `scripts\modules\probe.py`, результат `Reports_2026-11-21\results\modules_stage1_<дата>\probe.json` и таблица в отчёте. Для каждой пробы: вызов, ответ (первые 300 символов), время, итог: **МОЖНО / НЕЛЬЗЯ / ОБХОД** (+ какой). Пробовать варианты пути: сначала с `_приватным_полем`, потом через публичное свойство; `max_depth` 2, затем 4.

| ID | Что проверить | Как | Где |
|---|---|---|---|
| P01 | `get_all_components` у объекта | на `PigChef(Clone)`; записать список компонентов | Beach |
| P02 | Состояние игры через ScriptableObject | объект с компонентом `UIManager` → `"_gameStateManager._currentGameState"`, затем `"_gameStateManager.CurrentGameState"`; в каком виде приходит enum (число/строка) | Beach (Gameplay), затем открыть Esc (Pause) и Tab (Inventory), закрыть |
| P03 | Карты ввода | объект с `Protagonist` → `"_inputReader._gameInput.Gameplay.enabled"`, `".Menus.enabled"`, `".Dialogues.enabled"` | Beach, затем с открытым Esc |
| P04 | Инвентарь списком | объект с `InventoryManager` → `"_currentInventory._items"` (max_depth 2 и 4), `"_currentInventory._items[0]._amount"`, `"_currentInventory._items[0]._item.name"`; сравнить с экраном инвентаря (Tab) | Beach |
| P05 | Здоровье | `PigChef(Clone)` → `Damageable` → `"_currentHealthSO._currentHealth"`, `"_currentHealthSO.CurrentHealth"`, `"_currentHealthSO._maxHealth"` | Beach |
| P06 | Квест | объект с `GameManager` → `"_questManager._currentQuestlineIndex"`, `"_questManager._currentStepIndex"`, `"_questManager._currentStep"` (имя) | Beach (до разговоров!) |
| P07 | Сохранение в памяти | объект с `StartGame` (только в MainMenu) → `"_saveSystem.saveData._locationId"`, `"_saveSystem.saveData._finishedQuestlineItemsGUIds"`; сравнить с файлом save.chop | MainMenu (сделать ДО New Game) |
| P08 | Громкость микшера | объект с `AudioManager` → `call_component_method("AudioManager","GetGroupVolume","Assembly-CSharp",["MasterVolume"],["System.String"])`, то же `MusicVolume`, `SFXVolume`; поля `_masterVolume`, `_musicVolume`, `_sfxVolume` | MainMenu |
| P09 | Катсцена | объект с `CutsceneManager` → `"_activePlayableDirector"`, `".state"`, `".time"`; сразу после New Game (интро) и через 30 с | Beach после New Game |
| P10 | Агент навигации врага | `PlantCritter` → компонент `NavMeshAgent` (assembly `UnityEngine.AIModule`) → `"isStopped"`, `"remainingDistance"`, `"velocity"` | Field_Hill |
| P11 | Уведомление LOG | `add_notification_listener(NotificationType.LOG, cb, True)`; собрать сообщения за переход по меню читов в Field_Hill; сравнить с новыми строками Editor.log (совпадают ли ошибки/предупреждения) | переход Beach → Field_Hill |
| P12 | Уведомления LOADSCENE / UNLOADSCENE | то же, при переходе; записать имена сцен и время | то же |
| P13 | Переподключение после загрузки сцены | сразу после клика кнопки меню читов вызывать `get_all_loaded_scenes` каждые 0,5 с; записать, сколько секунд ошибки (`NoAppConnected`, таймаут) и какие | переход |
| P14 | Поиск по фильтру в пути | `find_objects(By.PATH, "//*[@component=Critter]")` и `find_objects(By.COMPONENT, "Critter")`: совпадает ли число | Field_Hill |
| P15 | AudioListener | `find_objects(By.COMPONENT, "AudioListener", enabled=False)`: сколько и на каких объектах (лог спамит «2 audio listeners») | Beach |

После этапа B: если P02, P04 или P05 = НЕЛЬЗЯ, дальше использовать запасной путь из таблицы раздела 3 `alttester-capabilities-2026-11-25.md` и записать это.

## 4. Этап C (≈15 мин): снимок модулей
Скрипт `scripts\modules\module_snapshot.py`. Для сцен **MainMenu, Beach, Field_Hill, Town_Market** (переходы: New Game, затем меню читов C): для каждого модуля M01…M19 записать в `module_snapshot_<сцена>.json`:
- найденные объекты и компоненты модуля (по таблице раздела 2 документа модулей: `find_objects(By.COMPONENT, …, enabled=False)`, имя, позиция, enabled);
- значения «оракулов», которые в этапе B оказались МОЖНО (состояние игры, карты ввода, инвентарь, здоровье, квест, громкости, катсцена);
- по сцене: число `LocationExit`/`LocationEntrance` (с `_locationToLoad`/путём, если читается), врагов (`Critter`), NPC (`NPC`, `StepController`), котлов (тег/объект `CookingPot`), `FallCatcher`, `AudioListener`, `EventSystem`, `PersistentManagers`-объектов (`SceneLoader`, `AudioManager`).
Итог этапа: таблица «модуль → что нашли, что читается, чего нет» в отчёте.

## 5. Этап D (10 мин): обновить справки
- В `alttester-capabilities-2026-11-25.md`, раздел 3, добавить столбец «Итог пробы 25.11» (МОЖНО/НЕЛЬЗЯ/ОБХОД + точная строка вызова, которая сработала). Значки ❓ заменить на ✅ или ❌ с датой.
- В `modules-decomposition-2026-11-25.md` в карточках модулей поправить строки «Читать:» под реальные пути (с пометкой «проверено 25.11, probe.json»).
- Ничего не удалять, только дописывать и помечать.

## 6. Этап E (≈60 мин): модульные проверки L1 в обычном Play
Только то, чему **не нужен** чистый Play. Перед каждой проверкой: телепорт в стартовую точку, `log_mark`, после — `exc_summary`. Каждая проверка — новая запись в `cases_state.json` (поля как у существующих + `module`, `level`, `source` = путь отчёта).

| ID | Модуль | Шаги | Критерий |
|---|---|---|---|
| M01-02 | M01 | После 3 переходов через меню читов (Beach → Field_Hill → Town_Market → Beach) посчитать объекты `SceneLoader`, `AudioManager`, `EventSystem`, `AudioListener`, `PigChef(Clone)` | каждого ровно 1 (AudioListener: записать число; если 2 — OBSERVATION «2 audio listeners», не FAIL) |
| M03-01 | M03 | **Таблица «состояние × клавиша»** без диалога. Состояния: Gameplay (Beach), Pause (Esc), Inventory (Tab), Combat (Field_Hill, телепорт в 3 м от PlantCritter, ждать `isPlayerInAlertZone`=True). Клавиши по одной: W (0,3 с), Space (0,1 с), E, F, Q, Tab, Esc, C. После каждой: состояние игры (P02), сдвиг игрока, какие панели открылись, исключения; вернуть исходное состояние. Ожидания: Pause — игрок не двигается, ничего кроме Esc не действует; Inventory — W не двигает; Combat — Tab и E не открывают инвентарь/разговор (по коду GameState) | FAIL: исключение или игра «застряла» (состояние не вернулось за 2 нажатия Esc/Tab). Остальное — таблица OBSERVATION для владельца |
| M07-01 | M07 | `Damageable.Kill` (как DTH-01) → после респавна расстояние камера–игрок через 2 и 5 с; то же после перехода Beach → Field_Hill | ≤ 11 м через 5 с, и d5 ≤ d2 + 0,5 |
| M08-01 | M08 | **Граф переходов.** В каждой из 9 локаций меню читов найти все `LocationExit`; для каждого: `_locationToLoad` (если читается) → телепорт T1 в центр триггера → ждать сцену ≤ 30 с → игрок ≤ 2 м от `LocationEntrance` с тем же путём → нет предупреждения CC-67 → вернуться меню читов. Beach→Field_Hill и Field_Hill→Beach уже PASS (LOC-01/02), не повторять | на каждый выход PASS/FAIL; итог «N из M». CC-67 при переходе — FAIL с пометкой «известный CC-67» |
| M10-01 | M10 | Для каждого вида врага, кроме PlantCritter (Klipper — Mountain_Cave, Gluecose/Slime — Field_Farms, RockCritter — где найдёт снимок): ENM-01 (тревога ≤ 3 с), ENM-02 (на 40 м тревога снята ≤ 3 с), ENM-03 (удары F с 1,2 м до 20 с: враг исчез или здоровье упало; выпал ли `CollectableItem`) | как ENM-01…03 |
| M10-02 | M09+M10 | Стоять в 1,2 м от PlantCritter 20 с без ударов | здоровье игрока уменьшилось (иначе OBSERVATION «враг не атакует») |
| M16-01 | M16 | Back to menu → New Game: каждые 0,5 с 40 с писать состояние игры (P02), директор катсцены (P09), виден ли «PLACEHOLDER», можно ли двигаться (W 0,3 с раз в 5 с) | записать длительность Cutscene и момент возврата управления. FAIL: управление не вернулось за 40 с или исключения. PLACEHOLDER — известный CC-85 |
| M18-01 | M18 | В Beach, Field_Hill, Town_Market: какой клип играет музыка (объект/компонент `MusicPlayer`, AudioSource `clip.name` у источника музыки, если читается) | музыка различается по локациям или OBSERVATION |
| M18-02 | M17+M18 | Settings → Audio: Master в 0 → Save → `GetGroupVolume("MasterVolume")`; вернуть как было → Save | значение микшера изменилось и вернулось; save.chop поменялся (потом восстановить из копии) |
| M06-01 | M06 | (Если осталось время, иначе BLOCKED «нет времени».) Для Field_Hill и Field_Farms: рамка пола (MeshCollider пола локации, bounds) и зонд края как BND-00 на 4 сторонах | наличие пола у края; падение без респавна — OBSERVATION (как CC-82) |

Порядок внутри этапа: M01-02 → M18-01 → M08-01 → M10-01 → M10-02 → M07-01 → M03-01 → M18-02 → M16-01 (последним: New Game) → M06-01.

## 7. Завершение
- Вернуть `save.chop` из копии и сверить хеши; `autoSyncTransforms = False`; язык English; Esc-меню и инвентарь закрыты; игра в MainMenu.
- **С BardHare за весь запуск не разговаривал** — подтвердить в отчёте (нужно для следующего этапа с чистым Play).
- Отчёт `Reports_2026-11-21\results\modules_stage1_<дата>\report.md`:
  1. Сводка (простыми словами): что AltTester может/не может для модулей (таблица этапа B), что нашёл снимок, вердикты этапа E (PASS/FAIL/OBSERVATION/BLOCKED/CANNOT).
  2. По каждой проверке одна строка с числами и путём к json.
  3. «Паузы и ошибки» (preflight, восстановления окна, сбои скриптов отдельно от игры).
  4. «Баг-кандидаты» (без Jira): что, где, шаги, как часто, к какому модулю.
  5. «Что не успел» и почему.
  6. «Состояние на завершение».
- Обновить `cases_state.json` (новые записи, `source` с путём отчёта).
- Jira и Confluence не трогать.

## 8. Что дальше (не делать в этом задании)
Этап 2 — проверки, которым нужен чистый Play (владелец перезапускает Play): черновики `queue\inbox_drafts\d01_clean_dialog_recipe_cook.md` (IT-03 разговоры → IT-04 готовка SweetCream = 3 Seed → IT-02 подтверждение CC-90) и `d02_clean_dialog_no_branch.md` (ветка No, Continue). Этап 3 — сквозной E2E-01.
