import sys; sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\modules")
from mlib import *

MODS = {
    "M01": ["SceneLoader", "InitializationLoader", "StartGame", "FadeController", "LoadingInterfaceController"],
    "M02": ["UIMainMenu", "UIMenuManager", "UIPause", "UIPopup", "UICredits"],
    "M03": ["UIManager", "InteractionManager"],
    "M04": ["StartGame"],
    "M05": ["Protagonist"],
    "M06": ["FallCatcher", "UnityEngine.CharacterController"],
    "M07": ["CameraManager"],
    "M08": ["LocationExit", "LocationEntrance", "SpawnSystem"],
    "M09": ["Damageable", "UIHealthBarManager", "UIHeartDisplay"],
    "M10": ["Critter", "Attacker", "ZoneTriggerController", "MovingCritterAttackController"],
    "M11": ["InteractionManager", "UIInteraction"],
    "M12": ["InventoryManager", "UIInventory", "ItemPicker", "CollectableItem", "UIActionButton"],
    "M13": ["UIItemForAnimation"],
    "M14": ["DialogueManager", "UIDialogueManager", "UIDialogueChoicesManager", "DialogueTrigger"],
    "M15": ["StepController", "GameManager"],
    "M16": ["CutsceneManager", "CutsceneTrigger", "TimelineBinder", "UnityEngine.Playables.PlayableDirector"],
    "M17": ["UISettingsController", "UISettingsAudioComponent", "UISettingsLanguageComponent", "SettingsSystem"],
    "M18": ["AudioManager", "MusicPlayer", "SoundEmitter", "AudioCue"],
    "M19": ["NPC", "NPCMovement", "NPCMovementSwitcher"],
}
SPECIAL = ["LocationExit", "LocationEntrance", "Critter", "NPC", "StepController", "FallCatcher", "AudioListener", "UnityEngine.EventSystems.EventSystem", "SceneLoader", "AudioManager"]
GLOBAL_ERRORS = []


def find(comp):
    try:
        l = d.find_objects(By.COMPONENT, comp, enabled=False)
    except Exception as e:
        return {"count": 0, "error": "%s: %s" % (type(e).__name__, str(e)[:120]), "objects": []}
    out = []
    for o in l[:40]:
        out.append({"name": o.name, "pos": [round(o.worldX, 1), round(o.worldY, 1), round(o.worldZ, 1)], "enabled": o.enabled})
    return {"count": len(l), "objects": out}


def first(comp):
    try:
        l = d.find_objects(By.COMPONENT, comp, enabled=False)
        return l[0] if l else None
    except Exception:
        return None


def rd(o, comp, prop, depth=2, asm=ASM):
    if o is None:
        return "no object"
    r = sget(o, comp, prop, asm, depth)
    return r["raw"] if r["ok"] else "ERR " + r["resp"][:100]


def oracles(scene):
    o = {}
    u = first("UIManager")
    if u:
        o["game_state"] = rd(u, "UIManager", "_gameStateManager._currentGameState")
    pr = first("Protagonist")
    if pr:
        o["input_maps"] = {m: rd(pr, "Protagonist", "_inputReader._gameInput.%s.enabled" % m) for m in ("Gameplay", "Menus", "Dialogues")}
    im = first("InventoryManager")
    if im:
        n = rd(im, "InventoryManager", "_currentInventory._items.Count")
        items = []
        if isinstance(n, int):
            for i in range(n):
                items.append((rd(im, "InventoryManager", "_currentInventory._items[%d].Item.name" % i), rd(im, "InventoryManager", "_currentInventory._items[%d].Amount" % i)))
        o["inventory"] = {"count": n, "items": items}
    p = pig() if scene != "MainMenu" else None
    if p:
        o["health"] = {"cur": rd(p, "Damageable", "_currentHealthSO.CurrentHealth"), "max": rd(p, "Damageable", "_currentHealthSO._maxHealth")}
    gm = first("GameManager")
    if gm:
        o["quest"] = {"questline_idx": rd(gm, "GameManager", "_questManager._currentQuestlineIndex"), "step_idx": rd(gm, "GameManager", "_questManager._currentStepIndex"), "step": rd(gm, "GameManager", "_questManager._currentStep.name")}
    am = first("AudioManager")
    if am:
        vol = {}
        for g in ("MasterVolume", "MusicVolume", "SFXVolume"):
            try:
                vol[g] = am.call_component_method("AudioManager", "GetGroupVolume", ASM, [g], ["System.String"])
            except Exception as e:
                vol[g] = "ERR " + type(e).__name__
        o["volumes"] = vol
    cm = first("CutsceneManager")
    if cm:
        o["cutscene"] = {"director": rd(cm, "CutsceneManager", "_activePlayableDirector"), "state": rd(cm, "CutsceneManager", "_activePlayableDirector.state")}
    sg = first("StartGame")
    if sg:
        o["save_in_memory"] = {"locationId": rd(sg, "StartGame", "_saveSystem.saveData._locationId"), "finished_n": len(rd(sg, "StartGame", "_saveSystem.saveData._finishedQuestlineItemsGUIds") or [])}
    return o


