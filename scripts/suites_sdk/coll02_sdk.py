# -*- coding: utf-8 -*-
"""[SDK-версия coll02.py, CLI-вызовы заменены адаптером lib_sdk.py; запуск: scripts\sdk_smoke\.venv\Scripts\python]
COLL-02 (+COLL-03): персонаж не проходит сквозь «твёрдые» объекты Beach (Test_Ai/collision_rules.md v0.1).

Предусловие P1: Beach загружен. Запуск:  python TestAI/suites/coll02.py <номер прогона> [имя_объекта_для_одного_прогона]
Объекты: 10 из группы «должен быть твёрдым» (Beach_Landmass исключён по заданию).
Метод: дойти до точки в 3 м от центра (pivot) объекта, затем короткие нажатия press <W|A|S|D> --duration 0.15 в сторону центра,
после каждого - расстояние по XZ до центра. 3 повтора на объект. Затем COLL-03: шаг назад 0,3 с.
Сравнение с rules: расстояние остановки vs (радиус коллайдера из collision_rules.md + 0,3 м радиус PigChef).
Время игры не меняется. Выход за безопасную высоту прерывает проверку.
"""
import csv
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import lib_sdk  # noqa: F401 (подменяет примитивы lib на вызовы SDK)
from lib import *  # noqa

PLAYER_R = 0.3
STAGE_D = 3.0
STEP_S = 0.15
MAX_STEPS = 30
NOPROG = 0.05          # шаг считается «без продвижения», если расстояние уменьшилось не более чем на это
STOP_RUN = 3           # столько шагов подряд без продвижения = упор
CROSS_M = 0.3          # проекция на исходное направление меньше -CROSS_M = ушёл на другую сторону
DEEP_LIMIT = -20.0     # аварийный порог для навигации (дно у скал уходит ниже -12, это не провал)
MIN_STOP = 0.3         # критерий COLL-02: упор при >= 0,3 м от центра
INSIDE_TOL = 0.25      # допуск на смещение центра коллайдера от pivot (до 0,22 м по collision_rules.md)
BACK_MIN = 0.5         # COLL-03

# имя, фильтр позиции из collision_inventory.csv (x, z), радиус капсулы из collision_rules.md (None - Box/Mesh)
OBJECTS = [
    ("Boat", (-203.21, -377.53), None, "BoxCollider x3 (лодка)"),
    ("Palm (3)", (-199.02, -389.99), 0.63, "CapsuleCollider r=0.63"),
    ("Palm (4)", (-201.11, -392.61), 0.63, "CapsuleCollider r=0.63"),
    ("Palm (2)", (-197.33, -393.49), 0.63, "CapsuleCollider r=0.63"),
    ("BeachPalm(Polybrush Clone)", (-197.95, -394.87), 0.28, "CapsuleCollider r=0.28"),
    ("Palm2(Polybrush Clone)", (-202.78, -395.03), 0.72, "CapsuleCollider r=0.72 (19 м от старта)"),
    ("Palm (5)", (-202.05, -399.66), 0.63, "CapsuleCollider r=0.63"),
    ("Palm2(Polybrush Clone)", (-201.02, -402.44), 0.72, "CapsuleCollider r=0.72 (26 м от старта)"),
    ("BigRock2 (4)", (-163.11, -360.41), None, "MeshCollider"),
    ("BigRock (8)", (-140.51, -364.05), None, "MeshCollider"),
]


def locate(name, xz):
    objs = find_all(value=name)
    if not isinstance(objs, list) or not objs:
        return None
    best = min(objs, key=lambda o: math.hypot(o["worldX"] - xz[0], o["worldZ"] - xz[1]))
    if math.hypot(best["worldX"] - xz[0], best["worldZ"] - xz[1]) > 2.0:
        return None
    return best


def pstate():
    r = get_prop(PLAYER, "UOP1.StateMachine.StateMachine", "_currentState._originSO.name", assembly="UOP1.StateMachine")
    return (r.get("data") or {}).get("value")


