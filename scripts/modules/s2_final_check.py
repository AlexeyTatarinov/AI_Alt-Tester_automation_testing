# -*- coding: utf-8 -*-
# stage2: только чтение. Состояние игры/сохранения после BLOCKED на restart_play (код 2).
import sys, json
sys.path.insert(0, r"Test_Ai\scripts\fast_run7")
from r4lib import *
d = connect()
R = {"scenes": scenes(),
     "frameCount": d.get_static_property("UnityEngine.Time", "frameCount", CORE),
     "autoSyncTransforms": d.get_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS),
     "save_hashes_equal_backup": save_hashes() == bk_hashes(),
     "save_hashes": {k[-60:]: v for k, v in save_hashes().items()}}
print(json.dumps(R, ensure_ascii=False, indent=1))
json.dump(R, open(r"Test_Ai\Reports_2026-11-21\results\modules_stage2_20261125\final_state.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
