from probe import *
off = json.load(open(os.path.join(R2, "b1.json"), encoding="utf-8"))["off"]
cx, cz = 5.27, 52.95
ax = (-0.369, -0.930); az = (0.930, -0.369)   # локальные оси коробки (yaw 111.65)
R = {"under": [], "around": [], "line": []}
def pr(k, r): R[k].append(r); print(k, r, flush=True); jdump(os.path.join(R2, "b4.json"), R)
autosync(True)
try:
    home = ppos(); R["home"] = home
    # пол под коробкой (старт ниже низа коробки 19.72 минус капсула 1.3)
    for u, w in ((0, 0), (0, 4), (0, -4)):
        pr("under", drop(cx + ax[0] * u + az[0] * w, 17.8, cz + ax[1] * u + az[1] * w, home))
        if "Town_Upper" not in scenes(): break
    # пол вокруг коробки сверху (вне её footprint)
    for u, w in ((2.5, 0), (-2.5, 0), (0, 8), (0, -8)):
        if "Town_Upper" not in scenes(): break
        pr("around", drop(cx + ax[0] * u + az[0] * w, 29.0, cz + ax[1] * u + az[1] * w, home))
    for x in (28.0, 22.0, 16.0, 13.0):
        if "Town_Upper" not in scenes(): break
        pr("line", drop(x, 33.0, 58.9 if x > 20 else 56.0, home))
    R["scenes"] = scenes(); R["exc"] = exc_summary(off)["total"]
finally:
    autosync(False); jdump(os.path.join(R2, "b4.json"), R)
