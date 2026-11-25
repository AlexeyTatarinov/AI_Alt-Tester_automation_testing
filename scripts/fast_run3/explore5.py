# -*- coding: utf-8 -*-
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastlib import *
d = connect()
def texts():
    out = []
    for o in d.find_objects(By.COMPONENT, "TMPro.TextMeshProUGUI", enabled=True):
        try: out.append((o.name, o.get_component_property("TMPro.TextMeshProUGUI", "text", "Unity.TextMeshPro")))
        except Exception as e: out.append((o.name, "ERR"))
    return out
print("menu?", any(True for _ in d.find_objects(By.NAME, "Settings_Panel_PR", enabled=True)))
d.find_object(By.NAME, "Language_Tab", enabled=False).click(); time.sleep(1.2)
print("LANG texts:", texts())
sc = sorted(set((o.name, o.type) for o in d.get_all_elements(enabled=True) if any(w in o.name.lower() for w in ("lang","option","arrow","left","right","next","prev","dropdown"))))
print(sc)
shot("settings_language")
