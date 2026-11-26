from s3blib import *
off = json.load(open(os.path.join(R2, "b1.json"), encoding="utf-8"))["off"]
print(st_now("перед", pause=pause_open(), cheat=cheat_open(), exc=exc_summary(off)["total"]), flush=True)
if cheat_open(): key("C", 0.1); time.sleep(1)
for loc in ("Beach", "Town_Upper"):
    try: print("goto", goto(loc), flush=True)
    except Exception as e: print("ERR", e, flush=True)
    time.sleep(2); wait_play_ready()
print(st_now("после"), flush=True)
if "Town_Upper" in scenes():
    R = {"exits": []}
    for o in d.find_objects(By.COMPONENT, "LocationExit", enabled=False):
        e = {"name": o.name, "to": str(rd(o, "LocationExit", "_locationToLoad.name", 1))}
        for k in ("min", "max"):
            v = rd(o, "UnityEngine.BoxCollider", "bounds." + k, 2, PHYS)
            e[k] = [round(v[a], 2) for a in "xyz"] if isinstance(v, dict) else str(v)[:60]
        R["exits"].append(e); print(e, flush=True)
    jdump(os.path.join(R2, "b6.json"), R)
