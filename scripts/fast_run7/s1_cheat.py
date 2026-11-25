# -*- coding: utf-8 -*-
import os, sys, json, re; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("s1_cheat")
off = log_mark()
print("pause", pause_open(), "dlg", dlg(), "state", pstate())
cm = d.find_object(By.NAME, "CheatMenu", enabled=False)
print("cheat active before:", len(d.find_objects(By.NAME, "CheatMenu", enabled=True)))
key("C", 0.1); time.sleep(1.5)
act = len(d.find_objects(By.NAME, "CheatMenu", enabled=True)); print("cheat active after C:", act)
print(shot("s1_cheat_open"))
kids = d.find_objects(By.PATH, "//CheatMenu/*", enabled=False)
rows = []
for k in kids:
    info = {"name": k.name, "enabled": k.enabled, "id": k.id}
    try: info["comps"] = [(c.get("componentName") if isinstance(c, dict) else str(c)) for c in k.get_all_components()]
    except Exception as e: info["comps"] = ["ERR"]
    try: info["text"] = k.get_text()
    except Exception: pass
    try:
        ch = d.find_objects(By.PATH, "//CheatMenu/%s/*" % k.name, enabled=False)
        info["children"] = [(c.name, (lambda c: c.get_text() if True else "")(c)) for c in ch][:8]
    except Exception: pass
    rows.append(info); print(info, flush=True)
json.dump(rows, open("s1_cheat.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(log_since(off))
