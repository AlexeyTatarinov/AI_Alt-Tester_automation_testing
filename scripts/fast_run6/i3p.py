import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("int03p")
print("pos", ppos(), "dxz", round(dxz(ppos(),HARE),2), "hint", hint(), "dlg", dlg(), "state", pstate())
for o in d.find_objects(By.COMPONENT, "UIInteraction", enabled=False): print("UIInteraction", o.name, o.enabled)
for o in d.find_objects(By.NAME, "BardHare", enabled=False): print("hare", o.name, o.worldX, o.worldY, o.worldZ)
