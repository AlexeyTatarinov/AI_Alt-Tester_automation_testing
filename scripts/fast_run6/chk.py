import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("chk")
print("state", pstate(), "pos", ppos(), "hash==bk", save_hashes()==bk_hashes())
p0=ppos(); key("W",0.3); time.sleep(0.6); print("moved", round(dxz(p0,ppos()),2), "state", pstate())
