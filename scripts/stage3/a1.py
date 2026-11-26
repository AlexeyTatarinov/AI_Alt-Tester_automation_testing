# -*- coding: utf-8 -*-
from s3lib import *
R = {}
def dump(): jdump(os.path.join(R2, "a1.json"), R)
prestage("a1")
R["frameCount0"] = d.get_static_property("UnityEngine.Time", "frameCount", CORE)
SKIP = "MainMenu" not in scenes()
R["resumed_after_script_error"] = SKIP
autosync(True)
try:
    guard.risky("a1")
    if not SKIP: print("new_game", new_game(), now(), flush=True)
    for _ in range(20):
        time.sleep(1.5)
        try: ppos(); break
        except Exception: pass
    time.sleep(2)
    for _ in range(30):
        if gstate() == 0: break
        time.sleep(1)
    off = log_mark(); R["off"] = off
    s0 = full_snap("A старт", off); R["snap_start"] = s0; print(json.dumps(s0, ensure_ascii=False), flush=True)
    R["hint1"] = to_hare(); print("hint", R["hint1"], flush=True)
    key("E", 0.1); time.sleep(1.0); assert dlg(), "не открылся"
    R["first"] = talk_first()
    s1 = full_snap("A после первого", off); R["snap_after_first"] = s1; R["diff_first"] = diff(s0, s1); R["save_info_first"] = save_info()
    print("FIRST", {k: v for k, v in R["first"].items() if k != "seq"}, R["diff_first"], flush=True); dump()
    # Back to menu -> Continue
    guard.risky("a1 back to menu")
    R["to_menu_s"] = to_menu(); print("to_menu", R["to_menu_s"], flush=True)
    for _ in range(20):
        time.sleep(1.5)
        if "MainMenu" in scenes() and d.find_objects(By.NAME, "Button Continue", enabled=False): break
    time.sleep(1); guard.restore_window("a1 continue")
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
    R["load_s"] = found; assert found
    time.sleep(3)
    for _ in range(20):
        try: ppos(); break
        except Exception: time.sleep(1.5)
    for _ in range(30):
        if gstate() == 0: break
        time.sleep(1)
    sa = full_snap("A после Continue", off); R["snap_after_load"] = sa; R["diff_load"] = diff(s1, sa); R["save_after_load"] = save_info()
    print("DIFF load", R["diff_load"], flush=True); dump()
    R["step2"] = conv_yes(off, "A2"); r = R["step2"]
    print("STEP2", r["first_line"], r["replies"], r["closed"], r["diff"], flush=True)
    R["exc"] = exc_summary(off); R["save_final"] = save_info(); dump()
    print("exc", R["exc"]["total"], R["exc"]["by_type"], flush=True)
    for k, v in R["exc"]["first_stacks"].items(): print(k, v[:5])
finally:
    autosync(False); dump()
