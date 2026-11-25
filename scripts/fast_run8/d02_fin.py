# -*- coding: utf-8 -*-
import os, sys, json
sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\fast_run7")
from r4lib import *
OUT = r"C:\Users\Aotat\Desktop\Test_Ai\Reports_2026-11-21\results\run8_d02_20261124"
d = connect()
R = {"before": save_hashes()}
R["restore_equal"] = restore(); R["after"] = save_hashes(); R["backup"] = bk_hashes()
R["autoSync"] = d.get_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS)
R["dlg_open"] = dlg(); R["choices"] = choices(); R["scenes"] = scenes()
R["window"] = guard.unity_window()
try: R["restores_log"] = open(guard.WIN_LOG, encoding="utf-8").read()[-600:]
except Exception as e: R["restores_log"] = str(e)
R["window_restores_state"] = guard._state().get("window_restores")
json.dump(R, open(os.path.join(OUT, "d02_fin.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print(json.dumps({k: R[k] for k in ("restore_equal","autoSync","dlg_open","choices","window","restores_log","window_restores_state")}, ensure_ascii=False, indent=1))
print("after==backup", R["after"] == R["backup"])
