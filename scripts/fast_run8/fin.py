import sys, json
sys.path.insert(0, r"Test_Ai\scripts\fast_run7")
from r4lib import *
d=connect()
print("autoSync", d.get_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS))
print("restore ok", restore()); print("hashes", save_hashes()); print("backup", bk_hashes())
