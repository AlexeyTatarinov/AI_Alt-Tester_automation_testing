# -*- coding: utf-8 -*-
"""[SDK-версия move.py, CLI-вызовы заменены адаптером lib_sdk.py; запуск: scripts\sdk_smoke\.venv\Scripts\python]
Набор MOVE (audit-and-testcases-2026-11-19.md, раздел 4.1).

Предусловие P1: Beach загружен, игрок на стартовом острове (после suites/menu.py).
Запуск:  python TestAI/suites/move.py <номер прогона>
Направления считаются относительно камеры: вперёд = от Main Camera к игроку в плоскости XZ.
Игровое время во время MOVE-04 и MOVE-05 замедляется; в finally всегда возвращается 1 и вызывается reset-input.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import lib_sdk  # noqa: F401 (подменяет примитивы lib на вызовы SDK)
from lib import *  # noqa

MIN_DISP, MAX_ANGLE = 0.5, 15.0
STOP_TOL = 0.05
JUMP_MIN, JUMP_RETURN_TOL = 0.3, 0.1
DIAG_RATIO_MAX = 1.1
DIAG_NOISE = 0.05


def expected(key, fwd):
    fx, fz = fwd
    right = (fz, -fx)
    return {"W": fwd, "S": (-fx, -fz), "D": right, "A": (-right[0], -right[1])}[key]


def safe_y(p):
    return p is None or p[1] > Y_FALL_LIMIT + 0.5


def main():
    run = run_no_from_argv()
    S = Suite("MOVE_sdk", run)
    reset_input()
    set_time_scale(1)
    passive = Passive()
    try:
        # ---------- MOVE-01 ----------
        def move01(t0):
            rows, bad = [], 0
            for rep in range(3):
                for key in ["W", "S", "A", "D"]:
                    p0 = player_pos()
                    fwd = cam_forward(p0)
                    press(key, 0.3)
                    time.sleep(0.4)
                    p1 = player_pos()
                    v = (p1[0] - p0[0], p1[2] - p0[2])
                    d = math.hypot(*v)
                    ang = angle_between(v, expected(key, fwd))
                    ok = d >= MIN_DISP and ang <= MAX_ANGLE
                    bad += 0 if ok else 1
                    rows.append((rep + 1, key, round(d, 2), round(ang, 1), ok))
                    if not safe_y(p1):
                        raise RuntimeError("игрок опустился ниже безопасной высоты: %s" % (p1,))
            per_key = {}
            for rep, key, d, ang, ok in rows:
                per_key.setdefault(key, []).append((d, ang))
            summ = "; ".join("%s: смещение %s м, угол %s°" % (k, [x[0] for x in v], [x[1] for x in v]) for k, v in per_key.items())
            S.rec("MOVE-01", PASS if bad == 0 else FAIL,
                  "нажатий в пределах критерия (смещение >= %.1f м, угол <= %.0f°) %d из 12; %s" % (MIN_DISP, MAX_ANGLE, 12 - bad, summ), t0)
        safe(S, "MOVE-01", move01)

        # ---------- MOVE-02 ----------
        def move02(t0):
            reps, bad = [], 0
            for rep in range(3):
                key = "W" if rep % 2 == 0 else "S"
                key_down(key)
                time.sleep(0.5)
                key_up(key)
                time.sleep(1.0)   # SDK: вызов ~20 мс, а не ~700 мс как у CLI; без паузы первый замер ловит выбег после key_up (ошибка переноса CC-68)
                a = player_pos(); time.sleep(0.3)
                b = player_pos(); time.sleep(0.3)
                c = player_pos()
                d1, d2 = dist3(a, b), dist3(b, c)
                ok = d1 <= STOP_TOL and d2 <= STOP_TOL
                bad += 0 if ok else 1
                reps.append((key, round(d1, 3), round(d2, 3)))
            S.rec("MOVE-02", PASS if bad == 0 else FAIL,
                  "повторов с остановкой (смещения между замерами <= %.2f м) %d из 3; (клавиша, смещение 1-2, смещение 2-3): %s" % (STOP_TOL, 3 - bad, reps), t0,
                  "замеры идут с интервалом ~1 с (сам вызов CLI ~0,7 с), а не 0,3 с")
        safe(S, "MOVE-02", move02)
        reset_input()

        # ---------- MOVE-03 ----------
        def move03(t0):
            reset_input()
            reps, bad = [], 0
            for rep in range(3):
                a = player_pos(); time.sleep(1.0)
                b = player_pos(); time.sleep(1.0)
                c = player_pos()
                d1, d2 = dist3(a, b), dist3(b, c)
                ok = d1 <= STOP_TOL and d2 <= STOP_TOL
                bad += 0 if ok else 1
                reps.append((round(d1, 3), round(d2, 3)))
            S.rec("MOVE-03", PASS if bad == 0 else FAIL,
                  "повторов без самопроизвольного движения (<= %.2f м) %d из 3; смещения (1-2, 2-3): %s" % (STOP_TOL, 3 - bad, reps), t0)
        safe(S, "MOVE-03", move03)

        # ---------- MOVE-04 ----------
        def move04(t0):
            reps = []
            for rep in range(3):
                base = player_pos()
                ys = []
                try:
                    set_time_scale(0.2)
                    press("Space", 0.1)
                    for _ in range(8):
                        p = player_pos()
                        if p:
                            ys.append(round(p[1] - base[1], 2))
                finally:
                    set_time_scale(1)
                    reset_input()
                time.sleep(2.0)
                end = player_pos()
                peak = max(ys) if ys else None
                back = end[1] - base[1]
                reps.append({"peak": peak, "back": round(back, 2), "ys": ys})
                time.sleep(0.5)
            ok = [r["peak"] is not None and r["peak"] >= JUMP_MIN and abs(r["back"]) <= JUMP_RETURN_TOL for r in reps]
            nums = "повторов в критерии (пик >= %.1f м над исходной y, возврат через 2 с в пределах %.1f м) %d из 3; пик по повторам %s; возврат %s; ряды y-y0 %s" % (
                JUMP_MIN, JUMP_RETURN_TOL, sum(ok), [r["peak"] for r in reps], [r["back"] for r in reps], [r["ys"] for r in reps])
            if all(ok):
                S.rec("MOVE-04", PASS, nums, t0)
            elif all((r["peak"] or 0) < 0.05 for r in reps):
                S.rec("MOVE-04", UNCONF, nums, t0, "прыжок не замечен ни в одном повторе: либо ввод Space не доходит через AltTester, либо прыжка нет; метод не различает")
            else:
                S.rec("MOVE-04", FAIL, nums, t0)
        safe(S, "MOVE-04", move04)
        set_time_scale(1)
        reset_input()

        # ---------- MOVE-05 ----------
        def held_speed(keys, hold_pre=0.5, n=4):
            """Скорость на установившемся участке: n замеров позиции при зажатых клавишах, v = путь(первый->последний) / время между ответами."""
            for k in keys:
                key_down(k)
            time.sleep(hold_pre)
            pts = []
            for _ in range(n):
                p = player_pos()
                pts.append((p, time.time()))
                time.sleep(0.6)   # SDK: замеры идут каждые ~20 мс; разносим до ~0,7 с как у CLI, иначе путь между замерами мал и скорость шумит (ошибка переноса CC-68)
            for k in keys:
                key_up(k)
            reset_input()
            if not safe_y(pts[-1][0]):
                raise RuntimeError("игрок опустился ниже безопасной высоты")
            path = dist_xz(pts[0][0], pts[-1][0])
            dt = pts[-1][1] - pts[0][1]
            return path / dt, path, dt

        def move05(t0):
            reps = []
            try:
                set_time_scale(0.3)
                for rep in range(3):
                    sa = held_speed(["W"])
                    time.sleep(1.0)
                    held_speed(["S"])        # вернуться
                    time.sleep(1.0)
                    sb = held_speed(["W", "D"])
                    time.sleep(1.0)
                    held_speed(["S", "A"])   # вернуться
                    time.sleep(1.0)
                    reps.append((round(sa[0], 2), round(sb[0], 2), round(sb[0] / sa[0], 2) if sa[0] > 0 else None, round(sa[1], 2), round(sb[1], 2)))
            finally:
                set_time_scale(1)
                reset_input()
            ratios = [r[2] for r in reps]
            nums = "отношение скорости по диагонали (W+D) к прямой (W) по повторам %s (порог <= %.1f); (v прямо, v диагональ, отношение, путь прямо, путь диагональ) %s; игровое время 0,3" % (ratios, DIAG_RATIO_MAX, reps)
            if any(r is None for r in ratios):
                S.rec("MOVE-05", UNCONF, nums, t0, "скорость прямого хода не измерена")
            elif all(r <= DIAG_RATIO_MAX for r in ratios):
                S.rec("MOVE-05", PASS, nums, t0, "скорость = путь первый->последний из 4 замеров / время между ответами CLI; замысел «диагональ не быстрее» у человека не уточнялся")
            elif all(r > DIAG_RATIO_MAX + DIAG_NOISE for r in ratios):
                S.rec("MOVE-05", FAIL, nums, t0, "нужно решение человека: замысел скорости по диагонали")
            else:
                S.rec("MOVE-05", UNCONF, nums, t0, "отношения у границы порога (запас на погрешность замера %.2f): метод не даёт однозначного ответа; погрешность — джиттер вызовов CLI" % DIAG_NOISE)
        safe(S, "MOVE-05", move05)
        set_time_scale(1)
        reset_input()

        # ---------- MOVE-06 (замер сделан menu.py сразу после появления игрока) ----------
        t0 = time.time()
        sp = os.path.join(RESULTS_DIR, "state_run%d.json" % run)
        try:
            st = json.load(open(sp, encoding="utf-8"))
            r = st.get("move06_result")
        except Exception:
            r = None
        if r:
            S.rec("MOVE-06", r[0], r[1], t0, r[2] + " (замер выполнен menu.py)", dt=0)
        else:
            S.rec("MOVE-06", UNCONF, "нет данных menu.py", t0)

        passive.report(S, "PASSIVE-MOVE")
    finally:
        try:
            set_time_scale(1)
            reset_input()
        except Exception:
            pass
    S.finish()


if __name__ == "__main__":
    main()
