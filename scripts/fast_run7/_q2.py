import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); print(scenes(), ppos())
for en in (True, False):
    l = d.find_objects_which_contain(By.NAME, "PlantCritter", enabled=en); print("enabled", en, len(l), [(o.name, o.enabled, round(o.worldX,1), round(o.worldZ,1)) for o in l][:14])
for n in ("Item", "Collect", "Reward", "Drop", "Coin", "Egg", "Pickup"):
    l = d.find_objects_which_contain(By.NAME, n, enabled=False); print(n, len(l), [o.name for o in l][:8])
