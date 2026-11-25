import sys; sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\modules")
from elib import *
ensure=None
print(scenes(), gstate())
for o in d.find_objects(By.COMPONENT,"LocationExit",enabled=False)[:3]:
    print(o.name, round(o.worldX,1),round(o.worldY,1),round(o.worldZ,1), [c.get("componentName") for c in o.get_all_components()])
    for comp,asm in (("UnityEngine.BoxCollider","UnityEngine.PhysicsModule"),("UnityEngine.SphereCollider","UnityEngine.PhysicsModule"),("UnityEngine.CapsuleCollider","UnityEngine.PhysicsModule")):
        try: print("  ",comp,o.get_component_property(comp,"bounds",asm,max_depth=3), o.get_component_property(comp,"isTrigger",asm))
        except Exception as e: pass
