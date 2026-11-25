# -*- coding: utf-8 -*-
import os, sys, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("s5_pick"); d.set_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS,True)
try:
    def items(): return [(o.name, o.worldX, o.worldY, o.worldZ) for o in d.find_objects(By.COMPONENT, "CollectableItem", enabled=False)]
    it = items(); print("items", it); assert it, "нет предмета"
    ip = it[0][1:]; s0 = save_info(); print("save0", s0, now())
    off = log_mark()
    # INT-07: далеко
    teleport("T1", ip[0]-4.0, ip[1]+0.3, ip[2]); time.sleep(1.5)
    print("dist", round(dxz(ppos(), ip),2), "hint", hint())
    key("E", 0.1); time.sleep(2.5)
    it7 = items(); s7 = save_info()
    print("INT-07 items", len(it7), "stacks same", s7.get("stacks") == s0.get("stacks"), "hint", hint())
    # INT-06: рядом
    teleport("T1", ip[0]-0.8, ip[1]+0.3, ip[2]); time.sleep(1.2)
    for i in range(4):
        step_towards(ip, 0.1)
        if hint(): break
    print("dist", round(dxz(ppos(), ip),2), "hint", hint(), shot("s5_near"))
    key("E", 0.1); time.sleep(2.8)
    it6 = items(); s6 = save_info()
    print("INT-06 items", len(it6), "hash", s0.get("hash"), "->", s6.get("hash"))
    print("stacks0", s0.get("stacks")); print("stacks6", s6.get("stacks"))
    print(log_since(off))
finally:
    d.set_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS,False); print("autoSync", d.get_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS))
