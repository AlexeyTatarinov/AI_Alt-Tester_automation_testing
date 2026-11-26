# -*- coding: utf-8 -*-
import os, sys, json, time
os.environ["MOD_OUT"] = "C:/Users/Aotat/Desktop/Test_Ai/Reports_2026-11-21/results/modules_stage5_20261126"
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

# ---- stage3b: гигиена и шторм
sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\play_control")
import housekeeping as hk
class Storm(Exception): pass
_exc_hist = []
def storm_check(off, label=""):
    """>50 исключений за 10 с => шторм. Возвращает total; бросает Storm."""
    t = exc_summary(off); n = t["total"]; _exc_hist.append((time.time(), n))
    while _exc_hist and time.time() - _exc_hist[0][0] > 10: _exc_hist.pop(0)
    if _exc_hist and n - _exc_hist[0][1] > 50:
        raise Storm("шторм %s: %s, +%d за 10 с; %s" % (label, t["by_type"], n - _exc_hist[0][1], {k: v[:3] for k, v in t["first_stacks"].items()}))
    return n
def hyg_start(tag, R):
    r = hk.setup(d); R.setdefault("hygiene", {})[tag] = {k: str(v)[:160] for k, v in r.items()}
    print("hygiene", tag, R["hygiene"][tag], flush=True)
def hyg_tick(R, tag=""):
    done, n = hk.tick(d); n2 = hk.console_count(d)
    R.setdefault("hygiene_ticks", []).append({"t": now(), "tag": tag, "cleared": done, "count_before": n, "count_after": n2})
    return done, n
def wait_play_ready(R=None):
    for _ in range(20):
        time.sleep(1.5)
        try: ppos(); break
        except Exception: pass
    time.sleep(2)
    for _ in range(30):
        if gstate() == 0: break
        time.sleep(1)
def go_continue():
    """Back to menu -> Continue; возвращает секунды загрузки"""
    guard.risky("back to menu"); to_menu()
    for _ in range(20):
        time.sleep(1.5)
        if "MainMenu" in scenes() and d.find_objects(By.NAME, "Button Continue", enabled=False): break
    time.sleep(1); guard.restore_window("continue")
    t0 = time.time(); d.find_object(By.NAME, "Button Continue", enabled=False).click()
    for _ in range(10):
        time.sleep(0.4)
        try: d.find_object(By.NAME, "PopupButton - 1", enabled=False).click(); break
        except Exception: pass
    found = None
    while time.time() - t0 < 60:
        try:
            if "Beach" in scenes() and pig(): found = round(time.time() - t0, 1); break
        except Exception: pass
        time.sleep(0.3)
    assert found, "Continue не загрузился"
    time.sleep(3); wait_play_ready()
    return found
def talk_close(max_sp=60, timeout=150):
    """листать разговор до закрытия (4 опроса подряд Gameplay и без панели); Yes при выборе"""
    seq = []; ok = 0; t0 = time.time(); yes = False; sp = 0
    while time.time() - t0 < timeout:
        l = line()
        if l and (not seq or seq[-1] != l): seq.append(l)
        if choices() and not yes:
            texts = [o.get_text() for o in d.find_objects(By.NAME, "TextChoice", enabled=True)]
            yi = [i for i, t in enumerate(texts) if t.strip().lower() == "yes"]
            if yi: d.find_object(By.NAME, "ButtonChoice%d" % (yi[0] + 1), enabled=True).click(); yes = texts; time.sleep(2.0); continue
        if gstate() == 0 and not dlg(): ok += 1
        else:
            ok = 0
            if dlg() and not choices() and sp < max_sp: key("Space", 0.1); sp += 1
        if ok >= 4: break
        time.sleep(1.2)
    return {"replies": len(seq), "seq": seq, "closed": ok >= 4, "choice_texts": yes, "space": sp}

# ---- stage3b_retry: общие функции
def pos_of(name):
    o = d.find_object(By.NAME, name, enabled=True); return (o.worldX, o.worldY, o.worldZ)
def approach(name):
    """телепорт к NPC с проверкой подсказки E"""
    tries = []
    for dist in (1.3, 1.1, 1.0, 1.5):
        t = pos_of(name); away_then_tp(t, dist)
        for i in range(5):
            h = hint(); tries.append((dist, round(dxz(ppos(), pos_of(name)), 2), h))
            if h: return True, tries
            step_towards(pos_of(name), 0.12); time.sleep(0.5)
    return False, tries
