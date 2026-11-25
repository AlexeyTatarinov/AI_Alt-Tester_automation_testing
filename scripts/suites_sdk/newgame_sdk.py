# -*- coding: utf-8 -*-
"""New Game через SDK (порт шага MENU-02): клик, подтверждение, ожидание Beach и игрока. Пишет state_run<N>.json.
Запуск: .venv python TestAI/suites/newgame_sdk.py <N>"""
import json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import lib_sdk  # noqa
from lib import *  # noqa

run = run_no_from_argv()
t0 = time.time()
lib_sdk.tap_by_name("Button New Game")
for _ in range(10):
    time.sleep(0.4)
    if find("PopupButton - 1"):
        lib_sdk.tap_by_name("PopupButton - 1")
        break
seen, pos = {}, None
while time.time() - t0 < 90:
    sc = scenes()
    for n in ("PersistentManagers", "Gameplay", "Beach"):
        if n in sc and n not in seen:
            seen[n] = round(time.time() - t0, 1)
    if "Beach" in sc:
        pos = player_pos()
        if pos:
            break
    time.sleep(0.3)
dt = round(time.time() - t0, 1)
print("New Game (SDK): игрок найден через %s с, сцены %s, позиция %s" % (dt, seen, pos))
json.dump({"run": run, "load_s": dt, "scene_times": seen, "spawn_pos": pos, "t_found": time.time()}, open(os.path.join(RESULTS_DIR, "state_run%d.json" % run), "w"), indent=1)
