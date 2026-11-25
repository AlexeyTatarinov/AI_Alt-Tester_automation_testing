# -*- coding: utf-8 -*-
"""SCENE-03 (SDK), бот v3. Запуск: .venv python TestAI/suites/scene03_bot_sdk_v3.py
Старт с текущей позиции. Маршрут до LocationExit считается по AABB коллайдеров (Reports/evidence/logs/colliders_rects_beach.json,
собирает TestAI/collect_rects.py) с запасом >= 0,7 м (если не находится, 0,5 и 0,3). При застревании: шаг вбок A/D 0,5 с, затем снова к вехе,
каждая вторая попытка с пересчётом маршрута; максимум 5 попыток на веху. Камера по calibration.md (мышь вправо = yaw растёт).
New Game не нажимается, Initialization не загружается. Лог: Reports/evidence/logs/scene03_bot_sdk_v3.json.
"""
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import lib_sdk  # noqa
from lib import *  # noqa
from plan_route_lib import plan_rects

EXIT = (-62.83, -358.87)
LIMIT_S = 720
WP_TOL = 0.5
REACH_M = 1.5
MIN_PROGRESS = 0.3
CHECK_EVERY = 3
MAX_TRIES_PER_WP = 5
DEG_PER_PX = 0.24
CX, CY = 553, 189
BASE = {"PersistentManagers", "Gameplay", "Beach"}
Y_NOTE, Y_STOP, Y_JUMP = -12.0, -25.0, 3.0
RECTS = os.path.join(LOGS, "colliders_rects_beach.json")
LOGF = os.path.join(LOGS, "scene03_bot_sdk_v3.json")

log = {"steps": [], "events": [], "verdict": None}
T0 = time.time()
cursor_x = None


