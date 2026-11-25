# -*- coding: utf-8 -*-
import re, shutil
B = r"C:\Users\Aotat\Desktop\Test_Ai"
OUT = B + r"\Reports_2026-11-21\results\modules_stage1_20261125"
CAP = B + r"\alttester-capabilities-2026-11-25.md"
MOD = B + r"\modules-decomposition-2026-11-25.md"
shutil.copy2(CAP, OUT + r"\alttester-capabilities.before_stageD.md")
shutil.copy2(MOD, OUT + r"\modules-decomposition.before_stageD.md")

# ---------------- capabilities ----------------
t = open(CAP, encoding="utf-8").read()
# section 1 markers
rep = [
    ("; ❓ `get_all_components`, фильтр `[@component=…]` в PATH", "; ✅ 25.11 `get_all_components` (список словарей `componentName`), ✅ 25.11 фильтр `//*[@component=Critter]` в PATH (6 = 6 с By.COMPONENT)"),
    ("; ❓ вложенные пути через ScriptableObject, списки", "; ✅ 25.11 вложенные пути через ScriptableObject и списки `[i]` (см. раздел 3; `max_depth=4` по спискам с префабами ❌ падает)"),
    ("| ❓ не пробовали ни разу. 📄 LOG даёт", "| ✅ 25.11 LOADSCENE/UNLOADSCENE/LOG работают (probe.json P11–P12). 📄 LOG даёт"),
]
for a, b in rep:
    assert a in t, a
    t = t.replace(a, b)
# section 3 table: add column
res = {
    "M03 состояние": "**МОЖНО** (✅ 25.11). `UIManager` → `get_component_property(\"UIManager\",\"_gameStateManager._currentGameState\",\"Assembly-CSharp\")` приходит ЧИСЛОМ (int); то же через публичное `\"_gameStateManager.CurrentGameState\"`. Наблюдали: 0 Gameplay, 1 Pause (Esc), 2 Inventory (Tab). По enum `GameState`: 3 Dialogue, 4 Cutscene, 5 LocationTransition, 6 Combat (не наблюдали в пробе).",
    "M03 ввод": "**МОЖНО** (✅ 25.11). `Protagonist` → `\"_inputReader._gameInput.Gameplay.enabled\"` / `.Menus.enabled` / `.Dialogues.enabled` → bool. Gameplay: G=True M=False D=False; Esc и Tab: G=False M=True D=False.",
    "M09 здоровье": "**МОЖНО** (✅ 25.11). `PigChef(Clone)` `Damageable`: `\"_currentHealthSO._currentHealth\"`=50, `\".CurrentHealth\"`=50, `\"_maxHealth\"`=50.",
    "M12 инвентарь": "**ОБХОД** (✅ 25.11). `_currentInventory._items` с max_depth 2 читается (список словарей `Amount`/`Item{…}`), с max_depth 4 ❌ `UnknownErrorException … 'transform' on GameObject` (сериализация префаба). Рабочий обход: `\"_currentInventory._items.Count\"` (=6), `\"_currentInventory._items[i].Item.name\"`, `\"_currentInventory._items[i].Amount\"`. `[0]._item.name` тоже работает, `[0]._amount` ❌ (поле зовётся иначе). Совпало с экраном Tab (6 = 6, имена и числа).",
    "M15 квест": "**МОЖНО** (✅ 25.11, до разговоров). `GameManager` → `\"_questManager._currentQuestlineIndex\"`=0, `\"_questManager._currentStepIndex\"`=0, `\"_questManager._currentStep.name\"`=None (шаг ещё не взят). Имя шага после разговора ещё не проверено.",
    "M04 сохранение": "**МОЖНО** (✅ 25.11, только MainMenu). Объект называется `StartGameController`, компонент `StartGame`: `\"_saveSystem.saveData._locationId\"`, `\"…_finishedQuestlineItemsGUIds\"` (5 шт.), `\"…_itemStacks\"` (max_depth 4) совпали с файлом save.chop. В Gameplay-сценах `StartGame` нет.",
    "M18 звук": "**МОЖНО** (✅ 25.11). `call_component_method(\"AudioManager\",\"GetGroupVolume\",\"Assembly-CSharp\",[\"MasterVolume\"],[\"System.String\"])` → 1.0 (так же Music, SFX; 0,02 с); поля `_masterVolume`, `_musicVolume`, `_sfxVolume` тоже читаются.",
    "M16 катсцены": "**МОЖНО читать**, значение пока пустое (✅ 25.11). `CutsceneManager` → `\"_activePlayableDirector\"` = None и через 0 с, и через 30 с после New Game (интро-директор в эти моменты не активен). Что даёт катсцена, смотреть в M16-01.",
    "M10 враги": "`isPlayerInAlertZone` ✅. **НЕЛЬЗЯ** (❌ 25.11) `NavMeshAgent`: у PlantCritter такого компонента нет (список: Transform, 2×CapsuleCollider, Animator, StateMachine, Critter, Attacker, Damageable, CritterAudio, BoneRenderer), в Field_Hill 0 NavMeshAgent. **ОБХОД**: позиция врага по времени + `Critter.isPlayerInAlertZone`. Имя объекта `PlantCritter`, компонент `Critter` (компонента `PlantCritter` нет).",
    "M14 диалог": "✅ (прогоны 1–8, не пробовали заново).",
    "M01 загрузки": "**МОЖНО** (✅ 25.11). LOADSCENE/UNLOADSCENE: при Field_Hill→Beach UNLOAD `Field_Hill` через 0,67 с после клика, LOAD `Beach` (`LoadSceneMode.Additive`) через 0,87 с; имя в поле `scene_name`. Опрос `get_all_loaded_scenes` каждые 0,5 с: **0 ошибок** (`NoAppConnected` не было) при загрузке 5,2 и 5,4 с.",
    "Все": "**МОЖНО с оговоркой** (✅ 25.11). `add_notification_listener(NotificationType.LOG, cb, True)` (импорт `alttester.commands.Notifications.notification_type`) получает `message`, `stack_trace`, `type`. Поле `type` во всех 81 сообщениях = 1 (уровень не отличить) — различать по тексту. В канал попадают и строки самого AltTester (`AltTester|DEBUG…`). За переход 60 сообщений игры, все «There are 2/no audio listeners in the scene» (51 и 9).",
}
lines = t.split("\n")
out = []
in3 = False
for ln in lines:
    if ln.startswith("## 3."):
        in3 = True
    elif ln.startswith("## 4."):
        in3 = False
    if in3 and ln.startswith("| Модуль |"):
        ln = ln + " Итог пробы 25.11 |"
    elif in3 and ln.startswith("|---"):
        ln = ln + "---|"
    elif in3 and ln.startswith("| ") and "Модуль" not in ln:
        key = ln.split("|")[1].strip()
        ln = ln + " " + res.get(key, "—") + " |"
    out.append(ln)
