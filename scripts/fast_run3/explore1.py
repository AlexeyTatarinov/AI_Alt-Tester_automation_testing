# -*- coding: utf-8 -*-
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastlib import *
d = connect()
print("preflight", {k: v for k, v in guard.preflight("explore").items() if k in ("consoleFlags","error_pause","play","alive")})
print("scenes", scenes(), "timeScale", d.get_static_property("UnityEngine.Time","timeScale",CORE))
# кнопки меню читов
key("C", 0.1); time.sleep(1.0)
for o in d.find_objects(By.COMPONENT, "LocationTeleporterButton", enabled=False):
    try: print("btn", o.get_component_property("LocationTeleporterButton", "label.text", ASM))
    except Exception as e: print("btn?", e)