def snapshot(scene):
    t0 = time.time()
    S = {"scene": scene, "time": time.strftime("%H:%M:%S"), "loaded_scenes": scenes(), "modules": {}, "scene_counts": {}, "oracles": {}}
    cache = {}
    for m, comps in MODS.items():
        S["modules"][m] = {}
        for c in comps:
            if c not in cache:
                cache[c] = find(c)
            S["modules"][m][c] = cache[c]
    for c in SPECIAL:
        if c not in cache:
            cache[c] = find(c)
        S["scene_counts"][c] = cache[c]["count"]
    # LocationExit/Entrance details
    ex = []
    try:
        for o in d.find_objects(By.COMPONENT, "LocationExit", enabled=False):
            ex.append({"name": o.name, "pos": [round(o.worldX, 1), round(o.worldY, 1), round(o.worldZ, 1)],
                       "to": rd(o, "LocationExit", "_locationToLoad.name"), "path": rd(o, "LocationExit", "_leadsToPath.name")})
    except Exception as e:
        ex.append("ERR " + str(e)[:100])
    S["location_exits"] = ex
    en = []
    try:
        for o in d.find_objects(By.COMPONENT, "LocationEntrance", enabled=False):
            en.append({"name": o.name, "pos": [round(o.worldX, 1), round(o.worldY, 1), round(o.worldZ, 1)], "path": rd(o, "LocationEntrance", "_entrancePath.name")})
    except Exception as e:
        en.append("ERR " + str(e)[:100])
    S["location_entrances"] = en
    for tag in ("CookingPot", "NPC", "Pickable", "Player"):
        try:
            l = d.find_objects(By.TAG, tag, enabled=False)
            S["scene_counts"]["tag:" + tag] = len(l)
            if tag in ("CookingPot", "NPC"):
                S.setdefault("tagged", {})[tag] = [{"name": o.name, "pos": [round(o.worldX, 1), round(o.worldY, 1), round(o.worldZ, 1)]} for o in l[:30]]
        except Exception as e:
            S["scene_counts"]["tag:" + tag] = "ERR " + type(e).__name__
    for nm in ("SceneLoader", "AudioManager", "PersistentManagers", "PigChef(Clone)", "EventSystem", "Pause_Screen", "CheatMenu"):
        try:
            S["scene_counts"]["name:" + nm] = len(d.find_objects(By.NAME, nm, enabled=False))
        except Exception as e:
            S["scene_counts"]["name:" + nm] = "ERR " + type(e).__name__
    # critter detail: враги по именам + список компонентов первого
    crit = d.find_objects(By.COMPONENT, "Critter", enabled=False)
    kinds = {}
    for o in crit:
        kinds[o.name.split(" (")[0]] = kinds.get(o.name.split(" (")[0], 0) + 1
    S["critter_kinds"] = kinds
    if crit:
        try:
            S["critter_components_first"] = [c.get("componentName") for c in crit[0].get_all_components()]
        except Exception as e:
            S["critter_components_first"] = "ERR " + str(e)[:80]
        # поиск навигации среди детей
        try:
            S["critter_navmesh_search"] = {"by_component_NavMeshAgent_in_scene": len(d.find_objects(By.COMPONENT, "UnityEngine.AI.NavMeshAgent", enabled=False))}
        except Exception as e:
            S["critter_navmesh_search"] = "ERR " + type(e).__name__ + str(e)[:80]
    # AudioListener подробно
    try:
        S["audio_listeners"] = [{"name": o.name, "active": o.enabled, "pos": [round(o.worldX, 1), round(o.worldY, 1), round(o.worldZ, 1)]} for o in d.find_objects(By.COMPONENT, "AudioListener", enabled=False)]
    except Exception:
        pass
    S["oracles"] = oracles(scene)
    S["seconds"] = round(time.time() - t0, 1)
    jdump(OUT + "/module_snapshot_%s.json" % scene, S)
    print("snapshot", scene, S["seconds"], "s; counts", S["scene_counts"], flush=True)
    return S