def qdetail():
    g = first("GameManager"); out = dict(quest() or {})
    for k, p in (("step_name", "_questManager._currentStep.name"), ("step_type", "_questManager._currentStep.Type"),
                 ("actor", "_questManager._currentStep.Actor.name"), ("item", "_questManager._currentStep.Item.name"),
                 ("quest_name", "_questManager._currentQuest.name")):
        v = str(rd(g, "GameManager", p, 1))[:120]; out[k] = None if v.startswith("ERR") else v
    return out
def converse(off, tag, name=None):
    """E и разговор до закрытия; снимки до/после"""
    r = {}
    if name:
        ok, tries = approach(name); r["hint"] = ok; r["tries"] = tries
        assert ok, "нет подсказки у " + name
    else:
        assert to_hare(), "нет подсказки у BardHare"
    r["before"] = full_snap(tag + " до", off); r["q_before"] = qdetail()
    key("E", 0.1); t0 = time.time()
    while time.time() - t0 < 3 and not dlg(): time.sleep(0.1)
    r["opened"] = dlg()
    if not dlg(): return r
    seq = []; ok = 0; t0 = time.time(); r["choice_texts"] = None; sp = 0
    while time.time() - t0 < 150:
        l = line()
        if l and (not seq or seq[-1] != l): seq.append(l)
        storm_check(off, tag)
        if choices():
            texts = [o.get_text() for o in d.find_objects(By.NAME, "TextChoice", enabled=True)]; r["choice_texts"] = texts
            yi = [i for i, t in enumerate(texts) if t.strip().lower() == "yes"]
            if yi: d.find_object(By.NAME, "ButtonChoice%d" % (yi[0] + 1), enabled=True).click(); time.sleep(2.0); continue
        if gstate() == 0 and not dlg(): ok += 1
        else:
            ok = 0
            if dlg() and not choices() and sp < 60: key("Space", 0.1); sp += 1
        if ok >= 4: break
        time.sleep(1.2)
    r.update(replies=len(seq), seq=seq, closed=ok >= 4, space=sp)
    r["after"] = full_snap(tag + " после", off); r["q_after"] = qdetail(); r["diff"] = diff(r["before"], r["after"])
    return r
def brief(r):
    return {k: r.get(k) for k in ("opened", "replies", "closed", "choice_texts", "space", "diff", "q_before", "q_after")}

# ---- Field_Hill
def crit(name):
    for c in d.find_objects(By.COMPONENT, "Critter", enabled=True):
        if c.name == name: return c
    return None
def cpos(c):
    c.update_object(); return (c.worldX, c.worldY, c.worldZ)
def alert(c):
    try: return c.get_component_property("Critter", "isPlayerInAlertZone", ASM)
    except Exception as e: return "ERR " + type(e).__name__
def collectables():
    out = {}
    for o in d.find_objects(By.COMPONENT, "CollectableItem", enabled=True):
        out[o.id] = (o, [round(o.worldX, 2), round(o.worldY, 2), round(o.worldZ, 2)], str(rd(o, "CollectableItem", "_currentItem.name", 1)))
    return out
def hp_now():
    try: return health()
    except Exception as e: return "ERR " + type(e).__name__
def st_now(label, **kw):
    r = {"t": now(), "label": label, "count": alert_count(), "state": sname(gstate()), "scenes": scene_now(), "hp": hp_now()}
    r.update(kw); print(json.dumps(r, ensure_ascii=False), flush=True); return r

def save_items():
    """инвентарь из save.chop с именами предметов (по GUID ассетов)"""
    import glob, re as _re
    m = {}
    for f in glob.glob(r"C:\Games\ChopChop\UOP1_Project\Assets\ScriptableObjects\Inventory\Items\*\*.asset"):
        g = _re.search(r"_guid: (\w+)", open(f, encoding="utf-8-sig").read())
        if g: m[g.group(1)] = os.path.splitext(os.path.basename(f))[0]
    j = json.load(open(SAVE0F, encoding="utf-8"))
    return {"inv": {m.get(s["itemGuid"], s["itemGuid"]): s["amount"] for s in j.get("_itemStacks", [])}, "locationId": j.get("_locationId"), "finished_n": len(j.get("_finishedQuestlineItemsGUIds", []))}
def locs():
    return [s for s in scenes() if s not in ("PersistentManagers", "Gameplay", "MainMenu")]
