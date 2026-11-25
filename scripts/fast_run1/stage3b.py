# -*- coding: utf-8 -*-
"""Этап 3b: вторая попытка INT-03, INT-04, INT-05 (после катсцены/смены состояния, которая сорвала первую попытку)."""
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
prev = {r["id"]: r for r in load_results()}
R = st["int"]["R"]

def cutscene_state():
    try:
        l = d.find_objects(By.COMPONENT, "UnityEngine.Playables.PlayableDirector", enabled=True)
        return [o.get_component_property("UnityEngine.Playables.PlayableDirector", "state", "UnityEngine.DirectorModule") for o in l][:3]
    except Exception as e:
        return "не прочитано"

def wait_ready(maxs=40):
    """управление вернулось: Tab открывает инвентарь"""
    t0 = time.time()
    while time.time() - t0 < maxs:
        key("Tab", 0.1); time.sleep(0.8)
        if inv():
            key("Tab", 0.1); time.sleep(0.8)
            if not inv(): return round(time.time() - t0, 1)
        time.sleep(1.5)
    return None
rdy = wait_ready()
print("управление вернулось через", rdy, "с", flush=True)

def int03b():
    h0 = save_hashes()
    tp(HARE[0] - (R + 0.3), HARE[1] + 0.3, HARE[2], 1.5)
    got = False
    for _ in range(6):
        step_towards(HARE, 0.15)
        if hint(): got = True; break
    if not got:
        return {"verdict": "Не проверено", "numbers": "попытка 2: подсказка не появилась перед E", "screenshot": shot("INT-03b_nohint")}
    key("E", 0.1)
    t0 = time.time(); opened = None
    while time.time() - t0 < 2.0:
        if dlg(): opened = round(time.time() - t0, 2); break
        time.sleep(0.1)
    if opened is None:
        return {"verdict": "Не пройдено", "numbers": "попытка 2: диалог не открылся за 2 с после E", "screenshot": shot("INT-03b_fail")}
    n = 0
    while n < 30 and dlg():
        key("Space", 0.1); n += 1; time.sleep(0.7)
    closed = not dlg()
    t_close = time.time(); timeline = []
    for ts in (1.0, 3.0, 8.0, 15.0):
        while time.time() - t_close < ts: time.sleep(0.1)
        timeline.append((ts, hint(), cutscene_state()))
    hint_1s = timeline[0][1]
    p0 = ppos(); step_dir((-1, 0), 0.3); moved = round(dxz(p0, ppos()), 2)
    h1 = save_hashes()
    ok = closed and hint_1s and moved >= 0.5
    a1 = prev.get("INT-03", {}).get("numbers", "")
    out = {"verdict": "Пройдено" if ok else "Не пройдено",
           "numbers": "попытка 2: диалог за %s с; закрылся=%s за N=%d; подсказка через 1/3/8/15 с и состояние катсцен=%s; шаг %s м; save.chop изменился=%s. Попытка 1: %s" % (opened, closed, n, timeline, moved, h0 != h1, a1[:260]),
           "evidence": "run1_int03.json"}
    if not ok: out["screenshot"] = shot("INT-03b_fail")
    return out
case("INT-03", int03b)

rdy2 = wait_ready()
print("управление вернулось (2) через", rdy2, "с", flush=True)

def int04b():
    h0 = save_hashes()
    tp(POT[0] - 1.3, POT[1] + 0.3, POT[2], 1.5)
    k, p = step_towards(POT, 0.15)
    h_ok = hint()
    key("E", 0.1); time.sleep(1.0)
    inv_open = inv(); near = tab = None
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
    verdict = "Пройдено" if ok else ("Не подтверждено" if (h_ok and inv_open and inv_closed and hint_back and moved >= 0.5 and str(tab).startswith("не прочитано")) else "Не пройдено")
    out = {"verdict": verdict, "numbers": "попытка 2 (управление вернулось через %s с): подсказка у котла=%s; после E инвентарь=%s, _isNearPot=%s, вкладка=%s (Recipe=2); после Tab закрыт=%s, подсказка=%s, шаг %s м; save.chop изменился=%s. Попытка 1: подсказка не появилась, управление было потеряно после INT-03" % (rdy2, h_ok, inv_open, near, tab, inv_closed, hint_back, moved, h0 != h1)}
    if verdict != "Пройдено": out["screenshot"] = shot("INT-04b_fail")
    return out
case("INT-04", int04b)

def int05b():
    h0 = save_hashes()
    tp(POT[0] - 10.0, POT[1] + 0.3, POT[2], 2.0)
    key("Tab", 0.1); time.sleep(1.0)
    if not inv():
        return {"verdict": "Не проверено", "numbers": "попытка 2: инвентарь не открылся по Tab", "screenshot": shot("INT-05b_noinv")}
    tabs = []
    for _ in range(4):
        try: t = INV.get_component_property("UIInventory", "_selectedTab.TabType", ASM)
        except Exception: t = "ошибка"
        tabs.append(t)
        if str(t) in ("2", "Recipe"): break
        key("Y", 0.1); time.sleep(0.6)
    near = INV.get_component_property("UIInventory", "_isNearPot", ASM)
    slots = d.find_objects(By.COMPONENT, "UIInventoryItem", enabled=True)
    if not slots or str(tabs[-1]) not in ("2", "Recipe"):
        key("Tab", 0.1); time.sleep(0.5)
        return {"verdict": "Не проверено", "numbers": "нет рецепта в инвентаре или вкладка не открылась: вкладки=%s, активных слотов=%d, _isNearPot=%s" % (tabs, len(slots or []), near)}
    slots[0].click(); time.sleep(0.6)
    try:
        btn = d.find_object(By.NAME, "ActionButton", enabled=False)
        inter = btn.get_component_property("UnityEngine.UI.Button", "interactable", "UnityEngine.UI")
    except Exception as e:
        inter = "не прочитано: %s" % str(e)[:60]
    try:
        err_active = INV.get_component_property("UIInventory", "_errorPotMessage.activeSelf", ASM)
    except Exception:
        err_active = "не прочитано"
    items_before = len(slots)
    key("Q", 0.1); time.sleep(0.6)
    items_after = len(d.find_objects(By.COMPONENT, "UIInventoryItem", enabled=True))
    key("Tab", 0.1); time.sleep(0.6)
    h1 = save_hashes()
    ok = (inter is False) and (err_active is True) and (not near) and items_before == items_after and h0 == h1
    unread = str(err_active).startswith("не прочитано") or str(inter).startswith("не прочитано")
    out = {"verdict": "Пройдено" if ok else ("Не подтверждено" if unread else "Не пройдено"),
           "numbers": "вкладки=%s; _isNearPot=%s; кнопка interactable=%s; _errorPotMessage активен=%s; слотов до/после Q: %d/%d; save.chop изменился=%s" % (tabs, near, inter, err_active, items_before, items_after, h0 != h1)}
    if not ok: out["screenshot"] = shot("INT-05b_fail")
    return out
case("INT-05", int05b)
teleport(M, SPAWN[0], SPAWN[1] + 0.3, SPAWN[2])
