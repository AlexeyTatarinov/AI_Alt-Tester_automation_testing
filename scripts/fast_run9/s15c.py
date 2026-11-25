import os, sys, json
sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\fast_run7")
from r4lib import *
d = connect()
kids = d.find_objects(By.PATH, "//Audio_Panel//*", enabled=True)
print(len(kids))
for o in kids[:40]:
    try: cs = [(c.get("componentName") if isinstance(c,dict) else str(c)) for c in o.get_all_components()]
    except Exception: cs = []
    try: t = o.get_text()
    except Exception: t = ""
    print(o.name, o.id, [c for c in cs if "UnityEngine." not in c][:3], repr(t)[:20])
