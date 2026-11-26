from probe import *
off = json.load(open(os.path.join(R2, "b1.json"), encoding="utf-8"))["off"]
R = {}
autosync(True)
try:
    assert "Town_Inner" in scenes()
    lg = log_mark(); teleport("T1", -21.89, 10.3, 25.0); t0 = time.time()
    R["s"] = None
    while time.time() - t0 < 25:
        time.sleep(1.0)
        try:
            if "Forest" in scenes() and pig() and len(scenes()) <= 3: R["s"] = round(time.time() - t0, 1); break
        except Exception: pass
    time.sleep(3); wait_play_ready()
    R["after"] = st_now("ToForest после", pos=[round(v, 2) for v in ppos()]); R["log"] = log_since(lg)
    R["entr"] = [(e.name, [round(e.worldX, 2), round(e.worldY, 2), round(e.worldZ, 2)], str(rd(e, "LocationEntrance", "_entrancePath.name", 1))) for e in d.find_objects(By.COMPONENT, "LocationEntrance", enabled=False)]
    R["exc"] = exc_summary(off)["total"]
    print(json.dumps(R, ensure_ascii=False), flush=True)
finally:
    autosync(False); jdump(os.path.join(R2, "b10.json"), R)
