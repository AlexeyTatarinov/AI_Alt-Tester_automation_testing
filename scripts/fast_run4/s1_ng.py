import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); pre = preflight("s1_ng")
print("scenes", scenes(), "hashes==backup", save_hashes() == bk_hashes())
guard.risky("New Game перед INT-03")
print("to_menu", to_menu()); time.sleep(3.0)
print("hash before NG == backup:", save_hashes() == bk_hashes())
print("new_game", new_game(), scenes(), "pigs", len(pigs()), "pos", ppos(), "pause", pause_open(), "timeScale", d.get_static_property("UnityEngine.Time","timeScale",CORE))
print("autoSync", d.get_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS))
