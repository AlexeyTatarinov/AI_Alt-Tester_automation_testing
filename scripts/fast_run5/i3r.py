import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("int03r")
print("pos", tuple(round(v,2) for v in ppos()), "dxz", round(dxz(ppos(),HARE),2), "hint", hint(), "dlg", dlg())
for i in range(6):
    p0 = ppos(); k, p1 = step_towards(HARE, 0.3); time.sleep(0.4)
    print(i, k, round(dxz(p0,p1),2), "dxz", round(dxz(p1,HARE),2), "hint", hint())
    if hint(): break
