import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); off = log_mark()
for o in d.find_objects(By.NAME, "TextChoice", enabled=True): print("text", repr(o.get_text()))
print(shot("q6_choices"))
b = d.find_object(By.NAME, "ButtonChoice2", enabled=True); b.click(); time.sleep(2.5)
print("after click ButtonChoice2: dlg", dlg(), "choices", choices(), "state", pstate())
print(log_since(off)); print("save", save_info().get("finished"), save_info().get("stacks"))
