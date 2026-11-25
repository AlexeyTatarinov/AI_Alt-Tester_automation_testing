import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("calib")
d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, True)
teleport("T1", -135.1, -27.8, -470.0); time.sleep(3.0)
for dur in (0.1, 0.15, 0.2, 0.25, 0.1, 0.15, 0.2, 0.25):
    p0 = ppos(); k = choose_key(p0, (p0[0], p0[1], p0[2]-5)); key(k, dur); time.sleep(0.3); p1 = ppos()
    print(dur, k, round(dxz(p0, p1), 2), "dz", round(p1[2]-p0[2], 2), "state", pstate())
