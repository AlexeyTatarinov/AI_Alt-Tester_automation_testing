# Модули Chop Chop, этап 1 — отчёт (25.11.2026)

**Задание выполнено частично, прогон остановлен.** Этапы A, B, C, D готовы полностью. Из этапа E выполнены 2 проверки из 10, одна (M08-01) частично; остальные не запускались: после теста выхода Field_Hill → Beach (JumpDown) игра зависла, и вернуть её можно только через Stop/Play, а задание их запрещает.

## 1. Сводка простыми словами

**Что AltTester умеет для модулей (этап B, 15 проб):** 13 из 15 проб — МОЖНО, 1 — ОБХОД (инвентарь), 1 — НЕЛЬЗЯ (NavMeshAgent у врага).

| Проба | Итог | Строка вызова, которая сработала / причина |
|---|---|---|
| P01 компоненты объекта | МОЖНО | `get_all_components()` на `PigChef(Clone)`, 0,03 с |
| P02 состояние игры | МОЖНО | `UIManager` → `_gameStateManager._currentGameState` (и `.CurrentGameState`), приходит числом: 0 Gameplay, 1 Pause, 2 Inventory |
| P03 карты ввода | МОЖНО | `Protagonist` → `_inputReader._gameInput.Gameplay/Menus/Dialogues.enabled` (bool) |
| P04 инвентарь | ОБХОД | `_items` с max_depth 2 читается, с 4 — ошибка (префаб). Рабочий путь: `_items.Count`, `_items[i].Item.name`, `_items[i].Amount`; совпало с экраном Tab (6 = 6) |
| P05 здоровье | МОЖНО | `Damageable` → `_currentHealthSO._currentHealth` / `.CurrentHealth` / `_maxHealth` = 50/50 |
| P06 квест | МОЖНО | `GameManager` → `_questManager._currentQuestlineIndex`=0, `_currentStepIndex`=0, `_currentStep.name`=None |
| P07 сохранение в памяти | МОЖНО | в MainMenu объект `StartGameController`, `StartGame` → `_saveSystem.saveData._locationId` и `_finishedQuestlineItemsGUIds`; совпали с файлом |
| P08 громкость | МОЖНО | `GetGroupVolume("MasterVolume"/"MusicVolume"/"SFXVolume")` = 1.0, поля `_masterVolume` и др. |
| P09 катсцена | МОЖНО читать | `CutsceneManager._activePlayableDirector` = None через 0 и 30 с после New Game (интро в эти моменты не идёт) |
| P10 NavMeshAgent врага | НЕЛЬЗЯ | на PlantCritter компонента нет (есть Critter, Attacker, Damageable, StateMachine…); в Field_Hill 0 NavMeshAgent. Обход: позиция врага + `Critter.isPlayerInAlertZone` |
| P11 уведомление LOG | МОЖНО с оговоркой | сообщения приходят, но поле `type` везде 1 (уровень не отличить), в канале есть и строки самого AltTester. За переход 60 сообщений игры: «2 audio listeners» ×51, «no audio listeners» ×9 |
| P12 LOADSCENE/UNLOADSCENE | МОЖНО | UNLOAD Field_Hill +0,67 с, LOAD Beach (Additive) +0,87 с |
| P13 переподключение | МОЖНО | 0 ошибок `NoAppConnected` при опросе каждые 0,5 с, 2 перехода (5,2 и 5,4 с) |
| P14 PATH vs COMPONENT | МОЖНО | `//*[@component=Critter]` = 6, `By.COMPONENT Critter` = 6 |
| P15 AudioListener | МОЖНО | Beach: 5 объектов (`Listener` + 4 `AudioListener`), активный 1; Field_Hill 2, Town_Market 2, MainMenu 1 |

Файлы: `probe.json`, `probe2.json` (P10/P11/P12/P04 повторены вторым прогоном; для каждой пробы ≤ 2 попытки).

