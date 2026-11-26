# IT-06 смерть от Klipper
from s3blib import *
R = {"trace": []}
off = json.load(open(os.path.join(R2, "b1.json"), encoding="utf-8"))["off"]
def dump(): jdump(os.path.join(R2, "b14.json"), R)
def hearts():
    out = []
    for h in d.find_objects(By.COMPONENT, "UIHeartDisplay", enabled=False):
        out.append((h.name, rd(h, "UIHeartDisplay", "_slidingImage.fillAmount", 1)))
    return out
def hud():
    u = first("UIHealthBarManager")
    return {"hearts": hearts(), "so_cur": rd(u, "UIHealthBarManager", "_protagonistHealth.CurrentHealth", 1), "so_max": rd(u, "UIHealthBarManager", "_protagonistHealth.MaxHealth", 1), "bars_active": len(d.find_objects(By.COMPONENT, "UIHeartDisplay", enabled=True))}
def S(label):
    r = {"label": label, "t": now(), "scenes": scene_now(), "count": alert_count(), "state": sname(gstate())}
    pl = pigs(); r["pigs"] = [(o.id, [round(o.worldX, 2), round(o.worldY, 2), round(o.worldZ, 2)]) for o in pl]
    if pl:
        r["hp"] = hp_now(); r["isDead"] = str(rd(pl[0], "Damageable", "IsDead", 1)); r["cam_d"] = round(dist3(cam_pos(), (pl[0].worldX, pl[0].worldY, pl[0].worldZ)), 2)
    R["trace"].append(r); print(json.dumps(r, ensure_ascii=False), flush=True); return r
hyg_tick(R, "b14"); prestage("b14")
if cheat_open(): key("C", 0.1); time.sleep(1)
if pause_open(): key("Escape", 0.1); time.sleep(1.5)
if "Mountain_Cave" not in scenes():
    try: print("goto", goto("Mountain_Cave"), flush=True)
    except Exception as e:
        print("ERR", e); goto("Town_Market"); time.sleep(2); print("goto", goto("Mountain_Cave"))
time.sleep(2); wait_play_ready(); autosync(True)
try:
    home = ppos(); R["before"] = S("прибытие"); R["hud_before"] = hud(); print(R["hud_before"], flush=True)
    id0 = R["before"]["pigs"][0][0]; lg = log_mark()
    ks = sorted([c for c in d.find_objects(By.COMPONENT, "Critter", enabled=True) if "Klipper" in c.name], key=lambda c: dxz(home, (c.worldX, c.worldY, c.worldZ)))
    c = ks[0]; R["klipper"] = [c.name, c.id]
    def goto_k():
        cp = cpos(c); vx, vz = home[0] - cp[0], home[2] - cp[2]; n = math.hypot(vx, vz) or 1
        teleport("T1", cp[0] + vx / n * 1.3, cp[1] + 0.3, cp[2] + vz / n * 1.3)
    goto_k(); autosync(False)
    t0 = time.time(); last_hp = 50; last_hit = t0; died = None; R["tp_count"] = 1; seen_low = 50; hud_mid = None
    while time.time() - t0 < 90:
        time.sleep(0.9)
        r = S("бой %.1f" % (time.time() - t0)); storm_check(off, "death")
        hp = r.get("hp")
        if r["pigs"] and r["pigs"][0][0] != id0 or r.get("isDead") == "True" or not r["pigs"] or (isinstance(hp, int) and hp > last_hp): died = round(time.time() - t0, 1); break
        if isinstance(hp, int) and hp < last_hp:
            last_hp = hp; last_hit = time.time()
            if hud_mid is None: hud_mid = R["hud_mid"] = hud(); R["hud_mid_hp"] = hp; print("HUD mid", hp, hud_mid, flush=True)
        if time.time() - last_hit > 10:
            autosync(True); goto_k(); autosync(False); R["tp_count"] += 1; last_hit = time.time()
    R["died_s"] = died; R["last_hp_seen"] = last_hp; d.get_png_screenshot(os.path.join(R2, "shots", "b14_death.png")); dump()
    if died is not None:
        t1 = time.time(); resp = None
        while time.time() - t1 < 40:
            time.sleep(1.0)
            try:
                r = S("после смерти %.1f" % (time.time() - t1))
            except Exception as e: print("ERR", type(e).__name__); continue
            if r["pigs"] and r["pigs"][0][0] != id0: resp = round(time.time() - t1, 1); break
        R["respawn_s"] = resp
        time.sleep(2); R["d2"] = S("респавн +2"); R["hud_after2"] = hud(); time.sleep(3); R["d5"] = S("респавн +5"); R["hud_after5"] = hud()
        print(R["hud_after5"], flush=True); d.get_png_screenshot(os.path.join(R2, "shots", "b14_respawn.png"))
        key("Tab", 0.1); time.sleep(1.5); R["tab_opens"] = inv(); R["state_tab"] = sname(gstate())
        if R["tab_opens"]: key("Tab", 0.1); time.sleep(1.5)
        p0 = ppos(); key("W", 0.3); time.sleep(1.0); R["w_moved"] = round(dxz(p0, ppos()), 2)
        R["end"] = S("конец")
    R["log"] = log_since(lg); R["exc"] = exc_summary(off); print("died", died, "resp", R.get("respawn_s"), "tab", R.get("tab_opens"), "w", R.get("w_moved"), R["log"], R["exc"]["total"], R["exc"]["by_type"], flush=True)
finally:
    autosync(False); dump()
