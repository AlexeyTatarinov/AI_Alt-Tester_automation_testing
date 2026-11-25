# -*- coding: utf-8 -*-
"""Остановить Play клавишей Ctrl+P (когда игра на паузе или не отвечает AltTester). Потом start_play.py."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import restart_play as r
w = r.unity_windows(); h = int(w[0][1]); fst = r.snapshot_focus(h)
if r.game_alive(4): print("игра отвечает, используйте restart_play.py"); sys.exit(2)
if not r.focus(h): r.give_back(h, fst); print("окно не стало активным"); sys.exit(4)
r.ctrl_p(); print("Ctrl+P (Stop) отправлен", r.now(), flush=True); time.sleep(5); r.give_back(h, fst)
