# -*- coding: utf-8 -*-
# 4.3.3 M03-02b: тревога, затем пешком на Beach через LocationExit_ToBeach
from s3blib import *
R = {"trace": [], "walk": []}
def dump(): jdump(os.path.join(R2, "b4b.json"), R)
off = json.load(open(os.path.join(R2, "b1.json"), encoding="utf-8"))["off"]; R["off"] = off
NAME = "PlantCritter (4)"
prestage("b4b"); hyg_tick(R, "b4"); autosync(True)
def tr(label, **kw): R["trace"].append(st_now(label, **kw)); dump()
try:
    R["before"] = full_snap("M03-02b до", off)
    ex = pos_of("LocationExit_ToBeach"); R["exit_pos"] = ex
    c = crit(NAME); assert c is not None
    cp = cpos(c); print("crit", [round(v, 2) for v in cp], "exit", [round(v, 2) for v in ex], "pig", [round(v, 2) for v in ppos()], flush=True)
    tr("до подхода", alert=alert(c))
    vx, vz = -55.0 - cp[0], -337.0 - cp[2]; n = math.hypot(vx, vz)
    teleport("T1", cp[0] + vx / n * 3.0, cp[1] + 0.3, cp[2] + vz / n * 3.0); t0 = time.time()
    while time.time() - t0 < 8:
        time.sleep(1.0)
        if alert(c) is True: break
    time.sleep(1.5)
    tr("тревога", alert=alert(c), pos=[round(v, 2) for v in ppos()])
    assert alert(c) is True, "тревога не сработала"
    W = [(-55.0, 8.3, -337.0), (-56.0, 8.3, -343.0), (-58.3, 8.3, -348.0), (-58.3, 8.3, -354.0)]; wi = 0; stuck = 0; i = 0; t0 = time.time()
    while i < 60 and time.time() - t0 < 120:
        i += 1
        if "Beach" in scenes() or "Field_Hill" not in scenes(): break
        try:
            p = ppos()
            if dxz(p, W[wi]) < 2.0 and wi < len(W) - 1: wi += 1; stuck = 0
            tgt = W[wi]
            if stuck >= 2:
                dx, dz = tgt[0] - p[0], tgt[2] - p[2]; m = math.hypot(dx, dz) or 1; sgn = 1 if ((stuck - 2) // 4) % 2 == 0 else -1
                step_dir((sgn * -dz / m, sgn * dx / m), 0.5)
            step_towards(tgt, 0.4); p2 = ppos()
        except Exception as e:
            R["walk"].append({"i": i, "err": type(e).__name__}); time.sleep(1.0); continue
        stuck = stuck + 1 if dxz(p, p2) < 0.4 else 0
        try:
            cc = crit(NAME); row = {"i": i, "t": now(), "pos": [round(v, 1) for v in p2], "d_exit": round(dxz(p2, ex), 1), "wp": wi, "alert": alert(cc) if cc else "нет объекта",
                   "d_crit": round(dxz(p2, cpos(cc)), 1) if cc else None, "count": alert_count(), "state": sname(gstate()), "hp": hp_now()}
        except Exception as e:
            row = {"i": i, "err": type(e).__name__}
        R["walk"].append(row); print(row, flush=True); dump()
    t0 = time.time()
    while time.time() - t0 < 30 and "Beach" not in scenes(): time.sleep(1.0)
    R["walked_to_beach"] = "Beach" in scenes()
    time.sleep(5)
    tr("после перехода", pos=[round(v, 2) for v in ppos()])
    R["after"] = full_snap("M03-02b после", off); R["diff"] = diff(R["before"], R["after"]); R["exc"] = exc_summary(off)
    print("walked", R["walked_to_beach"], R["after"], "exc", R["exc"]["total"], flush=True)
finally:
    autosync(False); dump()
