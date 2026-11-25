import os, sys, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); off = log_mark()
for i in range(25):
    if not dlg(): break
    key("Space", 0.1); time.sleep(1.2); print(i, (line() or "")[:80], "dlg", dlg(), "choices", choices())
time.sleep(2); si = save_info(); print(si.get("finished"), si.get("stacks"))
print(json.dumps(exc_summary(off), ensure_ascii=False)[:400]); print(json.dumps(inv_snapshot(), ensure_ascii=False)[:900])
