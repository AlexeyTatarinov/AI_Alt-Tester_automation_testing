# -*- coding: utf-8 -*-
# d01 этапы 1-2: New Game, первый разговор (Space 0.1/пауза 1.0 до закрытия), второй разговор, Yes.
import os, sys, json
sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\fast_run7")
from r4lib import *
d = connect()
OUT = r"C:\Users\Aotat\Desktop\Test_Ai\Reports_2026-11-21\results\run8_d01_20261124"; os.makedirs(OUT, exist_ok=True)
R = {}
print("restore_window", guard.restore_window("d01 A"))
pre = preflight("d01a")
R["rts"] = d.get_static_property("UnityEngine.Time", "realtimeSinceStartup", CORE)
R["frameCount"] = d.get_static_property("UnityEngine.Time", "frameCount", CORE)
R["save_before_newgame"] = save_info(); print("pre", R["rts"], R["frameCount"], R["save_before_newgame"]["finished"].__len__(), flush=True)
assert R["rts"] <= 1200
d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, True)
def seeds(): return save_info().get("stacks", {}).get("42396f")
try:
    guard.risky("d01 A"); off = log_mark(); R["log_off"] = off
    assert "MainMenu" in scenes()
    print("new_game", new_game(), now(), flush=True)
    for _ in range(20):
        time.sleep(1.5)
        try: ppos(); break
        except Exception: pass
    time.sleep(2); R["save_after_newgame"] = save_info()
    guard.restore_window("d01 A tp"); tp_hare(1.3)
    for i in range(12):
        if hint(): break
        step_towards(HARE, 0.2); time.sleep(0.4)
    R["hint1"] = bool(hint()); R["dist1"] = round(dxz(ppos(), HARE), 2); print("hint", R["hint1"], R["dist1"], flush=True)
    key("E", 0.1); time.sleep(1.0); assert dlg(), "диалог не открылся"
    n = 0; seq = []
    while n < 45:
        key("Space", 0.1); n += 1; time.sleep(1.0)
        l = line()
        if l and (not seq or seq[-1] != l): seq.append(l)
        if choices(): R["choices_in_first"] = True; break
        if not dlg(): break
    R["first"] = {"N_space": n, "closed": not dlg(), "replies": len(seq), "seq": seq}
    time.sleep(2); R["first"]["exc"] = exc_summary(off); R["save_after_first"] = save_info()
    print("FIRST N", n, "closed", not dlg(), "replies", len(seq), "exc", R["first"]["exc"]["total"], "finished", len(R["save_after_first"]["finished"]), flush=True)
    json.dump(R, open(os.path.join(OUT, "d01_a.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # --- второй разговор
    guard.restore_window("d01 A second"); off2 = log_mark()
    for i in range(12):
        if hint(): break
        step_towards(HARE, 0.2); time.sleep(0.4)
    R["hint2"] = bool(hint()); print("hint2", R["hint2"], round(dxz(ppos(), HARE), 2), flush=True)
    R["inv_before_yes"] = save_info()
    key("E", 0.1); t0 = time.time()
    while time.time() - t0 < 3 and not dlg(): time.sleep(0.1)
    assert dlg(), "второй диалог не открылся"
    R["second_first_line"] = line(); n2 = 0
    while n2 < 3:
        key("Space", 0.1); n2 += 1; time.sleep(1.0)
        print("second", n2, (line() or "")[:80], "choices", choices(), flush=True)
        if choices() or not dlg(): break
    R["second"] = {"N_space": n2, "choices": choices(), "line": line()}
    if choices():
        R["second"]["texts"] = [o.get_text() for o in d.find_objects(By.NAME, "TextChoice", enabled=True)]
        R["second"]["shot"] = shot("d01_choices")
        R["seeds_before"] = seeds()
        d.find_object(By.NAME, "ButtonChoice1", enabled=True).click(); time.sleep(2.0)
        R["after_click_line"] = line()
        for _ in range(6):
            if not dlg(): break
            key("Space", 0.1); time.sleep(1.2); R.setdefault("after_click_lines", []).append(line())
        time.sleep(2.5)
    R["seeds_after"] = seeds(); R["save_after_yes"] = save_info(); R["second"]["dlg_closed"] = not dlg()
    R["second"]["exc"] = exc_summary(off2)
    print("SECOND", json.dumps({k: R[k] for k in ("seeds_before", "seeds_after") if k in R}), R["second"], flush=True)
    json.dump(R, open(os.path.join(OUT, "d01_a.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
finally:
    d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, False)