def cheat_go(idx, want, timeout=60):
    if pause_open():
        close_pause()
    # дождаться Gameplay (ввод читов включён только там)
    u = None
    for _ in range(20):
        u = first("UIManager")
        if u is not None and rd(u, "UIManager", "_gameStateManager._currentGameState") == 0:
            break
        time.sleep(0.5)
    for attempt in range(2):
        for _ in range(3):
            if len(d.find_objects(By.NAME, "CheatMenu", enabled=True)):
                break
            key("C", 0.1)
            time.sleep(1.5)
        LAB = ["Beach via", "Field_Hill via", "Field_Farms via", "Town_Market via", "Town_Upper via", "Town_Inner via", "Forest via", "Mountain_Path via MountainCave_MountainPath_BottomExit", "Mountain_Path via MountainPath_MountainCave_Shaft", "Mountain_Cave via"]
        label = idx if isinstance(idx, str) else LAB[idx]
        btn = None
        txt = None
        for b in d.find_objects(By.PATH, "//CheatMenu/*", enabled=False):
            tx = d.find_objects(By.PATH, "//CheatMenu/%s/Text" % b.name, enabled=False)
            # имена кнопок повторяются в порядке списка: берём текст по id родителя через get_parent
            pass
        for tx_obj in d.find_objects(By.PATH, "//CheatMenu/*/Text", enabled=False):
            s = tx_obj.get_text()
            if s.startswith(label):
                btn = tx_obj.get_parent()
                txt = s
                break
        if btn is None:
            raise RuntimeError("cheat button not found: " + label)
        t0 = time.time()
        btn.click()
        errs = 0
        ok = False
        while time.time() - t0 < (timeout if attempt else 25):
            time.sleep(0.5)
            try:
                sc = scenes()
                if want in sc and pig() and time.time() - t0 > 2 and (len(sc) <= 3):
                    ok = True
                    break
            except Exception:
                errs += 1
        if ok:
            break
    time.sleep(3)
    if len(d.find_objects(By.NAME, "CheatMenu", enabled=True)):
        key("C", 0.1)
        time.sleep(1)
    if not ok:
        raise RuntimeError("cheat_go failed: %s scenes=%s" % (want, scenes()))
    return txt, round(time.time() - t0, 1), errs


def close_pause():
    if pause_open():
        key("Escape", 0.1)
        time.sleep(1.2)


if __name__ == "__main__":
    off0 = log_mark()
    SNAP = {}
    prestage("C_beach")
    d.set_static_property("UnityEngine.Application", "runInBackground", CORE, True)
    print("scenes", scenes())
    SNAP["Beach"] = snapshot("Beach")
    for idx, want, scn in ((1, "Field_Hill", "Field_Hill"), (3, "Town_Market", "Town_Market")):
        prestage("C_" + scn)
        print("go", cheat_go(idx, want))
        prestage("C_" + scn + "_arrived")
        SNAP[scn] = snapshot(scn)
    # MainMenu
    prestage("C_menu")
    sec = to_menu()
    print("to_menu", sec)
    time.sleep(3)
    prestage("C_mainmenu")
    SNAP["MainMenu"] = snapshot("MainMenu")
    print("exceptions", exc_summary(off0))
