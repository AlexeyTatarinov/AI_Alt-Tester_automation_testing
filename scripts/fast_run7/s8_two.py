# -*- coding: utf-8 -*-
import os, sys, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("s8_two"); d.set_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS,True)
def approach():
    for i in range(10):
        if hint(): return True
        step_towards(HARE, 0.2); time.sleep(0.4)
    return hint()
def talk_once(tag):
    ok = approach(); print(tag, "hint", ok, "dist", round(dxz(ppos(), HARE),2), flush=True)
    if not ok: return None
    key("E", 0.1); t0 = time.time()
    while time.time() - t0 < 3 and not dlg(): time.sleep(0.1)
    print(tag, "dlg open", dlg(), flush=True)
    if not dlg(): return None
    r = talk(120); print(tag, {k: v for k, v in r.items() if k != "log"}); print(tag, "reply", lines_seq(r["log"])[-3:] if lines_seq(r["log"]) else None)
    print(tag, "choices", choices(), "panel", comp_active("UIDialogueChoicesManager"), flush=True)
    return r
try:
    guard.risky("two talks"); off = log_mark()
    if "skipnew" not in sys.argv: print("new_game", new_game(), now())
    for _ in range(20):
        time.sleep(1.5)
        try: ppos(); break
        except Exception: pass
    time.sleep(2)
    tp_hare(1.3); si0 = save_info(); print("save0", si0.get("finished"), si0.get("stacks"))
    r1 = talk_once("T1"); time.sleep(2); print("closed", not dlg(), "save", save_info().get("finished"))
    if dlg(): print("диалог 1 остался открытым"); raise SystemExit
    time.sleep(2); print(shot("s8_after1"))
    r2 = talk_once("T2")
    if choices():
        ch = d.find_objects(By.PATH, "//Panel Choices/*", enabled=True) if False else d.find_objects(By.COMPONENT, "UIDialogueChoiceFiller", enabled=True)
        print("choice buttons", [(o.name, (lambda o: o.get_text() if True else "")(o)) for o in ch][:4]); print(shot("s8_choices"))
    print("exc", json.dumps(exc_summary(off), ensure_ascii=False)[:800]); print("save end", save_info().get("finished"), save_info().get("stacks"))
finally:
    d.set_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS,False)
