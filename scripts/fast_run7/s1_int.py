# -*- coding: utf-8 -*-
import os, sys, json, re; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("s1_int")
rows = []
for path in ("//Interactables_Beach/*", "//Interactables_Beach/*/*"):
    try: l = d.find_objects(By.PATH, path, enabled=False)
    except Exception as e: print(path, "ERR", e); continue
    print(path, len(l))
    for o in l:
        try: comps = [(c.get("componentName") if isinstance(c, dict) else str(c)) for c in o.get_all_components()]
        except Exception as e: comps = ["ERR"]
        r = (o.name, round(o.worldX,2), round(o.worldY,2), round(o.worldZ,2), o.enabled, [c for c in comps if not c.startswith("UnityEngine.") or "Collider" in c])
        rows.append(r); print(r, flush=True)
json.dump(rows, open("s1_int.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
