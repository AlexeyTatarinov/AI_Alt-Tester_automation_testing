# Chop Chop: разбиение игры на модули и план проверок по модулям (25.11.2026)

Автор: Opus. Источник: код и ассеты игры `C:\Games\ChopChop\UOP1_Project\Assets` (295 скриптов, сцены, ScriptableObjects; только чтение), отчёты прогонов 1–7b и ведомость `Reports_2026-11-21\results\opus_review_20261124\cases_state.json`, Jira CC-67…CC-90. Живую игру через AltTester в этот раз **не опрашивал**: всё нужное видно в коде, а второе подключение к драйверу мешает другим сессиям (известная проблема `NoAppConnected`). Снимок модулей на живой игре — первый шаг для Sonnet (раздел 7).

Как читать: раздел 1 — короткая картина. Раздел 2 — карточка на каждый модуль. Раздел 3 — как модули связаны и какие цепочки проверять вместе. Разделы 4–6 — уровни проверок, что уже покрыто, как переложить Jira. Раздел 7 — готовый план для Sonnet.

---

## 1. Коротко

1. Игра собрана из независимых систем, которые **не вызывают друг друга напрямую**, а общаются через «каналы событий» (ScriptableObject-каналы, 66 штук в `ScriptableObjects/EventChannels`). Это удобно для нас: у каждого модуля есть чёткие входы и выходы, и модуль можно проверить отдельно, а потом проверить стыки.
2. Предлагаю **18 игровых модулей** в 5 группах + 1 служебный (наши инструменты). Список ниже.
3. **Модульная проверка (L1)** = один модуль, всё остальное не меняется, результат читаем из состояния самого модуля. **Интеграционная (L2)** = цепочка из 2–4 модулей по одному каналу событий, проверяем результат на каждом звене. **Сквозная (L3)** = путь игрока от New Game до готового блюда.
4. Самые рискованные стыки (там уже 5 из 10 наших багов): **«Back to menu → New Game/Continue»** (повторные подписки), **«диалог → квест → инвентарь → сохранение»**, **«ввод ↔ состояние игры»** (что можно нажимать в диалоге, бою, паузе).
5. Две находки из кода прямо сейчас:
   - **Рецепт SweetCream_Recipe = 3 × Seed → SweetCream_Dish** (`ScriptableObjects/Inventory/Items/QuestItems/SweetCream_Recipe.asset`). Семян в стартовом инвентаре 20 (после ответа Yes 19), значит **готовку COOK-01 можно проверить сразу после получения рецепта**.
   - **Вероятная причина CC-90** (гипотеза по коду, не проверена): `QuestManagerSO.StartGame()` (QuestManagerSO.cs:45) подписывается на 4 канала при каждом старте игры, а отписывается только в `OnDisable` ScriptableObject-а, который вызывается при остановке Play, но не при выходе в меню. После «Back to menu → New Game» обработчик `EndDialogue` срабатывает дважды: первый завершает шаг, второй работает с уже пустым `_currentStep` → NullReference в QuestManagerSO.cs:235, а квест «перескакивает». Это совпадает со всеми симптомами CC-90 и CC-88 и объясняет, почему лечит только Stop/Play. Следствие: эксперимент «Continue вместо New Game» (черновик d02, шаг 3) скорее всего не поможет (подписки те же), а в собранной игре баг есть у обычного игрока.

---

## 2. Модули

Группы: **A. Основа** (запуск, сцены, ввод, состояние, сохранение), **B. Персонаж и мир**, **C. Взаимодействие и предметы**, **D. Сюжет**, **E. Интерфейс и оформление**, **T. Инструменты теста** (не игра).

### Сводная таблица

