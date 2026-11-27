# -*- coding: utf-8 -*-
"""Регрессия известных багов (CC-27), часть 1: #262 (отзывчивость после загрузки, MOVE-06, 3 раза) и поиск Slime-критеров для #426."""
import os, sys, json, math
sys.path.insert(0, r"Test_Ai\scripts\fast_run7")
from r4lib import *

OUT = r"Test_Ai\Reports_2026-11-21\results\run11_reg_20261124"
os.makedirs(OUT, exist_ok=True)
R = {"started": now()}
def save(): json.dump(R, open(os.path.join(OUT, "s13_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

d = connect(); preflight("s13")
off = log_mark()
try:
    # ---- #262: отзывчивость после загрузки Beach, 3 раза ----
    runs = []
    for k in range(3):
        guard.risky("s13 262 round %d" % (k + 1))
        if "MainMenu" not in scenes():
            to_menu()
            for _ in range(20):
                time.sleep(1.5)
                if "MainMenu" in scenes() and d.find_objects(By.NAME, "Button New Game", enabled=False): break
            time.sleep(1)
            restore()
        d.find_object(By.NAME, "Button New Game", enabled=False).click(); t_click = time.time()
        for _ in range(15):
            time.sleep(0.4)
            try: d.find_object(By.NAME, "PopupButton - 1", enabled=False).click(); break
            except Exception: pass
        o = None
        while time.time() - t_click < 60:
            try:
                if "Beach" in scenes() and pig(): o = True; break
            except Exception: pass
            time.sleep(0.1)
        t_ready = time.time(); p0 = None
        for _ in range(20):
            try: p0 = ppos(); break
            except Exception: time.sleep(0.1)
        t_first = None; samples = []
        for i in range(24):
            key("W", 0.1)
            try: p = ppos()
            except Exception: p = None
            tt = round(time.time() - t_ready, 2)
            if p and p0:
                dd = dxz(p, p0); samples.append((tt, round(dd, 2)))
                if dd > 0.1 and t_first is None: t_first = tt
            time.sleep(0.4)
        runs.append({"round": k + 1, "player_appeared_s": round(t_ready - t_click, 1), "first_move_after_ready_s": t_first, "samples": samples[:8]})
        print("262 round", k + 1, runs[-1]["first_move_after_ready_s"], flush=True)
        R["262"] = runs; save()
    R["262_verdict"] = {"max_first_move_s": max((r["first_move_after_ready_s"] or 99) for r in runs), "limit_s": 1.0}
    save()
    # ---- поиск Slime / Gluecose по локациям ----
    found = {}
    if 'Beach' not in scenes(): new_game()
    for idx, label in [(2, "Field_Farms"), (1, "Field_Hill"), (9, "Mountain_Cave")]:
        key("C", 0.1); time.sleep(1)
        d.find_objects(By.PATH, "//CheatMenu/*", enabled=False)[idx].click(); t1 = time.time()
        while time.time() - t1 < 60:
            time.sleep(1.0)
            try:
                if pig(): time.sleep(3); break
            except Exception: pass
        if len(d.find_objects(By.NAME, "CheatMenu", enabled=True)): key("C", 0.1); time.sleep(0.5)
        names = {}
        for pat in ("Slime", "Gluecose", "Critter", "Klipper"):
            for o in d.find_objects_which_contain(By.NAME, pat, enabled=False):
                names.setdefault(o.name, []).append([round(o.worldX, 1), round(o.worldY, 1), round(o.worldZ, 1)])
        found[label] = {k: v[:3] for k, v in list(names.items())[:12]}
        print(label, list(found[label].keys())[:8], flush=True)
        R["critters"] = found; save()
    ex = exc_summary(off); R["exceptions"] = ex["by_type"]; R["exceptions_total"] = ex["total"]
finally:
    R["finished"] = now(); save()
print(json.dumps(R, ensure_ascii=False, indent=1)[:5000])
