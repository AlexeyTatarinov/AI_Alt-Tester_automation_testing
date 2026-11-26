# DTH-04n: 10 ударов врага (Klipper, Mountain_Cave), NRE на каждый удар
from g6 import *
R = {"hits": [], "tp": 0}
def dump(): jdump(os.path.join(R2, "b2.json"), R)
off = json.load(open(os.path.join(R2, "b1.json"), encoding="utf-8"))["off"]
prestage("b2"); hyg_tick(R, "b2")
try:
    try: print("goto", goto("Mountain_Cave"), flush=True)
    except Exception as e:
        print("ERR", type(e).__name__, str(e)[:100]); goto("Beach"); time.sleep(2); print("goto", goto("Mountain_Cave"))
    time.sleep(2); wait_play_ready(); EX = exits()
    def nearest():
        home = ppos()
        ks = sorted([c for c in d.find_objects(By.COMPONENT, "Critter", enabled=True) if "Klipper" in c.name], key=lambda c: dxz(home, (c.worldX, c.worldY, c.worldZ)))
        return ks[0], home
    def goto_k():
        c, home = nearest(); cp = cpos(c); vx, vz = home[0] - cp[0], home[2] - cp[2]; n = math.hypot(vx, vz) or 1
        x, z = cp[0] + vx / n * 1.3, cp[2] + vz / n * 1.3
        assert not hits_exit(EX, x, z), "точка в выходе"
        autosync(True); teleport("T1", x, cp[1] + 0.3, z); time.sleep(0.2); autosync(False); R["tp"] += 1; R["enemy"] = c.name
    goto_k()
    t0 = time.time(); last_hp = hp_now(); last_id = pig().id; mark = log_mark(); last_hit = time.time()
    while len(R["hits"]) < 10 and time.time() - t0 < 240:
        time.sleep(1.0)
        try: hp = hp_now(); pid = pig().id; dead = str(rd(pig(), "Damageable", "IsDead", 1))
        except Exception: continue
        if not isinstance(hp, int): continue
        storm_check(off, "hits")
        hit = hp < last_hp or dead == "True" or (hp > last_hp and pid == last_id)
        if hit:
            time.sleep(1.0)
            e = exc_summary(mark); mark = log_mark()
            kill = hp > last_hp or dead == "True"
            h = {"n": len(R["hits"]) + 1, "t": now(), "hp": [last_hp, hp], "death": kill, "exc": e["total"], "by_type": e["by_type"]}
            if e["total"] and "stack" not in R: R["stack"] = e["first_stacks"]
            R["hits"].append(h); dump(); print(h, flush=True); last_hit = time.time()
            if kill:
                t1 = time.time()
                while time.time() - t1 < 25:
                    time.sleep(1.0)
                    try:
                        if pig().id != last_id: break
                    except Exception: pass
                time.sleep(3); h["exc_respawn"] = exc_summary(mark)["total"]; mark = log_mark()
                goto_k(); hp = hp_now(); pid = pig().id; last_hit = time.time()
        elif time.time() - last_hit > 9:
            goto_k(); last_hit = time.time()
        last_hp, last_id = hp, pid
    R["n_hits"] = len(R["hits"]); R["hits_with_nre"] = sum(1 for h in R["hits"] if h["by_type"].get("NullReferenceException"))
    R["exc"] = exc_summary(off); R["end"] = {"state": sname(gstate()), "count": alert_count(), "hp": hp_now()}
    print("hits", R["n_hits"], "with NRE", R["hits_with_nre"], "exc total", R["exc"]["total"], R["end"], "tp", R["tp"], flush=True)
finally:
    autosync(False); dump()
