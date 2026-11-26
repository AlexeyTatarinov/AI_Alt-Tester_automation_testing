# DTH-04n: 10 циклов смерти в FallCatcher_Lake с 3 ударами F (как DTH-04)
from g6 import *
R = {"cycles": []}
def dump(): jdump(os.path.join(R2, "b1.json"), R)
prestage("b1")
R["frameCount0"] = d.get_static_property("UnityEngine.Time", "frameCount", CORE); assert "MainMenu" in scenes()
guard.risky("b1"); print("frame", R["frameCount0"], "new_game", new_game(), flush=True)
wait_play_ready(); time.sleep(16); hyg_start("b1", R); R["off"] = off = log_mark()
try:
    print("goto", goto("Town_Market"), flush=True); time.sleep(2); wait_play_ready()
    EX = exits()
    def zone():
        o = d.find_object(By.NAME, "FallCatcher_Lake", enabled=False); return (o.worldX, o.worldY, o.worldZ)
    z = zone(); R["zone"] = z; R["zone_hits_exit"] = hits_exit(EX, z[0], z[2]); print("zone", z, R["zone_hits_exit"], flush=True); assert not R["zone_hits_exit"]
    for n in range(1, 11):
        z = zone(); lg = log_mark(); old = pig().id; r = {"n": n, "t": now()}
        autosync(True); teleport("T1", z[0], z[1] + 2.0, z[2]); t0 = time.time()
        for _ in range(3):
            try: key("F", 0.1)
            except Exception as e: r.setdefault("key_err", []).append(type(e).__name__)
            time.sleep(0.2)
        autosync(False)
        new = None
        while time.time() - t0 < 20:
            time.sleep(1.0)
            try:
                pl = pigs()
                if pl and pl[0].id != old and len(pl) == 1: new = round(time.time() - t0, 1); break
            except Exception: pass
        time.sleep(4.0)
        e = exc_summary(lg); storm_check(off, "dth")
        r.update(respawn_s=new, pos=[round(v, 1) for v in ppos()], hp=hp_now(), state=sname(gstate()), exc=e["total"], by_type=e["by_type"], log=log_since(lg)["samples"][:2])
        if e["total"] and "stack" not in R: R["stack"] = e["first_stacks"]
        R["cycles"].append(r); dump(); print(json.dumps(r, ensure_ascii=False), flush=True)
    R["cycles_with_nre"] = sum(1 for c in R["cycles"] if c["by_type"].get("NullReferenceException"))
    R["exc"] = exc_summary(off)
    print("NRE cycles", R["cycles_with_nre"], "of", len(R["cycles"]), R["exc"]["by_type"], R.get("stack"), flush=True)
finally:
    autosync(False); dump()
