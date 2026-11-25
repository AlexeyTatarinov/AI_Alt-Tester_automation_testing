import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect()
print(guard.save_log_tail(sys.argv[1]))
if len(sys.argv) > 2:
    key("Escape", 0.1); time.sleep(1.5)
    print("pause", pause_open(), "dlg", dlg(), "choices", choices(), "line", line())
    print(shot("dlg10b_r1_after_esc"))
