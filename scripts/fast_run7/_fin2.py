import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); print(scenes(), "restore", restore(), save_hashes() == bk_hashes())
if len(d.find_objects(By.NAME, "Settings_Panel_PR", enabled=True)): print("settings open")
print("autoSync", d.get_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS))
