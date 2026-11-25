import sys; sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\modules")
from elib import *
try:
    autosync(True)
    goto("Field_Hill"); time.sleep(2)
    print("in Field_Hill state", gstate())
    c=[x for x in d.find_objects(By.COMPONENT,"Critter",enabled=False) if x.name=="PlantCritter"][0]; c.update_object(); cp=(c.worldX,c.worldY,c.worldZ)
    teleport("T1",cp[0]-3,cp[1]+0.3,cp[2]); time.sleep(2); print("near", gstate(), c.get_component_property("Critter","isPlayerInAlertZone",ASM))
    ents=[o for o in d.find_objects(By.COMPONENT,"LocationEntrance",enabled=False)]
    far=max(ents,key=lambda o: math.hypot(o.worldX-cp[0],o.worldZ-cp[2]))
    print("far entrance", far.name)
    teleport("T1",far.worldX,far.worldY+0.5,far.worldZ); time.sleep(3)
    print("far", gstate(), c.get_component_property("Critter","isPlayerInAlertZone",ASM), scenes())
finally:
    autosync(False)
