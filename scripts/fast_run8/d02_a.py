# -*- coding: utf-8 -*-
# d02 этап 1: New Game, первый разговор до закрытия, второй разговор: E, один Space, No (ButtonChoice2)
import os, sys, json
sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\fast_run7")
from r4lib import *
OUT = r"C:\Users\Aotat\Desktop\Test_Ai\Reports_2026-11-21\results\run8_d02_20261124"; os.makedirs(OUT, exist_ok=True)
d = connect(); pre = preflight("d02a")
R = {"start": now()}
R["realtimeSinceStartup"] = d.get_static_property("UnityEngine.Time", "realtimeSinceStartup", CORE)
R["frameCount"] = d.get_static_property("UnityEngine.Time", "frameCount", CORE)
assert R["realtimeSinceStartup"] <= 1200
d.set_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS,True)
def seeds(): return save_info().get("stacks", {}).get("42396f")
def dump():
    json.dump(R, open(os.path.join(OUT, "d02_a.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
try:
    off = log_mark(); R["save_before_newgame"] = save_info()
    assert "MainMenu" in scenes()
    R["new_game_s"] = new_game(); print("new_game", R["new_game_s"], now(), flush=True)
    for _ in range(20):
        time.sleep(1.5)
        try: ppos(); break
        except Exception: pass
    time.sleep(2)
    R["save_after_newgame"] = save_info(); R["recipe_before"] = None
    tp_hare(1.3)
    for i in range(10):
        if hint(): break
        step_towards(HARE, 0.2); time.sleep(0.4)
    R["hint1"] = hint(); R["dist1"] = round(dxz(ppos(), HARE), 2)
    print("hint", R["hint1"], R["dist1"], "seeds", seeds(), flush=True)
    guard.risky("d02 conv1")
    key("E", 0.1); time.sleep(1.0); assert dlg(), "диалог не открылся"
    n = 0; seq = []; off1 = log_mark()
    while n < 45:
        key("Space", 0.1); n += 1; time.sleep(1.0)
        l = line()
        if l and (not seq or seq[-1] != l): seq.append(l)
        if choices() or not dlg(): break
    R["conv1"] = {"N": n, "replies": len(seq), "closed": not dlg(), "choices": choices(), "first": seq[:1], "last": seq[-1:], "seq": seq, "exc": exc_summary(off1)}
    time.sleep(2)
    R["save_after_conv1"] = save_info(); dump()
    print("conv1", {k: R["conv1"][k] for k in ("N","replies","closed","choices")}, "exc", R["conv1"]["exc"]["total"], "finished", R["save_after_conv1"]["finished"], flush=True)
    assert not dlg()
    # рецепт до второго разговора
    R["inv_before"] = inv_snapshot(); dump()
    print("inv_before", R["inv_before"], flush=True)
    for i in range(12):
        if hint(): break
        step_towards(HARE, 0.2); time.sleep(0.4)
    R["hint2"] = hint(); R["dist2"] = round(dxz(ppos(), HARE), 2); print("hint2", R["hint2"], R["dist2"], flush=True)
    R["seeds_before_no"] = seeds(); R["stacks_before_no"] = save_info()["stacks"]
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
    print("итог dlg", R["final_dlg"], "seeds", R["seeds_after_no"], "finished", R["save_after_no"]["finished"], "exc", R["exc_all"]["total"], flush=True)
    print("inv_after_no", R["inv_after_no"])
finally:
    d.set_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS,False); dump()
