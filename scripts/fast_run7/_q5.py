import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); off = log_mark()
for i in range(3):
    key("Space", 0.1); time.sleep(1.2); print(i, "dlg", dlg(), "choices", choices(), "panel", len(d.find_objects(By.NAME,"Panel Choices",enabled=True)), line())
print(log_since(off))
print(shot("q5"))
