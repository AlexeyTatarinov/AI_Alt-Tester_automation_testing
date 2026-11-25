import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); R = {}; preflight("dlg11b")
R["dlg_now"] = dlg(); R["inv_now"] = inv(); R["hint_now"] = hint(); R["state"] = pstate()
a = approach_step("A", 0.3, 0.6); R["control_step_m"] = a["moved_m"]; print("после Q+Space: диалог", R["dlg_now"], "инв", R["inv_now"], "подсказка", R["hint_now"], "шаг", a["moved_m"], flush=True)
off = log_mark()
R["to_menu_s"] = to_menu(); time.sleep(3.0)
R["ng_s"] = new_game()
for _ in range(10):
    try: ppos(); break
    except Exception: time.sleep(1)
time.sleep(1.0)
R["clean"] = {"dlg_panel_active": dlg(), "choices": choices(), "inv": inv(), "pause": pause_open(), "scenes": scenes(), "pigs": len(pigs()), "pos": tuple(round(v,2) for v in ppos()), "ts": d.get_static_property("UnityEngine.Time","timeScale",CORE)}
a = approach_step("A", 0.3, 0.6); R["clean"]["step_m"] = a["moved_m"]
R["log"] = log_since(off); R["exc"] = exc_summary(off)["by_type"]; R["alive"] = guard.alive()
print(json.dumps(R, ensure_ascii=False, default=str), flush=True)
json.dump(R, open("dlg11b_res.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
shot("dlg11_clean_after_NG")
