# -*- coding: utf-8 -*-
import os, sys, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("s10"); which = sys.argv[1] if len(sys.argv) > 1 else "ButtonChoice1"
d.set_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS,True)
def seeds():
    return save_info().get("stacks", {}).get("42396f")
try:
    off = log_mark(); print("start", now(), "dlg", dlg(), "seeds", seeds(), "finished", save_info().get("finished"))
    for i in range(12):
        if hint(): break
        step_towards(HARE, 0.2); time.sleep(0.4)
    print("hint", hint(), "dist", round(dxz(ppos(), HARE),2), flush=True)
    key("E", 0.1); t0 = time.time()
    while time.time() - t0 < 3 and not dlg(): time.sleep(0.1)
    print("dlg open", dlg(), "line", line(), flush=True); assert dlg()
    n = 0; t0 = time.time()
    while n < 20:
        key("Space", 0.1); n += 1; time.sleep(1.0)
        print(n, "line", (line() or "")[:70], "dlg", dlg(), "choices", choices(), flush=True)
        if choices() or not dlg(): break
    print("RESULT нажатий", n, "choices", choices(), "за %.1f с" % (time.time()-t0))
    if choices():
        print("texts", [o.get_text() for o in d.find_objects(By.NAME, "TextChoice", enabled=True)], shot("s10_choices"))
        print("seeds до", seeds(), "inv", [(o.name) for o in d.find_objects(By.NAME, "ButtonChoice1", enabled=True)])
        d.find_object(By.NAME, which, enabled=True).click(); time.sleep(2.0)
        print("после", which, "dlg", dlg(), "line", line(), "seeds", seeds())
        for _ in range(6):
            if not dlg(): break
            key("Space", 0.1); time.sleep(1.2); print("  line", line(), "dlg", dlg())
        time.sleep(2); print("итог dlg", dlg(), "seeds", seeds(), "finished", save_info().get("finished"))
    print("exc", json.dumps(exc_summary(off), ensure_ascii=False)[:500])
finally:
    d.set_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS,False)
