# -*- coding: utf-8 -*-
"""Проверка известных upstream-багов из бенчмарка CC-45 / CC-32: #483 (E в диалоге), #505 (коллайдер у печи Town_Market), #484 (townsfolk проходят сквозь BardHare).
Запуск: на чистом Play (после restart_play.py). Игру и проект не меняет. Результат: steps в JSON рядом с отчётом."""
import os, sys, json, math
sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\fast_run7")
from r4lib import *

OUT = r"C:\Users\Aotat\Desktop\Test_Ai\Reports_2026-11-21\results\run10_upstream_20261124"
os.makedirs(OUT, exist_ok=True)
R = {"started": now()}

def save():
    json.dump(R, open(os.path.join(OUT, "s12_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

d = connect(); pre = preflight("s12")
fr = int(d.get_static_property("UnityEngine.Time", "frameCount", "UnityEngine.CoreModule"))
rt = float(d.get_static_property("UnityEngine.Time", "realtimeSinceStartup", "UnityEngine.CoreModule"))
R["clean_play"] = {"frameCount": fr, "realtime": rt, "scenes": scenes()}
d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, True)
off = log_mark()
try:
    # ---------- #483: E в диалоге ----------
    guard.risky("s12 new game")
    new_game()
    for _ in range(20):
        time.sleep(1.5)
        try: ppos(); break
        except Exception: pass
    time.sleep(2); tp_hare(1.3)
    for i in range(12):
        if hint(): break
        step_towards(HARE, 0.2); time.sleep(0.4)
    R["483_hint_before"] = hint()
    key("E", 0.1); time.sleep(1.2)
    r483 = {"dialogue_open": dlg(), "first_line": line(), "hint_visible_in_dialogue": hint()}
    shot("s12_483_open")
    lines = []
    for k in range(5):
        key("E", 0.1); time.sleep(1.0); lines.append({"press": k + 1, "line": line(), "dlg": dlg()})
    r483["E_presses"] = lines
    r483["E_advanced"] = any(x["line"] != r483["first_line"] for x in lines)
    key("Space", 0.1); time.sleep(1.0)
    r483["after_space_line"] = line(); r483["space_advanced"] = r483["after_space_line"] != r483["first_line"]
    shot("s12_483_after_space")
    R["483"] = r483; save()
    # дочитать диалог до конца (Space, 0,1 с, пауза 1 с), чтобы не оставлять открытым
    n = 0
    while dlg() and n < 40:
        key("Space", 0.1); time.sleep(1.0); n += 1
    R["483"]["dialogue_closed_after_presses"] = n; save()
    # ---------- Town_Market ----------
    key("C", 0.1); time.sleep(1)
    d.find_objects(By.PATH, "//CheatMenu/*", enabled=False)[3].click(); t1 = time.time()
    while time.time() - t1 < 60:
        time.sleep(1.0)
        try:
            if pig(): time.sleep(3); break
        except Exception: pass
    if len(d.find_objects(By.NAME, "CheatMenu", enabled=True)): key("C", 0.1); time.sleep(0.5)
    R["scene_after_cheat"] = scenes()
    # ---------- #505: коллайдер у печи ----------
    def comps(o):
        try: return [(c.get("componentName") if isinstance(c, dict) else str(c)) for c in o.get_all_components()]
        except Exception as e: return ["ERR " + type(e).__name__]
    ovens = d.find_objects_which_contain(By.NAME, "ven", enabled=False)
    oven_info = []
    for o in ovens:
        nm = o.name
        if "oven" not in nm.lower(): continue
        info = {"name": nm, "pos": [round(o.worldX, 2), round(o.worldY, 2), round(o.worldZ, 2)], "components": comps(o)}
        try:
            kids = d.find_objects(By.PATH, "//%s//*" % nm, enabled=False)
            info["child_colliders"] = [(k.name, [c for c in comps(k) if "Collider" in c]) for k in kids if any("Collider" in c for c in comps(k))][:10]
            info["children"] = len(kids)
        except Exception as e:
            info["children_err"] = type(e).__name__
        oven_info.append(info)
    R["505"] = {"ovens": oven_info}; save()
    # физическая проверка: идём к центру печи и смотрим, насколько близко удалось подойти
    if oven_info:
        op = oven_info[0]["pos"]
        teleport("T1", op[0] - 4.0, op[1] + 0.5, op[2]); time.sleep(2.0)
        mind = 99
        for i in range(30):
            p = ppos(); dd = dxz(p, op); mind = min(mind, dd)
            step_towards(op, 0.3); time.sleep(0.2)
        R["505"]["min_distance_to_oven_center_walking"] = round(mind, 2); R["505"]["final_pos"] = ppos()
        shot("s12_505_oven")
        save()
    # ---------- #484: townsfolk сквозь BardHare ----------
    hare = None
    for o in d.find_objects_which_contain(By.NAME, "BardHare", enabled=False):
        hare = o; break
    folks = [o for o in d.find_objects_which_contain(By.NAME, "Townsfolk", enabled=False)]
    R["484"] = {"hare": hare.name if hare else None, "townsfolk_count": len(folks)}
    if hare and folks:
        hp = (hare.worldX, hare.worldZ)
        teleport("T1", hare.worldX - 6, hare.worldY + 1.0, hare.worldZ); time.sleep(2.0)
        track = {f.id: {"name": f.name, "min": 99.0, "positions": []} for f in folks}
        t0 = time.time()
        while time.time() - t0 < 60:
            for f in folks:
                try:
                    f.update_object(); dd = math.hypot(f.worldX - hp[0], f.worldZ - hp[1])
                    tr = track[f.id]; tr["min"] = min(tr["min"], dd)
                    if len(tr["positions"]) < 200: tr["positions"].append([round(f.worldX, 1), round(f.worldZ, 1)])
                except Exception: pass
            time.sleep(1.0)
        res = []
        for t in track.values():
            xs = [p[0] for p in t["positions"]]; zs = [p[1] for p in t["positions"]]
            move = round(math.hypot(max(xs) - min(xs), max(zs) - min(zs)), 1) if xs else None
            res.append({"name": t["name"], "min_distance_to_hare": round(t["min"], 2), "range_of_movement_m": move})
        R["484"]["townsfolk"] = sorted(res, key=lambda r: r["min_distance_to_hare"])[:8]
        R["484"]["moving_npcs"] = sum(1 for r in res if (r["range_of_movement_m"] or 0) > 1.0)
        R["484"]["closest_m"] = min(r["min_distance_to_hare"] for r in res)
        shot("s12_484_end"); save()
    ex = exc_summary(off); R["exceptions"] = ex["by_type"]; R["exceptions_total"] = ex["total"]
finally:
    d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, False)
    R["finished"] = now(); save()
print(json.dumps(R, ensure_ascii=False, indent=1)[:6000])
