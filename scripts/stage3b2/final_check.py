# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\play_control")
import restart_play as rp
d = rp.driver()
try:
    r = {"scenes": d.get_all_loaded_scenes(), "frameCount": d.get_static_property("UnityEngine.Time", "frameCount", rp.CORE),
         "autoSyncTransforms": d.get_static_property("UnityEngine.Physics", "autoSyncTransforms", "UnityEngine.PhysicsModule"),
         "save_equal_backup": rp.save_equal()}
    print(json.dumps(r))
finally:
    d.stop()
