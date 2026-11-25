# -*- coding: utf-8 -*-
"""Этап 2: TP-01, TP-02, CON-01."""
import os, sys, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastlib import *

d = connect(); st = load_state(); M = st["tp_method"]
d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, True)   # для T1; значение возвращается в конце

TARGETS = [("спавн", (SPAWN[0], SPAWN[1] + 0.3, SPAWN[2])),
           ("2 м от лодки", (BOAT[0] + 2.0, BOAT[1] + 0.3, BOAT[2])),
           ("2 м от котла", (POT[0] - 2.0, POT[1] + 0.3, POT[2])),
           ("2 м от зайца", (HARE[0] - 2.0, HARE[1] + 0.3, HARE[2])),
           ("стоп-точка v3", (STOP_V3[0], STOP_V3[1] + 0.3, STOP_V3[2]))]

def run_targets():
    rows = []
    for name, t in TARGETS:
        r = tp_and_check(M, t, name)
        att = 1
        if not r["ok"]:
            r2 = tp_and_check(M, t, name + " (попытка 2)"); att = 2
            r = r2 if r2["ok"] else r
        r["attempts"] = att; rows.append(r)
    return rows

def tp01():
    rows = run_targets()
    n_ok = sum(1 for r in rows if r["ok"])
    bad = [r for r in rows if not r["ok"]]
    numbers = "; ".join("%s: XZ0,5=%s XZ2=%s grounded=%s t_gr=%s dy=%s" % (r["label"].split(" (")[0], r.get("xz_0_5"), r.get("xz_2"), r.get("grounded_3s"), r.get("time_to_grounded_s"), r.get("dy")) for r in rows)
    out = {"verdict": "Пройдено" if n_ok == 5 else "Не пройдено", "numbers": "%d из 5. %s" % (n_ok, numbers), "evidence": "run1_tp01.json"}
    if bad: out["screenshot"] = shot("TP-01_fail")
    json.dump(rows, open(os.path.join(REPO_RES, "run1_tp01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return out

def tp02():
    off = log_mark()
    teleport(M, STOP_V3[0], STOP_V3[1] + 0.3, STOP_V3[2]); time.sleep(3.0)
    t0 = time.perf_counter(); teleport(M, POT[0] - 2.0, POT[1] + 0.3, POT[2])
    samples = {}
    for ts in (0.5, 2.0, 5.0):
        while time.perf_counter() - t0 < ts: time.sleep(0.02)
        p = ppos(); c = cam_pos(); samples[str(ts)] = round(dist3(p, c), 2)
    ok = samples["5.0"] <= 10.0
    out = {"verdict": "Пройдено" if ok else "Не пройдено", "numbers": "камера–игрок: 0,5 с=%s м, 2 с=%s м, 5 с=%s м (порог 10 м)" % (samples["0.5"], samples["2.0"], samples["5.0"]), "evidence": "run1_tp02.json"}
    if not ok: out["screenshot"] = shot("TP-02_fail")
    json.dump({"samples": samples, "log": log_since(off)}, open(os.path.join(REPO_RES, "run1_tp02.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return out

def con01():
    off = log_mark()
    teleport(M, SPAWN[0], SPAWN[1] + 0.3, SPAWN[2]); time.sleep(3.0)
    off = log_mark()
    time.sleep(60.0)                       # 60 с без действий
    idle = log_since(off)
    rows = run_targets()
    n_ok = sum(1 for r in rows if r["ok"])
    full = log_since(off)
    ok = full["exceptions"] == 0 and full["errors"] == 0
    out = {"verdict": "Пройдено" if ok else "Не пройдено",
           "numbers": "исключений %d, ошибок %d, предупреждений CC(inactive) %d, CC-67 %d, прочих предупреждений %d; телепорты %d из 5; за 60 с покоя: исключений %d, ошибок %d" % (full["exceptions"], full["errors"], full["cc_inactive_warnings"], full["cc67_locationentry"], full["warnings_other"], n_ok, idle["exceptions"], idle["errors"]),
           "evidence": "run1_con01.json"}
    if not ok: out["screenshot"] = shot("CON-01_fail")
    json.dump({"idle": idle, "full": full, "teleports": rows}, open(os.path.join(REPO_RES, "run1_con01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return out

case("TP-01", tp01)
case("TP-02", tp02)
case("CON-01", con01)
teleport(M, SPAWN[0], SPAWN[1] + 0.3, SPAWN[2])
