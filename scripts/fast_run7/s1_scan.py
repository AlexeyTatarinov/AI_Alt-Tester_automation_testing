# -*- coding: utf-8 -*-
import os, sys, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); pre = preflight("s1_scan")
guard.risky("New Game NEW5")
print("save hash", sha(SAVE0F), "backup", bk_hashes()[SAVE0F])
assert sha(SAVE0F) == bk_hashes()[SAVE0F]
off = log_mark(); t0 = now()
print("start", t0, "new_game ->", new_game(), "scenes", scenes(), flush=True)
out = {"start": t0, "scenes": scenes()}
for comp in ("CollectableItem", "Equip", "Recipe", "Pickup", "ItemStack", "Item", "RecipeSO", "ItemSO", "CookingPot", "Interaction"):
    try:
        l = d.find_objects(By.COMPONENT, comp, enabled=False)
        out[comp] = [(o.name, round(o.worldX,2), round(o.worldY,2), round(o.worldZ,2), o.enabled) for o in l][:60]
    except Exception as e:
        out[comp] = "ERR %s %s" % (type(e).__name__, str(e)[:100])
    print(comp, str(out[comp])[:600], flush=True)
json.dump(out, open("s1_scan.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(log_since(off))
