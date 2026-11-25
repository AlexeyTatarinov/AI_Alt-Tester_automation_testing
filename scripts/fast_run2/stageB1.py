# -*- coding: utf-8 -*-
"""Блок B, этап 1 (Beach): TP-02 (новый критерий), INV-11, INV-12, INV-10. Результаты дописываются в отчёт сразу."""
import os, sys, time, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastlib import *

d = connect(); st = load_state()
d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, True)
INV = ui_obj("UIInventory")
def inv(): return comp_active("UIInventory")
def tp(t, wait=3.0):
    teleport("T1", t[0], t[1] + 0.3, t[2]); time.sleep(wait)

def tab_type():
    try: return INV.get_component_property("UIInventory", "_selectedTab.TabType", ASM)
    except Exception: return None

def slots():
    out = []
    for s in d.find_objects(By.COMPONENT, "UIInventoryItem", enabled=True):
        try:
            out.append((s, s.get_component_property("UIInventoryItem", "currentItem.Item.name", ASM),
                        s.get_component_property("UIInventoryItem", "currentItem.Amount", ASM),
                        s.get_component_property("UIInventoryItem", "currentItem.Item.ItemType.ActionType", ASM)))
        except Exception:
            pass
    return [x for x in out if x[1]]

# ---------- TP-02 ----------
def tp02():
    reps = []; ok_all = True
    pairs = [(STOP_V3, POT), (POT, STOP_V3), (STOP_V3, POT)]
    for a, b in pairs:
        tp(a, 3.0)
        off = log_mark()
        teleport("T1", b[0], b[1] + 0.3, b[2])
        t0 = time.perf_counter(); r = {}
        for ts in (0.5, 2.0, 5.0):
            while time.perf_counter() - t0 < ts: time.sleep(0.02)
            r[ts] = round(dist3(cam_pos(), ppos()), 2)
        r["diff_5_2"] = round(r[5.0] - r[2.0], 2)
        r["ok"] = abs(r["diff_5_2"]) <= 0.5 and r[5.0] <= r[2.0]
        r["log_exc"] = log_since(off)["exceptions"]
        ok_all &= r["ok"]; reps.append(r)
    v = "Пройдено" if ok_all else "Не пройдено"
    out = {"verdict": v, "numbers": "расстояние камера–игрок 0,5/2/5 с по 3 телепортам на 50 м: %s; критерий |d5−d2| ≤ 0,5 и d5 ≤ d2 (не растёт, строгое чтение)" % [(r[0.5], r[2.0], r[5.0], r["diff_5_2"], r["ok"]) for r in reps], "evidence": "-"}
    if not ok_all: out["screenshot"] = shot("TP-02_fail")
    return out
r = case("TP-02", tp02)
md_row("TP-02", r["verdict"], r["numbers"], "новый критерий владельца 22.11")

# ---------- INV-11 ----------
def inv11():
    tp(SPAWN, 3.0)
    if inv(): key("Tab", 0.1); time.sleep(0.8)
    key("Tab", 0.1); time.sleep(1.0)
    open_1s = inv(); time.sleep(1.0); open_2s = inv()
    key("Tab", 0.1); time.sleep(1.0); closed = not inv()
    ok = open_1s and open_2s and closed
    out = {"verdict": "Пройдено" if ok else "Не пройдено", "numbers": "Tab 0,1 с: открыт через 1 с=%s, через 2 с=%s; второй Tab закрыл=%s" % (open_1s, open_2s, closed)}
    if not ok: out["screenshot"] = shot("INV-11_fail")
    return out
r = case("INV-11", inv11); md_row("INV-11", r["verdict"], r["numbers"])

# ---------- INV-12 ----------
def inv12():
    tp(SPAWN, 3.0)
    if not inv(): key("Tab", 0.1); time.sleep(1.0)
    found = []; seen_tabs = []
    for _ in range(4):
        t = tab_type(); sl = slots(); seen_tabs.append((t, [(n, a, at) for _, n, a, at in sl]))
        found += [(n, at) for _, n, a, at in sl if at == 2]   # ActionType 2 = Equip
        key("Y", 0.1); time.sleep(0.7)
    if inv(): key("Tab", 0.1); time.sleep(0.8)
    if not found:
        return {"verdict": "Не проверено", "numbers": "нет предмета с действием Equip (ActionType=2) ни на одной вкладке; содержимое: %s. Нужен предмет Equip (одежда или кухонная утварь) в инвентаре" % seen_tabs}
    off = log_mark()
    key("Tab", 0.1); time.sleep(1.0)
    return {"verdict": "Не проверено", "numbers": "найден Equip %s: проверка не реализована в этом скрипте" % found}
r = case("INV-12", inv12); md_row("INV-12", r["verdict"], r["numbers"])

# ---------- INV-10 ----------
def inv10():
    tp(SPAWN, 3.0)
    h0 = save_hashes(); off = log_mark()
    if not inv(): key("Tab", 0.1); time.sleep(1.0)
    use = None
    for _ in range(4):
        sl = slots()
        cand = [x for x in sl if x[3] == 1 and x[2] >= 2]
        if cand: use = (cand[0], sl); break
        key("Y", 0.1); time.sleep(0.7)
    if not use:
        if inv(): key("Tab", 0.1); time.sleep(0.8)
        return {"verdict": "Не проверено", "numbers": "нет предмета типа Use (ActionType=1) с количеством ≥ 2. Нужен такой предмет"}
    (slot, name, amt0, at), sl = use
    others = [x for x in sl if x[0].id != slot.id]
    # выбрать другой предмет и вернуться, 2 раза
    for _ in range(2):
        if others: others[0][0].click(); time.sleep(0.5)
        slot.click(); time.sleep(0.5)
    before = None
    for x in slots():
        if x[1] == name: before = x[2]
    key("Q", 0.1); time.sleep(1.0)
    after = None
    for x in slots():
        if x[1] == name: after = x[2]
    # состояние здоровья и лога
    lg = log_since(off)
    h1 = save_hashes()
    if inv(): key("Tab", 0.1); time.sleep(0.8)
    ok = (before is not None and after is not None and before - after == 1)
    out = {"verdict": "Пройдено" if ok else ("Не пройдено" if (before is not None and after is not None) else "Не подтверждено"),
           "numbers": "предмет %s (Use): количество до Q %s, после Q %s (ожидается −1; при подписках, накопленных выбором, было бы больше); выборов другого предмета и возврата: 2; исключений %s; save.chop изменился=%s" % (name, before, after, lg["exceptions"], h0 != h1)}
    if not ok: out["screenshot"] = shot("INV-10_fail")
    return out
r = case("INV-10", inv10); md_row("INV-10", r["verdict"], r["numbers"], "BC-4 (подписка на Q при выборе предметов)")
print("stage B1 готов")
