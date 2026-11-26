# -*- coding: utf-8 -*-
# New Game, Count, Mountain_Cave: выходы, Klipper, дистанции
from s3blib import *
R = {}
def dump(): jdump(os.path.join(R2, "c1.json"), R)
prestage("c1")
R["frameCount0"] = d.get_static_property("UnityEngine.Time", "frameCount", CORE); print("frameCount0", R["frameCount0"], flush=True)
assert "MainMenu" in scenes()
try:
    hyg_start("c1", R); guard.risky("c1")
    print("new_game", new_game(), now(), flush=True); wait_play_ready()
    hyg_start("c1_after_ng", R)
    R["off"] = off = log_mark()
    R["start"] = st_now("после New Game", frame=d.get_static_property("UnityEngine.Time", "frameCount", CORE)); dump()
    print("goto", goto("Mountain_Cave"), flush=True); time.sleep(2); wait_play_ready()
    R["arrive"] = st_now("Mountain_Cave", pos=[round(v, 2) for v in ppos()]); R["tab_arrive"] = None
    R["exits"] = []
    for o in d.find_objects(By.COMPONENT, "LocationExit", enabled=True):
        e = {"name": o.name, "pos": [round(o.worldX, 2), round(o.worldY, 2), round(o.worldZ, 2)], "to": str(rd(o, "LocationExit", "_locationToLoad.name", 1)), "path": str(rd(o, "LocationExit", "_leadsToPath.name", 1))}
        for comp in ("UnityEngine.BoxCollider", "UnityEngine.SphereCollider", "UnityEngine.CapsuleCollider", "UnityEngine.MeshCollider"):
            try:
                e["collider"] = comp; e["center"] = o.get_component_property(comp, "bounds.center", PHYS); e["size"] = o.get_component_property(comp, "bounds.size", PHYS); break
            except Exception: e.pop("collider", None)
        R["exits"].append(e); print(e, flush=True)
    R["entrances"] = [(o.name, [round(o.worldX, 2), round(o.worldY, 2), round(o.worldZ, 2)]) for o in d.find_objects(By.COMPONENT, "LocationEntrance", enabled=True)]
    print("entr", R["entrances"])
    R["klippers"] = []
    for c in d.find_objects(By.COMPONENT, "Critter", enabled=True):
        p = (c.worldX, c.worldY, c.worldZ)
        k = {"name": c.name, "id": c.id, "pos": [round(v, 2) for v in p], "alert": alert(c),
             "d_exits": {x["name"]: [round(dxz(p, x["pos"]), 1), round(p[1] - x["pos"][1], 1)] for x in R["exits"]}}
        R["klippers"].append(k); print(k, flush=True)
    R["exc"] = exc_summary(off); print("start", R["start"], "\narrive", R["arrive"], "\nexc", R["exc"]["total"])
    d.get_png_screenshot(os.path.join(R2, "shots", "c1_cave.png"))
finally:
    dump()