t = "\n".join(out)
t += "\n\n## Дописано 25.11.2026 (этап D, модульное задание, Sonnet)\n\nИсточник: `Reports_2026-11-21\\results\\modules_stage1_20261125\\probe.json` и `probe2.json` (P01–P15), отчёт `report.md` там же. Колонка «Итог пробы 25.11» в разделе 3 заполнена; значки ❓ в разделе 1 заменены на ✅/❌ с датой (`load_scene` не пробовали: не нужен, оставлен ❓).\n\nДополнительные факты пробы:\n- P01 `get_all_components(PigChef(Clone))` ✅: Transform, CapsuleCollider, CharacterController, Animator, StateMachine, Attacker, Damageable, BoneRenderer, ProtagonistAudio, Protagonist, RigBuilder …\n- P13 ✅ ошибок `NoAppConnected` при переходе по меню читов нет (опрос 0,5 с, 2 перехода).\n- P14 ✅ `By.PATH //*[@component=Critter]` и `By.COMPONENT Critter` дают одно число (6 в Field_Hill).\n- P15 ✅ `find_objects(By.COMPONENT,\"AudioListener\",enabled=False)` в Beach: 5 объектов (`Listener` + 4 `AudioListener`), с `enabled=True` — 1. Другие сцены: Field_Hill 2, Town_Market 2, MainMenu 1.\n- Параметр `enabled=False` в `find_objects` возвращает все объекты (и неактивные), `enabled=True` — только активные.\n"
open(CAP, "w", encoding="utf-8").write(t)

