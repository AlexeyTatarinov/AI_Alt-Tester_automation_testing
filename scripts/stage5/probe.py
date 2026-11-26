from s3blib import *
GC = "UnityEngine.CharacterController"
def sc(): return scene_now()
def drop(x, y, z, home, max_s=5.0):
    """T1 в (x,y,z), ждать приземления; вернуть y/позицию, grounded, сцены"""
    s0 = sc(); teleport("T1", x, y, z); last = None; r = {"from": [round(x, 2), round(y, 2), round(z, 2)]}; t0 = time.time()
    while time.time() - t0 < max_s:
        time.sleep(1.0)
        s = sc()
        if s != s0: r["scene_changed"] = [s0, s, round(time.time() - t0, 1)]; return r
        try: p = ppos(); g = grounded(pig())
        except Exception as e: r["err"] = type(e).__name__; continue
        r["land"] = [round(v, 2) for v in p]; r["grounded"] = g
        if p[1] < -30: r["void"] = True; teleport("T1", home[0], home[1] + 0.3, home[2]); time.sleep(1.5); return r
        if last is not None and abs(p[1] - last) < 0.03 and g: break
        last = p[1]
    return r
