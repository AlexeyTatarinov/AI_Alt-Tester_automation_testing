import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); print("dlg", dlg(), "choices", choices(), "pause", pause_open(), "line", line())
for n in ("TextChoice","ButtonChoice1","ButtonChoice2","Panel Choices"):
    l = d.find_objects(By.NAME, n, enabled=True); print(n, len(l), [o.get_text() for o in l] if n=="TextChoice" else "")
si = save_info(); print(si.get("finished"), si.get("stacks")); print(shot("q7"))
