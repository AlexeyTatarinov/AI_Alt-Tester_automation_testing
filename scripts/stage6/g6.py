# -*- coding: utf-8 -*-
# общие функции stage6
from s3blib import *
DM = "UnityEngine.DirectorModule"; PD = "UnityEngine.Playables.PlayableDirector"
GO = "UnityEngine.GameObject"; BC = "UnityEngine.BoxCollider"
def vec(v): return [round(v["x"], 2), round(v["y"], 2), round(v["z"], 2)] if isinstance(v, dict) else str(v)[:120]
def exits():
    out = []
    for o in d.find_objects(By.COMPONENT, "LocationExit", enabled=False):
        mn = rd(o, BC, "bounds.min", 2, PHYS); mx = rd(o, BC, "bounds.max", 2, PHYS)
        out.append({"name": o.name, "id": o.id, "pos": [round(o.worldX, 2), round(o.worldY, 2), round(o.worldZ, 2)],
                    "min": vec(mn), "max": vec(mx), "to": str(rd(o, "LocationExit", "_locationToLoad.name", 1))[:80],
                    "path": str(rd(o, "LocationExit", "_leadsToPath.name", 1))[:80]})
    return out
def hits_exit(ex, x, z, margin=0.8, skip=()):
    """имена выходов, чей AABB (+margin) накрывает точку по x/z (высота не учитывается: падение сверху)"""
    return [e["name"] for e in ex if e["name"] not in skip and isinstance(e["min"], list)
            and e["min"][0] - margin <= x <= e["max"][0] + margin and e["min"][2] - margin <= z <= e["max"][2] + margin]
def active_ids(name):
    return {o.id for o in d.find_objects_which_contain(By.NAME, name, enabled=True)}
def glue():
    out = []; act = active_ids("Gluecose_FarmAttack")
    for o in d.find_objects_which_contain(By.NAME, "Gluecose_FarmAttack", enabled=False):
        if not (o.name.startswith("Gluecose_FarmAttack") or o.name.startswith("CutGluecose_FarmAttack")): continue
        a = rd(o, "Critter", "isPlayerInAlertZone", 1)
        e = {"name": o.name, "id": o.id, "active": o.id in act, "pos": [round(o.worldX, 2), round(o.worldY, 2), round(o.worldZ, 2)]}
        e["critter"] = not str(a).startswith("ERR"); e["alert"] = a if e["critter"] else None
        out.append(e)
    return out
