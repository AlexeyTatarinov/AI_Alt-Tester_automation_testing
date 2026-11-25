# -*- coding: utf-8 -*-
"""Этап 5: BND-05 (детектор падения), BND-00 (зонд края), BND-01..04 (шаг наружу), BND-07 (возврат на спавн)."""
import os, sys, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastlib import *

d = connect(); st = load_state(); M = st["tp_method"]
d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, True)

def detect_fall(series):
    """падение = y < -25 или скачок > 3 м за шаг; первые 3 с после телепорта (приземление) не считаются скачком"""
    why = None
    for i, s in enumerate(series):
        if s["y"] < -25: why = "y<-25 на t=%s" % s["t"]; break
        if i > 0 and s["t"] >= 3.0 and abs(s["y"] - series[i - 1]["y"]) > 3.0: why = "скачок %.1f м на t=%s" % (series[i]["y"] - series[i - 1]["y"], s["t"]); break
    return why

def watch(seconds, t0=None, old_id=None):
    t0 = t0 or time.perf_counter(); out = []; new_id = None
    while time.perf_counter() - t0 < seconds:
        l = pigs()
        if l:
            o = l[0]; p = ppos(o)
            if old_id is not None and o.id != old_id and new_id is None: new_id = o.id
            out.append({"t": round(time.perf_counter() - t0, 2), "x": round(p[0], 2), "y": round(p[1], 2), "z": round(p[2], 2), "n": len(l)})
        time.sleep(0.5)
    return out, new_id

def bnd07(label):
    off = log_mark()
    r = tp_and_check(M, (SPAWN[0], SPAWN[1] + 0.3, SPAWN[2]), "BND-07 после " + label)
    p0 = ppos(); step_dir((-1, 0), 0.3); moved = round(dxz(p0, ppos()), 2)
    r["step_m"] = moved; r["ok"] = bool(r["ok"] and moved >= 0.5)
    return r

# ---- BND-05
def bnd05():
    o = pig(); old = o.id
    teleport(M, -135.1, -35.0, -378.1); t0 = time.perf_counter()
    series, new_id = watch(10.0, t0, old)
    y_end = series[-1]["y"]; fall = detect_fall(series)
    ok = y_end < -100 and new_id is None and fall is not None
    out = {"verdict": "Пройдено" if ok else "Не пройдено",
           "numbers": "y через 10 с = %s (норма < -100); респавна нет=%s; детектор падения сработал: %s; y-ряд (t,y)=%s" % (y_end, new_id is None, fall, [(s["t"], s["y"]) for s in series][::3]),
           "evidence": "run1_bnd05.json"}
    if not ok: out["screenshot"] = shot("BND-05_fail")
    json.dump(series, open(os.path.join(REPO_RES, "run1_bnd05.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    shared_fall["bnd05"] = y_end
    return out
shared_fall = {}
case("BND-05", bnd05)
r7 = bnd07("BND-05"); print("BND-07 после BND-05:", r7.get("ok"), r7.get("xz_2"), r7.get("step_m"), flush=True)
bnd07_rows = [{"after": "BND-05", "ok": r7.get("ok"), "xz_2": r7.get("xz_2"), "grounded": r7.get("grounded_3s"), "step_m": r7.get("step_m")}]

# ---- BND-00 + BND-01..04
EDGES = [("BND-01", "Запад", lambda off: (FRAME["x0"] + off, -378.1), (-1, 0)),
         ("BND-02", "Восток", lambda off: (FRAME["x1"] - off, -378.1), (1, 0)),
         ("BND-03", "Юг", lambda off: (-135.1, FRAME["z0"] + off), (0, -1)),
         ("BND-04", "Север", lambda off: (-135.1, FRAME["z1"] - off), (0, 1))]

def probe(point_fn):
    """BND-00: телепорт на y=40, ждать isGrounded до 6 с; первая точка с полом"""
    tries = []
    for off in (2, 5, 10, 20):
        x, z = point_fn(off)
        teleport(M, x, 40.0, z); t0 = time.perf_counter(); g = False; y = None
        while time.perf_counter() - t0 < 6.0:
            time.sleep(0.25)
            o = pig(); p = ppos(o); y = p[1]
            if grounded(o): g = True; break
            if y < -40: break
        tries.append({"offset": off, "x": x, "z": z, "grounded": g, "y": round(y, 2)})
        if g: return {"found": True, "x": p[0], "y": p[1], "z": p[2], "offset": off, "tries": tries}
    return {"found": False, "tries": tries}

def edge_case(cid, name, point_fn, out_vec):
    pr = probe(point_fn)
    if not pr["found"]:
        return {"verdict": "Не подтверждено", "numbers": "BND-00: пола нет ни на одном отступе (2/5/10/20 м): %s" % pr["tries"], "evidence": "run1_bnd_%s.json" % cid}
    off = log_mark()
    teleport(M, pr["x"], pr["y"] + 0.3, pr["z"]); time.sleep(3.0)
    o = pig(); old = o.id; p_before = ppos(o)
    t0 = time.perf_counter()
    step_dir(out_vec, 0.3)
    p_after = ppos(pig()); moved = round(dxz(p_before, p_after), 2)
    series, new_id = watch(10.0, t0, old)
    # ряд точек на 1/3/10 с
    def at(ts):
        c = min(series, key=lambda s: abs(s["t"] - ts)); return c["y"]
    fall = detect_fall(series); lg = log_since(off)
    fell = fall is not None
    y_end = series[-1]["y"]
    info = "точка края: x=%.1f y=%.2f z=%.1f (отступ %d м); смещение за шаг %s м; y через 1/3/10 с = %s/%s/%s; новый PigChef за 10 с=%s; падение=%s; исключений %d" % (pr["x"], pr["y"], pr["z"], pr["offset"], moved, at(1.0), at(3.0), at(10.0), new_id is not None, fall, lg["exceptions"])
    if not fell:
        verdict = "Пройдено"
    elif new_id is None:
        verdict = "Наблюдение: падение без респавна (вердикт за владельцем)"
    else:
        verdict = "Наблюдение: упал и вернулся через респавн"
    json.dump({"probe": pr, "series": series, "log": lg}, open(os.path.join(REPO_RES, "run1_bnd_%s.json" % cid), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    out = {"verdict": verdict, "numbers": info, "evidence": "run1_bnd_%s.json" % cid}
    if fell: out["screenshot"] = shot("%s_fall" % cid)
    out["fell"] = fell; out["y_end"] = y_end
    return out

edge_res = {}
for cid, name, pf, ov in EDGES:
    r = case(cid, edge_case, cid, name, pf, ov)
    edge_res[cid] = r
    if r.get("fell") or r.get("verdict", "").startswith("Не"):
        rr = bnd07(cid); bnd07_rows.append({"after": cid, "ok": rr.get("ok"), "xz_2": rr.get("xz_2"), "grounded": rr.get("grounded_3s"), "step_m": rr.get("step_m")})
        print("BND-07 после %s: ok=%s" % (cid, rr.get("ok")), flush=True)
json.dump(bnd07_rows, open(os.path.join(REPO_RES, "run1_bnd07.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
ok7 = all(r["ok"] for r in bnd07_rows)
add_result({"id": "BND-07", "verdict": "Пройдено" if ok7 else "Не пройдено", "numbers": "возвратов на спавн %d, все прошли=%s: %s" % (len(bnd07_rows), ok7, bnd07_rows), "evidence": "run1_bnd07.json"})
teleport(M, SPAWN[0], SPAWN[1] + 0.3, SPAWN[2])
