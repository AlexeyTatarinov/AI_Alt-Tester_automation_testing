import os, sys, json
sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\fast_run7")
from r4lib import *
d = connect()
objs = d.get_all_elements(enabled=True)
names = [(o.name, o.id) for o in objs if any(k in o.name.lower() for k in ("arrow","left","right","slider","volume","music","sound","selector","audio","save","reset"))]
print(names[:40])
for o in objs:
    if o.name in ("Master Volume","MasterVolume","Music","Sound FX"):
        try: print(o.name, [c.get("componentName") if isinstance(c,dict) else str(c) for c in o.get_all_components()])
        except Exception as e: print(o.name,"ERR",e)
