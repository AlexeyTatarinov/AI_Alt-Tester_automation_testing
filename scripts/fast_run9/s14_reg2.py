# -*- coding: utf-8 -*-
"""Регрессия известных багов (CC-27), часть 2: #499 (камень южнее зайца), #502 (прыжок в стену), #426 (слизень), #262b (отзывчивость после загрузки через меню читов)."""
import os, sys, json, math
sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\fast_run7")
from r4lib import *
from alttester import AltKeyCode

OUT = r"C:\Users\Aotat\Desktop\Test_Ai\Reports_2026-11-21\results\run11_reg_20261124"
R = {"started": now()}
def save(): json.dump(R, open(os.path.join(OUT, "s14_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
def fwd():
    p = ppos(); c = cam_pos(); f = (p[0] - c[0], p[2] - c[2]); n = math.hypot(*f) or 1.0
    return (f[0] / n, f[1] / n)
def comps(o):
    try: return [(c.get("componentName") if isinstance(c, dict) else str(c)) for c in o.get_all_components()]
    except Exception: return []
def load_loc(idx):
    key("C", 0.1); time.sleep(1)
    d.find_objects(By.PATH, "//CheatMenu/*", enabled=False)[idx].click(); t1 = time.time()
    while time.time() - t1 < 60:
        time.sleep(1.0)
        try:
            if pig(): time.sleep(3); break
        except Exception: pass
    if len(d.find_objects(By.NAME, "CheatMenu", enabled=True)): key("C", 0.1); time.sleep(0.5)

d = connect(); preflight("s14")
d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, True)
off = log_mark()
try:
    guard.risky("s14 new game")
    if "Beach" not in scenes():
        if "MainMenu" not in scenes(): raise SystemExit("игра не в MainMenu/Beach: %s" % scenes())
        new_game()
    for _ in range(20):
        try: ppos(); break
        except Exception: time.sleep(1.0)
    time.sleep(2)
    # ---------- #499: камни южнее зайца ----------
    rocks = []
    for o in d.find_objects_which_contain(By.NAME, "Rock", enabled=False):
        dz = o.worldZ - HARE[2]
        if -25 < dz < 0 and abs(o.worldX - HARE[0]) < 25: rocks.append((math.hypot(o.worldX - HARE[0], o.worldZ - HARE[2]), o))
    rocks.sort(key=lambda t: t[0])
    r499 = []
    for dist_h, o in rocks[:4]:
        op = (o.worldX, o.worldY, o.worldZ)
        teleport("T1", op[0], op[1] + 0.5, op[2] + 5.0); time.sleep(1.5)   # север от камня (камень южнее зайца)
        mind = 99; pos_hit = None
        for i in range(14):
            step_towards(op, 0.3); time.sleep(0.15)
            dd = dxz(ppos(), op); mind = min(mind, dd)
        # после упора: пробуем двигаться вбок (A, затем D) по 0,3 с
        p0 = ppos(); key("A", 0.3); time.sleep(0.2); p1 = ppos(); key("D", 0.3); time.sleep(0.2); p2 = ppos()
        lat = max(dxz(p0, p1), dxz(p1, p2))
        r499.append({"rock": o.name, "dist_from_hare": round(dist_h, 1), "min_dist_to_center": round(mind, 2), "lateral_move_after_hit_m": round(lat, 2), "stuck": lat < 0.3})
        print("499", r499[-1], flush=True)
    R["499"] = r499; save()
    # ---------- #502: прыжок в стену ----------
    def run_speed(wall_pos=None):
        """бег вперёд (W) 2,5 с; через 0,6 с прыжок; возвращает макс. скорость м/с по окнам 0,1 с"""
        d.press_key(AltKeyCode.W, power=1, duration=2.5, wait=False)
        samples = []; t0 = time.time(); jumped = False; last = ppos(); lt = time.time()
        while time.time() - t0 < 2.8:
            time.sleep(0.1)
            if not jumped and time.time() - t0 > 0.6 and wall_pos is not None:
                d.press_key(AltKeyCode.Space, power=1, duration=0.1, wait=False); jumped = True
            p = ppos(); now_t = time.time(); samples.append(dxz(p, last) / max(now_t - lt, 0.01)); last = p; lt = now_t
        time.sleep(0.5)
        return round(max(samples), 2), round(sum(samples) / len(samples), 2)
    walls = []
    for o in d.find_objects_which_contain(By.NAME, "BigRock", enabled=False):
        walls.append((math.hypot(o.worldX - HARE[0], o.worldZ - HARE[2]), o))
    walls.sort(key=lambda t: t[0]); r502 = {"baseline": [], "into_wall": []}
    if walls:
        w = walls[0][1]; wp = (w.worldX, w.worldY, w.worldZ); R["502_wall"] = {"name": w.name, "pos": [round(v, 1) for v in wp]}
        for k in range(3):   # базовая скорость на открытом месте: идём от стены
            teleport("T1", wp[0] + 30, wp[1] + 1.0, wp[2] + 30); time.sleep(1.5)
            r502["baseline"].append(run_speed(None))
        for k in range(3):   # прыжок в стену: ставим игрока так, чтобы W шёл на стену (камера смотрит на неё)
            teleport("T1", wp[0], wp[1] + 1.0, wp[2] + 10); time.sleep(1.5)
            f = fwd(); tx = wp[0] - f[0] * 7.0; tz = wp[2] - f[1] * 7.0
            teleport("T1", tx, wp[1] + 1.0, tz); time.sleep(1.5)
            r502["into_wall"].append(run_speed(wp))
        print("502", r502, flush=True)
    R["502"] = r502; save()
    # ---------- #426: слизень (Field_Farms) ----------
    load_loc(2)
    slimes = [o for o in d.find_objects_which_contain(By.NAME, "SlimeCritter_Mesh", enabled=False)]
    r426 = {"found": len(slimes), "tests": []}
    for o in slimes[:3]:
        try: o.update_object(); en = o.enabled
        except Exception: continue
        sp = (o.worldX, o.worldY, o.worldZ)
        info = {"pos": [round(v, 1) for v in sp], "enabled": en, "comps_parent": None}
        teleport("T1", sp[0] - 4.0, sp[1] + 1.0, sp[2]); time.sleep(2.0)
        y0 = ppos()[1]; ymax = y0; mind = 99
        for i in range(14):
            step_towards(sp, 0.3); time.sleep(0.15)
            p = ppos(); ymax = max(ymax, p[1]); mind = min(mind, dxz(p, sp))
        info.update({"y_start": round(y0, 2), "y_rise_max": round(ymax - y0, 2), "min_dist": round(mind, 2)})
        r426["tests"].append(info); print("426", info, flush=True)
    R["426"] = r426; save()
    # ---------- #262b: отзывчивость после загрузки через меню читов, 3 раза ----------
    r262 = []
    for k, idx in enumerate((1, 2, 3)):
        key("C", 0.1); time.sleep(1)
        d.find_objects(By.PATH, "//CheatMenu/*", enabled=False)[idx].click(); t_click = time.time()
        while time.time() - t_click < 60:
            try:
                if pig(): break
            except Exception: pass
            time.sleep(0.1)
        t_ready = time.time(); p0 = None
        for _ in range(20):
            try: p0 = ppos(); break
            except Exception: time.sleep(0.1)
        if len(d.find_objects(By.NAME, "CheatMenu", enabled=True)): key("C", 0.1)
        t_first = None
        for i in range(24):
            key("W", 0.1)
            try: p = ppos()
            except Exception: p = None
            if p and p0 and dxz(p, p0) > 0.1 and t_first is None: t_first = round(time.time() - t_ready, 2)
            time.sleep(0.3)
            if t_first: break
        r262.append({"scene_button": idx, "first_move_after_player_s": t_first}); print("262b", r262[-1], flush=True)
    R["262b"] = r262
    ex = exc_summary(off); R["exceptions"] = ex["by_type"]; R["exceptions_total"] = ex["total"]
finally:
    d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, False)
    R["finished"] = now(); save()
print(json.dumps(R, ensure_ascii=False, indent=1)[:5000])
