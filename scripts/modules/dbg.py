import sys; sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\modules")
from elib import *
print(scenes(), len(pigs()))
objs=d.get_all_elements(enabled=True)
print(len(objs)); print(sorted({o.name for o in objs})[:80])
print("scene counts: LocationEntrance", count_comp("LocationEntrance"), "SpawnSystem", count_comp("SpawnSystem"), "frames", d.get_static_property("UnityEngine.Time","frameCount",CORE), "timeScale", d.get_static_property("UnityEngine.Time","timeScale",CORE))
