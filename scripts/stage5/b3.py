# M08-01c: python b3.py <loc> <exit name>  -- только чтение коллайдера и капсулы
from s3blib import *
loc, name = sys.argv[1], sys.argv[2]
off = json.load(open(os.path.join(R2, "b1.json"), encoding="utf-8"))["off"]
hyg_tick({}, "b3")
if loc not in scenes(): print("goto", goto(loc), flush=True); time.sleep(2); wait_play_ready()
o = d.find_object(By.NAME, name, enabled=False)
R = {"loc": loc, "exit": name, "pos": [round(o.worldX, 3), round(o.worldY, 3), round(o.worldZ, 3)], "arrive": [round(v, 2) for v in ppos()]}
BC = "UnityEngine.BoxCollider"
for p in ("bounds.center", "bounds.size", "bounds.min", "bounds.max", "center", "size", "isTrigger", "enabled"):
    R["box." + p] = str(rd(o, BC, p, 2, PHYS))[:200]
for p in ("eulerAngles", "lossyScale"):
    R[p] = str(rd(o, "UnityEngine.Transform", p, 2, CORE))[:200]
pg = pig()
for p in ("height", "radius", "center", "stepOffset", "slopeLimit"):
    R["cc." + p] = str(rd(pg, "UnityEngine.CharacterController", p, 2, PHYS))[:100]
R["entrances"] = [(e.name, [round(e.worldX, 2), round(e.worldY, 2), round(e.worldZ, 2)], str(rd(e, "LocationEntrance", "_entrancePath.name", 1))) for e in d.find_objects(By.COMPONENT, "LocationEntrance", enabled=False)]
R["exc"] = exc_summary(off)["total"]
print(json.dumps(R, ensure_ascii=False)); jdump(os.path.join(R2, "b3_%s.json" % loc), R)
