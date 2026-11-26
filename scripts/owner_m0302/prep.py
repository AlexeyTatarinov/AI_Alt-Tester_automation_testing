# -*- coding: utf-8 -*-
# Сцена для ручной проверки владельца (M03-02): New Game -> Mountain_Cave -> тревога -> пешком в выход. Tab НЕ нажимать, игру оставить.
from s3blib import *
R = {}
CENTER = (104.76, 24.08, 76.9); POINT = (104.76, 22.4, 76.9 + 6.986 / 2 + 3.0)
def dump(): jdump(os.path.join(R2, "prep.json"), R)
prestage("prep")
assert "MainMenu" in scenes()
try:
    hyg_start("menu", R); guard.risky("prep")
    new_game(); wait_play_ready(); hyg_start("after_ng", R)
    R["off"] = off = log_mark()
    R["start_raw"] = st_now("после New Game")
    if R["start_raw"]["count"]:
        first("UIManager").call_component_method("UIManager", "_gameStateManager._alertEnemies.Clear", ASM, [], [])
    R["start"] = st_now("после очистки"); assert R["start"]["count"] == 0, "список не очистился"
    print("goto", goto("Mountain_Cave"), flush=True); time.sleep(2); wait_play_ready()
    R["arrive"] = st_now("Mountain_Cave")
    autosync(True); teleport("T1", *POINT); time.sleep(1.5); autosync(False)
    for i in range(5):
        R["alert"] = st_now("у выхода %d" % i)
        if R["alert"]["state"] == "Combat" and R["alert"]["count"]: break
        time.sleep(1.0)
    assert R["alert"]["state"] == "Combat", "нет тревоги, в выход не вхожу"
    t0 = time.time()
    while time.time() - t0 < 40 and "Mountain_Cave" in scenes():
        R["last_before"] = st_now("иду")
        if R["last_before"]["state"] != "Combat": raise AssertionError("тревога пропала до выхода")
        p0 = ppos()
        for k in range(2):
            if "Mountain_Cave" not in scenes(): break
            try: step_towards((CENTER[0], p0[1], CENTER[2]), 0.1)
            except AttributeError: break
        storm_check(off, "walk")
    t0 = time.time()
    while time.time() - t0 < 30:
        try:
            if "Mountain_Path" in scenes() and pig(): break
        except Exception: pass
        time.sleep(1.0)
    time.sleep(15)
    R["after"] = st_now("через 15 с после перехода", critters=len(d.find_objects(By.COMPONENT, "Critter", enabled=True)))
    d.get_png_screenshot(os.path.join(R2, "shots", "prep_after.png"))
    R["exc"] = exc_summary(off)["total"]; print("exc", R["exc"])
finally:
    autosync(False); dump()