# ---------------- modules decomposition ----------------
m = open(MOD, encoding="utf-8").read()
notes = {
    "M01 Запуск": ("Читать: `get_all_loaded_scenes`", " [проверено 25.11, probe.json: опрос `get_all_loaded_scenes` каждые 0,5 с при переходе — 0 ошибок; уведомления LOADSCENE/UNLOADSCENE работают (поле `scene_name`); `SceneLoader` 1, `FadeController` 1, `LoadingInterfaceController` 1 в каждой сцене]"),
    "M02 Меню": ("Читать: активные экраны", " [проверено 25.11: `Pause_Screen` ищется `By.NAME`, `UIPause`/`UIPopup` есть в Gameplay, `UIMainMenu`/`UIMenuManager`/`UICredits` только в MainMenu]"),
    "M03 Ввод": ("Читать: `GameStateSO.CurrentGameState`", " [проверено 25.11, probe.json P02/P03: `UIManager` → `_gameStateManager._currentGameState` (и `.CurrentGameState`) = число 0 Gameplay / 1 Pause / 2 Inventory; карты ввода: `Protagonist` → `_inputReader._gameInput.Gameplay|Menus|Dialogues.enabled` (bool). Объекты `UIManager` и `Protagonist` есть только в Gameplay-сценах]"),
    "M04 Сохранение": ("Читать: файл `save.chop`", " [проверено 25.11, P07: в MainMenu `StartGame` (объект `StartGameController`) → `_saveSystem.saveData._locationId` / `_finishedQuestlineItemsGUIds` / `_itemStacks` совпали с файлом]"),
    "M07 Камера": None,
    "M08 Локации": None,
    "M09 Здоровье": None,
    "M10 Враги": ("Критерии", ""),
    "M12 Инвентарь": None,
    "M15 Квесты": None,
    "M16 Катсцены": None,
    "M18 Звук": ("Читать: громкость микшера", " [проверено 25.11, P08: `AudioManager.GetGroupVolume(\"MasterVolume\"|\"MusicVolume\"|\"SFXVolume\")` = 1.0, поля `_masterVolume` и т.д.; `AudioListener`: Beach 5 объектов (1 активный), Field_Hill 2, Town_Market 2, MainMenu 1]"),
}


def add(card_prefix, anchor, text):
    global m
    i = m.find("**" + card_prefix)
    assert i >= 0, card_prefix
    j = m.find("\n\n", i)
    block = m[i:j]
    block2 = block + text
    m = m[:i] + block2 + m[j:]


