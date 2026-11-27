import sys; sys.path.insert(0, r"Test_Ai\scripts\modules")
from elib import *
print(goto("Beach"))
for i in range(6):
    print(i, gstate(), pause_open(), inv_open(), cheat_open(), scenes()); time.sleep(1)
print(to_gameplay(3))
print(gstate(), pause_open())
