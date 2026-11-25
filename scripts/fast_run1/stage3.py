# -*- coding: utf-8 -*-
"""Этап 3: INT-01..INT-05 (заяц-бард BardHare, котёл PotOverFire)."""
import os, sys, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastlib import *

d = connect(); st = load_state(); M = st["tp_method"]
d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, True)
INV = ui_obj("UIInventory")
def hint(): return comp_active("UIInteraction")
def dlg(): return comp_active("UIDialogueManager")
def inv(): return comp_active("UIInventory")
def tp(x, y, z, wait=1.5):
    teleport(M, x, y, z); time.sleep(wait)
def dist_to(t): return round(dxz(ppos(), t), 2)
shared = st.get("int", {})

# --- предварительная проверка: управляемость после New Game (интро) -------------------------------------------
def precheck():
    tp(HARE[0] - 1.2, HARE[1] + 0.3, HARE[2], 2.0)
    t0 = time.time(); vis = False
    while time.time() - t0 < 15:
        step_towards(HARE, 0.15)
        if hint(): vis = True; break
        time.sleep(1.0)
    return vis, round(time.time() - t0, 1), dist_to(HARE)
vis, tt, dd = precheck()
shared["precheck"] = {"hint_visible": vis, "seconds": tt, "dist": dd}
print("предпроверка подсказки у зайца:", shared["precheck"], flush=True)
if not vis:
    for cid in ("INT-01", "INT-02", "INT-03", "INT-04", "INT-05"):
        add_result({"id": cid, "verdict": "Не проверено", "numbers": "подсказка взаимодействия рядом с зайцем не появилась за 15 с (раздел 6: интро/катсцена или состояние не Gameplay)", "evidence": "run1_state.json"})
    st["int"] = shared; save_state(st); sys.exit(0)

