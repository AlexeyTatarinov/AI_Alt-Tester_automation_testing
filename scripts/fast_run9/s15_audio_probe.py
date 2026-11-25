import os, sys, json
sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\fast_run7")
from r4lib import *
d = connect(); preflight("s15")
print(scenes())
b = [o.name for o in d.find_objects_which_contain(By.NAME, "Settings", enabled=False)]
print("settings objs", b[:15])
d.find_object(By.NAME, "Button Settings ", enabled=False).click(); time.sleep(1.5)
for o in d.find_objects(By.COMPONENT, "UnityEngine.UI.Slider", enabled=True):
    try: v = o.get_component_property("UnityEngine.UI.Slider", "value", "UnityEngine.UI")
    except Exception as e: v = "ERR"
    print("slider", o.name, v)
print([o.name for o in d.find_objects(By.COMPONENT, "UnityEngine.UI.Button", enabled=True)][:25])
print([o.name for o in d.find_objects_which_contain(By.NAME, "Tab", enabled=True)][:12])
print(shot("s15_settings"))
