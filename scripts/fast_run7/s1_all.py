# -*- coding: utf-8 -*-
import os, sys, json, re; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("s1_all")
print(scenes(), "pig", pig() is not None)
allo = d.get_all_elements(enabled=False)
print("total", len(allo))
names = {}
for o in allo: names.setdefault(o.name, 0); names[o.name] += 1
json.dump(sorted(names.items()), open("s1_allnames.json","w",encoding="utf-8"), ensure_ascii=False, indent=0)
pat = re.compile(r"(?i)item|collect|pick|pot|recipe|equip|cook|loot|chest|ingred|food|cheat|interact|crate|barrel")
for n, c in sorted(names.items()):
    if pat.search(n): print(c, n)