| ID | Модуль | Группа | Главный код (Assets/Scripts) | Наши кейсы сейчас | Баги Jira | Покрытие |
|---|---|---|---|---|---|---|
| M01 | Запуск и загрузка сцен | A | SceneManagement/InitializationLoader, SceneLoader, StartGame; UI/FadeController, LoadingInterfaceController; сцены Initialization, PersistentManagers, Gameplay | MENU-08, SCENE-01/02, LOC-03 (время загрузки) | CC-67 | среднее |
| M02 | Главное меню и пауза | E | UI/UIMainMenu, UIMenuManager, UIPause, UIPopup, UICredits; Menu/* | MENU-*, PAUSE-01, MENU-08 | — | хорошее |
| M03 | Ввод и состояние игры | A | Input/InputReader, GameInput; Gameplay/GameStateSO (7 состояний: Gameplay, Pause, Inventory, Dialogue, Cutscene, LocationTransition, Combat) | косвенно: PAUSE-01, ENM-01, DLG-11, INT-02 | CC-81, CC-87 | **слабое** |
| M04 | Сохранение | A | SaveSystem/SaveSystem, FileManager, Save (поля: `_locationId`, `_itemStacks`, `_finishedQuestlineItemsGUIds`, громкости, графика, `_currentLocale`) | SAVE-05, SAVE-06, SET-01, хеши в каждом прогоне | — | среднее (нет Continue) |
| M05 | Движение персонажа | B | Characters/Protagonist; StateMachine/Actions (Horizontal, Aerial, Ascend/Descend, Slide, GroundGravity, Rotate) и Conditions | MOVE-*, GUARD-01 | — | хорошее |
| M06 | Коллизии и границы мира | B | CharacterController, коллайдеры сцен, SceneManagement/FallCatcher | COLL-02, BND-00…07, BND-05b | CC-82 | хорошее (Beach), нет других локаций |
| M07 | Камера | B | Camera/CameraManager, ShakeCamActionSO | CAM-01…04, TP-02 | — | среднее |
| M08 | Локации, переходы и спавн | A/B | SceneManagement/LocationExit, LocationEntrance, PathSO/LocationSO; Gameplay/SpawnSystem | LOC-01/02/03, TP-00/01 | CC-67 | хорошее (Beach↔Field_Hill), нет цепочки всех выходов |
| M09 | Здоровье, урон, смерть, респавн | B | Characters/Damageable, HealthSO, configs Health; actions ResetHealth, DestroyEntity; UI/UIHealthBarManager, UIHeartDisplay | DTH-01…04 | CC-84 | хорошее |
| M10 | Враги и бой | B | Characters/Critter, Attack, Attacker, ZoneTriggerController, MovingCritterAttackController; ChasingTarget, StopAgent; DropGroup, DropReward | ENM-01…03 | — (NavMesh «Stop» в Forest не заведён) | среднее (только PlantCritter) |
| M11 | Взаимодействие | C | Interaction/InteractionManager, Interaction; UI/UIInteraction, InteractionSO (типы: PickUp, Cook, Talk) | INT-01…07 | — | хорошее |
| M12 | Инвентарь и предметы | C | Inventory/InventoryManager, InventorySO, ItemSO, ItemStack, CollectableItem, ItemPicker; UI/Inventory/* (вкладки, UIActionButton Q) | INV-10, INV-11, INV-12, INT-06 | CC-81 | среднее |
| M13 | Готовка | C | InventoryManager.CookRecipe, ItemRecipeSO; UIManager (открытие у котла), UIItemForAnimation | INT-04/05, INV-13 (частично) | — | **нет реальной готовки** |
| M14 | Диалоги | D | Dialogues/DialogueManager, DialogueDataSO, ActorSO, DialogueTrigger; UI/Dialogue/* (выборы Yes/No) | INT-03, DLG-10b, DLG-11 | CC-87, CC-88 | среднее (только BardHare) |
| M15 | Квесты и награды | D | Quests/QuestManagerSO, StepController, QuestlineSO/QuestSO/StepSO (6 квестлайнов, 14 шагов); Gameplay/GameManager | QST-10, косвенно DLG-10 | CC-90, CC-88 | **слабое** (только QL1 шаги 1–2) |
| M16 | Катсцены | D | Cutscenes/CutsceneManager, CutsceneTrigger, TimelineBinder, DialogueTrack; 6 каналов StartCinematic-* | нет (PLACEHOLDER видели) | CC-85 | **нет** |
| M17 | Настройки и локализация | E | Systems/Settings/*, UI/Settings/*; Localization/*, таблицы в LocalizationFiles | L10N-01/02, SET-01 | CC-86, CC-89 | среднее (нет графики, звука) |
| M18 | Звук и музыка | E | Audio/AudioManager, MusicPlayer, SoundEmitter*, AudioCueSO | нет (AUD убрали из плана) | — | **нет** |
| M19 | NPC (кроме диалога) | B/D | Characters/NPC, NPCMovement (Pathway, Roaming), NPCMovementSwitcher | нет | — | **нет** |
| T01 | Инструменты теста | T | AltTester, меню читов (EditorTeleporter, только Editor), телепорт T1, guard.py, restart_play.py | TP-00, LOC-03 (кнопки), GUARD-01 | CC-70, CC-83 | — (находки здесь не баги игры) |

### Карточки модулей

Формат карточки: **что делает**; **входы/выходы** (каналы событий: кто посылает, кто слушает); **что читать через AltTester** (наблюдаемое состояние — это и есть «оракул» проверки); **нужен ли чистый Play**; **пробелы** — какие модульные проверки добавить (ID с префиксом модуля).

**M01 Запуск и загрузка сцен.** Initialization грузит PersistentManagers (AudioManager, SceneLoader, FadeController, LoadingScreen, SettingsSystem) и MainMenu. SceneLoader по каналам `LoadLocation`/`LoadMenu` выгружает и грузит сцены, затем шлёт `OnSceneReady` (его слушают SpawnSystem, LocationEntrance, MusicPlayer, UIManager) и `ToggleLoadingScreen`. Читать: `get_all_loaded_scenes`, время до появления PigChef, активность `LoadingScreen`, `FadeController`. Чистый Play: нет. Пробелы: M01-01 холодный старт (Play → MainMenu ≤ N с, 0 ошибок кроме известных Missing Prefab); M01-02 каждая загрузка оставляет ровно один набор менеджеров (PersistentManagers 1, EventSystem 1) — частично MENU-08.

_[проверено 25.11, probe.json: опрос `get_all_loaded_scenes` каждые 0,5 с при переходе по меню читов — 0 ошибок, загрузка 5,2–5,4 с; уведомления LOADSCENE/UNLOADSCENE работают (UNLOAD +0,67 с, LOAD +0,87 с, поле `scene_name`); `SceneLoader`, `FadeController`, `LoadingInterfaceController`, `AudioManager` — по 1 в каждой сцене]_

**M02 Меню и пауза.** Кнопки New Game/Continue (`StartNewGame`, `ContinueGameEvent` → StartGame), Settings, Credits (`CreditsFinishRollingEvent`), Exit; пауза `OnPauseOpened` (timeScale 0), Back to menu (`LoadMenu`). Читать: активные экраны (`Pause_Screen`, `UIPopup`), `Time.timeScale`. Пробелы: M02-01 Continue без сохранения (кнопка неактивна или ведёт куда-то?), M02-02 Credits до конца и возврат, M02-03 пауза в каждом состоянии (бой, инвентарь, диалог — частично: Esc в диалоге открывает паузу).

_[проверено 25.11, снимок: `Pause_Screen` ищется `By.NAME` (Esc → объект активен); `UIMainMenu`, `UIMenuManager`, `UICredits` есть только в MainMenu, `UIPause` и `UIPopup` — в Gameplay-сценах]_

**M03 Ввод и состояние игры.** InputReader переключает карты ввода (Gameplay, Menus, Dialogues, Cheats) и шлёт C#-события (Move, Jump, Attack, Interact, AdvanceDialogue, OpenInventory, InventoryActionButton, Pause, CheatMenu…). GameStateSO хранит текущее состояние и запрещает действия: в Combat нельзя инвентарь и диалог, в Dialogue нельзя двигаться и т.д. Этот модуль — источник CC-81 (Q в диалоге) и CC-87 (Space в «мёртвой» фазе). Читать: `GameStateSO.CurrentGameState` (через объект, на котором висит ссылка, напр. InteractionManager/UIManager — уточнить в снимке), активная карта ввода (`InputReader`/`GameInput` поле `asset`, enabled maps). Пробелы (главный пробел проекта): **M03-01 таблица «состояние × клавиша»**: для 7 состояний × 8 клавиш (WASD, Space, E, F, Q, Tab, Esc, C) записать, что происходит; ожидание — из кода (`IsInSpecificGameStateSO`, `InputReader.Enable*Input`). Это одна табличная проверка вместо десятков разрозненных; она поймает CC-81/CC-87-подобные баги системно.

_[проверено 25.11, probe.json P02/P03: **Читать:** `UIManager` → `"_gameStateManager._currentGameState"` (и публичное `".CurrentGameState"`) приходит числом: 0 Gameplay, 1 Pause (Esc), 2 Inventory (Tab); 3 Dialogue, 4 Cutscene, 5 LocationTransition, 6 Combat — по enum, не наблюдали. Карты ввода: `Protagonist` → `"_inputReader._gameInput.Gameplay.enabled"` / `.Menus.enabled` / `.Dialogues.enabled` (bool): Gameplay True/False/False, при Esc и Tab False/True/False. `UIManager` и `Protagonist` есть только в Gameplay-сценах]_

**M04 Сохранение.** Пишет `save.chop` (JSON) при New Game, загрузке локации, изменении инвентаря, завершении шага/квеста/квестлайна, Save в настройках. Continue читает инвентарь, квесты (`LoadSavedQuestlineStatus`) и локацию (`_locationId` через Addressables). Читать: файл `save.chop` (поля выше) и хеши. Пробелы: **M04-01 Continue** (ни разу не проверяли: сохранить в Field_Hill с рецептом → Back to menu → Continue → та же локация, тот же инвентарь, тот же шаг квеста), M04-02 отсутствующий/битый save.chop (BC-8, низкий приоритет).

_[проверено 25.11, P07: **Читать:** в MainMenu компонент `StartGame` (объект `StartGameController`) → `"_saveSystem.saveData._locationId"`, `"…_finishedQuestlineItemsGUIds"`, `"…_itemStacks"` — совпали с save.chop. В Gameplay-сценах `StartGame` нет, там читать файл. После New Game `_locationId` в памяти меняется (WriteEmpty)]_

**M05 Движение.** Protagonist + машина состояний (ходьба, бег, прыжок, падение, скольжение `Sliding` на крутом склоне), CharacterController (slope 50, step 0.15). Покрыто MOVE и GUARD-01. Пробелы: M05-01 прыжок (высота, приземление), M05-02 скольжение со склона заканчивается (не «вечный Sliding», как CC-49).

**M06 Коллизии и границы.** Покрыто для Beach (COLL-02, BND). Пробелы: M06-01 «зонд края» (BND-00) для остальных 9 локаций — только чтение рамок полов и одна проба падения; FallCatcher есть только в Town_Market, значит в каждой локации с краем возможен CC-82-подобный баг.

_[проверено 25.11, снимок: `FallCatcher` есть только в Town_Market (1); в Beach, Field_Hill, MainMenu 0. `CharacterController` у игрока 1 (в Beach найдено 4, причина не выяснена)]_

**M07 Камера.** CameraManager следует за якорем игрока (`PlayerInstantiated`/TransformAnchor), `CameraShake`. Покрыто CAM, TP-02. Пробелы: M07-01 камера после респавна и после смены локации (новый PigChef — новый якорь).

**M08 Локации и спавн.** LocationExit (триггер) → сохранение `_locationId` и путь `PathSO` → LoadLocation → SpawnSystem ставит игрока у LocationEntrance с тем же путём, иначе в DefaultSpawn с предупреждением (CC-67). Покрыто LOC-01/02/03. Пробелы: **M08-01 граф переходов**: все LocationExit во всех 10 локациях (телепорт в каждый выход, проверка «пришёл к входу с тем же путём, нет CC-67»). Сейчас проверен 1 выход из ~20.

_[проверено 25.11, снимок: `LocationExit` → `"_locationToLoad.name"` и `"_leadsToPath.name"` читаются; `LocationEntrance` → `"_entrancePath.name"`. Beach: 1 выход (Field_Hill), 1 вход; Field_Hill: 3 выхода (Field_Farms, Beach ×2 — `LocationExit_ToBeach` и `LocationExit_ToBeach_JumpDown`), 2 входа; Town_Market: 4 выхода (Town_Inner ×2, Mountain_Path, Field_Farms), 5 входов (в т.ч. `FromLakeFall`). `SpawnSystem` 1 в Gameplay-сценах]_

**M09 Здоровье и смерть.** Damageable (урон `ReceiveAnAttack`, лечение `Cure`, `DeathEvent`, `UpdateHealthUI`), Dying 4 с → респавн. Покрыто DTH. Пробелы: M09-01 лечение едой (`_restoreHealth` из UIInventory, `_healthResorationValue` у блюд) — интеграция с инвентарём; M09-02 смерть от врага (не через Kill).

_[проверено 25.11, P05: **Читать:** `Damageable` у `PigChef(Clone)` → `"_currentHealthSO._currentHealth"` / `".CurrentHealth"` / `"_maxHealth"` = 50/50 на старте. В Field_Hill `Damageable` у 7 объектов (игрок + 6 врагов)]_

**M10 Враги и бой.** Critter: зона тревоги → состояние Combat → атака → урон; удар F игрока → смерть врага → выпадение (`DropReward`, шанс у PlantCritterReward = 1). Покрыто ENM на PlantCritter. Пробелы: M10-01 те же 3 проверки для Klipper (Mountain_Cave), Gluecose/Slime (Field_Farms), RockCritter; M10-02 враг наносит урон (здоровье падает) — в ENM-01 урона не было за 10 с; M10-03 ошибка NavMesh «Stop» при загрузке Forest (заведение в Jira — решение владельца).

_[проверено 25.11, P10/P14: компонент врага `Critter` (имя объекта `PlantCritter`, компонента `PlantCritter` нет); `Critter.isPlayerInAlertZone` читается. **`NavMeshAgent` на враге нет** (в Field_Hill 0), `isStopped`/`remainingDistance` читать нельзя: оракул навигации = позиция врага по времени. Field_Hill: 6 `Critter`, все PlantCritter. `By.PATH //*[@component=Critter]` и `By.COMPONENT Critter` дают одно число]_

**M11 Взаимодействие.** Триггер InteractionDetector перед персонажем, теги NPC/CookingPot/Pickable, подсказка `UIInteraction`, E только в Gameplay. Покрыто INT-01…07 (радиус разговора 1,56 м лицом, подбора 0,68–1,06 м). Пробелов почти нет: M11-01 две цели в зоне одновременно (что выбирается).

**M12 Инвентарь.** InventorySO + InventoryManager (Add/Remove/Use/Equip/Reward/Give по каналам), вкладки (Use=1, 0, Recipe=2), кнопка Q (UIActionButton). Equip-обработчик пустой (не реализовано). Покрыто INV-10/11. Пробелы: M12-01 использование еды (лечит, количество −1), M12-02 переполнение/нулевое количество (последний предмет исчезает со слота), M12-03 вкладки по кругу (Y на последней вкладке, UX из прогона 4).

_[проверено 25.11, P04: **Читать:** `InventoryManager` → `"_currentInventory._items.Count"`, `"…_items[i].Item.name"`, `"…_items[i].Amount"`; `_items` целиком только с max_depth 2 (при 4 ошибка сериализации префаба). Совпало с экраном Tab (6 предметов: PhoenixChick 1, Seed 20, SlimeCritterEgg 20, GoldenEgg 20, RockCritterEgg 20, SpecialSpoon 1)]_

**M13 Готовка.** У котла E → `OnCookingStart` → UIManager открывает инвентарь на рецептах → выбор → Q → `CookRecipe` → InventoryManager снимает ингредиенты, добавляет блюдо, сохраняет; анимация `UIItemForAnimation`. Рецепты: SweetCream (3 Seed), RockCandy (PhoenixChick + SweetCream_Dish), SweetDough, SavoryDough, SpicySauce, SpicyCake, CakeWithRockCandy. Пробелы: **M13-01 готовка SweetCream** (Seed −3, Dish +1, save.chop изменился, 0 исключений); M13-02 нехватка ингредиентов (кнопка неактивна); M13-03 готовка вдали от котла заблокирована (уже INT-05).

**M14 Диалоги.** DialogueManager получает `StartDialogue` (от StepController), листает строки по AdvanceDialogue, показывает выборы (`ShowChoicesUIEvent`), шлёт `EndDialogueWithType`, `MakeWinningChoice`/`MakeLosingChoice`. Подписывается в Start и не отписывается (BC-1). Покрыто только BardHare. Пробелы: M14-01 диалог другого NPC (BardHare_Market, Felfel, Terra, Ayud, Cerise, ChefComb), M14-02 ветка No.

**M15 Квесты.** QuestManagerSO: 6 квестлайнов, шаги типа Dialogue/CheckItem/GiveItem, награды (`RewardItemEvent`), завершения пишут сохранение; GameManager реагирует на конец квестлайнов (рецепт RockCandy, открыть город, воспоминание Cerise, выбор блюд). Состояние живёт в ScriptableObject-ах (сбрасывается Stop/Play, не сбрасывается выходом в меню — CC-90). Пробелы: **M15-01 цепочка QL1 целиком** (сейчас пройдены только шаги 1–2), M15-02 шаг CheckItem/GiveItem (отдать блюдо NPC), M15-03 повторный разговор после завершения шага (шаг не засчитывается дважды).

_[проверено 25.11, P06: **Читать:** `GameManager` → `"_questManager._currentQuestlineIndex"`=0, `"_questManager._currentStepIndex"`=0, `"_questManager._currentStep.name"`=None до разговоров. `StepController`: Beach 1, Town_Market 19, Field_Hill 0]_

**M16 Катсцены.** Timeline + DialogueTrack, триггеры `StartCinematic-*` (IntroBeach, TownIntro, RockCandyDiscovery, SlimeCrittersAttack, Sweet/SavoryDishTasting). Во время катсцены состояние Cutscene, ввод отключён. Пробелы: M16-01 интро Beach после New Game (сейчас видим только PLACEHOLDER, CC-85): играет ли, сколько длится, возвращает ли управление.

_[проверено 25.11, P09: **Читать:** `CutsceneManager` → `"_activePlayableDirector"` (None, когда катсцены нет; через 0 и 30 с после New Game тоже None). `PlayableDirector` в сценах: Beach 2, Town_Market 1, Field_Hill 0; `CutsceneTrigger`: Beach 2, Town_Market 1]_

**M17 Настройки и локализация.** Вкладки Audio/Graphics/Language, Save пишет в save.chop. Покрыто языки (FAIL), Save. Пробелы: M17-01 громкости доходят до AudioManager (интеграция с M18), M17-02 графика (разрешение, полный экран) сохраняется после перезапуска.

**M18 Звук.** AudioManager (громкости Master/Music/SFX), MusicPlayer (музыка по `OnSceneReady`, пауза), звуки шагов/ударов (AudioCue). Читать: громкость микшера, активные AudioSource. Пробелы: M18-01 музыка меняется по локации, M18-02 громкость 0 действительно глушит (значение микшера). Предупреждение «2 audio listeners» спамит лог (раньше — до 33 КБ/с): записать как наблюдение.

_[проверено 25.11, P08/P15: **Читать:** `AudioManager.GetGroupVolume("MasterVolume"|"MusicVolume"|"SFXVolume")` (call_component_method, System.String) = 1.0; поля `_masterVolume`, `_musicVolume`, `_sfxVolume`. `AudioListener`: Beach 5 объектов (активный 1), Field_Hill 2, Town_Market 2, MainMenu 1; лог-сообщения «2 audio listeners» (51) и «no audio listeners» (9) пришли за один переход Field_Hill→Beach]_

**M19 NPC.** Движение горожан по маршрутам (Pathway/Roaming), остановка для разговора. Пробелы: M19-01 горожане не застревают (позиция меняется за 30 с) — низкий приоритет.

_[проверено 25.11, снимок: `NPC` Beach 1 (BardHare), Town_Market 19 (BardHare_Market, Felfel, 17 Townsfolk), `NPCMovement` Town_Market 18, `NPCMovementSwitcher` 0; теги `NPC` совпадают с числом компонентов `NPC`]_

**T01 Инструменты.** Не игра: находки здесь в Jira как баги игры не идут. Ограничения уже известны: T1 только с autoSync, меню читов только телепорты, Forest_Entrance нет, окно сворачивается, Error Pause.

---

## 3. Связи между модулями и интеграционные цепочки

### 3.1 Кто кого слушает (из кода: `RaiseEvent` / `OnEventRaised +=`)

```
M02 Меню ──StartNewGame/Continue──▶ StartGame ──▶ M04 Сохранение (WriteEmpty, SetNewGameData ─▶ M15 ResetQuestlines)
                                         └──LoadLocation──▶ M01 SceneLoader ──OnSceneReady──▶ M08 Spawn, M18 Music, UIManager
M08 Spawn ──PlayerInstantiated──▶ M07 Камера, M16 TimelineBinder
M08 LocationExit ──LoadLocation──▶ M01 ;  M04 пишет _locationId
M03 Ввод ──Interact──▶ M11 Взаимодействие ──StartTalking──▶ M15 StepController ──StartDialogue──▶ M14 Диалог
M14 ──EndDialogue / Win / Lose / ContinueStep──▶ M15 QuestManagerSO ──Reward/GiveItem──▶ M12 Инвентарь ──▶ M04
M15 ──Questline*Over──▶ GameManager (рецепт RockCandy, открыть город)
M11 ──OnCookingStart──▶ UIManager ──▶ M12/M13 UIInventory ──CookRecipe──▶ M12 InventoryManager ──▶ M04
M11 ──OnObjectPickup──▶ ItemPicker ──AddItem──▶ M12 ──▶ M04
M10 Враг ──атака──▶ M09 Damageable ──DeathEvent/UpdateHealthUI──▶ HUD, респавн (M08 Spawn)
M10 Враг умер ──DropReward──▶ CollectableItem на земле ──▶ M11
M10 ──CombatState──▶ M03 GameState ──▶ HUD сердца, запреты ввода
M12 UIInventory ──Cure──▶ M09 (еда лечит)
M17 Настройки ──Change*Volume──▶ M18 AudioManager ;  ──SaveSettings──▶ M04
M16 Катсцены ◀──PlayCutscene/PlayDialogue──▶ M14, ──▶ M03 (состояние Cutscene)
```

### 3.2 Интеграционные цепочки (L2) — что проверять вместе

| ID | Цепочка | Модули | Оракулы на звеньях | Сейчас | Риск |
|---|---|---|---|---|---|
| IT-01 | New Game | M02→M04→M15→M01→M08→M16 | save.chop пуст по квестам; сцены; PigChef у DefaultSpawn; интро/PLACEHOLDER; предупреждение CC-67 | частично (SAVE-06, MENU-08) | CC-67, CC-85 |
| IT-02 | **Back to menu → New Game / Continue (повторные подписки)** | M02→M01→M15/M14/M12 | после второго старта: первый диалог 17 реплик, 0 исключений, Q −1 предмет, награда +1 | DLG-10 = CC-90 | **высокий**: CC-88, CC-90, BC-1…BC-4 |
| IT-03 | **Разговор → квест → награда → сохранение** | M11→M15→M14→M15→M12→M04 | E → диалог; выбор Yes; Seed −1, рецепт +1; GUID шага в save.chop | INT-03, DLG-10b | CC-87/88/90 |
| IT-04 | **Готовка** | M11→M13→M12→M04 | у котла инвентарь на рецептах; Seed −3, SweetCream_Dish +1; save изменился; анимация | **нет** | — |
| IT-05 | Бой → дроп → подбор → инвентарь | M10→M09→M11→M12→M04 | тревога, Combat; враг исчез; CollectableItem появился; подбор +1; save | ENM-03, INT-06 | — |
| IT-06 | Урон → смерть → респавн → HUD → камера | M10/M09→M08→M07 | здоровье, сердца, новый PigChef, камера догнала | DTH-01/03 (без камеры) | CC-84 |
| IT-07 | Переход локации | M08→M04→M01→M08→M18/M07 | `_locationId`, вход тем же путём, музыка сменилась, камера | LOC-01/02 (без музыки) | CC-67 |
| IT-08 | Пауза поверх всего | M03→M02 в каждом состоянии | timeScale 0, ввод игры не проходит, возврат | PAUSE-01 (только Gameplay) | меню паузы блокирует загрузку |
| IT-09 | Состояние × ввод | M03 с M10/M12/M14/M16 | таблица M03-01 | **нет** | CC-81, CC-87 |
| IT-10 | Настройки → звук/язык → сохранение | M17→M18/M04 | громкость в микшере; язык после New Game и Continue | L10N, SET-01 | CC-86/89 |
| IT-11 | Еда лечит | M12→M09→HUD | здоровье +N, сердца, предмет −1 | **нет** | — |
| IT-12 | Квест отдать предмет | M15(GiveItem)→M12→M04 | блюдо −1, шаг завершён, следующий шаг | **нет** | — |

### 3.3 Сквозные сценарии (L3)

| ID | Путь игрока | Модули | Нужен чистый Play |
|---|---|---|---|
| E2E-01 | New Game → интро → BardHare (1-й разговор) → 2-й разговор Yes → рецепт → котёл → SweetCream → отдать (если шаг GiveItem) → следующий шаг | все группы C, D + M04 | да |
| E2E-02 | E2E-01 до рецепта → выход в Field_Hill → бой → дроп → назад → Continue после Back to menu | M04, M08, M10, M12 | да |

---

## 4. Уровни проверок и правила

| Уровень | Что это | Правило изоляции | Где результат |
|---|---|---|---|
| L1 модуль | Одна функция одного модуля | Остальные модули не трогаем; входное состояние фиксируем (телепорт, копия save.chop); оракул — состояние самого модуля | `cases_state.json`, поле `module` |
| L2 интеграция | Цепочка IT-xx | Проверяем каждое звено, а не только конец (иначе не понять, где сломалось) | то же, `level: L2` |
| L3 сквозной | E2E-xx | Только после того, как все L1 и L2 его модулей зелёные | то же |

Ограничения инструмента (важно для оракулов): AltTester не умеет подписаться на канал событий, поэтому «событие произошло» проверяем по его следствию (изменилось поле, появился объект, изменился save.chop, строка в Editor.log). Каждая проверка пишет: модуль, уровень, нужен ли чистый Play, версию метода (M-TP1, M-DLG2…).

Порядок работы: сначала L1 по модулям с пробелами, потом L2 по рискованным цепочкам, потом L3. Внутри одного чистого Play — все проверки, которым нужен свежий квест (группа D и M13), подряд.

---

## 5. Что уже покрыто (по модулям)

Зелёное (дальше только регресс при изменениях): M05 движение, M06 Beach, M07 камера, M09 смерть, M11 взаимодействие, M08 Beach↔Field_Hill, M02 меню.
Жёлтое (есть, но узко): M01, M04 (нет Continue), M10 (один вид врагов), M12, M14 (один NPC), M17.
Красное (почти нет): **M03 ввод×состояние, M13 готовка, M15 квесты дальше шага 2, M16 катсцены, M18 звук, M19 NPC**.

Баги по модулям: M03 — CC-81, CC-87; M15 — CC-90, CC-88 (вероятно одна причина, см. раздел 1); M06 — CC-82; M09 — CC-84; M16 — CC-85; M17 — CC-86, CC-89; M08 — CC-67.

---

## 6. Как переложить Jira (предложение, решение за владельцем)

1. **Components = модули** (M01…M19 с понятными именами, например «Quests», «Dialogue», «Input & Game state»). У каждого бага один главный компонент. Для интеграционных багов — главный компонент там, где падает, плюс метка `integration` и номер цепочки `IT-02`.
2. **Метки уровня**: `L1-module`, `L2-integration`, `L3-e2e`.
3. **Задачи-наборы** CC-74…CC-80 (наборы NEW-3…NEW-9) закрыть комментарием «выполнено, см. ведомость» и заменить задачами «M13 Готовка: модульные проверки», «IT-02 Back to menu» и т.п. Один модуль — одна задача, пока по нему есть пробелы.
4. **Связать** CC-88 и CC-87 с CC-90 (вероятно одна корневая причина в QuestManagerSO / DialogueManager подписках).
5. Доска: колонки по модулям не нужны; достаточно фильтров по Components.

---

## 7. План для Sonnet (по шагам)

Общие правила как в прошлых заданиях очереди (game_behaviors.md, ведомость, guard.preflight, save.chop из копии, autoSync, без мыши, Jira не трогать). Скрипты в `scripts\modules\`.

| Шаг | Что сделать | Результат | Оценка |
|---|---|---|---|
| 0 | Добавить в `cases_state.json` поля `module` (M01…M19/T01) и `level` (L1/L2/L3) всем существующим кейсам по таблице из раздела 2 и 5 | обновлённая ведомость | 15 мин, без игры |
| 1 | **Снимок модулей на живой игре** (только чтение): для MainMenu, Beach, Field_Hill, Town_Market — по каждому модулю найти его объекты и компоненты (`find_objects By.COMPONENT`), записать ключевые поля (GameStateSO текущее состояние, InventorySO, HealthSO, AudioManager громкости, активные карты ввода). Скрипт `module_snapshot.py`, вывод `module_snapshot_<сцена>.json`. Это превращает раздел 2 в проверенные факты и даёт «оракулы» | json по 4 сценам + список уточнений к этому документу | 20 мин |
| 2 | L1 «красных» модулей, обычный Play: M03-01 (таблица состояние×клавиша, без диалога), M08-01 (все выходы), M10-01 (другие враги), M06-01 (края других локаций), M18-01/02 | отчёт + ведомость | 40–60 мин, можно двумя заданиями |
| 3 | L1+L2 в **чистом Play №1**: IT-03 (разговоры) → M13-01 / IT-04 (готовка SweetCream) → IT-11 (если блюдо лечит) → M15-02/IT-12 (если следующий шаг — отдать блюдо) → в конце IT-02 (Back to menu → New Game, подтверждение CC-90) | отчёт + ведомость | 15 мин |
| 4 | Чистый Play №2: M14-02 (ветка No), M04-01 (Continue после сохранения с рецептом) | отчёт | 15 мин |
| 5 | L3 E2E-01 в чистом Play №3, только если шаги 3–4 зелёные | отчёт | 20 мин |
| 6 | Итог: таблица «модуль → зелёный/жёлтый/красный» с датой и ссылками | обновить раздел 5 этого файла | 10 мин |

Чистый Play: пока `scripts\play_control\restart_play.py` не проверен на живой игре, Stop/Play делает владелец (по одному разу перед шагами 3, 4, 5).

Что нужно от владельца перед стартом: (1) согласие с разбиением (можно объединить мелкие модули M18/M19 или M05/M06); (2) решение по Jira (раздел 6); (3) разрешение на снимок модулей (шаг 1) через AltTester, пока не идёт другой прогон.


---

_Дописано 25.11.2026 (этап D модульного задания): строки «проверено 25.11» в карточках модулей M01–M04, M06, M08–M10, M12, M15, M16, M18, M19 — источник `Reports_2026-11-21\results\modules_stage1_20261125\probe.json`, `probe2.json`, `module_snapshot_*.json`. Старые строки «Читать:» не менялись._

## Обновление раздела 5 (26.11.2026, по cases_state.json: 75 случаев, PASS 48, OBSERVATION 17, FAIL 5)
- Стало зелёным: M13 готовка (3 PASS), M11 (6 PASS), M15 квесты до questline 1 (E2E-01, E2E-01b), M10 бой/подбор (IT-05), лечение едой (IT-11).
- Жёлтое: M02/M04 (Continue ломает диалоги: IT-02c FAIL, E2E-02 FAIL, см. CC-90), M03 (M03-02 OBSERVATION, сценарий B в stage4), M08 (14 из 16 выходов), M16 (CC-85), M17/M18 (IT-10: громкость без Save).
- Красное: M17 (L10N-01/02 FAIL), M09 (DTH-04 FAIL), Gluecose BLOCKED(precondition), IT-01/IT-06/IT-08 не закрыты.
- Закрыто без прогона: IT-07, IT-09 составными вердиктами.
