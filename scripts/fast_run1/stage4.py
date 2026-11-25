# -*- coding: utf-8 -*-
"""Этап 4: DTH-02 (урон и HUD), DTH-01 (смерть и респавн). Проверка механики, не сценарий игрока (Kill/ReceiveAnAttack через SDK)."""
import os, sys, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastlib import *

d = connect(); st = load_state(); M = st["tp_method"]
d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, True)

def hearts():
    l = d.find_objects(By.COMPONENT, "UIHeartDisplay", enabled=False)
    vals = []
    for o in l:
        try: vals.append(round(float(o.get_component_property("UIHeartDisplay", "_slidingImage.fillAmount", ASM)), 3))
        except Exception as e: vals.append(None)
    return vals

def dth02():
    teleport(M, SPAWN[0], SPAWN[1] + 0.3, SPAWN[2]); time.sleep(2.0)
    o = pig(); h0 = health(o); f0 = hearts()
    o.call_component_method("Damageable", "ReceiveAnAttack", ASM, ["10"], ["System.Int32"])
    time.sleep(1.0)
    o = pig(); h1 = health(o); f1 = hearts()
    time.sleep(5.0)
    h2 = health(pig())
    s0 = sum(v for v in f0 if v is not None); s1 = sum(v for v in f1 if v is not None)
    readable = all(v is not None for v in f0 + f1) and len(f0) > 0
    ok_h = (h0 - h1 == 10) and h2 <= h1
    if not readable:
        verdict = "Не подтверждено" if ok_h else "Не пройдено"
    else:
        verdict = "Пройдено" if (ok_h and s1 < s0) else "Не пройдено"
    out = {"verdict": verdict, "numbers": "здоровье %s -> %s (через 6 с %s); сумма fillAmount сердец %s -> %s (%d сердец); fill до=%s после=%s" % (h0, h1, h2, round(s0, 3), round(s1, 3), len(f0), f0, f1)}
    if verdict != "Пройдено": out["screenshot"] = shot("DTH-02_fail")
    return out
case("DTH-02", dth02)

def dth01():
    off = log_mark()
    teleport(M, POT[0] - 2.0, POT[1] + 0.3, POT[2]); time.sleep(3.0)     # ~60 м от спавна
    o = pig(); old_id = o.id; start_dist = round(dxz(ppos(o), SPAWN), 1); h_before = health(o)
    t0 = time.perf_counter()
    o.call_component_method("Damageable", "Kill", ASM)
    series = []; new_t = None; new_id = None
    while time.perf_counter() - t0 < 10.0:
        t = round(time.perf_counter() - t0, 2)
        l = pigs(); ids = [x.id for x in l]
        series.append({"t": t, "count": len(l), "ids": ids})
        if new_t is None and any(i != old_id for i in ids):
            new_t = t; new_id = [i for i in ids if i != old_id][0]
        time.sleep(0.5)
    if new_t is None:
        return {"verdict": "Не пройдено", "numbers": "новый PigChef(Clone) не появился за 10 с; ряд (t,count)=%s" % [(s["t"], s["count"]) for s in series], "screenshot": shot("DTH-01_fail")}
    time.sleep(max(0, 1.0 - (time.perf_counter() - t0 - new_t)))
    l = pigs(); n_after = len(l); o2 = l[0] if l else None
    p = ppos(o2); dspawn = round(dxz(p, SPAWN), 2); h2 = health(o2)
    time.sleep(0.5)
    p0 = ppos(pig()); step_dir((-1, 0), 0.3); moved = round(dxz(p0, ppos(pig())), 2)
    lg = log_since(off)
    ok = (3.5 <= new_t <= 6.0) and n_after == 1 and dspawn <= 2.0 and h2 == 50 and moved >= 0.5 and lg["exceptions"] == 0
    out = {"verdict": "Пройдено" if ok else "Не пройдено",
           "numbers": "старт %s м от спавна, здоровье до=%s; новый PigChef через %s с (ряд %s); через 1 с объектов=%d; позиция нового %s м от спавна; здоровье=%s (норма 50); шаг %s м; исключений %d; CC-67 предупреждений %d (известный CC-67, не новый баг)" % (start_dist, h_before, new_t, [(s["t"], s["count"]) for s in series][:12], n_after, dspawn, h2, moved, lg["exceptions"], lg["cc67_locationentry"]),
           "evidence": "run1_dth01.json"}
    if not ok: out["screenshot"] = shot("DTH-01_fail")
    json.dump({"series": series, "log": lg}, open(os.path.join(REPO_RES, "run1_dth01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return out
case("DTH-01", dth01)
time.sleep(1.0)
teleport(M, SPAWN[0], SPAWN[1] + 0.3, SPAWN[2])
