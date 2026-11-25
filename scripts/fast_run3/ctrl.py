# -*- coding: utf-8 -*-
"""Контрольный прогон страховок: Beach -> Forest через меню читов; классификатор и alive()."""
import os, sys, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastlib import *
import guard
d = connect()
off = guard.log_mark(); out = {}
guard.risky("ctrl_forest_load")
key("C", 0.1); time.sleep(1.0)
btn = None
for o in d.find_objects(By.COMPONENT, "LocationTeleporterButton", enabled=False):
    try: lab = o.get_component_property("LocationTeleporterButton", "label.text", ASM)
    except Exception: lab = None
    print("кнопка:", lab)
    if lab and lab.startswith("Forest via"): btn = o
t0 = time.time(); out["button_found"] = btn is not None
if btn: btn.click()
res = []
while time.time() - t0 < 45:
    time.sleep(1.5)
    try:
        sc = scenes(); a = guard.alive(limit=4.0)
        res.append((round(time.time() - t0, 1), sc[-1], a[0]))
        if "Forest" in sc and a[0] and len(pigs()) >= 1: break
    except Exception as e:
        res.append((round(time.time() - t0, 1), type(e).__name__, None))
out["timeline"] = res
time.sleep(4)
out["alive_after"] = guard.alive()
out["classify"] = guard.classify(off)
lg = log_since(off); out["log_since"] = {k: lg[k] for k in ("errors", "exceptions")}; out["samples"] = lg["samples"][:4]
try: shot("ctrl_forest")
except Exception as e: out["shot"] = str(e)
guard.after_case("CTRL-Forest", "ok", str(out["alive_after"]))
print(json.dumps(out, ensure_ascii=False, default=str, indent=1))
