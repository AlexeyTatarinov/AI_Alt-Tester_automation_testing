# -*- coding: utf-8 -*-
import os, sys, json, time, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("save06_ng")
B = json.load(open("s6_before.json"))
guard.risky("New Game SAVE-06")
t0 = time.time(); d.find_object(By.NAME, "Button New Game", enabled=False).click()
for _ in range(15):
    time.sleep(0.4)
    try: d.find_object(By.NAME, "PopupButton - 1", enabled=False).click(); popup=True; break
    except Exception: pass
print("popup clicked", popup if 'popup' in dir() else False)
found=None
while time.time()-t0 < 60:
    try:
        if "Beach" in scenes() and pig(): found=round(time.time()-t0,1); break
    except Exception: pass
    time.sleep(0.3)
print("Beach loaded s", found)
time.sleep(5.0)
res = {}
for sd in SAVE_DIRS:
    p = os.path.join(sd, "save.chop")
    j = json.load(open(p, encoding="utf-8")); f = list(j.get("_finishedQuestlineItemsGUIds", []))
    res[sd[-40:]] = {"hash": sha(p), "n": len(f), "guids": f, "mtime": datetime.datetime.fromtimestamp(os.path.getmtime(p)).isoformat()}
print(json.dumps(res, indent=1))
j = json.load(open(SAVE0F, encoding="utf-8"))
print("keys", [k for k in j.keys()][:40])
print("stacks", {s["itemGuid"][:6]: s["amount"] for s in j.get("_itemStacks", [])}, "scenes", scenes())
json.dump({"after": res, "beach_s": found}, open("s6_after.json","w"), indent=1)
