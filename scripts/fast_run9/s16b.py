import os, sys, json
sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\fast_run7")
from r4lib import *
d = connect()
rows = []
for o in d.find_objects(By.PATH, "//Audio_Panel//*", enabled=True):
    if o.name in ("Setting_Title", "CurrentOption"):
        rows.append((o.name, o.get_text(), round(o.worldY, 1)))
print(rows)
print(shot("s16b_reopened"))
