import sys; sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\modules")
from elib import *
print("start", gstate(), pause_open())
key("Escape",0.1); time.sleep(1.5); print("after esc", gstate(), pause_open())
key("Tab",0.1); time.sleep(1.5); print("after tab", gstate(), inv_open())
key("Tab",0.1); time.sleep(1.5); print("after tab2", gstate(), inv_open())
print("enemies near? alert:", [ (c.name, c.get_component_property("Critter","isPlayerInAlertZone",ASM)) for c in d.find_objects(By.COMPONENT,"Critter",enabled=False)])
