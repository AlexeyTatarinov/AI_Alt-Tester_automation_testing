# -*- coding: utf-8 -*-
"""Повтор маршрута CLI-прогона 12 (подход к Palm2 26 м, затем к BigRock2 (4)) с записью (t, x, y, z) каждого замера.
Использует goto() из suites/coll02.py без изменений. Результат: Reports/results/passive_coll02_trace.json"""
import json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "suites"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
import coll02
trace = []
T0 = time.time()
_orig = lib.wpos
def wpos_tr(n):
    p = _orig(n)
    if n == lib.PLAYER and p:
        trace.append((round(time.time() - T0, 1),) + tuple(round(v, 2) for v in p))
    return p
lib.wpos = wpos_tr
coll02.wpos = wpos_tr
lib.reset_input()
for tgt in [(-201.0, -399.5), (-166.0, -363.0)]:
    try:
        print("goto", tgt, coll02.goto(tgt, tol=0.7, max_s=200), flush=True)
    except Exception as e:
        print("ошибка", e)
json.dump(trace, open(os.path.join(lib.RESULTS_DIR, "passive_coll02_trace.json"), "w"))
ys = [t[2] for t in trace]
m = min(trace, key=lambda t: t[2])
print("замеров", len(trace), "мин y", m, "макс y", max(ys))
