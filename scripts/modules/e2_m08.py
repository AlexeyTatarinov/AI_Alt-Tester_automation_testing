import sys; sys.path.insert(0, r"Test_Ai\scripts\modules")
from elib import *

F = OUT + "/m08_01.json"
SKIP = {("Beach", "LocationExit"), ("Field_Hill", "LocationExit_ToBeach")}   # LOC-01/02 уже PASS
try:
    D = json.load(open(F, encoding="utf-8"))
except Exception:
    D = {"exits": {}, "scenes": {}}
off_all = log_mark()
autosync(True)
LOCS = [("Field_Hill", "Field_Hill"), ("Field_Farms", "Field_Farms"), ("Town_Market", "Town_Market"), ("Town_Upper", "Town_Upper"), ("Town_Inner", "Town_Inner"),
        ("Forest", "Forest"), ("Mountain_Path_bottom", "Mountain_Path"), ("Mountain_Cave", "Mountain_Cave"), ("Beach", "Beach")]


def sgoto(name):
    for a in range(3):
        try:
            return goto(name)
        except RuntimeError as e:
            print("goto retry", name, a, str(e)[:100], flush=True)
            try:
                goto("Beach" if name != "Beach" else "Field_Hill")
            except Exception:
                pass
    raise RuntimeError("sgoto failed " + name)


def exits_here():
    out = []
    for o in d.find_objects(By.COMPONENT, "LocationExit", enabled=False):
        out.append({"name": o.name, "pos": (o.worldX, o.worldY, o.worldZ), "to": rd(o, "LocationExit", "_locationToLoad.name"), "path": rd(o, "LocationExit", "_leadsToPath.name")})
    return out


def entrances_here():
    return [{"name": o.name, "pos": (o.worldX, o.worldY, o.worldZ), "path": rd(o, "LocationEntrance", "_entrancePath.name")} for o in d.find_objects(By.COMPONENT, "LocationEntrance", enabled=False)]


def test_exit(src, ex):
    key_ = "%s/%s" % (src, ex["name"])
    r = {"src": src, "exit": ex["name"], "to": ex["to"], "path": ex["path"], "exit_pos": [round(v, 2) for v in ex["pos"]]}
    guard.before_case(key_)
    if pause_open():
        close_pause()
    off = log_mark()
    t0 = time.time()
    try:
        tp(ex["pos"][0], ex["pos"][1] + 0.5, ex["pos"][2], 0.2)
    except Exception as e:
        r.update(verdict="BLOCKED", why="teleport error %s" % type(e).__name__)
        return r
    arrived = None
    errs = 0
    while time.time() - t0 < 30:
        time.sleep(0.5)
        try:
            sc = scenes()
            if any(ex["to"] and ex["to"] in s for s in sc) and src not in [s for s in sc if s == src] and pig():
                arrived = round(time.time() - t0, 1)
                break
        except Exception:
            errs += 1
    r["arrived_s"] = arrived
    r["poll_errors"] = errs
    time.sleep(3)
    try:
        r["scenes_after"] = scene_now()
    except Exception:
        r["scenes_after"] = None
    if arrived is None:
        r.update(verdict="FAIL", why="сцена %s не загрузилась за 30 с (сцены: %s)" % (ex["to"], r["scenes_after"]))
        r["log"] = log_since(off)
        return r
    try:
        p = ppos()
        ents = [e for e in entrances_here() if e["path"] == ex["path"]]
        r["player_pos"] = [round(v, 2) for v in p]
        r["entrance_candidates"] = [(e["name"], e["path"], round(dxz(p, e["pos"]), 2), round(dist3(p, e["pos"]), 2)) for e in ents]
        best = min([c[2] for c in r["entrance_candidates"]]) if ents else None
        r["dist_xz_to_entrance_same_path"] = best
    except Exception as e:
        r.update(verdict="BLOCKED", why="read error %s" % type(e).__name__)
        return r
    r["log"] = log_since(off)
    cc67 = r["log"]["cc67_locationentry"]
    r["cc67"] = cc67
    if not ents:
        r.update(verdict="FAIL", why="в сцене нет входа с путём %s" % ex["path"])
    elif cc67:
        r.update(verdict="FAIL", why="CC-67 предупреждение (известный CC-67); расстояние до входа %.2f м" % best)
    elif best > 2.0:
        r.update(verdict="FAIL", why="игрок в %.2f м от входа с тем же путём (> 2 м)" % best)
    else:
        r.update(verdict="PASS", why="до входа %.2f м, CC-67 нет" % best)
    return r


for loc, scn in LOCS:
    prestage("m08_" + loc)
    if scn not in scenes() or True:
        info = sgoto(loc)
    time.sleep(2)
    ex = exits_here()
    D["scenes"][loc] = {"exits": [(e["name"], e["to"], e["path"]) for e in ex], "entrances": [(e["name"], e["path"]) for e in entrances_here()]}
    jdump(F, D)
    print("==", loc, D["scenes"][loc]["exits"], flush=True)
    for e in ex:
        k = "%s/%s" % (loc, e["name"])
        if (loc, e["name"]) in SKIP:
            D["exits"][k] = {"verdict": "SKIPPED", "why": "Beach<->Field_Hill уже PASS (LOC-01/02)"}
            continue
        if k in D["exits"] and D["exits"][k].get("verdict") in ("PASS", "FAIL"):
            continue
        # убедиться, что мы в исходной сцене
        if scn not in scenes():
            sgoto(loc)
            time.sleep(2)
        r = test_exit(loc, e)
        D["exits"][k] = r
        jdump(F, D)
        print("  ", k, r.get("verdict"), r.get("why"), flush=True)
        # вернуться в исходную локацию для следующего выхода (если он будет)
        if scn not in scenes() or r.get("arrived_s") is not None:
            try:
                sgoto(loc)
                time.sleep(2)
            except SystemExit:
                raise
            except Exception as ee:
                print("goto back err", ee)
exc = exc_summary(off_all)
V = [v.get("verdict") for v in D["exits"].values()]
n_pass = V.count("PASS")
n_tested = sum(1 for x in V if x in ("PASS", "FAIL", "BLOCKED"))
fails = [k for k, v in D["exits"].items() if v.get("verdict") == "FAIL"]
cc67 = [k for k, v in D["exits"].items() if v.get("cc67")]
D["summary"] = {"pass": n_pass, "tested": n_tested, "fails": fails, "cc67": cc67, "exceptions": exc["total"]}
jdump(F, D)
verdict = "PASS" if n_pass == n_tested and n_tested > 0 else "FAIL"
save_er("M08-01", {"verdict": verdict, "numbers": "N из M: %d из %d выходов прошли (кроме Beach<->Field_Hill ToBeach, уже PASS); FAIL: %s; CC-67 на: %s; исключений в логе %d" % (n_pass, n_tested, fails, cc67, exc["total"]), "source": "m08_01.json"})
