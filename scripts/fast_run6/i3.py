# -*- coding: utf-8 -*-
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
tag = sys.argv[1]
d = connect(); preflight("int03_" + tag)
d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, True)
guard.risky("диалог " + tag)
if tag == "b":
    print("Esc pause open before:", pause_open())
    print("to_menu s:", to_menu()); time.sleep(3.0)
    print("save hash in menu:", save_info()["hash"], len(save_info()["finished"]))
    print("new_game s:", new_game(), scenes(), "pigs", len(pigs()), "pause", pause_open())
    for _ in range(10):
        try: ppos(); break
        except Exception: time.sleep(1)
    preflight("dlg10_after_ng")
    d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, True)
S0 = save_info(); print("save before:", S0["hash"], len(S0["finished"]), S0["finished"])
tp_hare(1.3)
p = ppos(); print("pos", tuple(round(v,2) for v in p), "dxz hare", round(dxz(p, HARE),2))
p0 = ppos(); k, p1 = step_towards(HARE, 0.15)
mv = round(dxz(p0, p1),2); a = {"moved_m": mv}; steps = 1
print("step1", k, "moved", mv, "dxz", round(dxz(p1,HARE),2), "hint", hint())
while not hint() and steps < 14:
    k, _ = step_towards(HARE, 0.3); time.sleep(0.4); steps += 1
print("steps to hint", steps, "hint", hint(), "dxz", round(dxz(ppos(),HARE),2))
OFF = log_mark()
t0 = time.time(); key("E", 0.1); op=None
while time.time()-t0 < 2.0:
    if dlg(): op = round(time.time()-t0,2); break
    time.sleep(0.05)
print("dialog opened s:", op); time.sleep(0.5)
print(shot("int03_%s_open" % tag))
print("start line:", line())
r = talk(60)
print("closed", r["closed"], "used", r["used"], "per_method", r["per_method"], "elapsed", r["elapsed"])
for l in r["log"]: print(l)
time.sleep(2.0)
t1=time.time(); back=None
while time.time()-t1 < 20:
    if hint() and not dlg(): back = round(time.time()-t1,1); break
    time.sleep(0.5)
exc = exc_summary(OFF)
q0 = ppos(); a2 = approach_step("A", 0.3, 0.6)
S1 = save_info()
print("hint back s", back, "step after", a2["moved_m"], "save", S0["hash"], "->", S1["hash"], len(S0["finished"]), "->", len(S1["finished"]), S1["finished"])
print("exceptions", exc["by_type"], exc["total"])
for k2, v in exc["first_stacks"].items(): print(k2, v[:3])
print(shot("int03_%s_closed" % tag))
json.dump({"opened_s": op, "step_moved": mv, "approach": a["moved_m"], "talk": {k:v for k,v in r.items() if k!="log"}, "N": r["per_method"].get(r["used"],{}).get("presses") if r["used"] else None,
  "hint_back": back, "after_step": a2["moved_m"], "save_before": S0, "save_after": S1, "exc": exc, "log": r["log"]}, open("int03_%s.json" % tag, "w"), ensure_ascii=False, default=str, indent=1)
