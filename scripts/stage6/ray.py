from s3blib import *
V = "UnityEngine.Vector3, UnityEngine.CoreModule"
def hit(x, y, z, dist):
    return d.call_static_method("UnityEngine.Physics", "Raycast", PHYS,
        [{"x": x, "y": y, "z": z}, {"x": 0, "y": -1, "z": 0}, dist, -1, "Ignore"],
        [V, V, "System.Single", "System.Int32", "UnityEngine.QueryTriggerInteraction, UnityEngine.PhysicsModule"])
def ground(x, z, top=40.0, depth=45.0):
    """y первой не-триггерной поверхности под (x, top, z), точность ~0.1 м"""
    if str(hit(x, top, z, depth)).lower() != "true": return None
    lo, hi = 0.0, depth
    while hi - lo > 0.1:
        m = (lo + hi) / 2
        if str(hit(x, top, z, m)).lower() == "true": hi = m
        else: lo = m
        time.sleep(0.05)
    return round(top - hi, 2)
