# -*- coding: utf-8 -*-
import os, sys, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("s3_tp")
order = [int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else []
if "new" in sys.argv[2:]:
    guard.risky("new_game s3"); print("new_game", new_game(), scenes(), now()); time.sleep(3)
out = json.load(open("s3_tp.json", encoding="utf-8")) if os.path.exists("s3_tp.json") else {}
for idx in order:
    guard.before_case("tp%d" % idx)
    if not len(d.find_objects(By.NAME, "CheatMenu", enabled=True)): key("C", 0.1); time.sleep(1)
    btns = d.find_objects(By.PATH, "//CheatMenu/*", enabled=False)
    b = btns[idx]; txt = d.find_objects(By.PATH, "//CheatMenu/%s/Text" % b.name, enabled=False)[0].get_text()
    off = log_mark(); print(now(), "click", idx, txt, flush=True)
    sc0 = scenes(); b.click(); t1 = time.time()
    while time.time() - t1 < 60:
        time.sleep(1.0)
        try:
            if pig(): time.sleep(3); break
        except Exception: pass
    r = {"button": txt, "scenes_before": sc0, "scenes": scenes(), "pos": ppos(), "entrances": []}
    for e in d.find_objects(By.COMPONENT, "LocationEntrance", enabled=False):
        info = {"name": e.name, "pos": [round(e.worldX,2), round(e.worldY,2), round(e.worldZ,2)]}
        try: info["path"] = str(e.get_component_property("LocationEntrance", "EntrancePath", "Assembly-CSharp"))
        except Exception as ex: info["path"] = "ERR " + str(ex)[:60]
        info["dist"] = round(dist3(r["pos"], info["pos"]), 2); r["entrances"].append(info)
    r["log"] = log_since(off); out[txt] = r
    print(json.dumps(r, ensure_ascii=False)[:1800], flush=True)
    json.dump(out, open("s3_tp.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
