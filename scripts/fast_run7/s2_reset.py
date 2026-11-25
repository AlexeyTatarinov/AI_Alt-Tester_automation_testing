import os, sys, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("s2_reset")
guard.risky("to_menu NEW5")
print("to_menu", to_menu(), scenes(), now())
print("restore", restore(), save_hashes()[SAVE0F], bk_hashes()[SAVE0F])
assert sha(SAVE0F) == bk_hashes()[SAVE0F]
preflight("s2_newgame2")
print("new_game", new_game(), scenes(), now())
teleport("T1", HARE[0]-1.3, HARE[1]+0.3, HARE[2]); time.sleep(2.0)
print("pos", ppos(), "dist", round(dxz(ppos(), HARE),2))
