# -*- coding: utf-8 -*-
import os, sys, json, time
os.environ["MOD_OUT"] = "C:/Users/Aotat/Desktop/Test_Ai/Reports_2026-11-21/results/modules_stage3_20261125"
sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\modules")
from elib import *
import elib
R2 = OUT
SF = os.path.join(R2, "run_state.json")
def st_load():
    try: return json.load(open(SF, encoding="utf-8"))
    except Exception: return {"steps": {}, "restarts": []}
def st_set(k, v):
    s = st_load(); s["steps"][k] = v; jdump(SF, s)

def inv_items():
    o = first("InventoryManager")
    if o is None: return None
    c = rd(o, "InventoryManager", "_currentInventory._items.Count")
    if not isinstance(c, int): return "ERR %s" % c
    out = {}
    for i in range(c):
        n = rd(o, "InventoryManager", "_currentInventory._items[%d].Item.name" % i)
        a = rd(o, "InventoryManager", "_currentInventory._items[%d].Amount" % i)
        out[str(n)] = a
    return out
def quest():
    o = first("GameManager")
    if o is None: return None
    return {"line": rd(o, "GameManager", "_questManager._currentQuestlineIndex"), "step": rd(o, "GameManager", "_questManager._currentStepIndex")}
def alert_count():
    u = first("UIManager")
    if u is None: return "no UIManager"
    for depth in (2, 1):
        v = rd(u, "UIManager", "_gameStateManager._alertEnemies.Count", depth)
        if isinstance(v, int): return v
    v = rd(u, "UIManager", "_gameStateManager._alertEnemies", 1)
    return v
def snap(label, off=None):
    sf = os.path.join(SAVE_DIRS[0], "save.chop")
    s = {"label": label, "t": now(), "scenes": scene_now()}
    try: s["state"] = sname(gstate())
    except Exception as e: s["state"] = "ERR " + str(e)[:60]
    try: s["inv"] = inv_items()
    except Exception as e: s["inv"] = "ERR " + str(e)[:60]
    try: s["quest"] = quest()
    except Exception as e: s["quest"] = "ERR " + str(e)[:60]
    s["save_hash"] = sha(sf)
    si = save_info(); s["save_finished"] = len(si.get("finished", []))
    if off is not None:
        e = exc_summary(off); s["exc"] = e["total"]; s["exc_types"] = e["by_type"]
    return s
def diff(a, b):
    out = {}
    for k in ("state", "quest", "save_hash", "save_finished", "exc"):
        if a.get(k) != b.get(k): out[k] = [a.get(k), b.get(k)]
    ia, ib = a.get("inv"), b.get("inv")
    if isinstance(ia, dict) and isinstance(ib, dict):
        ch = {k: [ia.get(k, 0), ib.get(k, 0)] for k in set(ia) | set(ib) if ia.get(k, 0) != ib.get(k, 0)}
        if ch: out["inv"] = ch
    return out

def alert_count_snap():
    return {"count": alert_count(), "frameCount": d.get_static_property("UnityEngine.Time", "frameCount", CORE)}

def talk_first(n_max=25):
    n = 0; seq = []
    while n < n_max:
        key("Space", 0.1); n += 1; time.sleep(1.0)
        l = line()
        if l and (not seq or seq[-1] != l): seq.append(l)
        if choices() or not dlg(): break
    time.sleep(1.5)
    return {"N_space": n, "closed": not dlg(), "replies": len(seq), "choices": choices(), "seq": seq}
def away_then_tp(target, dist, away=10.0):
    """подсказка E: сначала уйти на 10 м, потом телепорт на dist"""
    teleport("T1", target[0] - away, target[1] + 0.3, target[2]); time.sleep(1.5)
    teleport("T1", target[0] - dist, target[1] + 0.3, target[2]); time.sleep(2.0)
def to_hare():
    for dist in (1.3, 1.1, 1.0):
        away_then_tp(HARE, dist)
        if hint(): return True
        for i in range(5):
            step_towards(HARE, 0.15)
            if hint(): return True
            time.sleep(0.1)
            if hint(): return True
    return False
def full_snap(label, off=None):
    s = snap(label, off); s["alert_count"] = alert_count(); return s
def wait_closed(polls=4, timeout=120):
    """диалог закрыт: Gameplay и панели нет 4 опроса подряд; жмёт Space, пока не закрыт"""
    t0 = time.time(); ok = 0
    while time.time() - t0 < timeout:
        if gstate() == 0 and not dlg(): ok += 1
        else:
            ok = 0
            if dlg(): key("Space", 0.1)
        if ok >= polls: return True
        time.sleep(1.2)
    return False
def conv_yes(off, tag, maxsp=40):
    ok = hint() or to_hare(); r = {"hint": ok}
    sp = full_snap(tag + " до", off); r["before"] = sp
    key("E", 0.1); t0 = time.time()
    while time.time() - t0 < 3 and not dlg(): time.sleep(0.1)
    assert dlg(), "диалог не открылся"
    n = 0; seq = []
    while n < 4:
        key("Space", 0.1); n += 1; time.sleep(1.0)
        l = line()
        if l and (not seq or seq[-1] != l): seq.append(l)
        if choices() or not dlg(): break
    r["first_line"] = seq[0] if seq else None
    assert choices(), "нет Yes/No"
    texts = [o.get_text() for o in d.find_objects(By.NAME, "TextChoice", enabled=True)]; r["texts"] = texts
    yi = [i for i, t in enumerate(texts) if t.strip().lower() == "yes"]; assert yi
    d.find_object(By.NAME, "ButtonChoice%d" % (yi[0] + 1), enabled=True).click(); time.sleep(2.0)
    k = 0; ok = 0
    t0 = time.time()
    while time.time() - t0 < 150:
        l = line()
        if l and (not seq or seq[-1] != l): seq.append(l)
        if gstate() == 0 and not dlg(): ok += 1
        else:
            ok = 0
            if dlg(): key("Space", 0.1)
        if ok >= 4: break
        time.sleep(1.2)
    r["replies"] = len(seq); r["seq"] = seq; r["closed"] = ok >= 4
    sa = full_snap(tag + " после", off); r["after"] = sa; r["diff"] = diff(sp, sa)
    return r
