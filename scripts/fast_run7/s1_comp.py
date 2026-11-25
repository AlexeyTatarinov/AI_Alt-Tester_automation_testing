# -*- coding: utf-8 -*-
import os, sys, json, re; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("s1_comp")
res = {}
for nm in ("CheatMenu", "Chest", "PotOverFire", "Pot", "Interactables_Beach", "IngredientForRecipe"):
    for o in d.find_objects(By.NAME, nm, enabled=False)[:12]:
        try:
            comps = [(c.get("componentName") if isinstance(c, dict) else str(c)) for c in o.get_all_components()]
        except Exception as e: comps = ["ERR " + str(e)[:80]]
        row = (nm, round(o.worldX,2), round(o.worldY,2), round(o.worldZ,2), o.enabled, comps)
        res.setdefault(nm, []).append(row); print(row, flush=True)
# все компоненты по неймспейсам игры на сцене: перебор всех объектов
alld = d.get_all_elements(enabled=False)
cnt = {}
import collections
for o in alld:
    pass
json.dump(res, open("s1_comp.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
