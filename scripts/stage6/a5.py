# P04: ENM попытка 2 (читать GetHit после каждого удара), затем CMB-05 (#426)
exec(open("a4.py", encoding="utf-8").read().split('prestage("a4")')[0].replace('"a4.json"', '"a5.json"'))
R.update({"enm2": [], "cmb": []})
def aim(c): step_towards(cpos(c), 0.08)
prestage("a5"); hyg_tick(R, "a5"); autosync(True)
try:
    EX = exits(); live = [g for g in glue() if g["active"]]; R["live"] = live; print([(g["name"], g["pos"]) for g in live], flush=True)
    t = live[1]; c = G(t["id"]); R["target"] = t
    for p in ("_healthConfigSO.InitialHealth", "_currentHealthSO.CurrentHealth", "_currentHealthSO.MaxHealth", "GetHit", "IsDead", "DroppableRewardConfig.name", "enabled"):
        R["dmg." + p] = str(prop(c, "Damageable", p))[:80]
    print({k: v for k, v in R.items() if k.startswith("dmg.")}, flush=True)
    R["items_before"] = [str(i) for i in collectables()]
    near(c, 1.1); time.sleep(0.5); aim(c)
    for n in range(1, 11):
        try:
            if dxz(ppos(), cpos(c)) > 1.5: near(c, 1.0); time.sleep(0.3)
            aim(c); key("F", 0.1)
            flags = []
            for i in range(3):
                flags.append((prop(c, "Damageable", "GetHit"), prop(c, "Damageable", "IsDead"))); time.sleep(0.15)
            e = {"n": n, "flags": flags, "hp": hp_now(), "dist": round(dxz(ppos(), cpos(c)), 2), "py": round(ppos()[1], 2), "ey": round(cpos(c)[1], 2), "state": sname(gstate())}
        except Exception as ex: e = {"n": n, "err": type(ex).__name__ + ": " + str(ex)[:100]}
        R["enm2"].append(e); dump(); print(e, flush=True); storm_check(off, "enm2")
        if any(f[1] is True for f in e.get("flags", [])) or "err" in e: break
        if n == 5: d.get_png_screenshot(os.path.join(R2, "shots", "a5_hit.png"))
        time.sleep(0.5)
    time.sleep(4)
    R["present"] = G(t["id"]) is not None
    R["new_items"] = [(v[2], v[1]) for i, v in collectables().items() if str(i) not in R["items_before"]]
    print("present", R["present"], "new", R["new_items"], flush=True); dump()
    # CMB-05
    time.sleep(2)
    live = [g for g in glue() if g["active"]]
    c = G(live[-1]["id"]) if live[-1]["id"] != t["id"] else G(live[0]["id"]); R["cmb_target"] = [c.name, c.id]
    near(c, 2.0); autosync(False); time.sleep(0.7)
    y0 = ppos()[1]; R["cmb_y0"] = round(y0, 2)
    def smp(tag):
        pp = ppos(); cp = cpos(c); s = {"tag": tag, "t": now(), "py": round(pp[1], 2), "dy": round(pp[1] - y0, 2), "ey": round(cp[1], 2), "dist": round(dxz(pp, cp), 2), "hp": hp_now(), "pos": [round(pp[0], 2), round(pp[2], 2)]}
        R["cmb"].append(s); print(s, flush=True)
    smp("база")
    for n in range(12):
        step_towards(cpos(c), 0.2); smp("шаг %d" % n); time.sleep(0.4); smp("после %d" % n)
        if hp_now() <= 20: break
    d.get_png_screenshot(os.path.join(R2, "shots", "a5_cmb.png"))
    R["cmb_max_dy"] = max(s["dy"] for s in R["cmb"]); R["cmb_min_dist"] = min(s["dist"] for s in R["cmb"])
    print("CMB", R["cmb_y0"], "max dy", R["cmb_max_dy"], "min dist", R["cmb_min_dist"], flush=True)
finally:
    autosync(False)
    R["exc"] = exc_summary(off); dump(); print("exc", R["exc"]["total"], R["exc"]["by_type"], flush=True)
