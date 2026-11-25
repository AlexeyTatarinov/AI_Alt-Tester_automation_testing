# -*- coding: utf-8 -*-
"""Только запуск Play (Ctrl+P), если Play остановлен. Используется, когда restart_play вернул код 4."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import restart_play as r
w = r.unity_windows(); h = int(w[0][1])
if r.game_alive(4): print("игра уже подключена, ничего не делаю"); sys.exit(0)
fst = r.snapshot_focus(h)
if not r.focus(h): r.give_back(h, fst); print("окно не стало активным"); sys.exit(4)
r.ctrl_p(); print("Ctrl+P отправлен", r.now(), flush=True); time.sleep(1.0); r.give_back(h, fst)
t0 = time.time()
while time.time() - t0 < 120:
    time.sleep(2)
    try:
        d = r.driver(timeout=8); a = r.snapshot(d); print("после", a, flush=True)
        if "MainMenu" in a["scenes"]:
            time.sleep(2.0); r.give_back(h, fst); sys.exit(0)
    except Exception: pass
sys.exit(3)
