import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); print(scenes(), len(pigs()))
try: print(ppos())
except Exception as e: print("ERR", e)
print(log_since(log_mark()-6000))
p = ppos()
for e in d.find_objects(By.COMPONENT, "LocationEntrance", enabled=False):
    print(e.name, round(e.worldX,2), round(e.worldY,2), round(e.worldZ,2), e.get_component_property("LocationEntrance","EntrancePath","Assembly-CSharp"), round(dist3(p,(e.worldX,e.worldY,e.worldZ)),2))
