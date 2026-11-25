# -*- coding: utf-8 -*-
"""Блок A: достижима ли кромка Beach пешком (CC-75). Бот идёт по дну к точке в 2 м от кромки (запад, юг, восток), до 120 с на кромку.
Телепорт (T1) только для возврата на спавн. За кромку не идёт: аварийный стоп в 1,2 м от кромки."""
import os, sys, time, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastlib import *
from plan_route_lib import plan_rects

d = connect(); st = load_state()
d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, True)
RECTS = os.path.join(REPO_RES, "blockA_rects.json")
LIM = 120.0
# (имя, точка кромки на полу, направление наружу (x,z))
EDGES = [("Запад", (-253.3, -378.1), (-1, 0)), ("Юг", (-135.1, -496.3), (0, -1)), ("Восток", (-16.9, -378.1), (1, 0))]
SP = SPAWN
SKIP = ("Landmass", "Seabed", "Water", "PigChef", "AttackCollider", "Underwater", "InteractionDetector", "LocationExit")


def collect():
    if os.path.exists(RECTS):
        return json.load(open(RECTS, encoding="utf-8"))
    out = []; t0 = time.time()
    for comp in ["UnityEngine.BoxCollider", "UnityEngine.CapsuleCollider", "UnityEngine.MeshCollider", "UnityEngine.SphereCollider"]:
        for o in d.find_objects(By.COMPONENT, comp, enabled=False):
            if any(s in o.name for s in SKIP) or not (-280 <= o.worldX <= 10 and -525 <= o.worldZ <= -230):
                continue
            try:
                if o.get_component_property(comp, "isTrigger", PHYS):
                    continue
                g = lambda k: o.get_component_property(comp, k, PHYS, max_depth=2)
                out.append((g("bounds.center.x"), g("bounds.center.z"), g("bounds.extents.x"), g("bounds.extents.z"), o.name))
            except Exception:
                pass
    json.dump(out, open(RECTS, "w", encoding="utf-8"), ensure_ascii=False)
    print("коллайдеров собрано", len(out), "за", round(time.time() - t0), "с", flush=True)
    return out


rects = [r[:4] for r in collect()]


def yaw_cam(p):
    c = cam_pos(); return math.degrees(math.atan2(p[0] - c[0], p[2] - c[2]))


def ydiff(a, b): return (b - a + 180) % 360 - 180


cursor = [553]
last_rot = [0.0]


def rot(err):
    dx = int(max(-190, min(190, err / 0.24))); nx = cursor[0] + dx
    if nx < 80 or nx > 1026:
        return False
    d.key_down(AltKeyCode.Mouse1)
    d.move_mouse({"x": nx, "y": 189}, duration=0.1, wait=True)
    d.key_up(AltKeyCode.Mouse1); cursor[0] = nx
    return True


def pstate():
    try:
        return pig().get_component_property("UOP1.StateMachine.StateMachine", "_currentState._originSO.name", "UOP1.StateMachine")
    except Exception:
        return None


def tp_spawn():
    teleport("T1", SP[0], SP[1] + 0.3, SP[2]); time.sleep(3.5)