def save():
    json.dump(log, open(LOGF, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)


def ev(msg, **kw):
    e = {"t": round(time.time() - T0, 1), "событие": msg}
    e.update(kw)
    log["events"].append(e)
    print(e, flush=True)


def g(c, pr, a="Assembly-CSharp"):
    return (get_prop(PLAYER, c, pr, assembly=a).get("data") or {}).get("value")


def pstate():
    return g("UOP1.StateMachine.StateMachine", "_currentState._originSO.name", "UOP1.StateMachine")


def last_hit():
    return {"collider": g("Protagonist", "lastHit.collider.name"), "normal": [g("Protagonist", "lastHit.normal." + a) for a in "xyz"],
            "point": [g("Protagonist", "lastHit.point." + a) for a in "xyz"]}


def dump_stuck(why):
    d = {"причина": why, "когда": datetime.datetime.now().isoformat(timespec="seconds"), "позиция_игрока": player_pos(), "состояние": pstate(), "lastHit": last_hit()}
    json.dump(d, open(os.path.join(LOGS, "BUG_sliding_stuck_scene03_bot_sdk_v3.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return d


def rotate_camera(err):
    global cursor_x
    dx = int(max(-190, min(190, err / DEG_PER_PX)))
    nx = cursor_x + dx
    if nx < 80 or nx > 1026:
        return False
    key_down("Mouse1")
    lib_sdk.move_mouse(nx, CY, 0.15)
    key_up("Mouse1")
    cursor_x = nx
    return True


def hold(keys, secs):
    for k in keys:
        key_down(k)
    time.sleep(secs)
    for k in keys:
        key_up(k)


def keys_8(e):
    a, side = abs(e), ("D" if e > 0 else "A")
    return ["W"] if a < 22.5 else ["W", side] if a < 67.5 else [side] if a < 112.5 else ["S", side] if a < 157.5 else ["S"]


def make_route(start, rects, goal):
    for m in (0.7, 0.5, 0.3):
        w, L, lat = plan_rects(start, goal, rects, margin=m)
        if w:
            return w, m, L, lat, None
    # маршрута нет: до ближайшей достижимой точки
    w, L, near = plan_rects(start, goal, rects, margin=0.3)
    return None, None, None, None, near


def main():
    global T0, cursor_x
    reset_input()
    p = player_pos()
    log["старт"] = {"позиция": p, "сцены": scenes(), "время": datetime.datetime.now().isoformat(timespec="seconds")}
    rects = [r[:4] for r in json.load(open(RECTS, encoding="utf-8"))]
    log["прямоугольников_коллайдеров"] = len(rects)
    lib_sdk.move_mouse(CX, CY, 0.1)
    cursor_x = CX
    log_off = log_offset()
    T0 = time.time()
    start = (p[0], p[2])
    wps, m, L, lat, near = make_route(start, rects, EXIT)
    if wps is None:
        # по AABB-модели прохода нет (AABB повёрнутых коробок завышены): пробуем напрямую к выходу с шагами вбок (максимум 5 попыток на веху)
        ev("маршрута по AABB-модели нет, идём напрямую с обходом шагом вбок", ближайшая_достижимая=near)
        log["маршрут_по_модели"] = "нет; ближайшая достижимая точка %s" % (tuple(round(v, 1) for v in near),)
        wps, m, L, lat = [start, EXIT], 0.0, math.hypot(EXIT[0] - start[0], EXIT[1] - start[1]), 0.0
    ev("маршрут", запас_м=m, длина_м=round(L, 1), боковое_м=round(lat, 1), вехи=[(round(a, 1), round(b, 1)) for a, b in wps])
    log["вехи"] = wps
    wi, step_i, last_check_d, tries, replans = 1 if len(wps) > 1 else 0, 0, None, {}, 0
    last_y, v_y, reached_at, verdict, reason = p[1], 0, None, None, None
    sidestep_dir = "A"
    while True:
        el = time.time() - T0
        if el > LIMIT_S:
            verdict, reason = UNCONF, "лимит времени %d с" % LIMIT_S
            break
        sc = scenes()
        if [s for s in sc if s not in BASE] or "Beach" not in sc:
            ev("смена сцены", сцены=sc, с_старта_бота=round(el, 1))
            t_find, found = time.time(), None
            while time.time() - t_find < 40:
                try:
                    found = player_pos()
                except Exception:
                    found = None
                if found:
                    break
                time.sleep(0.5)
            log["новая_сцена"] = {"сцены": sc, "время_от_старта_бота_с": round(el, 1), "игрок_найден": bool(found), "позиция": found}
            ev("игрок после смены сцены", найден=bool(found), позиция=found)
            verdict, reason = (PASS, "загрузилась сцена(ы) %s, игрок найден" % sc) if found else (UNCONF, "сцена сменилась (%s), игрок не найден за 40 с" % sc)
            break
        p = player_pos()
        st = pstate()
        if p[1] < Y_NOTE:
            v_y += 1
        if p[1] < Y_STOP or abs(p[1] - last_y) > Y_JUMP:
            verdict, reason = UNCONF, "возможный провал: y %.2f (было %.2f) в %s" % (p[1], last_y, tuple(round(v, 2) for v in p))
            break
        last_y = p[1]
        if st == "Sliding":
            d_ = dump_stuck("Sliding на шаге %d" % step_i)
            ev("SLIDING: остановка", данные=d_)
            verdict, reason = UNCONF, "Sliding в %s (шаг %d)" % (tuple(round(v, 2) for v in p), step_i)
            break
        dexit = dist_xz(p, (EXIT[0], 0, EXIT[1]))
        if dexit <= REACH_M:
            if reached_at is None:
                reached_at = time.time()
                ev("достиг LocationExit", до_цели=round(dexit, 2))
            if time.time() - reached_at > 10:
                verdict, reason = UNCONF, "дошёл до LocationExit (%.2f м), сцена не сменилась за 10 с" % dexit
                break
            time.sleep(0.4)
            continue
        wp = wps[wi]
        dw = dist_xz(p, (wp[0], 0, wp[1]))
        if dw <= WP_TOL and wi < len(wps) - 1:
            wi += 1
            ev("веха достигнута", номер=wi, позиция=[round(v, 2) for v in p])
            last_check_d = None
            continue
        tgt = wp if dw > WP_TOL else EXIT
        heading = math.degrees(math.atan2(tgt[0] - p[0], tgt[1] - p[2]))
        cs = cam_state()
        e = yaw_diff(cs[0], heading)
        stats = log_stats(log_since(log_off))
        row = {"t": round(el, 1), "позиция": [round(v, 2) for v in p], "веха": wi, "до_вехи_м": round(dw, 2), "до_выхода_м": round(dexit, 2),
               "yaw": round(cs[0], 1), "курс": round(heading, 1), "ошибка_курса": round(e, 1), "состояние": st,
               "ошибок_консоли": (stats["exceptions"] + stats["errors"]) if stats else None}
        if abs(e) > 8:
            ok = rotate_camera(e)
            row["поворот_камеры"] = ok
            if ok:
                time.sleep(0.5)
                e = yaw_diff(cam_state()[0], heading)
                row["ошибка_после_поворота"] = round(e, 1)
        if abs(e) <= 15:
            ks = ["W"]
        elif row.get("поворот_камеры") is False:
            ks = keys_8(e)
        else:
            ks = ["W"] if abs(e) < 25 else []
        secs = 0.15 if (dw < 3.0 or abs(e) > 8) else 0.3
        row["клавиши"], row["секунд"] = ks, secs
        if ks:
            hold(ks, secs)
        time.sleep(0.1)
        log["steps"].append(row)
        step_i += 1
        if step_i % CHECK_EVERY == 0:
            pp = player_pos()
            dd = dist_xz(pp, (wps[wi][0], 0, wps[wi][1]))
            if last_check_d is not None and last_check_d - dd < MIN_PROGRESS and dd > WP_TOL:
                tries[wi] = tries.get(wi, 0) + 1
                lh = last_hit()
                ev("нет прогресса к вехе %d (%.2f м за %d шага), попытка %d из %d" % (wi, last_check_d - dd, CHECK_EVERY, tries[wi], MAX_TRIES_PER_WP),
                   позиция=[round(v, 2) for v in pp], lastHit=lh)
                if tries[wi] > MAX_TRIES_PER_WP:
                    verdict, reason = UNCONF, "застревание у вехи %d %s в %s после %d попыток, до выхода %.1f м, последнее касание: %s" % (
                        wi, tuple(round(v, 1) for v in wps[wi]), tuple(round(v, 2) for v in pp), MAX_TRIES_PER_WP, dist_xz(pp, (EXIT[0], 0, EXIT[1])), lh.get("collider"))
                    break
                if tries[wi] % 2 == 0 and replans < 3:
                    replans += 1
                    new, m2, L2, lat2, near2 = make_route((pp[0], pp[2]), rects, EXIT)
                    if new:
                        wps = new
                        ev("пересчёт маршрута", запас_м=m2, длина_м=round(L2, 1), вехи=[(round(a_, 1), round(b_, 1)) for a_, b_ in new])
                        wi = 1 if len(wps) > 1 else 0
                        tries = {}
                        log["вехи"] = wps
                        last_check_d = None
                        continue
                # шаг вбок 0,5 с, чередуя сторону, затем снова к вехе
                hold(["S"], 0.2)
                hold([sidestep_dir], 0.5)
                sidestep_dir = "D" if sidestep_dir == "A" else "A"
                if pstate() == "Sliding":
                    d_ = dump_stuck("Sliding после шага вбок")
                    verdict, reason = UNCONF, "Sliding после шага вбок в %s" % (d_["позиция_игрока"],)
                    break
                dd = dist_xz(player_pos(), (wps[wi][0], 0, wps[wi][1]))
            last_check_d = dd
        if step_i % 20 == 0:
            save()
    reset_input()
    last = player_pos() if verdict != PASS else None
    log.update({"verdict": verdict, "причина": reason, "время_с": round(time.time() - T0, 1), "шагов": step_i, "пересчётов": replans,
                "шагов_y_ниже_-12": v_y, "консоль_за_прогон": log_stats(log_since(log_off)), "последняя_позиция": last})
    save()
    print("SCENE-03 v3: %s | %s | %.0f с, шагов %d, пересчётов %d, y<-12: %d" % (verdict, reason, log["время_с"], step_i, replans, v_y))


if __name__ == "__main__":
    try:
        main()
    finally:
        try:
            reset_input()
            set_time_scale(1)
        except Exception:
            pass
        save()
