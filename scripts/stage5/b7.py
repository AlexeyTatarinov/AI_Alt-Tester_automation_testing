from ray import *
R = {}
cx, cz = 5.27, 52.95
ax = (-0.369, -0.930); az = (0.930, -0.369)
pts = {}
for u in (-3, -2, -1, 0, 1, 2, 3):
    for w in (-5, 0, 5):
        pts["u%+d w%+d" % (u, w)] = (cx + ax[0] * u + az[0] * w, cz + ax[1] * u + az[1] * w)
try:
    for k, (x, z) in pts.items():
        R[k] = {"xz": [round(x, 2), round(z, 2)], "from40": ground(x, z), "from19": ground(x, z, 19.6, 25)}
        print(k, R[k], flush=True); time.sleep(0.3)
except Exception as e:
    print("ERR", type(e).__name__, str(e)[:300])
jdump(os.path.join(R2, "b7.json"), R)
