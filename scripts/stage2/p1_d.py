from s2lib import *
R = {}
autosync(True)
try:
    off = log_mark(); R["off"] = off
    s0 = snap("IT-12 до", off); R["snap_before"] = s0; print(json.dumps(s0, ensure_ascii=False))
    ok = False
    for dist in (1.3, 1.0, 0.8, 1.6):
        tp_hare(dist)
        for i in range(5):
            if hint(): ok = True; break
            step_towards(HARE, 0.2); time.sleep(0.4)
        if ok: break
    R["hint"] = ok; R["dist"] = round(dxz(ppos(), HARE), 2); print("hint", ok, R["dist"], flush=True)
    assert ok
    key("E", 0.1); time.sleep(1.2); assert dlg(), "диалог не открылся"
    n = 0; seq = []
    while n < 25:
        l = line()
        if l and (not seq or seq[-1] != l): seq.append(l)
        key("Space", 0.1); n += 1; time.sleep(1.0)
        if choices(): R["choices"] = True; break
        if not dlg(): break
    time.sleep(2.0)
    R["N_space"] = n; R["closed"] = not dlg(); R["seq"] = seq
    s2 = snap("IT-12 после", off); R["snap_after"] = s2; R["diff"] = diff(s0, s2)
    R["save_info"] = save_info()
    g = first("GameManager"); R["next_step_name"] = rd(g, "GameManager", "_questManager._currentStep.name")
    R["exc_detail"] = exc_summary(off)
    print("N", n, "closed", not dlg(), seq); print("AFTER", json.dumps(s2, ensure_ascii=False)); print("DIFF", json.dumps(R["diff"], ensure_ascii=False)); print("next step", R["next_step_name"])
    jdump(os.path.join(R2, "p1_d.json"), R)
finally:
    autosync(False)
