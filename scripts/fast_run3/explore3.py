# -*- coding: utf-8 -*-
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastlib import *
d = connect()
def texts():
    out = []
    for comp, prop_asm in (("TMPro.TextMeshProUGUI", "Unity.TextMeshPro"), ("UnityEngine.UI.Text", "UnityEngine.UI")):
        try:
            for o in d.find_objects(By.COMPONENT, comp, enabled=True):
                try: out.append((comp.split(".")[-1], o.name, o.get_component_property(comp, "text", prop_asm)))
                except Exception as e: out.append((comp, o.name, "ERR "+type(e).__name__))
        except Exception as e:
            out.append((comp, "-", "find ERR "+type(e).__name__+" "+str(e)[:60]))
    return out
print("HUD texts:", texts())
print("pigs", len(pigs()), "pos", ppos())
key("Escape", 0.1); time.sleep(1.5)
print("timeScale", d.get_static_property("UnityEngine.Time","timeScale",CORE))
print("PAUSE texts:", texts())
names = [o.name for o in d.get_all_elements(enabled=True)]
print("enabled elements:", len(names)); print([n for n in names if any(w in n.lower() for w in ("pause","menu","button","popup","resume","settings"))])
shot("explore_pause_open")
