import sys; sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\modules")
from elib import *
try:
    autosync(True)
    print(scenes(), gstate())
    o=[x for x in d.find_objects(By.COMPONENT,"LocationExit",enabled=False) if x.name=="LocationExit_ToMountainPath"][0]
    b=o.get_component_property("UnityEngine.BoxCollider","bounds","UnityEngine.PhysicsModule",max_depth=3)
    mn,mx=b["min"],b["max"]; print("bounds min",mn["x"],mn["y"],mn["z"],"max",mx["x"],mx["y"],mx["z"])
    ent=[e for e in d.find_objects(By.COMPONENT,"LocationEntrance",enabled=False)]
    en=min(ent,key=lambda e: math.hypot(e.worldX-o.worldX,e.worldZ-o.worldZ))
    vx,vz=en.worldX-o.worldX,en.worldZ-o.worldZ; n=math.hypot(vx,vz); print("entrance",en.name,round(n,1))
    px,pz=o.worldX+3*vx/n,o.worldZ+3*vz/n
    teleport("T1",px,o.worldY+0.5,pz); time.sleep(2); print("after tp",ppos())
    for i in range(40):
        p=ppos(); k=choose_key(p,(o.worldX,o.worldY,o.worldZ)); key(k,0.1); time.sleep(0.15)
        if i%4==0: print(i,k,[round(v,2) for v in ppos()], scenes())
        if "Mountain_Path" in scenes(): break
finally:
    autosync(False)
