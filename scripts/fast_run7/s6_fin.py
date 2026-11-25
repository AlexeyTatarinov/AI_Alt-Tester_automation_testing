import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("s6_fin"); guard.risky("to_menu fin")
print("to_menu", to_menu(), scenes()); print("restore", restore()); print(save_hashes() == bk_hashes(), save_hashes())
print("autoSync", d.get_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS), "pause", pause_open(), "dlg", dlg())
