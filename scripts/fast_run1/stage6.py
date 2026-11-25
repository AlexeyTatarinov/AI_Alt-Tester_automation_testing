# -*- coding: utf-8 -*-
"""Этап 6: LOC-01 (выход с Beach), LOC-02 (возврат в Beach)."""
import os, sys, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastlib import *

d = connect(); st = load_state(); M = st["tp_method"]
d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, True)

def read_prop(obj, comp, prop):
    try: return obj.get_component_property(comp, prop, ASM)
    except Exception as e: return "не прочитано: %s" % str(e)[:60]

def wait_scene(pred, maxs=30.0):
    t0 = time.perf_counter(); seen = {}
    while time.perf_counter() - t0 < maxs:
        try: sc = scenes()
        except Exception: sc = []
        for n in sc: seen.setdefault(n, round(time.perf_counter() - t0, 1))
        if pred(sc):
            try:
                if pig(): return round(time.perf_counter() - t0, 1), sc, seen
            except Exception: pass
        time.sleep(0.5)
    return None, scenes(), seen

def nearest_entrance(p):
    l = d.find_objects(By.COMPONENT, "LocationEntrance", enabled=False)
    if not l: return None, None
    best = min(l, key=lambda o: math.dist(p, (o.worldX, o.worldY, o.worldZ)))
    return (best.worldX, best.worldY, best.worldZ), len(l)

def loc01():
    off = log_mark(); h0 = save_hashes()
    ex = d.find_object(By.NAME, "LocationExit", enabled=False)
    dest_so = read_prop(ex, "LocationExit", "_locationToLoad.name")
    path_so = read_prop(ex, "LocationExit", "_leadsToPath.name")
    teleport(M, *EXIT_CENTER)
    t, sc, seen = wait_scene(lambda s: "Beach" not in s and any(n not in ("PersistentManagers", "Gameplay") for n in s), 30.0)
    if t is None:
        return {"verdict": "Не пройдено", "numbers": "новая локация не загрузилась за 30 с; сцены=%s, увиденные=%s; назначение выхода=%s" % (sc, seen, dest_so), "screenshot": shot("LOC-01_fail")}
    time.sleep(2.0)
    p = ppos(); ent, n_ent = nearest_entrance(p)
    dent = round(dxz(p, ent), 2) if ent else None
    lg = log_since(off); h1 = save_hashes()
    new_scene = [n for n in sc if n not in ("PersistentManagers", "Gameplay")]
    changed = h0 != h1
    ok = t <= 30 and "Beach" not in sc and dent is not None and dent <= 2.0 and lg["cc67_locationentry"] == 0 and changed
    out = {"verdict": "Пройдено" if ok else "Не пройдено",
           "numbers": "новая сцена %s за %s с (Beach выгружен=%s); назначение выхода `_locationToLoad`=%s, путь=%s; игрок %s м от ближайшего LocationEntrance (входов в сцене %s); CC-67 предупреждений %d; save.chop изменился=%s; исключений %d" % (new_scene, t, "Beach" not in sc, dest_so, path_so, dent, n_ent, lg["cc67_locationentry"], changed, lg["exceptions"]),
           "evidence": "run1_loc01.json"}
    if not ok: out["screenshot"] = shot("LOC-01_fail")
    json.dump({"scenes": sc, "seen": seen, "log": lg, "save_before": h0, "save_after": h1}, open(os.path.join(REPO_RES, "run1_loc01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return out
case("LOC-01", loc01)

def loc02():
    off = log_mark(); h0 = save_hashes()
    exits = d.find_objects(By.COMPONENT, "LocationExit", enabled=False)
    rows = []
    for e in exits:
        rows.append({"x": e.worldX, "y": e.worldY, "z": e.worldZ, "dest": read_prop(e, "LocationExit", "_locationToLoad.name")})
    to_beach = [r for r in rows if "Beach" in str(r["dest"])]
    how = "по полю _locationToLoad"
    if to_beach:
        r = to_beach[0]
    elif rows:
        p = ppos(); r = min(rows, key=lambda r: math.dist(p, (r["x"], r["y"], r["z"]))); how = "ближайший к точке появления (поле не прочитано)"
    else:
        return {"verdict": "Не проверено", "numbers": "в новой сцене не найден LocationExit", "screenshot": shot("LOC-02_noexit")}
    teleport(M, r["x"], r["y"] + 0.5, r["z"])
    t, sc, seen = wait_scene(lambda s: "Beach" in s, 30.0)
    if t is None:
        return {"verdict": "Не пройдено", "numbers": "Beach не загрузился за 30 с; выход выбран %s: %s; сцены=%s" % (how, r, sc), "screenshot": shot("LOC-02_fail")}
    time.sleep(2.0)
    p = ppos(); dent = round(dxz(p, ENTRANCE), 2)
    lg = log_since(off); h1 = save_hashes()
    ok = t <= 30 and dent <= 2.0 and lg["cc67_locationentry"] == 0
    out = {"verdict": "Пройдено" if ok else "Не пройдено",
           "numbers": "Beach загружен за %s с; выход выбран %s (всего выходов %d, назначения %s); игрок %s м от LocationEntrance Beach (%s); CC-67 предупреждений %d; save.chop изменился=%s; исключений %d" % (t, how, len(rows), [x["dest"] for x in rows], dent, ENTRANCE, lg["cc67_locationentry"], h0 != h1, lg["exceptions"]),
           "evidence": "run1_loc02.json"}
    if not ok: out["screenshot"] = shot("LOC-02_fail")
    json.dump({"exits": rows, "scenes": sc, "log": lg}, open(os.path.join(REPO_RES, "run1_loc02.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return out
case("LOC-02", loc02)
