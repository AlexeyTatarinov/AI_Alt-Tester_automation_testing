# -*- coding: utf-8 -*-
import os, sys, json, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastlib import *
d = connect()
r = guard.preflight("run4")
print(json.dumps(r, ensure_ascii=False, default=str, indent=1))
bk = r"C:\Users\Aotat\Desktop\Test_Ai\Reports_2026-11-21\evidence\save_backup\20261122_122526"
for root, _, fs in os.walk(bk):
    for f in fs: print("backup", os.path.join(root, f)[len(bk):], sha(os.path.join(root, f)))
print("live", save_hashes())
print("scenes", scenes())
try: print("pos", ppos(), "pigs", len(pigs()))
except Exception as e: print("pig err", e)
print("autoSync", d.get_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS), "runInBg", d.get_static_property("UnityEngine.Application", "runInBackground", CORE))
