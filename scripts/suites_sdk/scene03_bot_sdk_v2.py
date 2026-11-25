# -*- coding: utf-8 -*-
"""SCENE-03 (SDK), бот v2: следование по вехам. Запуск: .venv python TestAI/suites/scene03_bot_sdk_v2.py
Игра в Beach, New Game не нажимается, Initialization не загружается. Лог: Reports/evidence/logs/scene03_bot_sdk_v2.json.
Вехи (запас 0,7 м, обход бамбука с севера) заданы в задании. От текущей позиции до первой вехи маршрут считается планировщиком
(plan_route_lib.py) по коллайдерам сцены (SDK, bounds). При застревании - пересчёт от текущей точки до текущей вехи (максимум 3 раза).
Камера: мышь вправо (+x) -> yaw растёт (calibration.md, замер CAM-01 SDK: ~0,24 град/px); направление W = взгляд камеры.
"""
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import lib_sdk  # noqa
from lib import *  # noqa
from alttester import By
from plan_route_lib import plan

WAYPOINTS = [(-88.6, -356.2), (-84.6, -353.2), (-79.6, -353.4), (-74.8, -355.4), (-70.2, -357.6), (-65.2, -358.0), (-63.0, -359.0)]
EXIT = (-62.83, -358.87)
LIMIT_S = 720
WP_TOL = 0.5
REACH_M = 1.5
MIN_PROGRESS = 0.3
CHECK_EVERY = 3
MAX_REPLANS = 3
DEG_PER_PX = 0.24
CX, CY = 553, 189
BASE = {"PersistentManagers", "Gameplay", "Beach"}
SKIP = ("Landmass", "Seabed", "LocationExit", "PigChef", "AttackCollider", "InteractionDetector", "Water")
LOGF = os.path.join(LOGS, "scene03_bot_sdk_v2.json")
Y_NOTE, Y_STOP, Y_JUMP = -12.0, -25.0, 3.0

log = {"steps": [], "events": [], "verdict": None, "вехи_исходные": WAYPOINTS}
T0 = time.time()
cursor_x = None


