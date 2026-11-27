import sys; sys.path.insert(0, r"Test_Ai\scripts\modules")
from elib import *
print("hash==backup BEFORE:", save_hashes()==bk_hashes(), flush=True)
print("window iconic", guard.unity_window().get("iconic"))
prestage("s1b_start")
print("new_game:", new_game_from_menu(), flush=True)
time.sleep(3)
print(scenes(), "state", gstate())
