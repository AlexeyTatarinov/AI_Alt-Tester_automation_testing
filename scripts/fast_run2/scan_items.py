import os, sys, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastlib import *
import guard
d = connect(); BASE={"PersistentManagers","Gameplay"}
def locs(): return [s for s in scenes() if s not in BASE]
res={}
for loc in ["Beach","Field_Hill","Field_Farms","Mountain_Path","Mountain_Cave","Town_Market","Town_Inner","Town_Upper"]:
    guard.before_case("scan "+loc)
    key("C",0.1); time.sleep(0.8); btn=None
    for o in d.find_objects(By.COMPONENT,"LocationTeleporterButton",enabled=False):
        try: lab=o.get_component_property("LocationTeleporterButton","label.text",ASM)
        except Exception: lab=None
        if lab and lab.startswith(loc+" via"): btn=o; break
    b=locs(); btn.click(); t0=time.time()
    while time.time()-t0<30:
        time.sleep(0.5)
        try:
            if locs()!=b and len(pigs())>=1: break
        except Exception: pass
    time.sleep(2)
    its=d.find_objects(By.COMPONENT,"CollectableItem",enabled=False)
    res[loc]=[(o.name,round(o.worldX,1),round(o.worldY,1),round(o.worldZ,1)) for o in its]
    pots=d.find_objects_which_contain(By.NAME,"Cauldron",enabled=False)+d.find_objects_which_contain(By.NAME,"Pot",enabled=False)
    res[loc+"_pots"]=[(o.name,round(o.worldX,1),round(o.worldY,1),round(o.worldZ,1)) for o in pots[:4]]
    print(loc,len(its),res[loc][:3],res[loc+"_pots"][:2],flush=True)
