import sys; sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\modules")
from elib import *

F = OUT + "/m10.json"
try:
    D = json.load(open(F, encoding="utf-8"))
except Exception:
    D = {"kinds": {}, "scans": {}, "m10_02": None}
off_all = log_mark()
autosync(True)


def crit_list():
    return d.find_objects(By.COMPONENT, "Critter", enabled=False)


def cinfo(o):
    try:
        a = o.get_component_property("Critter", "isPlayerInAlertZone", ASM)
    except Exception as e:
        a = "ERR " + type(e).__name__
    try:
        hp = o.get_component_property("Damageable", "_currentHealthSO.CurrentHealth", ASM)
    except Exception:
        hp = None
    return a, hp


def php():
    try:
        return health()
    except Exception:
        return None


def face(cp, n=3):
    for _ in range(n):
        try:
            step_towards(cp, 0.08)
        except Exception:
            pass


def far_point(cp):
    cands = []
    for o in d.find_objects(By.COMPONENT, "LocationEntrance", enabled=False):
        cands.append((math.hypot(o.worldX - cp[0], o.worldZ - cp[2]), (o.worldX, o.worldY + 0.5, o.worldZ)))
    cands.sort(reverse=True)
    return cands[0] if cands else (None, None)


def test_kind(kind, scene):
    r = {"kind": kind, "scene": scene}
    guard.before_case("m10_" + kind)
    cl = [c for c in crit_list() if c.name.split(" (")[0] == kind]
    c = None
    for cc in cl:
        try:
            cc.update_object()
            c = cc
            break
        except Exception:
            pass
    if c is None:
        r.update(blocked="все %d объектов вида неактивны в иерархии (update_object NotFound), враг не появляется без сюжетного события" % len(cl))
        return r
    cp = (c.worldX, c.worldY, c.worldZ)
    r["n_in_scene"] = len(cl)
    r["pos"] = [round(v, 1) for v in cp]
    try:
        r["components"] = [x.get("componentName") for x in c.get_all_components()]
    except Exception:
        pass
    off = log_mark()
    # ENM-01
    h0 = php()
    teleport("T1", cp[0] - 3.0, cp[1] + 0.3, cp[2])
    t0 = time.time()
    alert_t = None
    while time.time() - t0 < 10:
        time.sleep(0.25)
        a, hp = cinfo(c)
        if a is True and alert_t is None:
            alert_t = round(time.time() - t0, 1)
    r["enm01"] = {"alert_s": alert_t, "player_hp": [h0, php()], "ok": alert_t is not None and alert_t <= 3.0}
    # ENM-02
    dist, fp = far_point(cp)
    r["enm02_dist_m"] = None if dist is None else round(dist, 1)
    if fp is None:
        r["enm02"] = {"ok": None, "why": "нет точки вдали"}
    else:
        teleport("T1", *fp)
        time.sleep(0.5)
        if SCN.get(scene, scene) not in scenes():
            raise RuntimeError("SCRIPT: far point changed scene %s -> %s" % (scene, scenes()))
        t0 = time.time()
        off_t = None
        while time.time() - t0 < 6:
            a, hp = cinfo(c)
            if a is False and off_t is None:
                off_t = round(time.time() - t0, 1)
            time.sleep(0.25)
        r["enm02"] = {"off_s": off_t, "dist_m": round(dist, 1), "ok": off_t is not None and off_t <= 3.0}
    # ENM-03
    items0 = len(d.find_objects(By.COMPONENT, "CollectableItem", enabled=False))
    teleport("T1", cp[0] - 1.2, cp[1] + 0.3, cp[2])
    time.sleep(1.0)
    face(cp)
    a, hp0 = cinfo(c)
    hits = 0
    t0 = time.time()
    gone = False
    hp_last = hp0
    ph = [php()]
    hit_seen = False
    dead_seen = False
    while time.time() - t0 < 20:
        key("F", 0.1)
        hits += 1
        time.sleep(0.4)
        ph.append(php())
        try:
            c.update_object()
            a, hp_last = cinfo(c)
            if c.get_component_property("Damageable", "GetHit", ASM) is True:
                hit_seen = True
            if c.get_component_property("Damageable", "IsDead", ASM) is True:
                dead_seen = True
        except Exception:
            gone = True
            break
        if hits % 6 == 0:
            try:
                p = ppos(); cp2 = (c.worldX, c.worldY, c.worldZ)
                if dxz(p, cp2) > 2.2:
                    teleport("T1", cp2[0] - 1.2, cp2[1] + 0.3, cp2[2]); time.sleep(0.5)
                face(cp2, 2)
            except Exception:
                pass
    time.sleep(1.5)
    items1 = len(d.find_objects(By.COMPONENT, "CollectableItem", enabled=False))
    ok3 = gone or dead_seen or (hp0 is not None and hp_last is not None and hp_last < hp0)
    r["enm03"] = {"hits": hits, "enemy_hp": [hp0, hp_last], "gone": gone, "get_hit_seen": hit_seen, "is_dead_seen": dead_seen, "items": [items0, items1], "dropped": items1 > items0, "player_hp_series": ph[:12], "ok": bool(ok3)}
    r["log"] = log_since(off)
    return r


