# -*- coding: utf-8 -*-
from s2blib import *
R = {}
def dump(): jdump(os.path.join(R2, "p2_c.json"), R)
def to_hare():
    for dist in (1.3, 1.0, 0.8):
        tp_hare(dist)
        for i in range(6):
            if hint(): return True
            step_towards(HARE, 0.2); time.sleep(0.4)
    return False
autosync(True)
try:
    off = log_mark(); R["off"] = off
    sb = snap("перед Back to menu", off); R["snap_before"] = sb; R["save_before"] = save_info(); print(json.dumps(sb, ensure_ascii=False), flush=True)
    guard.risky("p2 back to menu")
    R["to_menu_s"] = to_menu(); print("to_menu", R["to_menu_s"], flush=True)
    for _ in range(20):
        time.sleep(1.5)
        if "MainMenu" in scenes() and d.find_objects(By.NAME, "Button Continue", enabled=False): break
    time.sleep(1); guard.restore_window("p2 continue")
    R["save_in_menu"] = save_info()
    t0 = time.time(); d.find_object(By.NAME, "Button Continue", enabled=False).click()
    for _ in range(10):
        time.sleep(0.4)
        try: d.find_object(By.NAME, "PopupButton - 1", enabled=False).click(); R["popup_clicked"] = True; break
        except Exception: pass
    found = None
    while time.time() - t0 < 60:
        try:
            if "Beach" in scenes() and pig(): found = round(time.time() - t0, 1); break
        except Exception: pass
        time.sleep(0.3)
    R["load_s"] = found; print("continue loaded", found, scenes(), flush=True)
    assert found, "не загрузилась"
    time.sleep(3)
    for _ in range(20):
        try: ppos(); break
        except Exception: time.sleep(1.5)
    sa = snap("после Continue", off); R["snap_after_load"] = sa; R["save_after_load"] = save_info(); R["diff_load"] = diff(sb, sa)
    print("AFTER LOAD", json.dumps(sa, ensure_ascii=False), flush=True); print("DIFF", R["diff_load"], flush=True); dump()
    R["hint"] = to_hare(); print("hint", R["hint"], flush=True)
    off2 = log_mark(); key("E", 0.1); time.sleep(1.0); R["open"] = dlg(); R["first_line"] = line(); assert dlg()
    n = 0; seq = []
    while n < 45:
        key("Space", 0.1); n += 1; time.sleep(1.0)
        l = line()
        if l and (not seq or seq[-1] != l): seq.append(l)
        if choices() or not dlg(): break
    time.sleep(2)
    R["conv"] = {"N": n, "replies": len(seq), "closed": not dlg(), "choices": choices(), "seq": seq}
    if choices(): R["conv"]["texts"] = [o.get_text() for o in d.find_objects(By.NAME, "TextChoice", enabled=True)]
    sc = snap("после разговора (Continue)", off); R["snap_after_conv"] = sc; R["exc"] = exc_summary(off); R["save_after_conv"] = save_info(); R["state_after"] = sname(gstate())
    print("CONV", {k: v for k, v in R["conv"].items() if k != "seq"}, flush=True)
    for s in seq: print("  -", s[:100])
    print("quest", sc["quest"], "inv", sc["inv"], "exc", R["exc"]["total"], R["exc"]["by_type"], flush=True)
    for k, v in R["exc"]["first_stacks"].items(): print(k, v[:5])
finally:
    autosync(False); dump()
