import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("int03q")
for i in range(6):
    p0 = ppos(); k, p1 = step_towards(HARE, 0.3); time.sleep(0.4)
    print(i, k, "moved", round(dxz(p0,p1),2), "dxz", round(dxz(p1,HARE),2), "pos", tuple(round(v,2) for v in ppos()), "hint", hint(), "state", pstate())
    if hint(): break
