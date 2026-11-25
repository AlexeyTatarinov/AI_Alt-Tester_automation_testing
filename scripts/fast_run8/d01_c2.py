import sys, json
sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\fast_run7")
from r4lib import *
d=connect(); guard.restore_window("c2")
if not inv(): key("Tab",0.1); time.sleep(1.2)
for _ in range(5):
    if str(tab_type())=="2": break
    key("Y",0.1); time.sleep(0.7)
print("tab", tab_type())
sl=[s for s in slots() if s[1]=="SweetCream_Recipe"]; print(sl)
s=sl[0][0]
for path in ["currentItem.Item.IngredientsList","currentItem.Item.IngredientsList.Count","currentItem.Item.Ingredients","currentItem.Item.Dish","currentItem.Item.IngredientsList._items"]:
    try: print(path, s.get_component_property("UIInventoryItem", path, ASM))
    except Exception as e: print(path, "ERR", type(e).__name__, str(e)[:80])
try:
    print(s.get_all_fields("UIInventoryItem", ASM) if hasattr(s,"get_all_fields") else "no get_all_fields")
except Exception as e: print("fields ERR", e)
print([c for c in d.find_objects(By.NAME,"x",enabled=True)] if False else "")
