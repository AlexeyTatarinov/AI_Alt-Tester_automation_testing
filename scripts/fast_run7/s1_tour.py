# -*- coding: utf-8 -*-
import os, sys, json, re; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("s1_tour")
print("validate comp search NPC:", len(d.find_objects(By.COMPONENT, "NPC", enabled=False)))
COMPS = ("CollectableItem", "Equip", "Recipe", "Interaction", "NPC", "Chest", "Pickable", "CookingPot", "ItemPickup", "Collectable")
labels = [b for b in d.find_objects(By.PATH, "//CheatMenu/*", enabled=False)]
order = [int(x) for x in (sys.argv[1].split(",") if len(sys.argv) > 1 else ["1"])]
out = json.load(open("s1_tour.json", encoding="utf-8")) if os.path.exists("s1_tour.json") else {}
for idx in order:
    guard.before_case("tour%d" % idx)
    if not len(d.find_objects(By.NAME, "CheatMenu", enabled=True)): key("C", 0.1); time.sleep(1)
    btns = d.find_objects(By.PATH, "//CheatMenu/*", enabled=False)
    b = btns[idx]; txt = d.find_objects(By.PATH, "//CheatMenu/%s/Text" % b.name, enabled=False)[0].get_text()
    off = log_mark(); t0 = time.time(); print(now(), "click", idx, txt, flush=True)
    b.click()
    t1 = time.time(); ok = False
    while time.time() - t1 < 60:
        time.sleep(1.0)
        try:
            if pig(): ok = True; time.sleep(3); break
        except Exception: pass
    r = {"button": txt, "scenes": scenes(), "pig": ok, "load_s": round(time.time()-t0,1), "pos": None, "found": {}, "log": None}
    try: r["pos"] = ppos()
    except Exception: pass
    for c in COMPS:
        try:
            l = d.find_objects(By.COMPONENT, c, enabled=False)
            r["found"][c] = [(o.name, round(o.worldX,1), round(o.worldY,1), round(o.worldZ,1)) for o in l][:25]
        except Exception as e: r["found"][c] = "ERR"
    try:
        pat = re.compile(r"(?i)item|collect|pick|recipe|equip|loot|chest|ingred|food|crate|barrel|sword|shield|apple|mushroom|carrot|cabbage|potato")
        r["name_hits"] = sorted({o.name for o in d.get_all_elements(enabled=True) if pat.search(o.name) and not o.name.startswith(("UI", "Setting", "Inventory", "Item", "Panel", "Line", "Button"))})[:40]
    except Exception as e: r["name_hits"] = "ERR"
    r["log"] = log_since(off); out[txt] = r
    print(json.dumps(r, ensure_ascii=False)[:1500], flush=True)
    json.dump(out, open("s1_tour.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(shot("s1_tour_%s" % order[-1]))
