import sys; sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\modules")
from elib import *
try:
    autosync(True)
    ex=[o for o in d.find_objects(By.COMPONENT,"LocationExit",enabled=False)]
    for o in ex: print(o.name, round(o.worldX,1),round(o.worldY,1),round(o.worldZ,1), rd(o,"LocationExit","_locationToLoad.name"))
    e=[o for o in ex if "JumpDown" not in o.name][0]
    teleport("T1",e.worldX,e.worldY+0.5,e.worldZ)
    for i in range(20):
        time.sleep(1)
        sc=scenes()
        if "Field_Hill" in sc and pig(): break
    time.sleep(3); print(scenes(), gstate())
    c=[x for x in d.find_objects(By.COMPONENT,"Critter",enabled=False) if x.name=="PlantCritter"][0]; c.update_object(); cp=(c.worldX,c.worldY,c.worldZ)
    teleport("T1",cp[0]-3,cp[1]+0.3,cp[2]); time.sleep(2); print("near", gstate(), c.get_component_property("Critter","isPlayerInAlertZone",ASM))
    ents=[o for o in d.find_objects(By.COMPONENT,"LocationEntrance",enabled=False)]
    far=max(ents,key=lambda o: math.hypot(o.worldX-cp[0],o.worldZ-cp[2]))
    print("far entrance", far.name)
    teleport("T1",far.worldX,far.worldY+0.5,far.worldZ); time.sleep(3)
    print("far", gstate(), c.get_component_property("Critter","isPlayerInAlertZone",ASM), scenes())
finally:
    autosync(False)
