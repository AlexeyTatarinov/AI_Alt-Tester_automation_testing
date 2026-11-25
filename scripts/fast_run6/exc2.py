import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect()
print(guard.save_log_tail("dlg10b_r2_closed_no_buttons"))
off = log_mark() - 3_000_000
e = exc_summary(off)
print(e["by_type"])
for k, v in e["first_stacks"].items(): print(k); print("\n".join(v[:5]))
print("dlg", dlg(), "choices", choices(), "pause", pause_open(), "state", pstate())
print(save_info())
