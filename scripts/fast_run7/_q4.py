import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); print("dlg", dlg(), "choices", choices(), "pause", pause_open(), "line", line())
for o in d.find_objects_which_contain(By.NAME, "Choice", enabled=False): print(o.name, o.enabled, o.parentId if hasattr(o,'parentId') else '')
print(shot("q4"))
