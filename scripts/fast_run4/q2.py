import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); print(shot("s1_state"))
print("pigs", len(pigs()), "alive", guard.alive())
print("timeScale", d.get_static_property("UnityEngine.Time","timeScale",CORE))
