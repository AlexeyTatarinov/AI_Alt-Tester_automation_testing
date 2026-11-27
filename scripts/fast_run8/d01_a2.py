import sys, json
sys.path.insert(0, r"Test_Ai\scripts\fast_run7")
from r4lib import *
d=connect(); guard.restore_window("a2"); off=log_mark()
ls=[]
for i in range(20):
    if not dlg(): break
    key("Space",0.1); time.sleep(1.0); ls.append(line())
time.sleep(2.5)
print("closed", not dlg(), ls, "exc", exc_summary(off)["total"], save_info())
