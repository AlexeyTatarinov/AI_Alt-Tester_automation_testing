# -*- coding: utf-8 -*-
# BND-05b: южная кромка Beach. Старт (-135.1, y, z0) ~15 м севернее кромки z=-496.3; шаги на юг, проверка позиции после каждого шага
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("bnd05b")
Z0 = float(sys.argv[1]) if len(sys.argv) > 1 else -481.3
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 0.4
print("start", now(), "scenes", scenes(), flush=True)
OFF = log_mark(); guard.risky("bnd05b")
d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, True)
teleport("T1", -135.1, -27.8, Z0); time.sleep(3.0)
p = ppos(); print("after TP", tuple(round(v, 2) for v in p), "grounded", grounded(pig()), "state", pstate(), flush=True)
print(shot("bnd05b_start"))
steps = []; stuck = 0; stop = None; fall_at = None
for n in range(1, 61):
    p0 = ppos(); k = choose_key(p0, (p0[0], p0[1], p0[2] - 5)); key(k, DUR); time.sleep(0.25)
    p1 = ppos(); mv = dxz(p0, p1); dy = p1[1] - p0[1]
    steps.append({"n": n, "key": k, "x": round(p1[0], 2), "y": round(p1[1], 2), "z": round(p1[2], 2), "moved": round(mv, 2), "dy": round(dy, 2), "state": pstate()})
    print(steps[-1], flush=True)
    if dy < -1.0 or p1[1] < p0[1] - 1.0: stop = "падение (y упал на %.2f м за шаг)" % dy; fall_at = steps[-1]; break
    stuck = stuck + 1 if mv < 0.05 and abs(dy) < 0.05 else 0
    if stuck >= 3: stop = "стена: позиция не меняется 3 шага подряд"; break
else:
    stop = "60 шагов без падения и стены"
print("STOP:", stop, flush=True)
pe = ppos(); print("edge pos", tuple(round(v, 2) for v in pe))
print(shot("bnd05b_stop"))
resp = None
if fall_at:
    t0 = time.time(); ys = []
    while time.time() - t0 < 20:
        time.sleep(1.0)
        try:
            q = ppos(); ys.append((round(time.time() - t0), round(q[0], 1), round(q[1], 1), round(q[2], 1)))
            if q[1] > -20 and dxz(q, (-135.1, 0, pe[2])) > 30 or q[1] > pe[1] + 5: resp = round(time.time() - t0, 1); break
        except Exception as e: ys.append((round(time.time() - t0), type(e).__name__))
    print("после падения:", ys[:8], "...", ys[-2:], "респавн:", resp, "pigs", len(pigs()), flush=True)
    print(shot("bnd05b_after_fall"))
json.dump({"z0": Z0, "dur": DUR, "steps": steps, "stop": stop, "fall": fall_at, "respawn_s": resp}, open("bnd05b.json", "w"), ensure_ascii=False, indent=1)
print("exc", exc_summary(OFF)["by_type"], "ended", now())
