import sys; sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\modules")
from elib import *
try:
    autosync(True)
    cl=[c for c in d.find_objects(By.COMPONENT,"Critter",enabled=False) if c.name.startswith("Gluecose")]
    c=cl[0]; cp=(c.worldX,c.worldY,c.worldZ); print(c.name,cp)
    teleport("T1",cp[0]-3,cp[1]+0.3,cp[2]); time.sleep(2)
    for i in range(4):
        cl=[x for x in d.find_objects(By.COMPONENT,"Critter",enabled=False) if x.name.startswith("Gluecose")]
        print([ (x.name,x.id,x.enabled,round(x.worldX),round(x.worldZ)) for x in cl][:4])
        for x in cl[:3]:
            try: print(" ",x.name,"alert",x.get_component_property("Critter","isPlayerInAlertZone",ASM), "hpSO",x.get_component_property("Damageable","_currentHealthSO",ASM,max_depth=2), "dead",x.get_component_property("Damageable","IsDead",ASM))
            except Exception as e: print("  err",type(e).__name__)
        time.sleep(1)
finally:
    autosync(False)
