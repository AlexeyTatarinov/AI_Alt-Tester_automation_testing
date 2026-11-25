# -*- coding: utf-8 -*-
"""SCENE-03 (SDK): бот выхода из Beach к LocationExit. Запуск: .venv python TestAI/suites/scene03_bot_sdk.py
Игра в Beach после New Game. Initialization не загружается. Лог шагов: Reports/evidence/logs/scene03_bot_sdk.json.
Камера (calibration.md): мышь вправо -> yaw растёт (камера уходит влево, взгляд вправо); yaw = направление взгляда, 0 = +Z, + к +X.
Курс к цели: heading = atan2(dx, dz). e = heading - yaw: e > 0 цель справа. Поворот ~0,24 градуса на px (замер CAM-01 SDK).
Если курс камеры не подходит, используются 8 направлений WASD (движение относительно камеры).
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import lib_sdk  # noqa
from lib import *  # noqa

STEP_S = 0.3
LIMIT_S = 600
CHECK_EVERY = 3
MIN_PROGRESS = 0.3
MAX_BAD_DETOURS = 3
REACH_M = 1.5
DEG_PER_PX = 0.24
CX, CY = 553, 189
BASE = {"PersistentManagers", "Gameplay", "Beach"}
LOGF = os.path.join(LOGS, "scene03_bot_sdk.json")

log = {"steps": [], "events": [], "verdict": None}
T0 = time.time()
cursor_x = CX


def save():
    json.dump(log, open(LOGF, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)


def ev(msg, **kw):
    e = {"t": round(time.time() - T0, 1), "событие": msg}
    e.update(kw)
    log["events"].append(e)
    print(e, flush=True)


def keys_for(e):
    a = abs(e)
    side = "D" if e > 0 else "A"
    if a < 22.5:
        return ["W"]
    if a < 67.5:
        return ["W", side]
    if a < 112.5:
        return [side]
    if a < 157.5:
        return ["S", side]
    return ["S"]


def hold(keys, secs):
    for k in keys:
        key_down(k)
    time.sleep(secs)
    for k in keys:
        key_up(k)


def rotate_camera(err):
    """Повернуть камеру на err градусов (вправо +) зажатой ПКМ; курсор отслеживается, края экрана 80..1026."""
    global cursor_x
    dx = int(max(-200, min(200, err / DEG_PER_PX)))
    nx = cursor_x + dx
    if nx < 80 or nx > 1026:
        return False
    key_down("Mouse1")
    lib_sdk.move_mouse(nx, CY, 0.2)
    key_up("Mouse1")
    cursor_x = nx
    return True


def stuck_state():
    return pstate()


def pstate():
    r = get_prop(PLAYER, "UOP1.StateMachine.StateMachine", "_currentState._originSO.name", assembly="UOP1.StateMachine")
    return (r.get("data") or {}).get("value")


def dump_stuck(why):
    g = lambda c, p, a="Assembly-CSharp": (get_prop(PLAYER, c, p, assembly=a).get("data") or {}).get("value")
    d = {"причина": why, "когда": datetime.datetime.now().isoformat(timespec="seconds"), "позиция_игрока": player_pos(),
         "состояние": pstate(), "lastHit.collider": g("Protagonist", "lastHit.collider.name"),
         "lastHit.normal": [g("Protagonist", "lastHit.normal." + a) for a in "xyz"],
         "lastHit.point": [g("Protagonist", "lastHit.point." + a) for a in "xyz"]}
    json.dump(d, open(os.path.join(LOGS, "BUG_sliding_stuck_scene03_bot_sdk.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return d


def main():
    global T0
    reset_input()
    ex = find("LocationExit")
    target = (ex["worldX"], ex["worldZ"])
    log["цель"] = {"LocationExit": [ex["worldX"], ex["worldY"], ex["worldZ"]]}
    p = player_pos()
    log["старт"] = {"позиция": p, "дистанция_м": round(dist_xz(p, (target[0], 0, target[1])), 1), "сцены": scenes()}
    ev("старт бота", позиция=p, до_цели=log["старт"]["дистанция_м"])
    log_off = log_offset()
    T0 = time.time()
    bad_detours, last_check_d, step_i, violations_y = 0, dist_xz(p, (target[0], 0, target[1])), 0, 0
    reached_at = None
    verdict, reason = None, None
    while True:
        el = time.time() - T0
        if el > LIMIT_S:
            verdict, reason = UNCONF, "лимит времени %d с" % LIMIT_S
            break
        sc = scenes()
        new = [s for s in sc if s not in BASE]
        if new or "Beach" not in sc:
            ev("смена сцены", сцены=sc, с_старта_бота=round(el, 1))
            t_find = time.time()
            found = None
            while time.time() - t_find < 40:
                try:
                    found = player_pos()
                except Exception:
                    found = None
                if found:
                    break
                time.sleep(0.5)
            log["новая_сцена"] = {"сцены": sc, "время_от_старта_бота_с": round(el, 1), "игрок_найден": bool(found), "позиция": found,
                                  "ожидание_игрока_с": round(time.time() - t_find, 1)}
            ev("игрок после смены сцены", найден=bool(found), позиция=found)
            if found:
                verdict, reason = PASS, "загрузилась сцена(ы) %s, игрок найден" % sc
            else:
                verdict, reason = UNCONF, "сцена сменилась (%s), но игрок не найден за 40 с" % sc
            break
        p = player_pos()
        st = pstate()
        d = dist_xz(p, (target[0], 0, target[1]))
        cs = cam_state()
        yaw = cs[0]
        heading = math.degrees(math.atan2(target[0] - p[0], target[1] - p[2]))
        e = yaw_diff(yaw, heading)
        stats = log_stats(log_since(log_off))
        row = {"t": round(el, 1), "позиция": [round(v, 2) for v in p], "yaw_камеры": round(yaw, 1), "курс_к_цели": round(heading, 1),
               "ошибка_курса": round(e, 1), "до_цели_м": round(d, 2), "состояние": st,
               "ошибок_консоли": (stats["exceptions"] + stats["errors"]) if stats else None}
        if p[1] < Y_FALL_LIMIT:
            violations_y += 1
            row["y_ниже_-12"] = True
        if p[1] < -25:
            verdict, reason = UNCONF, "высота ниже -25 (%s): остановка" % (p,)
            break
        if st == "Sliding":
            d_ = dump_stuck("Sliding на шаге %d" % step_i)
            ev("SLIDING: остановка", данные=d_)
            verdict, reason = UNCONF, "персонаж в состоянии Sliding у %s (шаг %d)" % (tuple(round(v, 2) for v in p), step_i)
            break
        if d <= REACH_M:
            if reached_at is None:
                reached_at = time.time()
                ev("достиг цели", до_цели=round(d, 2))
            if time.time() - reached_at > 10:
                verdict, reason = UNCONF, "дошёл до LocationExit (%.2f м), но сцена не сменилась за 10 с" % d
                break
            time.sleep(0.5)
            continue
        # курс: камера, затем клавиши
        rotated = False
        if abs(e) > 50:
            rotated = rotate_camera(e)
            row["поворот_камеры"] = rotated
            if rotated:
                time.sleep(0.6)
                cs = cam_state()
                e = yaw_diff(cs[0], heading)
        ks = keys_for(e)
        row["клавиши"] = ks
        hold(ks, STEP_S)
        time.sleep(0.15)
        log["steps"].append(row)
        step_i += 1
        # прогресс каждые 3 шага
        if step_i % CHECK_EVERY == 0:
            pp = player_pos()
            dd = dist_xz(pp, (target[0], 0, target[1]))
            if last_check_d - dd < MIN_PROGRESS:
                bad_detours += 1
                ev("нет прогресса (%.2f м за %d шага), обход %d" % (last_check_d - dd, CHECK_EVERY, bad_detours), позиция=pp)
                if bad_detours > MAX_BAD_DETOURS - 1 and bad_detours >= MAX_BAD_DETOURS:
                    verdict, reason = UNCONF, "3 неудачных обхода подряд у %s, до цели %.1f м" % (tuple(round(v, 2) for v in pp), dd)
                    break
                # назад, вбок, снова вперёд (вбок чередуем)
                hold(["S"], 0.4)
                side = "A" if bad_detours % 2 else "D"
                hold([side], 0.9)
                hold(keys_for(yaw_diff(cam_state()[0], math.degrees(math.atan2(target[0] - pp[0], target[1] - pp[2])))), 0.9)
                if pstate() == "Sliding":
                    d_ = dump_stuck("Sliding после обхода")
                    verdict, reason = UNCONF, "Sliding после обхода у %s" % (d_["позиция_игрока"],)
                    break
                dd = dist_xz(player_pos(), (target[0], 0, target[1]))
            else:
                bad_detours = 0
            last_check_d = dd
        if step_i % 20 == 0:
            save()
    reset_input()
    log["verdict"] = verdict
    log["причина"] = reason
    log["время_с"] = round(time.time() - T0, 1)
    log["шагов"] = step_i
    log["y_ниже_-12_шагов"] = violations_y
    st = log_stats(log_since(log_off))
    log["консоль_за_прогон"] = st
    save()
    print("SCENE-03 (SDK): %s | %s | %.0f с, шагов %d, y<-12: %d, консоль: %s" % (verdict, reason, log["время_с"], step_i, violations_y, st))


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
