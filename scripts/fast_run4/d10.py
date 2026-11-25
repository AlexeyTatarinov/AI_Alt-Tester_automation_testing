import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); R = {}; preflight("dlg10")
R["before_state"] = save_info(); R["hash_eq_backup_before"] = save_hashes() == bk_hashes()
print("до: hash==backup", R["hash_eq_backup_before"], R["before_state"]["hash"], "finished", len(R["before_state"]["finished"]))
R["restored_from_backup"] = restore() if not R["hash_eq_backup_before"] else None
print("restore", R["restored_from_backup"], "hash==backup", save_hashes() == bk_hashes())
guard.risky("DLG-10: Back to menu -> New Game")
R["S_menu_before"] = save_info()
off0 = log_mark(); R["to_menu_s"] = to_menu(); time.sleep(3.0); print("to_menu", R["to_menu_s"], scenes())
R["hash_eq_backup_at_menu"] = save_hashes() == bk_hashes()
R["ng_s"] = new_game(); print("NG", R["ng_s"], scenes())
for _ in range(10):
    try: ppos(); break
    except Exception: time.sleep(1)
R["pos_after_ng"] = ppos(); R["dlg_after_ng"] = dlg(); R["pause_after_ng"] = pause_open()
R["S_ng"] = save_info(); print("после NG", R["S_ng"]["hash"], len(R["S_ng"]["finished"]))
R["inv_before"] = inv_snapshot(); print("инвентарь до:", R["inv_before"])
tp_hare(1.3); print("dxz", round(dxz(ppos(), HARE), 2))
k, p1 = step_towards(HARE, 0.15); R["hint_after_step1"] = hint(); steps = 1
while not hint() and steps < 6:
    step_towards(HARE, 0.15); time.sleep(0.4); steps += 1
R["steps_to_hint"] = steps; R["hint"] = hint(); print("hint", hint(), "steps", steps, "dxz", round(dxz(ppos(), HARE), 2))
guard.risky("DLG-10 диалог")
off = log_mark(); R["log_off"] = off
t0 = time.time(); key("E", 0.1); op = None
while time.time() - t0 < 2.0:
    if dlg(): op = round(time.time() - t0, 2); break
    time.sleep(0.05)
R["open_s"] = op; print("открылся", op)
tk = talk(); R["talk"] = {k: tk[k] for k in ("closed", "used", "per_method", "elapsed")}
R["N_total"] = sum(v["presses"] for v in tk["per_method"].values()); R["lines"] = lines_seq(tk["log"]); R["log"] = tk["log"]
print("closed", tk["closed"], "used", tk["used"], tk["per_method"], "N_total", R["N_total"], "lines", len(R["lines"]))
t0 = time.time(); back = None
while time.time() - t0 < 60:
    if hint() and not dlg(): back = round(time.time() - t0, 1); break
    time.sleep(0.5)
R["hint_back_s"] = back
a = approach_step("A", 0.3, 0.6); R["step_m"] = a["moved_m"]
R["S_after"] = save_info(); R["exc"] = exc_summary(off); R["log_since"] = log_since(off)
print("exc", R["exc"]["by_type"], "step", R["step_m"], "hint_back", back)
shot("dlg10_after")
R["inv_after"] = inv_snapshot(); print("инвентарь после:", R["inv_after"])
R["alive"] = guard.alive()[0]
json.dump(R, open("dlg10_res.json", "w"), ensure_ascii=False, indent=1, default=str)
print("saved")
