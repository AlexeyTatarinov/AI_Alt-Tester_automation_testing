import sys; sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\modules")
from elib import *

F = OUT + "/m06_01.json"
try:
    D = json.load(open(F, encoding="utf-8"))
except Exception:
    D = {}
off_all = log_mark()
autosync(True)


def bnds(o, comp):
    r = sget(o, comp, "bounds", PHYS, 3)
    return r


def mm(v):
    return (v["x"], v["y"], v["z"])


def floors():
    out = []
    for comp in ("UnityEngine.MeshCollider", "UnityEngine.TerrainCollider"):
        try:
            l = d.find_objects(By.COMPONENT, comp, enabled=False)
        except Exception:
            continue
        for o in l:
            r = bnds(o, comp)
            if not r["ok"]:
                out.append({"name": o.name, "comp": comp, "err": r["resp"][:100]})
                continue
            b = r["raw"]
            try:
                c, e = mm(b["center"]), mm(b["extents"])
            except Exception:
                try:
                    c, e = mm(b["center"]), (b["size"]["x"] / 2, b["size"]["y"] / 2, b["size"]["z"] / 2)
                except Exception:
                    out.append({"name": o.name, "comp": comp, "raw": str(b)[:150]})
                    continue
            out.append({"name": o.name, "comp": comp, "center": c, "ext": e, "area": 4 * e[0] * e[2]})
    return out


def probe_side(side, x0, x1, z0, z1, ytop, ent):
    r = {"side": side, "tries": []}
    if side == "W":
        pts = lambda off: (x0 + off, (z0 + z1) / 2, (-1, 0))
    elif side == "E":
        pts = lambda off: (x1 - off, (z0 + z1) / 2, (1, 0))
    elif side == "S":
        pts = lambda off: ((x0 + x1) / 2, z0 + off, (0, -1))
    else:
        pts = lambda off: ((x0 + x1) / 2, z1 - off, (0, 1))
    first_floor = None
    for off in (2, 5, 10, 20):
        x, z, dirv = pts(off)
        teleport("T1", x, ytop, z)
        t0 = time.time()
        g = False
        while time.time() - t0 < 6:
            time.sleep(0.3)
            try:
                if grounded(pig()):
                    g = True
                    break
            except Exception:
                pass
        try:
            y = round(ppos()[1], 1)
        except Exception:
            y = None
        r["tries"].append({"off": off, "grounded": g, "y": y})
        if g and y is not None and y > ytop - 400:
            first_floor = (off, x, z, y, dirv)
            break
    r["first_floor"] = first_floor[:4] if first_floor else None
    if first_floor and first_floor[0] <= 5:
        off, x, z, y, dirv = first_floor
        time.sleep(0.5)
        n0 = len(pigs())
        step_dir(dirv, 0.3)
        ys = []
        t0 = time.time()
        for ts in (1, 3, 5):
            while time.time() - t0 < ts:
                time.sleep(0.1)
            try:
                ys.append(round(ppos()[1], 1))
            except Exception:
                ys.append(None)
        r["step_out_y_1_3_5s"] = ys
        r["fell"] = ys[-1] is not None and ys[-1] < y - 25
        r["respawned"] = None
        if r["fell"]:
            time.sleep(3)
            r["pig_ids_after"] = [p.id for p in pigs()]
    # возврат на безопасную точку
    teleport("T1", ent[0], ent[1] + 0.5, ent[2])
    time.sleep(3)
    return r


def location(name):
    prestage("m06_" + name)
    goto(name)
    time.sleep(2)
    res = {"name": name}
    fl = floors()
    res["floor_candidates"] = sorted([f for f in fl if "area" in f], key=lambda f: -f["area"])[:5]
    res["floor_errors"] = [f for f in fl if "area" not in f][:5]
    ents = d.find_objects(By.COMPONENT, "LocationEntrance", enabled=False)
    ent = (ents[0].worldX, ents[0].worldY, ents[0].worldZ)
    if not res["floor_candidates"]:
        res["verdict"] = "BLOCKED"
        res["why"] = "рамка пола не прочиталась"
        return res
    big = res["floor_candidates"][0]
    c, e = big["center"], big["ext"]
    x0, x1, z0, z1 = c[0] - e[0], c[0] + e[0], c[2] - e[2], c[2] + e[2]
    ytop = c[1] + e[1] + 10
    res["frame"] = {"x0": round(x0, 1), "x1": round(x1, 1), "z0": round(z0, 1), "z1": round(z1, 1), "ytop": round(ytop, 1), "floor": big["name"]}
    res["sides"] = []
    for side in ("W", "E", "S", "N"):
        guard.before_case("m06_%s_%s" % (name, side))
        res["sides"].append(probe_side(side, x0, x1, z0, z1, ytop, ent))
        print(name, side, res["sides"][-1], flush=True)
    falls = [s["side"] for s in res["sides"] if s.get("fell")]
    nofloor = [s["side"] for s in res["sides"] if not s["first_floor"]]
    res["falls"] = falls
    res["no_floor_within_20m"] = nofloor
    res["verdict"] = "OBSERVATION" if falls else "PASS"
    return res


for loc in ("Field_Hill", "Field_Farms"):
    if loc in D and D[loc].get("verdict"):
        continue
    D[loc] = location(loc)
    jdump(F, D)
exc = exc_summary(off_all)
parts = {k: (v.get("verdict"), v.get("falls"), v.get("no_floor_within_20m"), v.get("frame")) for k, v in D.items() if isinstance(v, dict) and "verdict" in v}
vs = [p[0] for p in parts.values()]
verdict = "BLOCKED" if "BLOCKED" in vs else ("OBSERVATION" if "OBSERVATION" in vs else "PASS")
save_er("M06-01", {"verdict": verdict, "numbers": "рамка пола и зонд края (4 стороны, отступы 2/5/10/20 м): %s; падение без респавна — OBSERVATION (как CC-82); исключений %d" % (parts, exc["total"]), "source": "m06_01.json"})
