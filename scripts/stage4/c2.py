# -*- coding: utf-8 -*-
# M03-02 B: T1 в 3 м перед триггером выхода, тревога, вход пешком, замеры после перехода
from s3blib import *
R = {"trace": [], "walk": []}
def dump(): jdump(os.path.join(R2, "c2.json"), R)
off = json.load(open(os.path.join(R2, "c1.json"), encoding="utf-8"))["off"]; R["off"] = off
prestage("c2"); hyg_tick(R, "c2")
assert "Mountain_Cave" in scenes()
CENTER = (104.76, 24.08, 76.9); EDGE_Z = 76.9 + 6.986 / 2   # грань триггера со стороны пещеры
POINT = (104.76, 22.4, EDGE_Z + 3.0)
def klippers():
    out = []
    for c in d.find_objects(By.COMPONENT, "Critter", enabled=True):
        p = (c.worldX, c.worldY, c.worldZ); out.append((dxz(p, POINT), abs(p[1] - POINT[1]), c, p))
    return sorted(out, key=lambda t: math.hypot(t[0], t[1]))
def klip(kid):
    for c in d.find_objects(By.COMPONENT, "Critter", enabled=True):
        if c.id == kid: return c
def read(label, kid):
    p = ppos(); c = klip(kid)
    r = {"t": now(), "label": label, "pos": [round(v, 2) for v in p], "to_edge_z": round(p[2] - EDGE_Z, 2), "count": alert_count(), "state": sname(gstate()), "hp": hp_now(),
         "alert": alert(c) if c else None, "d_klipper": round(dxz(p, (c.worldX, c.worldY, c.worldZ)), 1) if c else None, "scenes": scene_now()}
    print(json.dumps(r), flush=True); return r
autosync(True)
try:
    ks = klippers(); dist, dy, c, cp = ks[0]; kid = c.id
    R["point"] = POINT; R["klipper"] = {"id": kid, "name": c.name, "pos": cp, "d_to_point": round(dist, 2), "dy": round(dy, 2)}
    print("klipper", R["klipper"], flush=True)
    R["trace"].append(read("до T1", kid))
    guard.risky("c2 tp"); teleport("T1", *POINT); time.sleep(1.5)
    autosync(False)
    first_r = read("после T1", kid); R["trace"].append(first_r)
    d.get_png_screenshot(os.path.join(R2, "shots", "c2_after_t1.png"))
    for i in range(4):
        if R["trace"][-1]["count"] not in (0,) and R["trace"][-1]["state"] == "Combat": break
        time.sleep(1.0); R["trace"].append(read("ждём тревогу %d" % i, kid))
    dump()
    in_alert = R["trace"][-1]["state"] == "Combat"
    R["alert_at_point"] = in_alert
    if in_alert:
        t0 = time.time(); stuck = 0
        while time.time() - t0 < 40:
            try:
                if "Mountain_Cave" not in scenes(): break
                row = read("walk", kid)
                if "Mountain_Cave" not in row["scenes"]: break
                R["walk"].append(row)
                if row["state"] != "Combat" or row["count"] == 0: R["alert_lost"] = row; break
                p0 = ppos()
                for k in range(2):
                    step_towards((CENTER[0], p0[1], CENTER[2]), 0.1)
                    if "Mountain_Cave" not in scenes(): break
                if "Mountain_Cave" in scenes() and dxz(p0, ppos()) < 0.15:
                    stuck += 1
                    if stuck >= 4: R["stuck"] = True; break
            except Exception as e:
                R["walk"].append({"t": now(), "err": type(e).__name__}); time.sleep(0.5)
            storm_check(off, "walk")
        R["last_before"] = [w for w in R["walk"] if "count" in w][-1]
        if "Mountain_Cave" not in scenes():
            t_left = time.time(); loaded = None
            while time.time() - t_left < 30:
                try:
                    if "Mountain_Path" in scenes() and pig(): loaded = time.time(); break
                except Exception: pass
                time.sleep(1.0)
            R["left_cave"] = True; R["new_scene"] = scene_now(); R["load_s"] = round((loaded or time.time()) - t_left, 1)
            for sec in (5, 15):
                while time.time() - (loaded or t_left) < sec: time.sleep(0.2)
                r = {"t": now(), "sec": sec, "scenes": scene_now(), "count": alert_count(), "state": sname(gstate()), "hp": hp_now(), "pos": [round(v, 2) for v in ppos()], "dialogue": dlg()}
                R["after%d" % sec] = r; print("AFTER", json.dumps(r), flush=True); dump()
            R["critters_new"] = []
            for cc in d.find_objects(By.COMPONENT, "Critter", enabled=True):
                R["critters_new"].append({"name": cc.name, "d": round(dxz(ppos(), (cc.worldX, cc.worldY, cc.worldZ)), 1), "alert": alert(cc)})
            print("critters", R["critters_new"], flush=True)
            d.get_png_screenshot(os.path.join(R2, "shots", "c2_after15.png"))
            key("Tab", 0.1); time.sleep(1.5)
            R["tab_opens"] = inv(); R["state_after_tab"] = sname(gstate())
            d.get_png_screenshot(os.path.join(R2, "shots", "c2_after_tab.png"))
            if R["tab_opens"]: key("Tab", 0.1); time.sleep(1.5)
            print("tab_opens", R["tab_opens"], R["state_after_tab"], flush=True)
    R["exc"] = exc_summary(off); print("exc", R["exc"]["total"], R["exc"]["by_type"], flush=True)
except Storm as e:
    R["STORM"] = str(e); print("STORM", e, flush=True)
finally:
    autosync(False); dump()