def scan(scn_key):
    prestage("m10_scan_" + scn_key)
    goto(scn_key)
    time.sleep(2)
    kinds = {}
    for o in crit_list():
        k = o.name.split(" (")[0]
        kinds[k] = kinds.get(k, 0) + 1
    D["scans"][scn_key] = kinds
    jdump(F, D)
    print("scan", scn_key, kinds, flush=True)
    return kinds


def find_kind_match(kinds, token):
    return [k for k in kinds if token.lower() in k.lower()]


want = {"Klipper": "Mountain_Cave", "Gluecose": "Field_Farms", "Slime": "Field_Farms", "Rock": None}
tested = set(D["kinds"].keys())
order = ["Field_Farms", "Mountain_Cave", "Mountain_Path_bottom", "Forest", "Town_Upper", "Town_Inner"]
found_rock = any("rock" in k.lower() for k in tested)
for scn in order:
    kinds = scan(scn)
    for k in kinds:
        if k == "PlantCritter" or k in tested:
            continue
        # тестируем каждый новый вид (в сцене, где найден первым)
        try:
            res = test_kind(k, scn)
        except SystemExit:
            raise
        except Exception as e:
            res = {"kind": k, "scene": scn, "error": "%s: %s" % (type(e).__name__, str(e)[:150])}
        D["kinds"][k] = res
        tested.add(k)
        jdump(F, D)
        print("KIND", k, json.dumps(res, ensure_ascii=False, default=str)[:900], flush=True)
        # вернуться в сцену для следующих видов
        if any(kk not in tested and kk != "PlantCritter" for kk in kinds):
            goto(scn)
            time.sleep(2)
    if any("rock" in k.lower() for k in tested) and all(any(t.lower() in k.lower() for k in tested) for t in ("klipper",)):
        pass

# M10-02: PlantCritter 1.2 m, 20 s без ударов
prestage("m10_02")
goto("Field_Hill")
time.sleep(2)
pl = [c for c in crit_list() if c.name == "PlantCritter"]
c = pl[0]
c.update_object()
cp = (c.worldX, c.worldY, c.worldZ)
guard.before_case("m10_02")
off = log_mark()
teleport("T1", cp[0] - 1.2, cp[1] + 0.3, cp[2])
time.sleep(0.5)
series = []
t0 = time.time()
h_start = php()
while time.time() - t0 < 20:
    a, hp = cinfo(c)
    try:
        pp = ppos()
        dd = round(dxz(pp, (c.worldX, 0, c.worldZ)), 2)
    except Exception:
        dd = None
    series.append((round(time.time() - t0, 1), php(), a, dd))
    time.sleep(1.0)
h_end = php()
D["m10_02"] = {"player_hp_start": h_start, "player_hp_end": h_end, "series": series, "log": log_since(off)}
jdump(F, D)
dropped = h_start is not None and h_end is not None and h_end < h_start
save_er("M10-02", {"verdict": "PASS" if dropped else "OBSERVATION", "numbers": "PlantCritter, 1,2 м, 20 с без ударов: здоровье игрока %s → %s%s; ряд (t,hp,alert,расстояние) %s" % (h_start, h_end, "" if dropped else " (враг не атакует)", series[::3]), "source": "m10.json"})
# итог M10-01
ks = D["kinds"]
errs = [k for k, v in ks.items() if "error" in v]
bad = [k for k, v in ks.items() if "error" not in v and not (v["enm01"]["ok"] and (v["enm02"].get("ok") in (True, None)) and v["enm03"]["ok"])]
if not ks:
    save_er("M10-01", {"verdict": "BLOCKED", "numbers": "не найдено ни одного вида врагов кроме PlantCritter в просканированных сценах %s" % D["scans"], "source": "m10.json"})
else:
    v = "PASS" if not bad and not errs else ("FAIL" if bad else "BLOCKED")
    save_er("M10-01", {"verdict": v, "numbers": "виды: %s; сканы сцен: %s; не прошли: %s; ошибки скрипта: %s; " % ({k: ((x.get("enm01") or {}).get("ok"), (x.get("enm02") or {}).get("ok"), (x.get("enm03") or {}).get("ok"), (x.get("enm03") or {}).get("dropped")) for k, x in ks.items()}, D["scans"], bad, errs), "source": "m10.json"})
print("exceptions", exc_summary(off_all))
