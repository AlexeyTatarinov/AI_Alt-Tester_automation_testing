# M08-01d: геометрия выходов (только чтение). python b3.py <loc>
from g6 import *
loc = sys.argv[1]
prestage("b3"); hyg_tick({}, "b3")
if cheat_open(): key("C", 0.1); time.sleep(1)
if gstate() == 6:
    c = first("LocationEntrance"); autosync(True); teleport("T1", c.worldX, c.worldY + 0.3, c.worldZ); time.sleep(3); autosync(False)
if loc not in scenes():
    try: print("goto", goto(loc), flush=True)
    except Exception as e:
        print("ERR", type(e).__name__); goto("Beach"); time.sleep(2); print("goto", goto(loc))
    time.sleep(2); wait_play_ready()
EX = exits()
for e in EX:
    o = [x for x in d.find_objects(By.COMPONENT, "LocationExit", enabled=False) if x.id == e["id"]][0]
    e["center"] = vec(rd(o, BC, "center", 2, PHYS)); e["size"] = vec(rd(o, BC, "size", 2, PHYS))
    e["euler"] = vec(rd(o, "UnityEngine.Transform", "eulerAngles", 2, CORE)); e["scale"] = vec(rd(o, "UnityEngine.Transform", "lossyScale", 2, CORE))
    print(json.dumps(e, ensure_ascii=False), flush=True)
catchers = [(o.name, [round(o.worldX, 2), round(o.worldY, 2), round(o.worldZ, 2)]) for o in d.find_objects(By.COMPONENT, "FallCatcher", enabled=False)]
print("catchers", catchers)
jdump(os.path.join(R2, "b3_%s.json" % loc), {"exits": EX, "catchers": catchers, "arrive": ppos()})
