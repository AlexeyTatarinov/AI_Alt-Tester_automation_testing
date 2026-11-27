import sys, json
sys.path.insert(0, r"Test_Ai\scripts\fast_run7")
from r4lib import *
d=connect(); guard.restore_window("c3")
s=[s for s in slots() if s[1]=="SweetCream_Recipe"][0][0]
for p in ["currentItem.Item.ResultingDish.name","currentItem.Item.ResultingDish.Guid"]:
    try: print(p, s.get_component_property("UIInventoryItem", p, ASM))
    except Exception as e: print(p,"ERR",str(e)[:80])
key("Tab",0.1); time.sleep(1.0); print("inv open", inv())
