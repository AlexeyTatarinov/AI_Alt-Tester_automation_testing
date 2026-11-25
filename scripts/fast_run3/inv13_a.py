# -*- coding: utf-8 -*-
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inv_lib import *
pre = guard.preflight("inv13a"); print("preflight", {k: pre[k] for k in ("consoleFlags","error_pause","play","alive")}, "iconic", pre["window"].get("iconic"))
if pre["window"].get("iconic") or pre["error_pause"]: raise SystemExit("стоп")
d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, True)
print("scenes", scenes(), "pos", ppos(), "inv open", inv(), "hint", hint())
if inv(): key("Tab", 0.1); time.sleep(0.8)
teleport("T1", POT[0] - 3.0, POT[1] + 0.3, POT[2]); time.sleep(3.5)
steps = 0; dist_hint = None
for _ in range(14):
    k, p = step_towards(POT, 0.15); steps += 1
    if hint(): dist_hint = round(dxz(p, POT), 2); break
print("шагов", steps, "подсказка на", dist_hint, "м; pos", ppos())
shot("inv13_at_pot")
key("E", 0.1); time.sleep(1.2)
print("inv open", inv(), "_isNearPot", INV().get_component_property("UIInventory", "_isNearPot", ASM), "tab", tab_type())
shot("inv13_after_E")
tabs = all_tabs(); print("TABS:", json.dumps(tabs, ensure_ascii=False))
print("tab now", tab_type()); b, i = action_button(); print("ActionButton interactable (без выбора):", i)
