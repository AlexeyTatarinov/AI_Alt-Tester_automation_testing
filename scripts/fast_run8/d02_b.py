# -*- coding: utf-8 -*-
# d02 этап 2: повторить второй разговор после No; если Yes/No снова - нажать Yes
import os, sys, json
sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\fast_run7")
from r4lib import *
OUT = r"C:\Users\Aotat\Desktop\Test_Ai\Reports_2026-11-21\results\run8_d02_20261124"
d = connect(); pre = preflight("d02b"); R = {"start": now()}
d.set_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS,True)
def seeds(): return save_info().get("stacks", {}).get("42396f")
def dump(): json.dump(R, open(os.path.join(OUT, "d02_b.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
try:
    assert "Beach" in scenes() and not dlg()
    off = log_mark(); R["seeds_before"] = seeds(); R["finished_before"] = save_info()["finished"]
    tp_hare(1.3)
    for i in range(12):
        if hint(): break
        step_towards(HARE, 0.2); time.sleep(0.4)
    R["hint"] = hint(); R["dist"] = round(dxz(ppos(), HARE), 2); print("hint", R["hint"], R["dist"], flush=True)
    guard.risky("d02 conv3 repeat")
    key("E", 0.1); time.sleep(1.0); R["open"] = dlg(); R["first_line"] = line(); print("open", R["open"], R["first_line"], flush=True)
    assert dlg()
    key("Space", 0.1); time.sleep(1.0)
    R["after_space_line"] = line(); R["choices"] = choices()
    R["texts"] = [o.get_text() for o in d.find_objects(By.NAME, "TextChoice", enabled=True)] if choices() else None
    print("after space", R["after_space_line"], "choices", R["choices"], R["texts"], flush=True); dump()
    if choices():
        R["shot"] = shot("d02_choices_repeat")
        d.find_object(By.NAME, "ButtonChoice1", enabled=True).click(); time.sleep(2.0)
        R["after_yes"] = {"dlg": dlg(), "line": line(), "seeds": seeds()}; print("after Yes", R["after_yes"], flush=True)
        sp = []
        for _ in range(14):
            if not dlg(): break
            key("Space", 0.1); time.sleep(1.2); sp.append((line(), dlg()))
        R["after_yes_spaces"] = sp
    time.sleep(2)
    R["final_dlg"] = dlg(); R["seeds_after"] = seeds(); R["save_after"] = save_info(); R["exc"] = exc_summary(off)
    R["inv_after"] = inv_snapshot() if not dlg() else "диалог открыт"
    dump()
    print("итог dlg", R["final_dlg"], "seeds", R["seeds_after"], "finished", R["save_after"]["finished"], "exc", R["exc"]["total"], R["exc"]["by_type"], flush=True)
    print("inv_after", R["inv_after"])
finally:
    d.set_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS,False); dump()
