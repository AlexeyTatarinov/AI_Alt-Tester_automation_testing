import sys; sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\modules")
from elib import *
print(scenes(), "state", gstate(), "pause", pause_open(), "cheat", cheat_open(), "pigs", len(pigs()))
print("pos", ppos())
print(guard.unity_window().get("iconic"))
