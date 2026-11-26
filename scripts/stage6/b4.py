# M08-01d: сброс сверху в выходы FallDown/JumpDown. python b4.py <loc> [имя выхода ...]
from g6 import *
from pts import point, inside
src = sys.argv[1]; names = sys.argv[2:]
F4 = os.path.join(R2, "b4.json")
try: R = json.load(open(F4, encoding="utf-8"))
except Exception: R = {}
def dump(): jdump(F4, R)
def ensure(loc):
    for via in ("Beach", "Beach", None):
        if loc in scenes() and gstate() == 0: return True
        try:
            if via and via != loc: goto(via); time.sleep(3)
            goto(loc)
        except Exception as e: print("goto ERR", type(e).__name__, str(e)[:80], flush=True)
        time.sleep(3)
    return loc in scenes()
prestage("b4"); hyg_tick({}, "b4")
ex = json.load(open(os.path.join(R2, "b3_%s.json" % src), encoding="utf-8"))["exits"]
for name in names:
    e = [x for x in ex if x["name"] == name][0]; r = {"src": src, "exit": name, "to": e["to"], "path": e["path"], "trig_y": [e["min"][1], e["max"][1]], "samples": []}
    others = [o for o in ex if o["name"] != name]
    p = point(ex, e)
    if p.get("none"):
        # разрешено только перекрытие с выходом того же назначения и пути, лежащим целиком НИЖЕ этого триггера
        x, z = e["pos"][0], e["pos"][2]
        ov = [o for o in others if inside(o, x, z, 1.0)]
        assert ov and all(o["to"] == e["to"] and o["path"] == e["path"] and o["max"][1] < e["min"][1] for o in ov), "нет безопасной точки: %s" % [o["name"] for o in ov]
        p = {"x": x, "z": z, "y": round(e["max"][1] + 3, 2), "from_center": 0.0, "margin": 0, "lower_overlap": [o["name"] for o in ov]}
    r["point"] = p
    if not ensure(src): r["result"] = "не попали в " + src; R[name] = r; dump(); continue
    time.sleep(1.5); wait_play_ready()
    live = [o.name for o in d.find_objects(By.COMPONENT, "LocationExit", enabled=False)]; assert name in live
    pr = first("Protagonist"); off = log_mark(); r["hp0"] = hp_now()
    autosync(True); teleport("T1", p["x"], p["y"], p["z"]); autosync(False); t0 = time.time(); changed = None
    while time.time() - t0 < 10:
        s = {"dt": round(time.time() - t0, 2)}
        try:
            s["y"] = round(ppos()[1], 2); s["map"] = rd(pr, "Protagonist", "_inputReader._gameInput.Gameplay.enabled", 2)
        except Exception as ex_: s["err"] = type(ex_).__name__
        sc = scene_now(); s["sc"] = sc; r["samples"].append(s)
        if src not in sc: changed = s["dt"]; break
        time.sleep(0.25)
    r["left_s"] = changed
    if changed is not None:
        t1 = time.time()
        while time.time() - t1 < 30:
            time.sleep(1.0)
            try:
                if scene_now() and pig() and gstate() == 0: break
            except Exception: pass
        time.sleep(3)
    r["scenes_after"] = scene_now(); r["pos_after"] = [round(v, 2) for v in ppos()]; r["state"] = sname(gstate()); r["hp"] = hp_now()
    ent = [(o.name, round(dxz(r["pos_after"], (o.worldX, o.worldY, o.worldZ)), 2), str(rd(o, "LocationEntrance", "_entrancePath.name", 1))) for o in d.find_objects(By.COMPONENT, "LocationEntrance", enabled=False)]
    r["entrances_same_path"] = [x for x in ent if x[2] == e["path"]]
    lg = log_since(off); r["cc67"] = lg["cc67_locationentry"]; ex_ = exc_summary(off); r["exc"] = ex_["total"]; r["by_type"] = ex_["by_type"]
    if ex_["total"]: r["stack"] = ex_["first_stacks"]
    ys = [s["y"] for s in r["samples"] if "y" in s]; r["y_trace"] = [ys[0], min(ys), ys[-1]] if ys else None
    r["map_off_y"] = next((s.get("y") for s in r["samples"] if s.get("map") is False), None)
    R[name] = r; dump(); print(json.dumps({k: v for k, v in r.items() if k != "samples"}, ensure_ascii=False), flush=True)
    if changed is None: print(r["samples"][-6:], flush=True)