**Что нашёл снимок (этап C):** `module_snapshot_MainMenu/Beach/Field_Hill/Town_Market.json`.

| Модуль | Что нашли / что читается | Чего нет |
|---|---|---|
| M01 | SceneLoader, FadeController, LoadingInterfaceController по 1 во всех сценах; `InitializationLoader` 0 (так и должно быть) | — |
| M02 | MainMenu: UIMainMenu, UIMenuManager, UICredits; Gameplay: UIPause, UIPopup | — |
| M03 | состояние и карты ввода читаются (см. P02/P03) | в MainMenu `UIManager` нет |
| M04 | в MainMenu читается `saveData`; в Gameplay-сценах `StartGame` нет | чтение в игре — только файл |
| M05/M07/M09/M11/M12 | Protagonist, CameraManager, Damageable (в Field_Hill 7: игрок + 6 врагов), InteractionManager, InventoryManager по 1 | — |
| M06 | FallCatcher только в Town_Market | в Beach и Field_Hill нет (известно) |
| M08 | `LocationExit/Entrance` читают `_locationToLoad.name`, `_leadsToPath.name`, `_entrancePath.name`. Beach 1/1; Field_Hill 3 выхода (Farms, Beach, Beach_JumpDown)/2 входа; Town_Market 4/5 | — |
| M10 | Field_Hill: 6 PlantCritter; ZoneTriggerController 13 | NavMeshAgent, MovingCritterAttackController |
| M13/котлы | тег `CookingPot`: Beach 1, Town_Market 3 | — |
| M14/M15/M19 | Beach: NPC 1 (BardHare); Town_Market: NPC 19 + StepController 19, NPCMovement 18 | в Field_Hill NPC нет |
| M16 | CutsceneManager везде кроме MainMenu; PlayableDirector Beach 2, Town_Market 1 | активного директора в пробах нет |
| M17/M18 | UISettings*/SettingsSystem, AudioManager, MusicPlayer читаются | — |
| Прочее | `EventSystem` ищется по имени (по компоненту 0); по сцене AudioListener см. P15; `PersistentManagers` как объект по имени не находится (это сцена) | — |

**Вердикты этапа E:**

| ID | Вердикт |
|---|---|
| M01-02 | **OBSERVATION** |
| M18-01 | **PASS** |
| M08-01 | **FAIL (частично, 1 образец)** |
| M10-01, M10-02, M07-01, M03-01, M18-02, M16-01, M06-01 | **BLOCKED** (игра зависла, см. раздел 4) |

## 2. По каждой проверке (числа и пути)

- **M01-02** (`m01_02_m18_01.json`): после 3 переходов Beach→Field_Hill→Town_Market→Beach SceneLoader, AudioManager, EventSystem, PigChef(Clone) = по 1 на каждом шаге. AudioListener: объектов с компонентом 5/2/2/5 (Beach/Field_Hill/Town_Market/Beach), активный всегда 1. По критерию «если 2 — OBSERVATION»: «2 audio listeners» (в логе 51 сообщение за переход). Исключений 0.
- **M18-01** (`m01_02_m18_01.json`): трек сцены (`MusicPlayer._thisSceneSO.musicTrack.name`) Music_Beach / Music_Field / Music_Town; реально играет зацикленно Music_Beach / Music_Glade / Music_Town: 3 разных набора из 3. Замечание: в Field_Hill имя трека (Music_Field) и клип (Music_Glade) различаются — вероятно, разные имена у AudioCue и клипа, не дефект.
- **M08-01** (`m08_01.json`): Field_Hill → Farms: PASS (игрок 0,00 м от LocationEntrance с путём FieldsHill_FieldsFarms, загрузка 2,3 с, CC-67 нет). Field_Hill ToBeach: пропущен (LOC-02 уже PASS). **Field_Hill ToBeach_JumpDown: FAIL** — Beach появился за 0,9 с, но PigChef после этого не найден, затем игра осталась только со сценами PersistentManagers и Gameplay. Итог «N из M»: 1 из 2 проверенных выходов; остальные 8 локаций не проверены. Были два ложных «FAIL/BLOCKED» из-за ошибки моего скрипта (порядок кнопок меню читов менялся, выбор по индексу) — они исправлены и в итог не входят.
- M10-01, M10-02, M07-01, M03-01, M18-02, M16-01, M06-01: скрипты написаны (`scripts\modules\e3…e7`), не запускались.

