# -*- coding: utf-8 -*-
import os, sys, json, time, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect()
pre = preflight("save06_pre")
print("scenes", scenes(), "window iconic", pre["window"].get("iconic"), "fg", pre["window"].get("foreground"))
def info():
    out = {}
    for sd in SAVE_DIRS:
        p = os.path.join(sd, "save.chop")
        if os.path.exists(p):
            j = json.load(open(p, encoding="utf-8")); f = list(j.get("_finishedQuestlineItemsGUIds", []))
            out[sd[-40:]] = {"hash": sha(p), "n": len(f), "guids": f, "mtime": datetime.datetime.fromtimestamp(os.path.getmtime(p)).isoformat(), "bak": sha(p + ".bak")}
        else: out[sd[-40:]] = None
    return out
i = info(); print(json.dumps(i, indent=1))
print("hashes==backup", save_hashes() == bk_hashes())
json.dump({"before": i, "log0": log_mark()}, open("s6_before.json", "w"), indent=1)
print("autoSync", d.get_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS))
