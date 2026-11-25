# -*- coding: utf-8 -*-
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastlib import *
d = connect()
def cheat_open(): return any(True for o in d.find_objects(By.COMPONENT, "LocationTeleporterButton", enabled=True))
if not cheat_open(): key("C", 0.1); time.sleep(0.8)
btn = [o for o in d.find_objects(By.COMPONENT, "LocationTeleporterButton", enabled=False) if (o.get_component_property("LocationTeleporterButton","label.text",ASM) or "").startswith("Beach via")][0]
t0 = time.time(); btn.click()
while time.time()-t0 < 40:
    time.sleep(0.5)
    sc = scenes()
    if "Beach" in sc and "Town_Inner" not in sc and len(pigs())>=1: break
print("scenes", scenes(), round(time.time()-t0,1))
time.sleep(3)
if cheat_open(): key("C", 0.1); time.sleep(0.8)
print("cheat_open", cheat_open(), "pos", ppos(), "timeScale", d.get_static_property("UnityEngine.Time","timeScale",CORE))
# активные UI-объекты
for o in d.get_all_elements(enabled=True)[:0]: pass
