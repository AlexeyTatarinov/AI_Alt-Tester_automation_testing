# -*- coding: utf-8 -*-
# 4.3.5 Back to menu -> Continue
from s3blib import *
R = {}
def dump(): jdump(os.path.join(R2, "b8.json"), R)
off = json.load(open(os.path.join(R2, "b1.json"), encoding="utf-8"))["off"]
prestage("b8"); hyg_tick(R, "b8"); autosync(True)
try:
    R["before"] = full_snap("до Back to menu", off); R["q_before"] = qdetail(); R["save_before"] = save_items(); R["hp_before"] = hp_now()
    print("BEFORE", R["before"], R["save_before"], R["hp_before"], flush=True)
    guard.risky("b8 back to menu"); R["to_menu_s"] = to_menu()
    for _ in range(20):
        time.sleep(1.5)
        if "MainMenu" in scenes() and d.find_objects(By.NAME, "Button Continue", enabled=False): break
    time.sleep(1); guard.restore_window("b8 continue")
    R["save_in_menu"] = save_items(); R["exc_menu"] = exc_summary(off)["total"]
    off2 = log_mark(); R["off_after_continue"] = off2
    t0 = time.time(); d.find_object(By.NAME, "Button Continue", enabled=False).click()
    for _ in range(10):
        time.sleep(0.4)
        try: d.find_object(By.NAME, "PopupButton - 1", enabled=False).click(); R["popup"] = True; break
        except Exception: pass
    found = None
    while time.time() - t0 < 60:
        try:
            if locs() and "MainMenu" not in scenes() and pig(): found = round(time.time() - t0, 1); break
        except Exception: pass
        time.sleep(1.0)
    R["load_s"] = found; assert found, "Continue не загрузился"
    time.sleep(3); wait_play_ready()
    R["after"] = full_snap("после Continue", off); R["q_after"] = qdetail(); R["save_after"] = save_items(); R["hp_after"] = hp_now()
    print("AFTER", R["after"], R["save_after"], R["hp_after"], R["q_after"], flush=True)
    R["inv_equals_save"] = R["after"]["inv"] == R["save_after"]["inv"]
    key("Tab", 0.1); time.sleep(1.5); R["tab_opens"] = inv(); R["state_in_tab"] = sname(gstate())
    if inv(): key("Tab", 0.1); time.sleep(1.5)
    R["exc_after_load"] = exc_summary(off2); R["exc_total"] = exc_summary(off)
    print("inv==save", R["inv_equals_save"], "tab", R["tab_opens"], "load", found, "exc", R["exc_total"]["total"], flush=True)
finally:
    autosync(False); dump()
