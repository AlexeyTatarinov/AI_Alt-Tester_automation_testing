# -*- coding: utf-8 -*-
import os, sys, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("s7_radius")
d.set_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS,True)
try:
    guard.risky("new_game s7"); print("new_game", new_game(), scenes(), now()); time.sleep(3)
    guard.before_case("s7_cheat")
    key("C", 0.1); time.sleep(1)
    d.find_objects(By.PATH, "//CheatMenu/*", enabled=False)[1].click(); t1 = time.time()
    while time.time() - t1 < 60:
        time.sleep(1.0)
        try:
            if pig(): time.sleep(3); break
        except Exception: pass
    print(scenes(), ppos(), flush=True)
    if len(d.find_objects(By.NAME, "CheatMenu", enabled=True)): key("C", 0.1); time.sleep(0.5)
    names = []
    for c in d.find_objects_which_contain(By.NAME, "PlantCritter", enabled=False):
        if c.id not in [x.id for x in names]: names.append(c)
    c = names[0]; c.update_object(); cp = (c.worldX, c.worldY, c.worldZ)
    teleport("T1", cp[0]-1.2, cp[1]+0.3, cp[2]); time.sleep(0.8)
    for i in range(30):
        c.update_object(); cp = (c.worldX, c.worldY, c.worldZ)
        if dxz(ppos(), cp) < 1.4: break
        step_towards(cp, 0.15); time.sleep(0.1)
    gone = False
    for h in range(10):
        key("F", 0.1); time.sleep(0.7)
        try: c.update_object()
        except Exception: gone = True; break
    time.sleep(1.5)
    it = [(o.name, o.worldX, o.worldY, o.worldZ) for o in d.find_objects(By.COMPONENT, "CollectableItem", enabled=False)]
    print("killed", gone, "hits", h+1, "items", it, flush=True)
    assert it, "предмет не выпал"
    ip = it[0][1:]; rows = []
    for dist in [4.0, 3.5, 3.0, 2.5, 2.0, 1.75, 1.5, 1.25, 1.0, 0.75, 0.5]:
        teleport("T1", ip[0]-dist, ip[1]+0.3, ip[2]); time.sleep(0.9)
        real = round(dxz(ppos(), ip), 2); h_ = hint(); rows.append((dist, real, h_)); print("dist", dist, "real", real, "hint", h_, flush=True)
    key("E", 0.1); time.sleep(2.8)
    print("после E на 0,5 м: предметов", len(d.find_objects(By.COMPONENT, "CollectableItem", enabled=False)))
    json.dump(rows, open("s7_radius.json", "w"))
finally:
    d.set_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS,False); print("autoSync", d.get_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS))
