# -*- coding: utf-8 -*-
# 4.4 IT-11: урон от Klipper (<=5 с), затем отход
from s3blib import *
R = {"hits": []}
def dump(): jdump(os.path.join(R2, "b6.json"), R)
off = json.load(open(os.path.join(R2, "b1.json"), encoding="utf-8"))["off"]
prestage("b6"); hyg_tick(R, "b6")
if "Mountain_Cave" not in scenes(): print("goto", goto("Mountain_Cave"), flush=True)
time.sleep(2); wait_play_ready(); autosync(True)
try:
    home = ppos(); R["home"] = home; R["arrive"] = st_now("Mountain_Cave")
    cl = [c for c in d.find_objects(By.COMPONENT, "Critter", enabled=True)]
    print([(c.name, [round(v, 1) for v in (c.worldX, c.worldY, c.worldZ)], round(dxz(home, (c.worldX, c.worldY, c.worldZ)), 1)) for c in cl], flush=True)
    ks = sorted([c for c in cl if "Klipper" in c.name], key=lambda c: dxz(home, (c.worldX, c.worldY, c.worldZ)))
    assert ks, "нет Klipper"
    c = ks[0]; cp = cpos(c); R["klipper"] = [c.name, cp]
    vx, vz = home[0] - cp[0], home[2] - cp[2]; n = math.hypot(vx, vz) or 1
    h0 = hp_now(); teleport("T1", cp[0] + vx / n * 1.5, cp[1] + 0.3, cp[2] + vz / n * 1.5); t0 = time.time()
    while time.time() - t0 < 5:
        time.sleep(0.8); h = hp_now(); R["hits"].append((round(time.time() - t0, 1), h, alert(c)))
        if isinstance(h, int) and h < h0: break
    teleport("T1", home[0], home[1] + 0.3, home[2]); time.sleep(4.0)
    R["left"] = st_now("отход", alert=alert(c)); R["hp0"] = h0; print("hits", R["hits"], flush=True)
    R["exc"] = exc_summary(off); print("exc", R["exc"]["total"], flush=True)
finally:
    autosync(False); dump()
