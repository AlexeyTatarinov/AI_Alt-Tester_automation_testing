# только чтение: что произошло после перехода и какие коллайдеры были на пути падения
from s3blib import *
off = json.load(open(os.path.join(R2, "b1.json"), encoding="utf-8"))["off"]
R = {}
def box(o): return {k: {a: round(v[a], 2) for a in "xyz"} for k, v in (("min", rd(o, "UnityEngine.BoxCollider", "bounds.min", 2, PHYS)), ("max", rd(o, "UnityEngine.BoxCollider", "bounds.max", 2, PHYS))) if isinstance(v, dict)}
time.sleep(3)
R["state"] = st_now("после перехода", pos=[round(v, 2) for v in ppos()])
R["entr"] = [(e.name, [round(e.worldX, 2), round(e.worldY, 2), round(e.worldZ, 2)]) for e in d.find_objects(By.COMPONENT, "LocationEntrance", enabled=False)]
R["exc"] = exc_summary(off)["total"]
print(R, flush=True)
print("goto", goto("Town_Upper"), flush=True); time.sleep(2); wait_play_ready()
R["exits"] = []
for o in d.find_objects(By.COMPONENT, "LocationExit", enabled=False):
    e = {"name": o.name, "pos": [round(o.worldX, 2), round(o.worldY, 2), round(o.worldZ, 2)], "to": str(rd(o, "LocationExit", "_locationToLoad.name", 1)), **box(o)}
    R["exits"].append(e); print(e, flush=True)
jdump(os.path.join(R2, "b5.json"), R)