# --- INT-01 ----------------------------------------------------------------------------------------------------
def int01():
    tp(HARE[0] - 3.0, HARE[1] + 0.3, HARE[2], 1.5)
    series = []; R = None
    for i in range(1, 13):
        if hint() and R is None and i > 1: pass
        k, p = step_towards(HARE, 0.15)
        h = hint(); series.append({"step": i, "dist": round(dxz(p, HARE), 2), "hint": h})
        if h: R = round(dxz(p, HARE), 2); break
    ok = R is not None and 0.6 <= R <= 1.6
    shared["R"] = R
    out = {"verdict": "Пройдено" if ok else "Не пройдено", "numbers": "R=%s м (шаг %s); критерий 0,6–1,6 м; серия: %s" % (R, len(series), [(s["step"], s["dist"], s["hint"]) for s in series]),
           "evidence": "run1_int01.json"}
    if not ok: out["screenshot"] = shot("INT-01_fail")
    json.dump(series, open(os.path.join(REPO_RES, "run1_int01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return out
case("INT-01", int01)
R = shared.get("R")

# --- INT-02 ----------------------------------------------------------------------------------------------------
def int02():
    if R is None:
        return {"verdict": "Не проверено", "numbers": "нет R из INT-01"}
    tp(HARE[0] - (R + 1.3), HARE[1] + 0.3, HARE[2], 1.5)
    k, p = step_towards(HARE, 0.15)
    dist_after = round(dxz(p, HARE), 2); h_before = hint()
    key("E", 0.1); time.sleep(2.0)
    h_after = hint(); dl = dlg()
    ok = (not h_before) and (not h_after) and (not dl)
    out = {"verdict": "Пройдено" if ok else "Не пройдено", "numbers": "после шага расстояние %s м (R+1 м = %s); подсказка до E=%s, после E=%s; диалог активен=%s" % (dist_after, round(R + 1.0, 2), h_before, h_after, dl)}
    if not ok: out["screenshot"] = shot("INT-02_fail")
    return out
case("INT-02", int02)

# --- INT-03 ----------------------------------------------------------------------------------------------------
def int03():
    if R is None:
        return {"verdict": "Не проверено", "numbers": "нет R из INT-01"}
    h0 = save_hashes()
    tp(HARE[0] - (R + 0.3), HARE[1] + 0.3, HARE[2], 1.5)
    got = False
    for _ in range(6):
        step_towards(HARE, 0.15)
        if hint(): got = True; break
    if not got:
        return {"verdict": "Не проверено", "numbers": "подсказка не появилась перед E", "screenshot": shot("INT-03_nohint")}
    key("E", 0.1)
    t0 = time.time(); opened = None
    while time.time() - t0 < 2.0:
        if dlg(): opened = round(time.time() - t0, 2); break
        time.sleep(0.1)
    if opened is None:
        return {"verdict": "Не пройдено", "numbers": "диалог не открылся за 2 с после E", "screenshot": shot("INT-03_fail")}
    n = 0; tstart = time.time(); choices = []
    while n < 30 and dlg():
        key("Space", 0.1); n += 1; time.sleep(0.7)
        try:
            choices.append(len([o for o in d.find_objects(By.COMPONENT, "UIDialogueChoiceItem", enabled=True)]))
        except Exception:
            choices.append(None)
    closed = not dlg(); dt = round(time.time() - tstart, 1)
    time.sleep(1.0)
    hint_back = hint(); p0 = ppos(); step_dir((-1, 0), 0.3); p1 = ppos(); moved = round(dxz(p0, p1), 2)
    h1 = save_hashes(); changed = h0 != h1
    shared["N"] = n
    ok = closed and hint_back and moved >= 0.5
    out = {"verdict": "Пройдено" if ok else "Не пройдено",
           "numbers": "диалог открылся за %s с; закрылся=%s за N=%d нажатий (%s с); подсказка после=%s; шаг %s м; выборы по шагам=%s; save.chop изменился=%s" % (opened, closed, n, dt, hint_back, moved, choices, changed),
           "evidence": "save_hashes в run1_int03.json"}
    if not ok: out["screenshot"] = shot("INT-03_fail")
    json.dump({"before": h0, "after": h1, "N": n}, open(os.path.join(REPO_RES, "run1_int03.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return out
case("INT-03", int03)

# --- INT-04 ----------------------------------------------------------------------------------------------------
def int04():
    h0 = save_hashes()
    tp(POT[0] - 1.3, POT[1] + 0.3, POT[2], 1.5)
    k, p = step_towards(POT, 0.15)
    h_ok = hint()
    key("E", 0.1); time.sleep(1.0)
    inv_open = inv()
    near = tab = None
    try:
        near = INV.get_component_property("UIInventory", "_isNearPot", ASM)
        tab = INV.get_component_property("UIInventory", "_selectedTab.TabType", ASM)
    except Exception as e:
        tab = "не прочитано: %s" % str(e)[:80]
    key("Tab", 0.1); time.sleep(1.0)
    inv_closed = not inv(); hint_back = hint()
    p0 = ppos(); step_dir((-1, 0), 0.3); moved = round(dxz(p0, ppos()), 2)
    h1 = save_hashes()
    tab_recipe = str(tab) in ("2", "Recipe")
    ok = h_ok and inv_open and tab_recipe and inv_closed and hint_back and moved >= 0.5
    verdict = "Пройдено" if ok else ("Не подтверждено" if (h_ok and inv_open and inv_closed and not tab_recipe and str(tab).startswith("не прочитано")) else "Не пройдено")
    out = {"verdict": verdict, "numbers": "подсказка у котла=%s; после E инвентарь=%s, _isNearPot=%s, вкладка=%s (Recipe=2); после Tab закрыт=%s, подсказка=%s, шаг %s м; save.chop изменился=%s" % (h_ok, inv_open, near, tab, inv_closed, hint_back, moved, h0 != h1)}
    if verdict != "Пройдено": out["screenshot"] = shot("INT-04_fail")
    return out
case("INT-04", int04)

# --- INT-05 ----------------------------------------------------------------------------------------------------
def int05():
    h0 = save_hashes()
    tp(POT[0] - 10.0, POT[1] + 0.3, POT[2], 2.0)
    near_before = None
    key("Tab", 0.1); time.sleep(1.0)
    if not inv():
        return {"verdict": "Не проверено", "numbers": "инвентарь не открылся по Tab", "screenshot": shot("INT-05_noinv")}
    tabs = []
    for _ in range(4):
        try: t = INV.get_component_property("UIInventory", "_selectedTab.TabType", ASM)
        except Exception as e: t = "ошибка"
        tabs.append(t)
        if str(t) in ("2", "Recipe"): break
        key("Y", 0.1); time.sleep(0.6)
    near = INV.get_component_property("UIInventory", "_isNearPot", ASM)
    slots = d.find_objects(By.COMPONENT, "UIInventoryItem", enabled=True)
    if not slots or str(tabs[-1]) not in ("2", "Recipe"):
        key("Tab", 0.1); time.sleep(0.5)
        return {"verdict": "Не проверено", "numbers": "нет рецепта в инвентаре или вкладка не открылась: вкладки=%s, слотов=%d" % (tabs, len(slots or []))}
    slots[0].click(); time.sleep(0.6)
    err_msg = None
    try:
        em = d.find_objects(By.NAME, "ErrorPotMessage", enabled=True)
    except Exception:
        em = []
    try:
        btn = d.find_object(By.NAME, "ActionButton", enabled=False)
        inter = btn.get_component_property("UnityEngine.UI.Button", "interactable", "UnityEngine.UI")
    except Exception as e:
        inter = "не прочитано: %s" % str(e)[:60]
    err_active = None
    try:
        err_active = INV.get_component_property("UIInventory", "_errorPotMessage.activeSelf", ASM)
    except Exception as e:
        err_active = "не прочитано"
    items_before = len(slots)
    key("Q", 0.1); time.sleep(0.6)
    items_after = len(d.find_objects(By.COMPONENT, "UIInventoryItem", enabled=True))
    key("Tab", 0.1); time.sleep(0.6)
    h1 = save_hashes()
    ok = (inter is False) and (err_active is True) and (not near) and items_before == items_after and h0 == h1
    shot_p = None if ok else shot("INT-05_fail")
    out = {"verdict": "Пройдено" if ok else ("Не подтверждено" if str(err_active).startswith("не прочитано") or str(inter).startswith("не прочитано") else "Не пройдено"),
           "numbers": "вкладки=%s; _isNearPot=%s; слот выбран; кнопка interactable=%s; _errorPotMessage активен=%s; слотов до/после Q: %d/%d; save.chop изменился=%s" % (tabs, near, inter, err_active, items_before, items_after, h0 != h1)}
    if shot_p: out["screenshot"] = shot_p
    return out
case("INT-05", int05)

st["int"] = shared; save_state(st)
teleport(M, SPAWN[0], SPAWN[1] + 0.3, SPAWN[2])
