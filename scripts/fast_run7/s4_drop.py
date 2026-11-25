# -*- coding: utf-8 -*-
import os, sys, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("s4_drop")
btn = int(sys.argv[1]) if len(sys.argv) > 1 else 1
guard.before_case("drop")
if not len(d.find_objects(By.NAME, "CheatMenu", enabled=True)): key("C", 0.1); time.sleep(1)
b = d.find_objects(By.PATH, "//CheatMenu/*", enabled=False)[btn]; b.click(); t1 = time.time()
while time.time() - t1 < 60:
    time.sleep(1.0)
    try:
        if pig(): time.sleep(3); break
    except Exception: pass
print(now(), scenes(), ppos(), flush=True)
if len(d.find_objects(By.NAME, "CheatMenu", enabled=True)): key("C", 0.1); time.sleep(0.5)
crit = d.find_objects_which_contain(By.NAME, "PlantCritter", enabled=False)
print("critters", len(crit), [(c.name, round(c.worldX,1), round(c.worldZ,1)) for c in crit][:20], flush=True)
off = log_mark(); res = []; items_all = []
for i, c in enumerate(crit):
    guard.before_case("kill%d" % i)
    try: c.update_object(); cp = (c.worldX, c.worldY, c.worldZ)
    except Exception: res.append((i, "gone-before")); continue
    teleport("T1", cp[0] - 1.2, cp[1] + 0.3, cp[2]); time.sleep(0.8)
    hits = 0; gone = False; t0 = time.time()
    while time.time() - t0 < 12:
        key("F", 0.1); hits += 1; time.sleep(0.4)
        try: c.update_object()
        except Exception: gone = True; break
    items = []
    t0 = time.time()
    while time.time() - t0 < 4:
        l = d.find_objects(By.COMPONENT, "CollectableItem", enabled=False)
        if l: items = [(o.name, round(o.worldX,1), round(o.worldY,1), round(o.worldZ,1)) for o in l]; break
        time.sleep(0.3)
    res.append((i, c.name if False else "crit%d" % i, hits, gone, items)); print(now(), res[-1], flush=True)
    if items: items_all = items; break
print("RESULT", json.dumps(res, ensure_ascii=False)); print("items", items_all); print(log_since(off))
print(shot("s4_drop_end"))
