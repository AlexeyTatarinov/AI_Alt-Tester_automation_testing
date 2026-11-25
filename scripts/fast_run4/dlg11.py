import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); R = {}; preflight("dlg11")
def save_R():
    json.dump(R, open("dlg11_res.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
R["hash_eq_backup_before"] = save_hashes() == bk_hashes()
if not R["hash_eq_backup_before"]: R["restored"] = restore()
print("hash==backup перед NG:", save_hashes() == bk_hashes(), flush=True)
guard.risky("DLG-11: Q в диалоге"); R["checkpoint"] = json.load(open(guard.STATE_F, encoding="utf-8")).get("risky_checkpoint")
R["to_menu_s"] = to_menu(); time.sleep(3.0); R["ng_s"] = new_game()
for _ in range(10):
    try: ppos(); break
    except Exception: time.sleep(1)
R["S_ng"] = save_info(); print("NG", R["ng_s"], scenes(), flush=True)
tp_hare(1.3); steps = 0
while steps < 6:
    step_towards(HARE, 0.15); time.sleep(0.4); steps += 1
    if hint(): break
R["steps_to_hint"] = steps; R["hint"] = hint(); print("hint", hint(), steps, flush=True)
t0 = time.time(); key("E", 0.1); op = None
while time.time() - t0 < 2.0:
    if dlg(): op = round(time.time() - t0, 2); break
    time.sleep(0.05)
R["open_s"] = op; time.sleep(1.0)
R["line_before_Q"] = line(); R["dlg_before_Q"] = dlg(); R["inv_before_Q"] = inv(); R["ts_before"] = d.get_static_property("UnityEngine.Time", "timeScale", CORE)
R["state_before_Q"] = pstate(); R["save_before_Q"] = save_info(); shot("dlg11_before_Q"); save_R()
print("диалог", op, R["line_before_Q"], "alive", guard.alive(), flush=True)
OFF = log_mark(); R["log_off_Q"] = OFF
f0 = d.get_static_property("UnityEngine.Time", "frameCount", CORE)
key("Q", 0.1); tQ = time.time()
R["Q_pressed"] = True; save_R()
snap = []
while time.time() - tQ < 10.5:
    try:
        row = {"t": round(time.time() - tQ, 1), "frame": d.get_static_property("UnityEngine.Time", "frameCount", CORE), "dlg": dlg(), "inv": inv(), "choices": choices(), "line": line(), "pstate": pstate()}
    except Exception as e:
        row = {"t": round(time.time() - tQ, 1), "err": "%s" % type(e).__name__}
    snap.append(row); time.sleep(1.0)
R["after_Q_timeline"] = snap
shot("dlg11_after_Q")
R["exc"] = exc_summary(OFF); R["log_since"] = log_since(OFF); R["log_size_delta"] = log_mark() - OFF
R["errors_new_10s"] = R["log_since"]["exceptions"] + R["log_since"]["errors"]
R["alive_after"] = guard.alive(); R["frames_10s"] = (snap[-1].get("frame") or 0) - f0
R["ts_after"] = d.get_static_property("UnityEngine.Time", "timeScale", CORE)
R["panel_left"] = dlg(); R["inv_opened"] = inv(); R["save_after_Q"] = save_info(); save_R()
print("после Q:", json.dumps({k: R[k] for k in ("panel_left", "inv_opened", "errors_new_10s", "frames_10s", "alive_after", "ts_after")}, default=str), flush=True)
print("exc", R["exc"]["by_type"], flush=True)
# листается ли реплика после Q
adv = {}
if dlg():
    b = line(); key("Space", 0.1); time.sleep(0.6); a1 = line(); key("Space", 0.1); time.sleep(0.6); a2 = line()
    adv = {"before": b, "after1": a1, "after2": a2, "advances": (a1 != b or a2 != a1), "dlg_open_after": dlg()}
    shot("dlg11_after_space")
R["advance_after_Q"] = adv; R["exc_after_advance"] = exc_summary(OFF)["by_type"]; save_R(); print("advance", adv, R["exc_after_advance"], flush=True)
