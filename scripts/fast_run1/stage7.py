# -*- coding: utf-8 -*-
"""Этап 7: вернуть autoSyncTransforms и runInBackground, сводка Editor.log, вернуть save.chop и сверить хеш."""
import os, sys, time, json, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastlib import *

d = connect(); st = load_state(); fin = {}
# 1) вернуть исходные значения
d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, st.get("orig_autoSync", False))
fin["autoSyncTransforms_restored"] = d.get_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS)
fin["autoSyncTransforms_orig"] = st.get("orig_autoSync")
d.set_static_property("UnityEngine.Application", "runInBackground", CORE, st["orig_runInBackground"])
fin["runInBackground_restored"] = d.get_static_property("UnityEngine.Application", "runInBackground", CORE)
fin["runInBackground_orig"] = st["orig_runInBackground"]
fin["scenes_end"] = scenes()
# 2) Editor.log за весь прогон
fin["editor_log_total"] = log_since(st["editor_log_offset0"])
# 3) сохранения: что изменилось за прогон и возврат копии
fin["saves_after_run"] = save_hashes()
fin["saves_before"] = st["saves_hash_before"]
bk = st["backup_dir"]
for sub, sd in (("Unity_Technologies", SAVE_DIRS[0]), ("Unity_Open_Projects", SAVE_DIRS[1])):
    for f in ("save.chop", "save.chop.bak"):
        src = os.path.join(bk, sub, f)
        if os.path.exists(src): shutil.copy2(src, os.path.join(sd, f))
fin["saves_after_restore"] = save_hashes()
fin["save_restore_ok"] = fin["saves_after_restore"] == fin["saves_before"]
fin["save_files_changed_during_run"] = [os.path.basename(os.path.dirname(k)) + "\\" + os.path.basename(k) for k in fin["saves_before"] if fin["saves_before"][k] != fin["saves_after_run"].get(k)]
fin["finished"] = datetime.datetime.now().isoformat(timespec="seconds")
json.dump(fin, open(os.path.join(REPO_RES, "run1_final.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(fin, ensure_ascii=False, indent=1)[:3000])
