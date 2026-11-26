from s3blib import *
R = {}
def v(o, comp, p, asm):
    r = rd(o, comp, p, 2, asm)
    return [r[a] for a in "xyz"] if isinstance(r, dict) else None
for o in d.find_objects(By.COMPONENT, "LocationExit", enabled=False):
    if not (o.name.endswith("Slope") or "InnerTown_FallDown" in o.name or "ForestEntrance" in o.name or "ToMarket_FallDown" in o.name): continue
    e = {"pos": [o.worldX, o.worldY, o.worldZ], "euler": v(o, "UnityEngine.Transform", "eulerAngles", CORE), "scale": v(o, "UnityEngine.Transform", "lossyScale", CORE),
         "c": v(o, "UnityEngine.BoxCollider", "center", PHYS), "s": v(o, "UnityEngine.BoxCollider", "size", PHYS),
         "comps": [c["componentName"] for c in o.get_all_components() if "Collider" in c["componentName"]]}
    R[o.name] = e
def inside(e, x, z, margin):
    t = math.radians(e["euler"][1]); dx, dz = x - e["pos"][0], z - e["pos"][2]
    lx = dx * math.cos(t) - dz * math.sin(t); lz = dx * math.sin(t) + dz * math.cos(t)
    lx -= e["c"][0] * e["scale"][0]; lz -= e["c"][2] * e["scale"][2]
    gx = abs(lx) - abs(e["s"][0] * e["scale"][0]) / 2; gz = abs(lz) - abs(e["s"][2] * e["scale"][2]) / 2
    return {"gap_x": round(gx, 2), "gap_z": round(gz, 2), "overlaps_xz": gx < margin and gz < margin}
for name, e in R.items():
    e["center_point"] = inside(e, 5.27, 52.95, 0.3); e["probe_point_4.35_50.62"] = inside(e, 4.35, 50.62, 0.3)
    print(name, [round(a, 1) for a in e["euler"]], e["comps"], "center", e["center_point"], "probe", e["probe_point_4.35_50.62"], flush=True)
jdump(os.path.join(R2, "b8.json"), R)
