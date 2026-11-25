# -*- coding: utf-8 -*-
# DLG-10b: Space с паузой 1,0 с, счёт нажатий до Yes/No. Аргумент: круг (1|2)
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
rnd = sys.argv[1]
d = connect(); preflight("dlg10b_r" + rnd)
def panel(): return any(True for _ in d.find_objects(By.NAME, "Panel Choices", enabled=True))
print("start", now(), "scenes", scenes(), "hash==backup", save_hashes() == bk_hashes(), flush=True)
if rnd == "2" or "MainMenu" not in scenes():
    print("to_menu s:", to_menu()); time.sleep(3.0)
print("new_game s:", new_game(), scenes(), flush=True)
for _ in range(10):
    try: ppos(); break
    except Exception: time.sleep(1)
preflight("dlg10b_r%s_ng" % rnd)
d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, True)
guard.risky("dlg10b " + rnd)
tp_hare(1.3)
p0 = ppos(); k, p1 = step_towards(HARE, 0.15); mv = round(dxz(p0, p1), 2)
steps = 1
while not hint() and steps < 30:
    k, _ = step_towards(HARE, 0.1 if dxz(ppos(), HARE) < 1.3 else 0.3); time.sleep(0.5); steps += 1
print("step1 moved", mv, "steps to hint", steps, "hint", hint(), "dxz", round(dxz(ppos(), HARE), 2), flush=True)
if mv < 0.3: print("GUARD-01: Invalid (шаг <0.3)")
OFF = log_mark(); T0 = time.time(); key("E", 0.1); op = None
while time.time() - T0 < 2.0:
    if dlg(): op = round(time.time() - T0, 2); break
    time.sleep(0.05)
print("dialog opened s", op, "line:", line(), flush=True)
print(shot("dlg10b_r%s_open" % rnd))
log = []; found = None; last_change_t = None; prev = line(); t_start = time.time()
for n in range(1, 41):
    if not dlg(): log.append((n, "dialog closed before choices")); break
    key("Space", 0.05); time.sleep(1.0)
    ln = line(); ch = choices(); pn = panel(); t = round(time.time() - t_start, 1)
    if ln != prev: last_change_t = t; prev = ln
    log.append((n, t, dlg(), ch, pn, (ln or "")[:60]))
    print(log[-1], flush=True)
    if ch or pn:
        found = n; t_found = t; break
res = {"round": rnd, "opened_s": op, "step1_moved": mv, "found_at_press": found, "last_line_change_t": last_change_t,
       "t_found": t_found if found else None, "pause_no_buttons_s": round(t_found - last_change_t, 1) if found and last_change_t is not None else None}
print("RESULT", res, flush=True)
print(shot("dlg10b_r%s_end" % rnd))
if found:
    print("texts", dlg_texts()[:12])
    names = [o.name for o in d.find_objects(By.COMPONENT, "UnityEngine.UI.Button", enabled=True)]
    print("buttons", names)
json.dump({"res": res, "log": log}, open("dlg10b_r%s.json" % rnd, "w"), ensure_ascii=False, default=str, indent=1)
print("exc", exc_summary(OFF)["by_type"])
print("ended", now())
