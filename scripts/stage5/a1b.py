# -*- coding: utf-8 -*-
# Play A: 1.1 M16-01b (PlayableDirector) + 1.2 IT-01; New Game ровно 1 раз
from s3blib import *
DM = "UnityEngine.DirectorModule"; PD = "UnityEngine.Playables.PlayableDirector"
R = {}
def dump(): jdump(os.path.join(R2, "a1b.json"), R)
def directors():
    out = []
    for o in d.find_objects(By.COMPONENT, PD, enabled=False):
        e = {"name": o.name, "id": o.id, "go_enabled": o.enabled}
        for p in ("state", "time", "playableAsset.name", "duration", "playOnAwake"):
            try: e[p] = o.get_component_property(PD, p, DM, max_depth=1)
            except Exception as ex: e[p] = "ERR %s: %s" % (type(ex).__name__, str(ex)[:100])
        out.append(e)
    return out
def sample(tag, t0):
    s = {"tag": tag, "dt": round(time.time() - t0, 2), "t": now()}
    s["directors"] = directors()
    try: s["state"] = sname(gstate())
    except Exception as ex: s["state"] = "ERR " + type(ex).__name__
    c = first("CutsceneManager")
    s["_activePlayableDirector"] = str(rd(c, "CutsceneManager", "_activePlayableDirector", 1))[:200] if c else "no CutsceneManager"
    R["samples"].append(s); print(json.dumps(s, ensure_ascii=False), flush=True)
off = json.load(open(os.path.join(R2, "a1.json"), encoding="utf-8"))["off"]
I = R["it01"] = {}
I["save"] = save_info(); I["scenes"] = scenes(); I["state"] = sname(gstate()); I["quest"] = qdetail()
pl = pigs(); I["pig_count"] = len(pl); I["pig"] = [[round(o.worldX, 2), round(o.worldY, 2), round(o.worldZ, 2)] for o in pl]; I["pig_active_find"] = len(d.find_objects(By.NAME, "PigChef(Clone)", enabled=True))
sp = []
for o in d.find_objects(By.PATH, "//*[@component=SpawnSystem]/*", enabled=False):
    sp.append((o.name, [round(o.worldX, 2), round(o.worldY, 2), round(o.worldZ, 2)]))
I["spawnsystem_children"] = sp
I["entrances"] = [(o.name, [round(o.worldX, 2), round(o.worldY, 2), round(o.worldZ, 2)], str(rd(o, "LocationEntrance", "_entrancePath.name", 1))[:60]) for o in d.find_objects(By.COMPONENT, "LocationEntrance", enabled=False)]
s = first("SpawnSystem")
I["lastPathTaken"] = str(rd(s, "SpawnSystem", "_pathTaken.lastPathTaken", 1))[:100]
I["log"] = log_since(off); I["exc"] = exc_summary(off); I["alert_count"] = alert_count()
print("IT01", json.dumps(I, ensure_ascii=False, default=str), flush=True)
R["directors"] = directors()
print(R["directors"])
dump()