## 3. Паузы и ошибки

- preflight перед каждой сценой: consoleFlags 7683 всегда, Error Pause не включалась, `alive` True.
- Окно Unity свёрнуто в начале (восстановлено, 2 восстановления за запуск, лимит 5), к концу снова свёрнуто.
- **Ошибки скриптов (не игры):** `NotificationType` импортировался не оттуда; в LOG-пробе читалось поле `level` вместо `type` (повторено вторым прогоном); первые версии `cheat_go` выбирали кнопку по индексу (порядок меню читов не постоянен) — исправлено выбором по тексту; запуск в фоне ограничен 10 минутами.
- Не нарушены: мышь/computer use не использовались, Ctrl+P / Ctrl+Shift+P не нажимались, Stop/Play не трогал, с BardHare не говорил, Initialization не загружал.

## 4. Баг-кандидаты (без Jira)

1. **Soft-lock после выхода Field_Hill → Beach (`LocationExit_ToBeach_JumpDown`), модуль M08/M01.** Шаги: New Game → меню читов Field_Hill → телепорт T1 (autoSync=True) в позицию выхода (−71,0; −6,28; −300,7) → Beach загрузился за 0,9 с, но PigChef нет; дальнейшие клики по меню читов не грузят локации, Esc не открывает паузу, экран чёрный с индикатором загрузки, сцены: PersistentManagers + Gameplay; в Editor.log исключений нет, только спам «There are no audio listeners». Частота: 1 раз из 1, не воспроизведено. Возможная причина — телепорт прямо в триггер (не путь игрока), нужна ручная проверка владельцем (выпрыгнуть вниз в Field_Hill). Для выхода нужен Stop/Play.
2. **Тревога врагов/музыка/катсцены:** новых багов нет. Наблюдение: интро-катсцена в пробах не идёт (директор None) — согласуется с CC-85.
3. **AudioListener:** 2–5 объектов с компонентом в сценах, активный 1; спам «2 audio listeners» при переходах (известное).

## 5. Что не успел и почему

M10-01, M10-02, M07-01, M03-01, M18-02, M16-01, M06-01 и 8 из 9 локаций M08-01: игра в зависшем состоянии, а Stop/Play задание запрещает (требуется владелец). Скрипты готовы: `scripts\modules\e3_m10.py`, `e4_m07_m03.py`, `e5_m18_02.py`, `e6_m16.py`, `e7_m06.py`, `e2_m08.py` (дозапуск продолжает с места, JumpDown стоит проверять первым и с ручным проходом).

## 6. Состояние на завершение

- `save.chop` возвращён из копии, хеши равны копии (проверено). `autoSyncTransforms` = False, `runInBackground` = True (как до задания).
- **Игра НЕ в MainMenu:** зависла (сцены PersistentManagers + Gameplay, чёрный экран). Esc-меню и инвентарь закрыты. Язык не менялся (English). Окно Unity свёрнуто.
- Чтобы продолжать, владельцу нужно перезапустить Play (после этого же получится и чистый Play для этапа 2).
- **С BardHare за весь запуск не разговаривал** — подтверждаю; New Game нажимался 1 раз, Play «грязным» не стал; но из-за перезапуска это уже не важно.
- Обновлено: `cases_state.json` (поля module/level у 50 записей + 10 новых: M01-02, M18-01, M08-01, 7 BLOCKED), `alttester-capabilities-2026-11-25.md`, `modules-decomposition-2026-11-25.md` (только дописано; копии «до» лежат рядом в папке результатов). Jira и Confluence не трогал.