def walk(name, edge, out):
    inward = (-out[0], -out[1])
    stop = (edge[0] + inward[0] * 2.0, edge[1] + inward[1] * 2.0)
    r = {"edge": name, "edge_point": edge, "stop_point": stop}
    p = ppos(); r["start"] = p
    off = log_mark()
    wps = None
    for m in (0.5, 0.3, 0.1):
        wps, L, lat = plan_rects((p[0], p[2]), stop, rects, margin=m, h=0.5, pad=15.0, spacing=6.0, free_r=1.0)
        if wps:
            r["plan_margin"] = m; break
    if not wps:
        r["plan"] = "маршрута по AABB нет, ближайшая %s: идём напрямую" % (tuple(round(v, 1) for v in lat),)
        wps = [(p[0], p[2]), stop]
    else:
        r["plan"] = "длина %.0f м, боковое %.0f м, вехи %d" % (L, lat, len(wps))
    wi = 1 if len(wps) > 1 else 0
    t0 = time.time(); path = 0.0; last = p; miny = p[1]; tr = []
    d_at = {}; verdict = None; reason = ""; replans = 0; stuck_t = time.time(); stuck_ref = p
    cursor[0] = 553
    d.move_mouse({"x": 553, "y": 189}, duration=0.1, wait=True)
    d.key_down(AltKeyCode.W)
    try:
        while True:
            el = time.time() - t0
            p = ppos(); path += dxz(p, last); last = p; miny = min(miny, p[1])
            dtarget = dxz(p, (stop[0], 0, stop[1]))
            for mark in (60, 120):
                if el >= mark and mark not in d_at:
                    d_at[mark] = round(dtarget, 1)
            to_edge = (edge[0] - p[0]) * out[0] + (edge[1] - p[2]) * out[1]
            if dtarget <= 1.0:
                verdict, reason = "Достижима пешком", "дошёл до точки в 2 м от кромки (до точки %.2f м, до кромки %.2f м)" % (dtarget, to_edge); break
            if to_edge < 1.2:
                verdict, reason = "Достижима пешком", "аварийный стоп: до кромки %.2f м" % to_edge; break
            if el > LIM:
                verdict, reason = "Не подтверждено", "лимит %d с без застревания, расстояние до точки %.1f м" % (LIM, dtarget); break
            if not tr or el - tr[-1][0] >= 2.0:
                tr.append((round(el, 1), round(p[0], 1), round(p[1], 1), round(p[2], 1), round(dtarget, 1)))
            if pstate() == "Sliding":
                verdict, reason = "Не достижима", "Sliding в (%.1f; %.1f; %.1f), расстояние до точки %.1f м" % (p[0], p[1], p[2], dtarget); break
            wp = wps[wi]
            if dxz(p, (wp[0], 0, wp[1])) <= 1.5 and wi < len(wps) - 1:
                wi += 1; wp = wps[wi]
            hd = math.degrees(math.atan2(wp[0] - p[0], wp[1] - p[2]))
            e = ydiff(yaw_cam(p), hd)
            if abs(e) > 10 and time.time() - last_rot[0] >= 0.6:   # камера доезжает с задержкой: не чаще раза в 0,6 с и с коэффициентом 0,6
                last_rot[0] = time.time()
                if not rot(0.6 * e):
                    k = AltKeyCode.D if e > 0 else AltKeyCode.A
                    d.key_down(k); time.sleep(0.25); d.key_up(k)
            time.sleep(0.12)
            if time.time() - stuck_t >= 5.0:
                if dxz(p, stuck_ref) < 1.0:
                    replans += 1
                    d.key_up(AltKeyCode.W)
                    key("S", 0.3); key("A" if replans % 2 else "D", 0.6)
                    wps2, L2, lat2 = plan_rects((p[0], p[2]), stop, rects, margin=0.3, h=0.25, pad=10.0, spacing=5.0, free_r=0.8)
                    if wps2:
                        wps = wps2; wi = 1 if len(wps2) > 1 else 0
                    d.key_down(AltKeyCode.W)
                    if replans >= 6:
                        verdict, reason = "Не достижима", "застрял в (%.1f; %.1f; %.1f) после %d обходов, до точки %.1f м" % (p[0], p[1], p[2], replans, dtarget); break
                stuck_t = time.time(); stuck_ref = p
    finally:
        d.key_up(AltKeyCode.W)
        try:
            d.reset_input()
        except Exception:
            pass
    r.update({"verdict": verdict, "reason": reason, "seconds": round(time.time() - t0, 1), "path_m": round(path, 1), "min_y": round(miny, 2),
              "dist_at_60s": d_at.get(60), "dist_at_120s": d_at.get(120), "final_pos": tuple(round(v, 2) for v in ppos()), "replans": replans,
              "log": log_since(off), "trace": tr})
    return r


res = {}
for name, edge, out in EDGES:
    tp_spawn()
    try:
        r = walk(name, edge, out)
    except StopRun:
        raise
    except Exception as e:
        r = {"edge": name, "verdict": "Не подтверждено", "reason": "ошибка: %s: %s" % (type(e).__name__, str(e)[:150])}
    res[name] = r
    json.dump(res, open(os.path.join(REPO_RES, "blockA_detail2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    v = r.get("verdict")
    verdict = v if v != "Не достижима" else "Не достижима (%s)" % r.get("reason", "")
    md_row("A-кромка %s (попытка 2)" % name, verdict, "время %s с, путь %s м, min y %s, расстояние до точки через 60/120 с: %s/%s, конечная позиция %s, обходов %s, исключений %s, ошибок %s; причина: %s; план: %s" % (
        r.get("seconds"), r.get("path_m"), r.get("min_y"), r.get("dist_at_60s"), r.get("dist_at_120s"), r.get("final_pos"), r.get("replans"),
        (r.get("log") or {}).get("exceptions"), (r.get("log") or {}).get("errors"), r.get("reason"), r.get("plan")), "blockA_detail2.json")
tp_spawn()
d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, st.get("orig_autoSync", False))
print("блок A готов")
