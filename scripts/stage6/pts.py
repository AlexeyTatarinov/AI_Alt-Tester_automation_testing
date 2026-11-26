# точки сброса: центр выхода или ближайшая к центру точка внутри его контура и вне всех прочих (OBB по x/z)
import json, math, sys
import os
O = r"C:\Users\Aotat\Desktop\Test_Ai\Reports_2026-11-21\results\modules_stage6_20261126"
def F(name): return os.path.join(O, name)
def local(e, x, z):
    t = math.radians(e["euler"][1]); dx, dz = x - e["pos"][0], z - e["pos"][2]
    return dx * math.cos(t) - dz * math.sin(t), dx * math.sin(t) + dz * math.cos(t)
def half(e): return e["size"][0] * e["scale"][0] / 2, e["size"][2] * e["scale"][2] / 2
def inside(e, x, z, m):
    u, w = local(e, x, z); a, b = half(e); return abs(u) <= a + m and abs(w) <= b + m
def point(ex, e):
    others = [o for o in ex if o["name"] != e["name"]]
    a, b = half(e); t = math.radians(e["euler"][1]); cand = []
    for i in range(-40, 41):
        for j in range(-40, 41):
            u, w = i / 40 * (a - 0.5), j / 40 * (b - 0.5)
            x = e["pos"][0] + u * math.cos(t) + w * math.sin(t); z = e["pos"][2] - u * math.sin(t) + w * math.cos(t)
            cand.append((math.hypot(u, w), x, z))
    cand.sort()
    for margin in (1.0, 0.5):
        for dist, x, z in cand:
            if not any(inside(o, x, z, margin) for o in others):
                return {"x": round(x, 2), "z": round(z, 2), "y": round(e["max"][1] + 3, 2), "from_center": round(dist, 2), "margin": margin,
                        "center_overlaps": [o["name"] for o in others if inside(o, e["pos"][0], e["pos"][2], 0.5)]}
    return {"none": True, "center_overlaps": [o["name"] for o in others if inside(o, e["pos"][0], e["pos"][2], 0.5)]}
if __name__ == "__main__":
    loc = sys.argv[1]; ex = json.load(open(F("b3_%s.json" % loc), encoding="utf-8"))["exits"]
    P = {e["name"]: point(ex, e) for e in ex if ("FallDown" in e["name"] or "JumpDown" in e["name"]) and "Forest" not in e["name"]}
    for k, v in P.items(): print(k, v)
    json.dump(P, open(F("pts_%s.json" % loc), "w"), indent=1)
