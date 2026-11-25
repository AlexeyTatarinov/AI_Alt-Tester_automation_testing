# -*- coding: utf-8 -*-
"""Сбор AABB непригодных для прохода коллайдеров (не trigger) в области; пишет Reports/evidence/logs/colliders_rects_beach.json. Только чтение."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_sdk; from lib import *
from alttester import By
P = "UnityEngine.PhysicsModule"
SKIP = ("Landmass", "Seabed", "Water", "PigChef", "AttackCollider", "Underwater")
def collect(bbox):
    d = lib_sdk.driver(); out = []
    for comp in ["UnityEngine.BoxCollider", "UnityEngine.CapsuleCollider", "UnityEngine.MeshCollider", "UnityEngine.SphereCollider"]:
        for o in d.find_objects(By.COMPONENT, comp, enabled=False):
            if any(s in o.name for s in SKIP) or not (bbox[0] <= o.worldX <= bbox[1] and bbox[2] <= o.worldZ <= bbox[3]):
                continue
            try:
                if o.get_component_property(comp, "isTrigger", P):
                    continue
                g = lambda k: o.get_component_property(comp, k, P, max_depth=2)
                out.append((g("bounds.center.x"), g("bounds.center.z"), g("bounds.extents.x"), g("bounds.extents.z"), o.name))
            except Exception:
                pass
    return out
if __name__ == "__main__":
    r = collect((-100, -50, -380, -330))
    json.dump(r, open(os.path.join(LOGS, "colliders_rects_beach.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print("прямоугольников:", len(r))
