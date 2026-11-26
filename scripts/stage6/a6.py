# CMB-05, попытка 2: подход вплотную с полным HP, y читается во время движения
exec(open("a4.py", encoding="utf-8").read().split('prestage("a4")')[0].replace('"a4.json"', '"a6.json"'))
R["runs"] = []
def one(g):
    c = G(g["id"]); r = {"enemy": [g["name"], g["id"]], "samples": []}; R["runs"].append(r)
    autosync(True); near(c, 1.6); autosync(False); time.sleep(0.6)
    y0 = ppos()[1]; hp0 = hp_now(); r["y0"] = round(y0, 2); r["hp0"] = hp0
    def smp(tag):
        pp = ppos(); cp = cpos(c); s = {"tag": tag, "py": round(pp[1], 2), "dy": round(pp[1] - y0, 2), "ey": round(cp[1], 2), "dist": round(dxz(pp, cp), 2)}
        r["samples"].append(s); return s
    smp("база")
    for n in range(7):
        p = ppos(); k = choose_key(p, cpos(c))
        d.press_key(getattr(AltKeyCode, k), power=1, duration=0.5, wait=False)
        for i in range(3): smp("%s%d.%d" % (k, n, i)); time.sleep(0.12)
        time.sleep(0.2); s = smp("после %d" % n); h = hp_now(); r["samples"][-1]["hp"] = h; print(s, flush=True); dump()
        if h < 20 or s["dist"] > 6: break
    r["max_dy"] = max(s["dy"] for s in r["samples"]); r["min_dist"] = min(s["dist"] for s in r["samples"])
    close = [s["dy"] for s in r["samples"] if s["dist"] <= 1.0]; r["n_close"] = len(close); r["max_dy_close"] = max(close) if close else None
    r["n"] = len(r["samples"]); r["state"] = sname(gstate())
    print("RUN", {k: r[k] for k in r if k != "samples"}, flush=True)
    d.get_png_screenshot(os.path.join(R2, "shots", "a6_%s.png" % len(R["runs"])))
    autosync(True)
    far = ppos(); teleport("T1", 75.36 - 1.3, 1.9, -149.84); time.sleep(8)  # к Ayud: подальше от врагов
    print("after", hp_now(), sname(gstate()), alert_count(), [round(v, 2) for v in ppos()], flush=True)
prestage("a6"); hyg_tick(R, "a6"); autosync(True)
try:
    EX = exits()
    teleport("T1", 74.06, 1.9, -149.84); time.sleep(6)
    live = [g for g in glue() if g["active"]]; print([(g["name"], g["pos"]) for g in live], "hp", hp_now(), sname(gstate()), flush=True)
    for g in live[:2]:
        one(g)
finally:
    autosync(False)
    R["end"] = {"state": sname(gstate()), "count": alert_count(), "hp": hp_now()}
    R["exc"] = exc_summary(off); dump(); print("end", R["end"], "exc", R["exc"]["total"], R["exc"]["by_type"], flush=True)
