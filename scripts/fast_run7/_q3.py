import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("q3"); d.set_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS,True)
print("pos", ppos(), "autoSync", d.get_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS))
c = d.find_objects(By.NAME, "PlantCritter", enabled=False)[0]; c.update_object(); cp=(c.worldX,c.worldY,c.worldZ); print("crit", cp, c.enabled)
print([ (x.get("componentName") if isinstance(x,dict) else str(x)) for x in c.get_all_components()])
print(teleport("T1", cp[0]-1.2, cp[1]+0.3, cp[2])); time.sleep(1); print("pos after", ppos(), dxz(ppos(), cp))
