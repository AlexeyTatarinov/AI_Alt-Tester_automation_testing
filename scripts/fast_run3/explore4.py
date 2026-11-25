# -*- coding: utf-8 -*-
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastlib import *
d = connect()
print("preflight", {k: v for k, v in guard.preflight("explore4").items() if k in ("consoleFlags","error_pause","alive")})
def texts(enabled=True):
    out = []
    for comp, asm in (("TMPro.TextMeshProUGUI", "Unity.TextMeshPro"), ("UnityEngine.UI.Text", "UnityEngine.UI")):
        try:
            for o in d.find_objects(By.COMPONENT, comp, enabled=enabled):
                try: out.append((o.name, o.get_component_property(comp, "text", asm)))
                except Exception as e: out.append((o.name, "ERR "+type(e).__name__))
        except Exception as e: pass
    return out
o = d.find_objects(By.NAME, "Text (TMP)", enabled=True)
for x in o: print("HUD obj", x.name, "parent", x.get_parent().name if x.get_parent() else None, x.worldX, x.worldY)
key("Escape", 0.1); time.sleep(1.5)
d.find_object(By.NAME, "SettingsButton", enabled=False).click(); time.sleep(1.5)
print("SETTINGS texts:", texts())
names = sorted(set(o.name for o in d.get_all_elements(enabled=True)))
print([n for n in names if any(w in n.lower() for w in ("lang","locale","dropdown","slider","toggle","tab","setting","audio","graphic","resolution"))])
shot("settings_open")
