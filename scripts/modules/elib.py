# -*- coding: utf-8 -*-
import sys; sys.path.insert(0, r"Test_Ai\scripts\modules")
from mlib import *
import module_snapshot as ms
from module_snapshot import cheat_go, close_pause, first, rd

ER = OUT + r"\results_E.json"
BTN = {"Beach": 0, "Field_Hill": 1, "Field_Farms": 2, "Town_Market": 3, "Town_Upper": 4, "Town_Inner": 5, "Forest": 6, "Mountain_Path_bottom": 7, "Mountain_Path_shaft": 8, "Mountain_Cave": 9}
SCN = {"Beach": "Beach", "Field_Hill": "Field_Hill", "Field_Farms": "Field_Farms", "Town_Market": "Town_Market", "Town_Upper": "Town_Upper", "Town_Inner": "Town_Inner", "Forest": "Forest", "Mountain_Path_bottom": "Mountain_Path", "Mountain_Path_shaft": "Mountain_Path", "Mountain_Cave": "Mountain_Cave"}


LABEL = {"Beach": "Beach via", "Field_Hill": "Field_Hill via", "Field_Farms": "Field_Farms via", "Town_Market": "Town_Market via", "Town_Upper": "Town_Upper via", "Town_Inner": "Town_Inner via", "Forest": "Forest via", "Mountain_Path_bottom": "Mountain_Path via MountainCave_MountainPath_BottomExit", "Mountain_Path_shaft": "Mountain_Path via MountainPath_MountainCave_Shaft", "Mountain_Cave": "Mountain_Cave via"}


def load_er():
    try:
        return json.load(open(ER, encoding="utf-8"))
    except Exception:
        return {}


def save_er(cid, rec):
    r = load_er()
    r[cid] = rec
    jdump(ER, r)
    print("[%s] %s -> %s | %s" % (now(), cid, rec.get("verdict"), str(rec.get("numbers", ""))[:400]), flush=True)


def autosync(v):
    d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, v)


def tp(x, y, z, wait=2.0):
    teleport("T1", x, y, z)
    time.sleep(wait)


def goto(name, timeout=60):
    """меню читов -> локация; возвращает (текст, секунды, ошибок опроса)"""
    prestage("goto_" + name)
    return cheat_go(LABEL[name], SCN[name], timeout)


def new_game_from_menu():
    prestage("new_game")
    t = new_game()
    return t


def scene_now():
    return [s for s in scenes() if s not in ("PersistentManagers", "Gameplay")]


def count_name(n, enabled=False):
    return len(d.find_objects(By.NAME, n, enabled=enabled))


def count_comp(c, enabled=False):
    return len(d.find_objects(By.COMPONENT, c, enabled=enabled))


STATE_NAMES = {0: "Gameplay", 1: "Pause", 2: "Inventory", 3: "Dialogue", 4: "Cutscene", 5: "LocationTransition", 6: "Combat"}


def gstate():
    u = first("UIManager")
    v = rd(u, "UIManager", "_gameStateManager._currentGameState")
    return v if isinstance(v, int) else None


def sname(v):
    return STATE_NAMES.get(v, str(v))


def cheat_open():
    return len(d.find_objects(By.NAME, "CheatMenu", enabled=True)) > 0


def panels():
    return {"pause": pause_open(), "inventory": inv_open(), "cheat": cheat_open(), "dialogue": dlg(), "hint": hint_on()}


def inv_open():
    return comp_active("UIInventory")


def hint_on():
    return comp_active("UIInteraction")


def to_gameplay(max_presses=2, ok=(0,)):
    """вернуть Gameplay: закрыть читы (C), паузу (Esc), инвентарь (Tab). Возвращает (вернулось?, нажатий)"""
    n = 0
    for _ in range(max_presses + 1):
        s = gstate()
        if s in ok and not cheat_open() and not pause_open() and not inv_open():
            return True, n
        if n >= max_presses + (1 if cheat_open() else 0):
            break
        if cheat_open():
            key("C", 0.1)
        elif pause_open() or s == 1:
            key("Escape", 0.1)
        elif inv_open() or s == 2:
            key("Tab", 0.1)
        else:
            key("Escape", 0.1)
        n += 1
        time.sleep(1.2)
    s = gstate()
    return (s in ok and not cheat_open() and not pause_open() and not inv_open()), n
