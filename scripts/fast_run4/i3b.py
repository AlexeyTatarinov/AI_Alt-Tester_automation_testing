import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("int03b")
print("pos", ppos(), "dxz", round(dxz(ppos(),HARE),2), "hint", hint(), "dlg", dlg(), "scenes", scenes())
for i in range(5):
    k,p = step_towards(HARE, 0.15); time.sleep(0.4)
    print(i, k, "dxz", round(dxz(p,HARE),2), "hint", hint(), "state", pstate())
    if hint(): break
for o in d.find_objects(By.COMPONENT, "UIInteraction", enabled=False): print("UIInteraction obj", o.name, o.enabled)
