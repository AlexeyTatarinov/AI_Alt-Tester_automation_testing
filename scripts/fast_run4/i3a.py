import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); pre = preflight("int03")
d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, True)
guard.risky("INT-03 диалог")
H0 = save_hashes(); json.dump({"h0": H0, "log0": log_mark()}, open("int03_h0.json","w"))
print("h0==bk", H0 == bk_hashes(), "dlg", dlg(), "inv", comp_active("UIInventory"))
tp_hare(1.3)
p = ppos(); print("pos", p, "dxz hare", round(dxz(p, HARE),2))
p0 = ppos(); k, p1 = step_towards(HARE, 0.15); print("step", k, "moved", round(dxz(p0,p1),2), "dxz hare", round(dxz(p1,HARE),2), "hint", hint())
print("hint", hint()); print(shot("int03_hint"))
t0 = time.time(); key("E", 0.1); op=None
while time.time()-t0 < 2.0:
    if dlg(): op = round(time.time()-t0,2); break
    time.sleep(0.05)
print("dialog opened s:", op)
time.sleep(0.5)
print(shot("int03_dlg_open"))
for t in dlg_texts(): print("T", t)
print("choices", choices())
o = ui_obj("UIDialogueManager"); print("mgr", o.name if o else None)
