import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("int03e")
J = json.load(open("int03_h0.json")); OFF = J["log0"]
t0=time.time(); back=None
while time.time()-t0 < 60:
    if hint() and not dlg(): back = round(time.time()-t0,1); break
    time.sleep(0.5)
print("hint back s:", back, "hint", hint(), "dlg", dlg(), "pos", ppos(), "dxz", round(dxz(ppos(),HARE),2), "state", pstate())
a = approach_step("S" if False else "A", 0.3, 0.6); print("step", a["key"], a["moved_m"])
H1 = save_hashes(); print("save changed vs h0:", H1 != J["h0"])
for k in H1: print(k[-40:], J["h0"][k], "->", H1[k])
lg = log_since(OFF); print("log", lg)
print(shot("int03_closed"))
print("autosync", d.get_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS), "ts", d.get_static_property("UnityEngine.Time","timeScale",CORE))
