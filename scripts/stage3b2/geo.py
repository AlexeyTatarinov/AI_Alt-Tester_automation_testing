# -*- coding: utf-8 -*-
from s3blib import *
for n in ("LocationExit_ToBeach",):
    o = d.find_object(By.NAME, n, enabled=True)
    for comp in ("UnityEngine.BoxCollider", "UnityEngine.SphereCollider", "UnityEngine.MeshCollider", "UnityEngine.CapsuleCollider"):
        for p in ("bounds.center", "bounds.size"):
            try: print(n, comp, p, o.get_component_property(comp, p, PHYS))
            except Exception as e: break
for o in d.find_objects(By.COMPONENT, "LocationEntrance", enabled=True): print("entrance", o.name, [round(o.worldX, 2), round(o.worldY, 2), round(o.worldZ, 2)])
for o in d.find_objects(By.COMPONENT, "SpawnSystem", enabled=False): print("spawnsys", o.name)
print("pig", [round(v, 2) for v in ppos()], sname(gstate()), alert_count())
c = crit("PlantCritter (4)"); print("crit4", [round(v, 2) for v in cpos(c)], alert(c))
