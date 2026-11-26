# -*- coding: utf-8 -*-
from s3blib import *
R = {}
prestage("b2probe")
hyg_tick(R, "b2")
if "Field_Farms" not in scenes(): print("goto", goto("Field_Farms"), flush=True)
time.sleep(2); wait_play_ready()
print(scene_now(), sname(gstate()), "pig", [round(v, 2) for v in ppos()], "count", alert_count(), flush=True)
for q in ((By.NAME, "Ayud"), (By.NAME, "Ayud(Clone)"), (By.COMPONENT, "NPC"), (By.COMPONENT, "StepController")):
    for o in d.find_objects(q[0], q[1], enabled=True):
        extra = ""
        if q[1] == "StepController": extra = str(rd(o, "StepController", "_actor.name"))
        print(q[1], o.name, o.id, [round(o.worldX, 2), round(o.worldY, 2), round(o.worldZ, 2)], extra, flush=True)
