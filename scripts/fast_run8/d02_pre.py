# -*- coding: utf-8 -*-
import os, sys, json
sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\fast_run7")
from r4lib import *
d = connect()
pre = preflight("d02pre")
rt = d.get_static_property("UnityEngine.Time", "realtimeSinceStartup", CORE)
fc = d.get_static_property("UnityEngine.Time", "frameCount", CORE)
out = {"time": now(), "realtimeSinceStartup": rt, "frameCount": fc, "scenes": scenes(), "save": save_info(),
       "hashes": save_hashes(), "backup_hashes": bk_hashes(), "dlg": dlg(), "choices": choices(), "autoSync": d.get_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS),
       "pre": {k: pre[k] for k in ("consoleFlags","error_pause","play","alive")}}
print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
