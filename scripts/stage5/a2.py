# -*- coding: utf-8 -*-
# 1.3 REG-90-a: 3x (пауза -> Back to menu -> New Game), затем разговор 1 и разговор 2 (Yes)
from s3blib import *
R = {"loops": []}
def dump(): jdump(os.path.join(R2, "a2.json"), R)
off = json.load(open(os.path.join(R2, "a1.json"), encoding="utf-8"))["off"]
prestage("a2"); hyg_tick(R, "a2")
def menu_loop(i):
    r = {"i": i, "before": full_snap("loop%d до" % i, off)}
    guard.risky("loop"); r["to_menu_s"] = to_menu()
    for _ in range(20):
        time.sleep(1.5)
        if "MainMenu" in scenes() and d.find_objects(By.NAME, "Button New Game", enabled=False): break
    time.sleep(1.5); guard.restore_window("loop%d" % i)
    r["new_game_s"] = new_game(); wait_play_ready(); time.sleep(16)  # интро 15 с
    r["after"] = full_snap("loop%d после" % i, off); r["q"] = qdetail()
    R["loops"].append(r); print("loop", i, r["to_menu_s"], r["new_game_s"], r["after"]["state"], r["after"]["inv"], r["after"]["save_finished"], r["after"].get("exc"), r["q"], flush=True); dump()
    storm_check(off, "loop%d" % i)
try:
    autosync(True)
    for i in (1, 2, 3): menu_loop(i)
    for k in (1, 2):
        r = converse(off, "talk%d" % k); R["talk%d" % k] = r; R["exc_after_talk%d" % k] = exc_summary(off); dump()
        print("talk", k, json.dumps(brief(r), ensure_ascii=False, default=str), flush=True)
        print("exc", R["exc_after_talk%d" % k]["total"], R["exc_after_talk%d" % k]["by_type"], flush=True)
        d.get_png_screenshot(os.path.join(R2, "shots", "a2_talk%d.png" % k))
        if not r.get("closed"): R["stopped"] = "диалог %d не закрылся" % k; break
except Storm as e:
    R["storm"] = str(e); print("STORM", e, flush=True); to_menu()
finally:
    autosync(False); R["exc"] = exc_summary(off); R["save"] = save_info(); dump()
