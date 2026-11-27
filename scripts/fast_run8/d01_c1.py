import sys, json
sys.path.insert(0, r"Test_Ai\scripts\fast_run7")
from r4lib import *
d=connect(); guard.restore_window("c1"); preflight("d01c")
t = inv_snapshot()
print(json.dumps(t, ensure_ascii=False))
json.dump(t, open(r"Test_Ai\Reports_2026-11-21\results\run8_d01_20261124\inv_after_yes.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
