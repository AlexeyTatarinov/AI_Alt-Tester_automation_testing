from s2lib import *
R = {}
autosync(True)
try:
    off = log_mark(); R["off"] = off
    s0 = snap("IT-02 до", off); R["snap_before"] = s0; print(json.dumps(s0, ensure_ascii=False))
    guard.risky("p1 back to menu")
    R["to_menu_s"] = to_menu(); print("to_menu", R["to_menu_s"], flush=True)
    for _ in range(20):
        time.sleep(1.5)
        if "MainMenu" in scenes() and d.find_objects(By.NAME, "Button New Game", enabled=False): break
    time.sleep(1); guard.restore_window("p1 ng")
    R["new_game_s"] = new_game(); print("new_game", R["new_game_s"], flush=True)
    for _ in range(20):
        time.sleep(1.5)
        try: ppos(); break
        except Exception: pass
    time.sleep(3)
    s1 = snap("после New Game", off); R["snap_after_ng"] = s1; print(json.dumps(s1, ensure_ascii=False))
    ok = False
    for dist in (1.3, 1.0, 0.8):
        tp_hare(dist)
        for i in range(5):
            if hint(): ok = True; break
            step_towards(HARE, 0.2); time.sleep(0.4)
        if ok: break
    R["hint"] = ok; print("hint", ok, flush=True)
    key("E", 0.1); time.sleep(1.2); R["dlg_open"] = dlg()
    n = 0; seq = []
    while n < 45 and (dlg() or n == 0):
        key("Space", 0.1); n += 1; time.sleep(1.0); l = line()
        if l and (not seq or seq[-1] != l): seq.append(l)
        if choices(): R["choices"] = True; break
    time.sleep(2.5)
    R["N_space"] = n; R["closed"] = not dlg(); R["seq"] = seq; R["replies"] = len(seq)
    s2 = snap("IT-02 после", off); R["snap_after"] = s2; R["diff"] = diff(s0, s2); R["exc_detail"] = exc_summary(off)
    R["state_after"] = sname(gstate())
    print("N", n, "closed", R["closed"], "replies", len(seq), seq[:3], seq[-2:]); print("AFTER", json.dumps(s2, ensure_ascii=False)); print("EXC", json.dumps(R["exc_detail"], ensure_ascii=False)[:2500])
    jdump(os.path.join(R2, "p1_e.json"), R)
finally:
    autosync(False)