def save():
    json.dump(log, open(LOGF, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)


def ev(msg, **kw):
    e = {"t": round(time.time() - T0, 1), "событие": msg}
    e.update(kw)
    log["events"].append(e)
    print(e, flush=True)


def pstate():
    r = get_prop(PLAYER, "UOP1.StateMachine.StateMachine", "_currentState._originSO.name", assembly="UOP1.StateMachine")
    return (r.get("data") or {}).get("value")


def dump_stuck(why):
    g = lambda c, p, a="Assembly-CSharp": (get_prop(PLAYER, c, p, assembly=a).get("data") or {}).get("value")
    d = {"причина": why, "когда": datetime.datetime.now().isoformat(timespec="seconds"), "позиция_игрока": player_pos(), "состояние": pstate(),
         "lastHit.collider": g("Protagonist", "lastHit.collider.name"),
         "lastHit.normal": [g("Protagonist", "lastHit.normal." + a) for a in "xyz"],
         "lastHit.point": [g("Protagonist", "lastHit.point." + a) for a in "xyz"]}
    json.dump(d, open(os.path.join(LOGS, "BUG_sliding_stuck_scene03_bot_sdk_v2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return d


def collect_obstacles(bbox):
    """Коллайдеры в bbox=(x0,x1,z0,z1): круг радиусом max(extents x,z) + 0,3 (радиус игрока)."""
    d = lib_sdk.driver()
    obs = []
    for comp in ["UnityEngine.BoxCollider", "UnityEngine.CapsuleCollider", "UnityEngine.MeshCollider", "UnityEngine.SphereCollider"]:
        for o in d.find_objects(By.COMPONENT, comp, enabled=False):
            if any(s in o.name for s in SKIP):
                continue
            if not (bbox[0] <= o.worldX <= bbox[1] and bbox[2] <= o.worldZ <= bbox[3]):
                continue
            try:
                ex = o.get_component_property(comp, "bounds.extents.x", "UnityEngine.PhysicsModule", max_depth=2)
                ez = o.get_component_property(comp, "bounds.extents.z", "UnityEngine.PhysicsModule", max_depth=2)
                cx = o.get_component_property(comp, "bounds.center.x", "UnityEngine.PhysicsModule", max_depth=2)
                cz = o.get_component_property(comp, "bounds.center.z", "UnityEngine.PhysicsModule", max_depth=2)
            except Exception:
                continue
            r = (0.8 * (ex + ez) / 2 if comp.endswith('MeshCollider') else max(ex, ez)) + 0.3   # меш по AABB завышен: берём 0,8 среднего
            obs.append((cx, cz, r))
    return obs


def rotate_camera(err):
    """Повернуть камеру на err градусов (вправо +) зажатой ПКМ. Курсор отслеживается; границы 80..1026."""
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


def main():
    global T0, cursor_x
    reset_input()
    p = player_pos()
    log["старт"] = {"позиция": p, "сцены": scenes(), "время": datetime.datetime.now().isoformat(timespec="seconds")}
    lib_sdk.move_mouse(CX, CY, 0.1)
    cursor_x = CX
    log_off = log_offset()
    T0 = time.time()
    # --- маршрут от текущей позиции до первой вехи ---
    wps = list(WAYPOINTS)
    if dist_xz(p, (wps[0][0], 0, wps[0][1])) > 3.0:
        bbox = (min(p[0], wps[0][0]) - 15, max(p[0], wps[0][0]) + 15, min(p[2], wps[0][1]) - 15, max(p[2], wps[0][1]) + 15)
        obs = collect_obstacles(bbox)
        log["препятствий_в_области_подхода"] = len(obs)
        pre, L, lat = None, None, None
        for m in (0.7, 0.5, 0.3):
            pre, L, lat = plan((p[0], p[2]), wps[0], obs, margin=m)
            if pre:
                ev("маршрут до первой вехи", запас_м=m, длина_м=round(L, 1), боковое_м=round(lat, 1), вехи=[(round(a, 1), round(b, 1)) for a, b in pre], препятствий=len(obs))
                break
        if not pre:
            ev("маршрута до первой вехи нет", ближайшая=lat)
            log["verdict"], log["причина"] = UNCONF, "планировщик не нашёл маршрут от %s до первой вехи" % (p,)
            save()
            print("SCENE-03 v2:", log["verdict"], log["причина"])
            return
        wps = pre[1:] + wps
    log["вехи_итоговые"] = wps
    replans, wi, step_i, last_check_d, last_y = 0, 0, 0, None, p[1]
    reached_at, verdict, reason, v_y = None, None, None, 0
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
            verdict, reason = UNCONF, "персонаж в состоянии Sliding в %s (шаг %d)" % (tuple(round(v, 2) for v in p), step_i)
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
                e2 = yaw_diff(cam_state()[0], heading)
                row["ошибка_после_поворота"] = round(e2, 1)
                e = e2
        if abs(e) <= 15:
            ks = ["W"]
        elif abs(e) <= 50 and not row.get("поворот_камеры", True) is False:
            ks = ["W"] if abs(e) < 25 else []   # ждём доворота камеры, без шага вбок
        else:
            ks = keys_8(e) if row.get("поворот_камеры") is False else []
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
                replans += 1
                ev("нет прогресса к вехе %d (%.2f м за %d шага), пересчёт %d" % (wi, last_check_d - dd, CHECK_EVERY, replans), позиция=[round(v, 2) for v in pp])
                if replans > MAX_REPLANS:
                    verdict, reason = UNCONF, "застревание после %d пересчётов в %s у вехи %d %s, до выхода %.1f м" % (MAX_REPLANS, tuple(round(v, 2) for v in pp), wi, wps[wi], dist_xz(pp, (EXIT[0], 0, EXIT[1])))
                    break
                hold(["S"], 0.3)
                bbox = (min(pp[0], wps[wi][0]) - 12, max(pp[0], wps[wi][0]) + 12, min(pp[2], wps[wi][1]) - 12, max(pp[2], wps[wi][1]) + 12)
                obs = collect_obstacles(bbox)
                new = None
                for m in (0.5, 0.3, 0.15):
                    new, L, lat = plan((pp[0], pp[2]), wps[wi], obs, margin=m, h=0.1, pad=6)
                    if new:
                        ev("пересчёт маршрута", запас_м=m, вехи=[(round(a, 1), round(b, 1)) for a, b in new], препятствий=len(obs))
                        break
                if new:
                    wps = wps[:wi] + new[1:-1] + wps[wi:]
                    log["вехи_итоговые"] = wps
            else:
                if last_check_d is not None and last_check_d - dd >= MIN_PROGRESS:
                    pass
            last_check_d = dd
        if step_i % 20 == 0:
            save()
    reset_input()
    log.update({"verdict": verdict, "причина": reason, "время_с": round(time.time() - T0, 1), "шагов": step_i, "пересчётов": replans,
                "шагов_y_ниже_-12": v_y, "консоль_за_прогон": log_stats(log_since(log_off)), "последняя_позиция": player_pos() if verdict != PASS else None})
    save()
    print("SCENE-03 v2: %s | %s | %.0f с, шагов %d, пересчётов %d, y<-12: %d" % (verdict, reason, log["время_с"], step_i, replans, v_y))


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
