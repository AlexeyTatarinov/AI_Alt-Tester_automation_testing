# -*- coding: utf-8 -*-
from s2blib import *
R = json.load(open(os.path.join(R2, "p3_a.json"), encoding="utf-8")); off = R["off"]
def dump(): jdump(os.path.join(R2, "p3_b.json"), R)
autosync(True)
try:
    s0 = snap("3 котёл до", off); R["pot_before"] = s0
    ok = False
    teleport("T1", POT[0] - 1.5, POT[1] + 0.3, POT[2]); time.sleep(2.0)
    for i in range(4):
        if hint(): ok = True; break
        time.sleep(0.5)
    R["pot_hint"] = ok; R["pot_dist"] = round(dxz(ppos(), POT), 2); print("pot hint", ok, R["pot_dist"], flush=True)
    assert ok
    key("E", 0.1); time.sleep(1.5)
    assert inv(), "UI не открылся"
    sl = [x for x in slots() if "SweetCream" in x[1]]; assert sl, "нет рецепта"
    sl[0][0].click(); time.sleep(1.0)
    cook = None
    for o in d.find_objects(By.NAME, "Text (TMP)", enabled=True):
        try:
            if o.get_text().strip() == "Cook": cook = o.get_parent()
        except Exception: pass
    assert cook is not None, "нет Cook"
    st0 = save_info(); guard.risky("p3 cook")
    cook.click(); time.sleep(3.0)
    if inv(): key("Tab", 0.1); time.sleep(1.5)
    s1 = snap("3 котёл после", off); R["pot_after"] = s1; R["pot_diff"] = diff(s0, s1); R["state"] = sname(gstate())
    print("POT", json.dumps(R["pot_diff"], ensure_ascii=False), R["state"], "exc", s1["exc"], flush=True); dump()
finally:
    autosync(False); dump()
