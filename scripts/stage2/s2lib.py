# -*- coding: utf-8 -*-
import os, sys, json, time
os.environ["MOD_OUT"] = "Test_Ai/Reports_2026-11-21/results/modules_stage2_20261125"
sys.path.insert(0, r"Test_Ai\scripts\modules")
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
