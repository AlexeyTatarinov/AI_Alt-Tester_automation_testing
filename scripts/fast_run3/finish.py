# -*- coding: utf-8 -*-
import os, sys, json, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from l10n_lib import *
d = connect()
pre = guard.preflight("finish"); print("preflight", {k: pre[k] for k in ("consoleFlags","error_pause","play","alive")}, "iconic", pre["window"].get("iconic"))
BK = r"Test_Ai\Reports_2026-11-21\evidence\save_backup\20261122_122526"
MAP = {"Unity_Technologies": SAVE_DIRS[0], "Unity_Open_Projects": SAVE_DIRS[1]}
print("до возврата:", save_hashes())
for sub, dst in MAP.items():
    for f in ("save.chop", "save.chop.bak"):
        s = os.path.join(BK, sub, f)
        if os.path.exists(s): shutil.copy2(s, os.path.join(dst, f))
bk = {os.path.join(dst, f): sha(os.path.join(BK, sub, f)) for sub, dst in MAP.items() for f in ("save.chop", "save.chop.bak")}
now_h = save_hashes(); print("после возврата:", now_h); print("ХЕШИ СОВПАЛИ С КОПИЕЙ:", now_h == bk)
d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, False)
print("autoSyncTransforms =", d.get_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS), "runInBackground =", d.get_static_property("UnityEngine.Application", "runInBackground", CORE))
print("scenes", scenes(), "pigs", len(pigs()), "timeScale", d.get_static_property("UnityEngine.Time", "timeScale", CORE), "pause menu", any(True for _ in d.find_objects(By.NAME, "Pause_Screen", enabled=True)), "inv", inv() if False else comp_active("UIInventory"))
lg = log_since(44591989); print("Editor.log за прогон:", lg)
st = load_state(); print("unpause_attempts", st.get("unpause_attempts"))
json.dump({"hashes_final": now_h, "backup": bk, "equal": now_h == bk, "log_run": lg}, open(os.path.join(REPO_RES, "final_state.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
