# -*- coding: utf-8 -*-
# Play A: 1.1 M16-01b (PlayableDirector) + 1.2 IT-01; New Game ровно 1 раз
from s3blib import *
DM = "UnityEngine.DirectorModule"; PD = "UnityEngine.Playables.PlayableDirector"
R = {"samples": []}
def dump(): jdump(os.path.join(R2, "a1.json"), R)
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
prestage("a1")
R["frameCount0"] = d.get_static_property("UnityEngine.Time", "frameCount", CORE)
assert "MainMenu" in scenes()
R["save_before"] = save_info(); R["save_before_hash"] = {k: v for k, v in save_hashes().items()}; R["save_equals_backup"] = save_hashes() == bk_hashes()
print("frame", R["frameCount0"], "save", R["save_before"], "eq", R["save_equals_backup"], flush=True)
hyg_start("a1", R); guard.risky("a1")
R["off"] = off = log_mark()
try:
    d.find_object(By.NAME, "Button New Game", enabled=False).click()
    for _ in range(15):
        time.sleep(0.4)
        try: d.find_object(By.NAME, "PopupButton - 1", enabled=False).click(); break
        except Exception: pass
    t1 = time.time()
    while time.time() - t1 < 60:
        try:
            if "Beach" in scenes(): break
        except Exception: pass
        time.sleep(0.3)
    t0 = time.time()
    for at in (0, 2, 5, 10):
        while time.time() - t0 < at: time.sleep(0.1)
        sample("%ds" % at, t0)
    d.get_png_screenshot(os.path.join(R2, "shots", "a1_intro_10s.png"))
    # IT-01
    I = R["it01"] = {}
    I["save"] = save_info(); I["scenes"] = scenes(); I["state"] = sname(gstate()); I["quest"] = qdetail()
    I["pig"] = [round(v, 2) for v in ppos()]; I["pig_count"] = len(pigs())
    sp = []
    for o in d.find_objects(By.PATH, "//*[@component=SpawnSystem]/*", enabled=False):
        sp.append((o.name, [round(o.worldX, 2), round(o.worldY, 2), round(o.worldZ, 2)]))
    I["spawnsystem_children"] = sp
    I["entrances"] = [(o.name, [round(o.worldX, 2), round(o.worldY, 2), round(o.worldZ, 2)], str(rd(o, "LocationEntrance", "_entrancePath.name", 1))[:60]) for o in d.find_objects(By.COMPONENT, "LocationEntrance", enabled=False)]
    s = first("SpawnSystem")
    I["lastPathTaken"] = str(rd(s, "SpawnSystem", "_pathTaken.lastPathTaken", 1))[:100]
    I["log"] = log_since(off); I["exc"] = exc_summary(off); I["alert_count"] = alert_count()
    print("IT01", json.dumps(I, ensure_ascii=False, default=str), flush=True)
finally:
    dump()