def dump_stuck(name, rep, why):
    """Сохранить данные зависания (как BUG_sliding_stuck_*.json) и вернуть описание."""
    g = lambda c, p, a="Assembly-CSharp": (get_prop(PLAYER, c, p, assembly=a).get("data") or {}).get("value")
    ev = {"объект": name, "повтор": rep, "причина": why, "когда": datetime.datetime.now().isoformat(timespec="seconds"),
          "позиция_игрока": player_pos(), "позиция_объекта": wpos(name), "состояние": pstate(),
          "lastHit.collider": g("Protagonist", "lastHit.collider.name"),
          "lastHit.normal": [g("Protagonist", "lastHit.normal." + a) for a in "xyz"],
          "lastHit.point": [g("Protagonist", "lastHit.point." + a) for a in "xyz"]}
    fn = os.path.join(LOGS, "BUG_sliding_stuck_%s_sdk.json" % name.replace(" ", "").replace("(", "").replace(")", ""))
    json.dump(ev, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return ev


def basis():
    f = cam_forward()
    return f, (f[1], -f[0])


def key_toward(vx, vz, fwd, right):
    cf = vx * fwd[0] + vz * fwd[1]
    cr = vx * right[0] + vz * right[1]
    if abs(cf) >= abs(cr):
        return "W" if cf > 0 else "S"
    return "D" if cr > 0 else "A"


OPP = {"W": "S", "S": "W", "A": "D", "D": "A"}


def goto(target, tol=0.7, max_s=150):
    """Грубый подход к точке: ступенчато вдоль доминирующей оси камеры; при застревании - боковой обход."""
    t_end = time.time() + max_s
    fwd, right = basis()
    stuck, n, frozen = 0, 0, 0
    last = player_pos()
    while time.time() < t_end:
        p = player_pos()
        if p[1] < DEEP_LIMIT:
            raise RuntimeError("игрок ниже безопасной высоты %s" % (p,))
        vx, vz = target[0] - p[0], target[1] - p[2]
        d = math.hypot(vx, vz)
        if d <= tol:
            return True, d
        n += 1
        if n % 5 == 0:
            fwd, right = basis()
        moved = dist_xz(p, last)
        if n > 1 and moved < 0.15:
            stuck += 1
        else:
            stuck = 0
        if n > 1 and moved < 0.01:
            frozen += 1
            if frozen >= 4:
                raise RuntimeError("персонаж не двигается (состояние: %s): проверка невозможна" % pstate())
        else:
            frozen = 0
        last = p
        k = key_toward(vx, vz, fwd, right)
        if stuck >= 2:
            # боковой обход: перпендикулярно текущему направлению
            side = {"W": "D", "S": "A", "A": "W", "D": "S"}[k] if (n // 4) % 2 == 0 else {"W": "A", "S": "D", "A": "S", "D": "W"}[k]
            press(side, 0.8)
            time.sleep(0.2)
            if stuck >= 10:
                return False, d
            continue
        press(k, max(0.15, min(1.0, d / 3.6 - 0.2)))
        time.sleep(0.2)
    return False, d


def approach(center, u0, tag, fh):
    """Короткие шаги по 0,15 с к центру. Возвращает (причина, расстояние остановки, шаги)."""
    fwd, right = basis()
    rows = []
    p = player_pos()
    d_prev = dist_xz(p, (center[0], 0, center[1]))
    rows.append((0, "-", round(d_prev, 3), 0.0, round((p[0] - center[0]) * u0[0] + (p[2] - center[1]) * u0[1], 3)))
    noprog = 0
    reason = "лимит %d шагов" % MAX_STEPS
    stop_d = None
    for i in range(1, MAX_STEPS + 1):
        if i % 8 == 0:
            fwd, right = basis()
        vx, vz = center[0] - p[0], center[1] - p[2]
        k = key_toward(vx, vz, fwd, right)
        press(k, STEP_S)
        time.sleep(0.25)
        q = player_pos()
        if q[1] < DEEP_LIMIT:
            reason = "игрок ниже безопасной высоты"
            rows.append((i, k, None, None, None))
            raise RuntimeError(reason)
        d = dist_xz(q, (center[0], 0, center[1]))
        proj = (q[0] - center[0]) * u0[0] + (q[1 + 1] - center[1]) * u0[1]
        step = dist_xz(q, p)
        rows.append((i, k, round(d, 3), round(step, 3), round(proj, 3)))
        progress = d_prev - d
        noprog = noprog + 1 if progress <= NOPROG else 0
        p, d_prev = q, d
        if proj <= -CROSS_M:
            reason = "прошёл на другую сторону центра (проекция %.2f м)" % proj
            stop_d = d
            break
        if noprog >= STOP_RUN:
            reason = "упор: %d шага подряд без продвижения" % STOP_RUN
            stop_d = d
            break
    if all((r[3] or 0) < 0.01 for r in rows[1:]):
        reason = "персонаж не сдвинулся ни на одном шаге (состояние: %s): это не упор, результат недействителен" % pstate()
        stop_d = None
    with open(fh, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["шаг", "клавиша", "расстояние_до_центра_м", "смещение_за_шаг_м", "проекция_на_направление_подхода_м"])
        w.writerows(rows)
    return reason, (stop_d if stop_d is not None else rows[-1][2]), rows


def backoff(center):
    """COLL-03: шаг назад 0,3 с: смещение >= 0,5 м."""
    p0 = player_pos()
    fwd, right = basis()
    k = OPP[key_toward(center[0] - p0[0], center[1] - p0[2], fwd, right)]
    press(k, 0.3)
    time.sleep(0.4)
    p1 = player_pos()
    return dist_xz(p0, p1)


def main():
    run = run_no_from_argv()
    only = sys.argv[2].split(",") if len(sys.argv) > 2 and sys.argv[2] else None
    nreps = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    S = Suite("COLL02_sdk", run)
    reset_input()
    set_time_scale(1)
    passive = Passive()
    summary = []
    halted = False
    for idx, (name, xz, radius, desc) in enumerate(OBJECTS):
        if only and (name not in only and ('%s@%d' % (name, idx + 1)) not in only):
            continue
        tag = "%02d_%s" % (idx + 1, name.replace(" ", "").replace("(", "").replace(")", ""))
        cid = "COLL-02 %s%s" % (name, " (19 м)" if (name.startswith("Palm2") and xz[1] > -396) else (" (26 м)" if name.startswith("Palm2") else ""))
        t0 = time.time()
        try:
            o = locate(name, xz)
            if not o:
                S.rec(cid, UNCONF, "объект не найден в сцене рядом с (%s, %s)" % xz, t0)
                continue
            center = (o["worldX"], o["worldZ"])
            reps = []
            for rep in range(1, nreps + 1):
                p = player_pos()
                u = (p[0] - center[0], p[2] - center[1])
                n = math.hypot(*u) or 1.0
                u0 = (u[0] / n, u[1] / n)
                stage = (center[0] + u0[0] * STAGE_D, center[1] + u0[1] * STAGE_D)
                ok, dd = goto(stage)
                p = player_pos()
                u = (p[0] - center[0], p[2] - center[1])
                n = math.hypot(*u) or 1.0
                u0 = (u[0] / n, u[1] / n)
                start_d = dist_xz(p, (center[0], 0, center[1]))
                fh = os.path.join(LOGS, "COLL02_sdk_run%d_%s_rep%d.csv" % (run, tag, rep))
                reason, stop_d, rows = approach(center, u0, tag, fh)
                if stop_d is None:
                    raise RuntimeError(reason)
                back = backoff(center)
                st_after = pstate()
                if st_after == "Sliding" or back < 0.01:
                    ev = dump_stuck(name, rep, "после шага назад %.2f м, состояние %s" % (back, st_after))
                    S.rec(cid, UNCONF, "ОСТАНОВКА: персонаж завис у объекта в повторе %d: %s" % (rep, ev), t0, "цепочка остановлена по заданию; остальные объекты не проверялись и провалом не помечены")
                    halted = True
                    break
                S.say("  %s rep%d: старт %.2f м (точка подхода достигнута: %s), %s, расстояние остановки %.2f м, шаг назад %.2f м; состояние после шага назад: %s; ряд: %s" % (
                    name, rep, start_d, ok, reason, stop_d, back, st_after, [(r[0], r[2]) for r in rows]))
                reps.append({"start": round(start_d, 2), "staged": ok, "reason": reason, "stop": stop_d, "back": round(back, 2), "state_after": st_after,
                             "crossed": reason.startswith("прошёл"), "stopped": reason.startswith("упор"), "min_d": min(r[2] for r in rows if r[2] is not None)})
                # отойти ещё назад для следующего повтора (goto сам вернёт в точку 3 м)
            if halted:
                break
            stops = [r["stop"] for r in reps]
            crossed = sum(r["crossed"] for r in reps)
            stopped = sum(r["stopped"] and r["stop"] >= MIN_STOP for r in reps)
            backs = [r["back"] for r in reps]
            expected = None if radius is None else round(radius + PLAYER_R, 2)
            inside = None
            if expected is not None:
                inside = sum((r["stop"] < expected - INSIDE_TOL) for r in reps)
            nums = ("центр %s; расстояния остановки по 3 повторам %s м; причины %s; ожидаемая остановка (радиус коллайдера из rules + 0,3) %s м; "
                    "остановок при >= %.1f м от центра %d из 3; проходов насквозь %d из 3; повторов внутри коллайдера (остановка < ожидаемой - %.2f) %s из 3; "
                    "шаг назад (COLL-03) %s м (порог >= %.1f)") % (
                tuple(round(c, 2) for c in center), [round(x, 2) for x in stops], [r["reason"] for r in reps], expected, MIN_STOP, stopped, crossed, INSIDE_TOL, inside, backs, BACK_MIN)
            if crossed >= 1:
                status = FAIL
            elif stopped == 3 and (inside is None or inside == 0):
                status = PASS
            elif inside == 3 or (stopped == 3):
                status = FAIL if inside == 3 else UNCONF
            else:
                status = UNCONF
            note = desc
            if inside:
                note += "; КАНДИДАТ В БАГ: персонаж остановился ближе, чем радиус коллайдера + 0,3 м (внутри коллайдера по данным rules)"
            S.rec(cid, status, nums, t0, note)
            back_ok = sum(b >= BACK_MIN for b in backs)
            S.rec(cid.replace("COLL-02", "COLL-03"), PASS if back_ok == 3 else FAIL,
                  "шаг назад 0,3 с после упора: %s м; повторов >= %.1f м: %d из 3" % (backs, BACK_MIN, back_ok), 0, "входит в COLL-02", dt=0)
            summary.append({"name": name, "cid": cid, "status": status, "reps": reps, "expected": expected, "inside": inside})
        except Exception as e:
            reset_input()
            if "не двигается" in str(e) or "не сдвинулся" in str(e):
                ev = dump_stuck(name, len(locals().get("reps") or []) + 1, str(e))
                S.rec(cid, UNCONF, "ОСТАНОВКА: %s" % ev, t0, "цепочка остановлена по заданию")
                break
            part = locals().get("reps") or []
            S.rec(cid, UNCONF, "ошибка выполнения после %d завершённых повторов: %s" % (len(part), [(round(r["stop"], 2), r["back"], r["state_after"]) for r in part]), t0,
                  "%s: %s" % (type(e).__name__, e))
            summary.append({"name": name, "cid": cid, "status": UNCONF, "reps": part, "error": str(e)})
    reset_input()
    with open(os.path.join(RESULTS_DIR, "COLL02_sdk_run%d_detail.json" % run), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1, default=str)
    passive.report(S, "PASSIVE-COLL02")
    S.finish()


if __name__ == "__main__":
    main()
