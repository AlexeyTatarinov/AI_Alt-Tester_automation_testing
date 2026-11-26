# JumpDown, образец 2: что делает PigChef и директоры Beach после загрузки
from g6 import *
from pts import point
R = {"samples": []}
def dump(): jdump(os.path.join(R2, "b7.json"), R)
prestage("b7"); hyg_tick({}, "b7")
if "Field_Hill" not in scenes():
    try: print("goto", goto("Field_Hill"), flush=True)
    except Exception as e_:
        print("ERR", e_); goto("Town_Market"); time.sleep(3); print("goto", goto("Field_Hill"))
time.sleep(2); wait_play_ready()
ex = json.load(open(os.path.join(R2, "b3_Field_Hill.json"), encoding="utf-8"))["exits"]
e = [x for x in ex if x["name"] == "LocationExit_ToBeach_JumpDown"][0]; p = point(ex, e); R["point"] = p; R["hp0"] = hp_now(); R["q"] = quest(); R["save_finished"] = len(save_info().get("finished", []))
off = log_mark(); autosync(True); teleport("T1", p["x"], p["y"], p["z"]); autosync(False); t0 = time.time(); ys = []
try:
    while time.time() - t0 < 28:
        s = {"dt": round(time.time() - t0, 1)}
        try:
            s["sc"] = scene_now(); pl = pigs(); s["pig_found"] = len(pl); s["pig_active"] = len(d.find_objects(By.NAME, "PigChef(Clone)", enabled=True))
            if pl: s["pig"] = [round(pl[0].worldX, 2), round(pl[0].worldY, 2), round(pl[0].worldZ, 2)]
            s["state"] = sname(gstate())
            if "Beach" in s["sc"]:
                s["dirs"] = {o.name: (o.get_component_property(PD, "state", DM, max_depth=1), round(float(o.get_component_property(PD, "time", DM, max_depth=1)), 2)) for o in d.find_objects(By.COMPONENT, PD, enabled=False)}
        except Exception as ex_: s["err"] = type(ex_).__name__ + ": " + str(ex_)[:80]
        R["samples"].append(s); print(json.dumps(s, ensure_ascii=False), flush=True)
        time.sleep(1.5)
    d.get_png_screenshot(os.path.join(R2, "shots", "b7_end.png"))
    R["pos_after"] = [round(v, 2) for v in ppos()]; R["hp"] = hp_now(); R["state"] = sname(gstate())
    R["entrances"] = [(o.name, round(dxz(R["pos_after"], (o.worldX, o.worldY, o.worldZ)), 2), str(rd(o, "LocationEntrance", "_entrancePath.name", 1))) for o in d.find_objects(By.COMPONENT, "LocationEntrance", enabled=False)]
    p0 = ppos(); key("W", 0.3); time.sleep(1.0); R["w_moved"] = round(dxz(p0, ppos()), 2)
    lg = log_since(off); R["cc67"] = lg["cc67_locationentry"]; e_ = exc_summary(off); R["exc"] = e_["total"]
    print({k: v for k, v in R.items() if k != "samples"}, flush=True)
finally:
    dump()
