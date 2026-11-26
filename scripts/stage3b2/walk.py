# -*- coding: utf-8 -*-
# пешком по путевым точкам; аргументы: метка x,z x,z ...
from s3blib import *
import sys
label = sys.argv[1]; W = [tuple(float(v) for v in a.split(",")) for a in sys.argv[2:]]
R = {"waypoints": W, "walk": []}
autosync(True)
try:
    wi = 0; stuck = 0; t0 = time.time(); i = 0
    while time.time() - t0 < 90 and "Field_Hill" in scenes():
        i += 1
        try:
            p = ppos()
            if math.hypot(p[0] - W[wi][0], p[2] - W[wi][1]) < 2.0:
                if wi == len(W) - 1: break
                wi += 1; stuck = 0
            tgt = (W[wi][0], p[1], W[wi][1])
            if stuck >= 3: break
            step_towards(tgt, 0.5); p2 = ppos()
        except Exception as e:
            R["walk"].append({"i": i, "err": type(e).__name__}); time.sleep(1.0); continue
        stuck = stuck + 1 if dxz(p, p2) < 0.35 else 0
        if i % 3 == 0 or stuck:
            row = {"i": i, "t": now(), "pos": [round(v, 1) for v in p2], "wp": wi, "count": alert_count(), "state": sname(gstate())}
            R["walk"].append(row); print(row["pos"], wi, row["state"], row["count"], "stuck" if stuck else "", flush=True)
    time.sleep(4)
    R["end"] = {"scenes": scene_now(), "pos": [round(v, 2) for v in ppos()], "state": sname(gstate()), "count": alert_count()}
    print("END", R["end"], flush=True)
    if "Field_Hill" in R["end"]["scenes"]: d.get_png_screenshot(os.path.join(R2, "shots", label + ".png"))
finally:
    autosync(False); jdump(os.path.join(R2, "walk_%s.json" % label), R)
