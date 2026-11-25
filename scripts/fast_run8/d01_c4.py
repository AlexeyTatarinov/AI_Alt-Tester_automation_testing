import sys, json
sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\fast_run7")
from r4lib import *
d=connect(); guard.restore_window("c4"); preflight("d01c4")
d.set_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS,True)
try:
    teleport("T1", POT[0]+1.3, POT[1]+0.3, POT[2]); time.sleep(2.0)
    for i in range(12):
        if hint(): break
        step_towards(POT, 0.2); time.sleep(0.4)
    print("hint", hint(), "dist", round(dxz(ppos(),POT),2), flush=True)
    guard.risky("d01 cook E"); off=log_mark(); print("save before", save_info())
    key("E",0.1); time.sleep(1.5)
    print("inv", inv(), "dlg", dlg(), "tab", tab_type())
    print("slots", [(n,a,at) for _,n,a,at in slots()])
    print(shot("d01_pot_E"))
    print("exc", exc_summary(off)["total"])
finally:
    d.set_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS,False)