add("M01 Запуск", "", "\n\n_[проверено 25.11, probe.json: опрос `get_all_loaded_scenes` каждые 0,5 с при переходе по меню читов — 0 ошибок, загрузка 5,2–5,4 с; уведомления LOADSCENE/UNLOADSCENE работают (UNLOAD +0,67 с, LOAD +0,87 с, поле `scene_name`); `SceneLoader`, `FadeController`, `LoadingInterfaceController`, `AudioManager` — по 1 в каждой сцене]_")
add("M02 Меню", "", "\n\n_[проверено 25.11, снимок: `Pause_Screen` ищется `By.NAME` (Esc → объект активен); `UIMainMenu`, `UIMenuManager`, `UICredits` есть только в MainMenu, `UIPause` и `UIPopup` — в Gameplay-сценах]_")
add("M03 Ввод", "", "\n\n_[проверено 25.11, probe.json P02/P03: **Читать:** `UIManager` → `\"_gameStateManager._currentGameState\"` (и публичное `\".CurrentGameState\"`) приходит числом: 0 Gameplay, 1 Pause (Esc), 2 Inventory (Tab); 3 Dialogue, 4 Cutscene, 5 LocationTransition, 6 Combat — по enum, не наблюдали. Карты ввода: `Protagonist` → `\"_inputReader._gameInput.Gameplay.enabled\"` / `.Menus.enabled` / `.Dialogues.enabled` (bool): Gameplay True/False/False, при Esc и Tab False/True/False. `UIManager` и `Protagonist` есть только в Gameplay-сценах]_")
add("M04 Сохранение", "", "\n\n_[проверено 25.11, P07: **Читать:** в MainMenu компонент `StartGame` (объект `StartGameController`) → `\"_saveSystem.saveData._locationId\"`, `\"…_finishedQuestlineItemsGUIds\"`, `\"…_itemStacks\"` — совпали с save.chop. В Gameplay-сценах `StartGame` нет, там читать файл. После New Game `_locationId` в памяти меняется (WriteEmpty)]_")
add("M06 Коллизии", "", "\n\n_[проверено 25.11, снимок: `FallCatcher` есть только в Town_Market (1); в Beach, Field_Hill, MainMenu 0. `CharacterController` у игрока 1 (в Beach найдено 4, причина не выяснена)]_")
add("M08 Локации", "", "\n\n_[проверено 25.11, снимок: `LocationExit` → `\"_locationToLoad.name\"` и `\"_leadsToPath.name\"` читаются; `LocationEntrance` → `\"_entrancePath.name\"`. Beach: 1 выход (Field_Hill), 1 вход; Field_Hill: 3 выхода (Field_Farms, Beach ×2 — `LocationExit_ToBeach` и `LocationExit_ToBeach_JumpDown`), 2 входа; Town_Market: 4 выхода (Town_Inner ×2, Mountain_Path, Field_Farms), 5 входов (в т.ч. `FromLakeFall`). `SpawnSystem` 1 в Gameplay-сценах]_")
add("M09 Здоровье", "", "\n\n_[проверено 25.11, P05: **Читать:** `Damageable` у `PigChef(Clone)` → `\"_currentHealthSO._currentHealth\"` / `\".CurrentHealth\"` / `\"_maxHealth\"` = 50/50 на старте. В Field_Hill `Damageable` у 7 объектов (игрок + 6 врагов)]_")
add("M10 Враги", "", "\n\n_[проверено 25.11, P10/P14: компонент врага `Critter` (имя объекта `PlantCritter`, компонента `PlantCritter` нет); `Critter.isPlayerInAlertZone` читается. **`NavMeshAgent` на враге нет** (в Field_Hill 0), `isStopped`/`remainingDistance` читать нельзя: оракул навигации = позиция врага по времени. Field_Hill: 6 `Critter`, все PlantCritter. `By.PATH //*[@component=Critter]` и `By.COMPONENT Critter` дают одно число]_")
add("M12 Инвентарь", "", "\n\n_[проверено 25.11, P04: **Читать:** `InventoryManager` → `\"_currentInventory._items.Count\"`, `\"…_items[i].Item.name\"`, `\"…_items[i].Amount\"`; `_items` целиком только с max_depth 2 (при 4 ошибка сериализации префаба). Совпало с экраном Tab (6 предметов: PhoenixChick 1, Seed 20, SlimeCritterEgg 20, GoldenEgg 20, RockCritterEgg 20, SpecialSpoon 1)]_")
add("M15 Квесты", "", "\n\n_[проверено 25.11, P06: **Читать:** `GameManager` → `\"_questManager._currentQuestlineIndex\"`=0, `\"_questManager._currentStepIndex\"`=0, `\"_questManager._currentStep.name\"`=None до разговоров. `StepController`: Beach 1, Town_Market 19, Field_Hill 0]_")
add("M16 Катсцены", "", "\n\n_[проверено 25.11, P09: **Читать:** `CutsceneManager` → `\"_activePlayableDirector\"` (None, когда катсцены нет; через 0 и 30 с после New Game тоже None). `PlayableDirector` в сценах: Beach 2, Town_Market 1, Field_Hill 0; `CutsceneTrigger`: Beach 2, Town_Market 1]_")
add("M18 Звук", "", "\n\n_[проверено 25.11, P08/P15: **Читать:** `AudioManager.GetGroupVolume(\"MasterVolume\"|\"MusicVolume\"|\"SFXVolume\")` (call_component_method, System.String) = 1.0; поля `_masterVolume`, `_musicVolume`, `_sfxVolume`. `AudioListener`: Beach 5 объектов (активный 1), Field_Hill 2, Town_Market 2, MainMenu 1; лог-сообщения «2 audio listeners» (51) и «no audio listeners» (9) пришли за один переход Field_Hill→Beach]_")
add("M19 NPC", "", "\n\n_[проверено 25.11, снимок: `NPC` Beach 1 (BardHare), Town_Market 19 (BardHare_Market, Felfel, 17 Townsfolk), `NPCMovement` Town_Market 18, `NPCMovementSwitcher` 0; теги `NPC` совпадают с числом компонентов `NPC`]_")
m += "\n\n---\n\n_Дописано 25.11.2026 (этап D модульного задания): строки «проверено 25.11» в карточках модулей M01–M04, M06, M08–M10, M12, M15, M16, M18, M19 — источник `Reports_2026-11-21\\results\\modules_stage1_20261125\\probe.json`, `probe2.json`, `module_snapshot_*.json`. Старые строки «Читать:» не менялись._\n"
open(MOD, "w", encoding="utf-8").write(m)
print("ok")
