import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("reset")
key("Escape", 0.1); time.sleep(1.5); print("pause", pause_open(), "dlg", dlg())
print("to_menu", to_menu()); time.sleep(2)
print("restore equal:", restore(), "scenes", scenes())
print("hash==bk", save_hashes()==bk_hashes())
print("new_game", new_game(), scenes(), "pigs", len(pigs()), "dlg", dlg(), "state", pstate())
