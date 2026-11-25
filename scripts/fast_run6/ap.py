import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("approach")
print("pos", ppos(), "hare dxz", round(dxz(ppos(), HARE),2), "dlg", dlg(), "hint", hint())
for i in range(12):
    p=ppos(); k=choose_key(p, HARE); key(k, 0.1); time.sleep(0.5)
    print(i, k, tuple(round(v,2) for v in ppos()), round(dxz(ppos(),HARE),2), "hint", hint())
    if hint(): break
