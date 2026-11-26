from probe import *
from ray import ground
off = json.load(open(os.path.join(R2, "b1.json"), encoding="utf-8"))["off"]
R = {}
def wait_scene(want, s=25):
    t0 = time.time()
    while time.time() - t0 < s:
        time.sleep(1.0)
        try:
            if want in scenes() and pig() and len(scenes()) <= 3: return round(time.time() - t0, 1)
        except Exception: pass
    return None
autosync(True)
try:
    assert "Town_Upper" in scenes()
    lg = log_mark()
    R["slope_before"] = {"scenes": scene_now(), "pig": ppos()}
    teleport("T1", 5.27, 21.9, 52.95)
    R["slope_s"] = wait_scene("Town_Inner"); time.sleep(3); wait_play_ready()
    R["slope_after"] = st_now("Slope после", pos=[round(v, 2) for v in ppos()]); R["slope_log"] = log_since(lg)
    print("slope", R["slope_s"], R["slope_log"], flush=True)
    jdump(os.path.join(R2, "b9.json"), R)
    # ToForest: только чтение
    o = d.find_object(By.NAME, "LocationExit_ToForest", enabled=False)
    F = R["forest"] = {"pos": [o.worldX, o.worldY, o.worldZ]}
    for p in ("bounds.min", "bounds.max", "center", "size"):
        v = rd(o, "UnityEngine.BoxCollider", p, 2, PHYS); F[p] = [round(v[a], 2) for a in "xyz"] if isinstance(v, dict) else str(v)[:80]
    F["euler_y"] = rd(o, "UnityEngine.Transform", "eulerAngles.y", 2, CORE); F["scale"] = str(rd(o, "UnityEngine.Transform", "lossyScale", 2, CORE))[:80]
    F["others"] = [(e.name, [round(e.worldX, 2), round(e.worldY, 2), round(e.worldZ, 2)]) for e in d.find_objects(By.COMPONENT, "LocationExit", enabled=False)]
    cx, cz = (F["bounds.min"][0] + F["bounds.max"][0]) / 2, (F["bounds.min"][2] + F["bounds.max"][2]) / 2
    F["center_world"] = [round(cx, 2), round((F["bounds.min"][1] + F["bounds.max"][1]) / 2, 2), round(cz, 2)]
    F["ground"] = {}
    for dx in (-3, -1.5, 0, 1.5, 3, 5, 8):
        for dz in (-2, 0, 2):
            F["ground"]["%+.1f,%+d" % (dx, dz)] = [ground(cx + dx, cz + dz), ground(cx + dx, cz + dz, F["bounds.max"][1], 30)]
    print(json.dumps(F, ensure_ascii=False), flush=True)
finally:
    autosync(False); jdump(os.path.join(R2, "b9.json"), R)
