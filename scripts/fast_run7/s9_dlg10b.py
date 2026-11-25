# -*- coding: utf-8 -*-
import os, sys, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("s9"); which = sys.argv[1] if len(sys.argv) > 1 else "ButtonChoice1"
d.set_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS,True)
def seeds():
    for k, v in save_info().get("stacks", {}).items():
        if k == "42396f": return v
try:
    guard.risky("dlg10b " + which); off = log_mark()
    if "MainMenu" not in scenes():
        to_menu()
        for _ in range(20):
            time.sleep(1.5)
            if "MainMenu" in scenes() and d.find_objects(By.NAME, "Button New Game", enabled=False): break
        time.sleep(1)
    print("restore", restore()); print("new_game", new_game(), now())
    for _ in range(20):
        time.sleep(1.5)
        try: ppos(); break
        except Exception: pass
    time.sleep(2); tp_hare(1.3)
    for i in range(10):
        if hint(): break
        step_towards(HARE, 0.2); time.sleep(0.4)
    print("hint", hint(), "seeds", seeds(), flush=True)
    key("E", 0.1); time.sleep(1.0); assert dlg(), "диалог не открылся"
    t0 = time.time(); n = 0; last = None; t_last = t0
    while n < 45:
        key("Space", 0.1); n += 1; time.sleep(1.0)
        l = line()
        if l != last: last = l; t_last = time.time(); print(n, "реплика:", (l or "")[:70], flush=True)
        if choices(): break
        if not dlg(): break
    print("RESULT нажатий", n, "choices", choices(), "dlg", dlg(), "с последней реплики до кнопок: %.1f с" % (time.time() - t_last), "всего %.1f" % (time.time()-t0))
    if choices():
        print("texts", [o.get_text() for o in d.find_objects(By.NAME, "TextChoice", enabled=True)], shot("s9_choices_" + which))
        s_before = seeds(); print("seeds до выбора", s_before, "inv", save_info().get("stacks"))
        d.find_object(By.NAME, which, enabled=True).click(); time.sleep(2.0)
        print("после клика", which, "dlg", dlg(), "line", line(), "seeds", seeds(), flush=True)
        for _ in range(4):
            if not dlg(): break
            key("Space", 0.1); time.sleep(1.2)
        time.sleep(2); print("итог dlg", dlg(), "seeds", seeds(), "finished", save_info().get("finished"))
    print("exc", json.dumps(exc_summary(off), ensure_ascii=False)[:500])
finally:
    d.set_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS,False)
