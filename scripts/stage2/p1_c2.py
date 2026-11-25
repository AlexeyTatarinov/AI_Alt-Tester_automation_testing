from s2lib import *
R = json.load(open(os.path.join(R2, "p1_c1.json"), encoding="utf-8")); off = R["off"]
autosync(True)
try:
    assert hint()
    R["tp_dist_final"] = round(dxz(ppos(), POT), 2)
    key("E", 0.1); time.sleep(1.5)
    print("inv", inv(), "state", sname(gstate()), "tab", tab_type())
    print("slots", [(n, a, at) for _, n, a, at in slots()])
    btns = {}
    for o in d.find_objects(By.COMPONENT, "UnityEngine.UI.Button", enabled=True):
        btns[o.name] = o.id
    print("buttons", list(btns))
    print(shot("p1_pot_open"))
    # тексты в UI инвентаря
    print([t for t in dlg_texts()][:40])
    R["snap_opened"] = snap("котёл открыт", off)
    jdump(os.path.join(R2, "p1_c1.json"), R)
finally:
    autosync(False)
