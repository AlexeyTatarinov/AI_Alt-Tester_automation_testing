import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("s2_tp")
print("scenes", scenes(), "pigs", len(pigs()), "pause", pause_open(), "dlg", dlg(), "inv", inv(), "cheat", len(d.find_objects(By.NAME,"CheatMenu",enabled=True)), "state", pstate())
print("pos", ppos(), "cc", cc_enabled(pig()))
teleport("T1", HARE[0]-1.3, HARE[1]+0.3, HARE[2])
for t in (0.3, 1, 2, 3): time.sleep(t if t==0.3 else 1); print(t, ppos(), grounded(pig()))
