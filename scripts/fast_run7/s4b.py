# -*- coding: utf-8 -*-
import os, sys, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("s4b"); d.set_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS,True)
crit = [c for c in d.find_objects(By.NAME, "PlantCritter", enabled=False)]
names = []
for c in d.find_objects_which_contain(By.NAME, "PlantCritter", enabled=False):
    if c.id not in [x.id for x in names]: names.append(c)
print(len(names), [(c.name, c.id) for c in names])
c = names[int(sys.argv[1]) if len(sys.argv) > 1 else 0]
c.update_object(); cp = (c.worldX, c.worldY, c.worldZ)
def hp():
    try: return c.get_component_property("Damageable", "_currentHealthSO.CurrentHealth", ASM)
    except Exception as e: return "ERR"
print("start", cp, "hp", hp())
teleport("T1", cp[0]-3.0, cp[1]+0.3, cp[2]); time.sleep(1.0)
for i in range(30):
    c.update_object(); cp = (c.worldX, c.worldY, c.worldZ); p = ppos(); dd = dxz(p, cp)
    if dd < 1.4: break
    step_towards(cp, 0.15); time.sleep(0.1)
print("tp dist", round(dxz(ppos(), cp),2)); print("dist", round(dxz(ppos(), cp),2), "steps", i, shot("s4b_near"))
for h in range(8):
    key("F", 0.1); time.sleep(0.7)
    try: c.update_object(); st = (c.enabled, hp(), round(c.worldX,1), round(c.worldZ,1))
    except Exception as e: st = "gone: " + type(e).__name__
    print("hit", h+1, st, "items", len(d.find_objects(By.COMPONENT, "CollectableItem", enabled=False)), flush=True)
    if isinstance(st, str): break
time.sleep(1.5)
l = d.find_objects(By.COMPONENT, "CollectableItem", enabled=False)
print("ITEMS", [(o.name, round(o.worldX,1), round(o.worldY,1), round(o.worldZ,1)) for o in l]); print(shot("s4b_end"))

d.set_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS,False); print("autoSync", d.get_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS))
