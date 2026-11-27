# -*- coding: utf-8 -*-
# d02 этап 1: New Game, первый разговор до закрытия, второй разговор: E, один Space, No (ButtonChoice2)
import os, sys, json
sys.path.insert(0, r"Test_Ai\scripts\fast_run7")
from r4lib import *
OUT = r"Test_Ai\Reports_2026-11-21\results\run8_d02_20261124"; os.makedirs(OUT, exist_ok=True)
d = connect(); pre = preflight("d02a")
R = json.load(open(os.path.join(OUT, "d02_a.json"), encoding="utf-8")); R["resume"] = now(); R["E_without_hint_dlg_opened"] = False
_rt = d.get_static_property("UnityEngine.Time", "realtimeSinceStartup", CORE)
_fc = d.get_static_property("UnityEngine.Time", "frameCount", CORE)

d.set_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS,True)
def seeds(): return save_info().get("stacks", {}).get("42396f")
def dump():
    json.dump(R, open(os.path.join(OUT, "d02_a2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
try:
    assert "Beach" in scenes() and not dlg()
    off = log_mark()
    tp_hare(1.3)
    for i in range(12):
        if hint(): break
        step_towards(HARE, 0.2); time.sleep(0.4)
    R["hint2b"] = hint(); R["dist2b"] = round(dxz(ppos(), HARE), 2); print("hint2b", R["hint2b"], R["dist2b"], flush=True)
    R["seeds_before_no"] = seeds(); R["stacks_before_no"] = save_info()["stacks"]; print("seeds", seeds(), flush=True)
    guard.risky("d02 conv2 No"); off2 = log_mark()
    key("E", 0.1); time.sleep(1.0); R["conv2_open"] = dlg(); R["conv2_first_line"] = line(); print("conv2 open", R["conv2_open"], R["conv2_first_line"], flush=True)
    assert dlg()
    key("Space", 0.1); time.sleep(1.0)
    R["conv2_after_space_line"] = line(); R["conv2_choices"] = choices()
    R["conv2_texts"] = [o.get_text() for o in d.find_objects(By.NAME, "TextChoice", enabled=True)] if choices() else None
    R["conv2_shot"] = shot("d02_choices_No") if choices() else None
    print("choices", R["conv2_choices"], R["conv2_texts"], flush=True); dump()
    assert choices()
    d.find_object(By.NAME, "ButtonChoice2", enabled=True).click(); time.sleep(2.0)
    R["after_no"] = {"dlg": dlg(), "line": line(), "seeds": seeds(), "texts_now": dlg_texts()[:6]}
    print("after No", R["after_no"], flush=True)
    sp = []
    for _ in range(6):
        if not dlg(): break
        key("Space", 0.1); time.sleep(1.2); sp.append((line(), dlg()))
    R["after_no_spaces"] = sp
    time.sleep(2)
    R["final_dlg"] = dlg(); R["seeds_after_no"] = seeds(); R["save_after_no"] = save_info()
    R["exc_conv2"] = exc_summary(off2); R["exc_all"] = exc_summary(off)
    R["inv_after_no"] = inv_snapshot() if not dlg() else "диалог открыт"
    dump()
    print("итог dlg", R["final_dlg"], "seeds", R["seeds_after_no"], "finished", R["save_after_no"]["finished"], "exc", R["exc_conv2"]["total"], flush=True)
    print("inv_after_no", R["inv_after_no"])
finally:
    d.set_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS,False); dump()
