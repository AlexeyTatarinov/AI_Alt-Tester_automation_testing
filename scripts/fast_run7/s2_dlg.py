# -*- coding: utf-8 -*-
import os, sys, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("s2_dlg")
print("start", now()); off = log_mark(); guard.risky("dialog NEW5")
before = inv_snapshot(); print("inv before", json.dumps(before, ensure_ascii=False))
si0 = save_info(); print("save before", si0)
tp_hare(1.3); print("pos", ppos(), "hint", hint())
moved = None
for i in range(8):
    p0 = ppos(); k, p1 = step_towards(HARE, 0.2); m = dxz(p0, p1)
    if i == 0: moved = m
    time.sleep(0.4); print("step", i, k, round(m,2), "hint", hint(), "dist", round(dxz(p1, HARE),2), flush=True)
    if hint(): break
print("first step moved", round(moved,2), "(GUARD-01 ok)" if moved >= 0.3 else "(GUARD-01 INVALID)")
if not hint(): print("НЕТ ПОДСКАЗКИ"); sys.exit()
key("E", 0.1); t0 = time.time()
while time.time() - t0 < 3 and not dlg(): time.sleep(0.1)
print("dlg open", dlg(), round(time.time()-t0,2))
if dlg():
    r = talk(120); print({k: v for k, v in r.items() if k != "log"}); print(lines_seq(r["log"]))
time.sleep(2)
print("dlg", dlg(), "pause", pause_open(), "state", pstate())
print("exc", json.dumps(exc_summary(off), ensure_ascii=False)[:1500])
after = inv_snapshot(); print("inv after", json.dumps(after, ensure_ascii=False))
print("save after", save_info()); print("end", now())
print(shot("s2_after_dialog"))
