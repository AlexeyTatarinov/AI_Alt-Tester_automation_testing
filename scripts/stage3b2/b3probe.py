# -*- coding: utf-8 -*-
from s3blib import *
R = {}
prestage("b3probe"); hyg_tick(R, "b3")
if scene_now() != ["Field_Hill"]: print("goto", goto("Field_Hill"), flush=True)
time.sleep(2); wait_play_ready()
p = ppos(); print(scene_now(), sname(gstate()), "pig", [round(v, 2) for v in p], "count", alert_count(), "hp", health(), "hpmax", rd(pig(), "Damageable", "_currentHealthSO.MaxHealth"), flush=True)
for q in ((By.COMPONENT, "Critter"), (By.COMPONENT, "LocationExit"), (By.COMPONENT, "CollectableItem")):
    for o in d.find_objects(q[0], q[1], enabled=True):
        print(q[1], o.name, o.id, [round(o.worldX, 2), round(o.worldY, 2), round(o.worldZ, 2)], "d", round(dxz(p, (o.worldX, o.worldY, o.worldZ)), 1), flush=True)
