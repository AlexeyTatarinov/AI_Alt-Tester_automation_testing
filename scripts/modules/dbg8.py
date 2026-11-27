import sys; sys.path.insert(0, r"Test_Ai\scripts\modules")
from elib import *
for i in range(8):
    print(i, gstate(), scenes()); time.sleep(2)
print("walk W"); key("W",0.5); time.sleep(2); print(gstate())
