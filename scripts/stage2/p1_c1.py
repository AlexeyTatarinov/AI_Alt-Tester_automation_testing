from s2lib import *
R = {}
autosync(True)
try:
    off = log_mark(); R["off"] = off
    s0 = snap("IT-04 до", off); R["snap_before"] = s0; print(json.dumps(s0, ensure_ascii=False))
    teleport("T1", POT[0] + 1.7, POT[1] + 0.3, POT[2]); time.sleep(2.0)
    R["tp_dist"] = round(dxz(ppos(), POT), 2)
    for i in range(8):
        if hint(): break
        step_towards(POT, 0.1); time.sleep(0.4)
    R["hint"] = bool(hint()); R["dist"] = round(dxz(ppos(), POT), 2); print("hint", R["hint"], R["dist"], "tp", R["tp_dist"], flush=True)
    if R["hint"]:
        key("E", 0.1); time.sleep(1.5)
        print("inv", inv(), "state", sname(gstate()), "tab", tab_type())
        print("slots", [(n, a, at) for _, n, a, at in slots()])
        # кнопки с текстами
        for o in d.find_objects(By.COMPONENT, "UnityEngine.UI.Button", enabled=True):
            try:
                t = [c.get_text() for c in o.get_all_components() if False]
            except Exception: t = None
        btns = []
        for o in d.find_objects(By.COMPONENT, "UnityEngine.UI.Button", enabled=True):
            btns.append(o.name)
        print("buttons", btns)
        print(shot("p1_pot_open"))
    jdump(os.path.join(R2, "p1_c1.json"), R)
finally:
    autosync(False)
