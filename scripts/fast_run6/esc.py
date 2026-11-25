import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("esc")
for o in d.find_objects(By.COMPONENT, "UIDialogueChoicesManager", enabled=False): print("choicesMgr", o.name, o.enabled)
key("Escape", 0.1); time.sleep(1.5)
print("pause", pause_open(), "dlg", dlg(), "choices", choices(), "ts", d.get_static_property("UnityEngine.Time","timeScale",CORE))
print(shot("esc_in_dialog"))
