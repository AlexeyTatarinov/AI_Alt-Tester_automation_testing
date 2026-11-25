# -*- coding: utf-8 -*-
"""Общая библиотека прогона 1 быстрых кейсов (CC-74/75/76/78, DTH-01/02 из CC-77).
Python SDK AltTester-Driver 2.4.1; запуск интерпретатором scripts\\sdk_smoke\\.venv. Игру и проект не меняет."""
import os, sys, time, json, re, shutil, hashlib, datetime, math, traceback

from alttester import AltDriver, By, AltKeyCode

REPO_RES = "C:/Users/Aotat/Desktop/Test_Ai/Reports_2026-11-21/results/run5_new3_20261123"
TESTAI = r"C:\Users\Aotat\Desktop\Test_Ai"
EDLOG = r"C:\Users\Aotat\AppData\Local\Unity\Editor\Editor.log"
SAVE_DIRS = [r"C:\Users\Aotat\AppData\LocalLow\Unity Technologies\Chop Chop", r"C:\Users\Aotat\AppData\LocalLow\Unity Open Projects\Chop Chop"]
STATE_F = os.path.join(REPO_RES, "run5_state.json")
RES_F = os.path.join(REPO_RES, "run5_results.json")
SHOTS = os.path.join(REPO_RES, "shots")
os.makedirs(REPO_RES, exist_ok=True); os.makedirs(SHOTS, exist_ok=True)

CORE = "UnityEngine.CoreModule"; PHYS = "UnityEngine.PhysicsModule"; ASM = "Assembly-CSharp"

# --- цели из раздела 3.1 документа
SPAWN = (-195.58, -9.42, -376.9)
BOAT = (-203.21, -9.69, -377.53)
HARE = (-138.81, -3.85, -326.21)
POT = (-144.25, -4.39, -324.21)
EXIT = (-62.83, -4.81, -358.87)
EXIT_CENTER = (-62.83, -4.31, -358.87)
ENTRANCE = (-58.27, -5.32, -369.79)
STOP_V3 = (-73.8, -4.65, -359.35)
FRAME = dict(x0=-273.3, x1=3.1, z0=-516.3, z1=-239.9)


class StopRun(Exception):
    pass

class _Done(Exception):
    def __init__(self, r): super().__init__(); self.r = r


d = None
def connect():
    global d
    if d is None:
        d = AltDriver(host="127.0.0.1", port=13000, enable_logging=False, timeout=20)
    guard.SHARED = d
    return d


def now(): return datetime.datetime.now().strftime("%H:%M:%S")

def load_state():
    try: return json.load(open(STATE_F, encoding="utf-8"))
    except Exception: return {}

def save_state(s): json.dump(s, open(STATE_F, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def load_results():
    try: return json.load(open(RES_F, encoding="utf-8"))
    except Exception: return []

def add_result(r):
    res = load_results()
    res = [x for x in res if x.get("id") != r["id"]] + [r]
    json.dump(res, open(RES_F, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("[%s] %s -> %s | %s" % (now(), r["id"], r["verdict"], str(r.get("numbers", ""))[:300]), flush=True)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16] if os.path.exists(p) else None

def save_hashes():
    out = {}
    for sd in SAVE_DIRS:
        for f in ("save.chop", "save.chop.bak"):
            out[os.path.join(sd, f)] = sha(os.path.join(sd, f))
    return out


# --- Editor.log
def log_mark():
    return os.path.getsize(EDLOG)

BENIGN = ("AltTester|",)
def log_since(offset):
    with open(EDLOG, "rb") as f:
        f.seek(offset); txt = f.read().decode("utf-8", errors="replace")
    lines = [l for l in txt.split("\n") if l.strip() and not any(b in l for b in BENIGN)]
    exc = [l for l in lines if re.match(r"^\s*[A-Za-z0-9_.]*Exception\b", l)]
    err = [l for l in lines if re.search(r"(?i)^\s*(\[error\]|error\b)|: error |assertion failed", l)]
    cc = [l for l in lines if "CharacterController.Move called on inactive" in l]
    loc = [l for l in lines if "LocationEntry that doesn't exist" in l]
    warn = [l for l in lines if re.search(r"(?i)warning", l) and l not in cc and l not in loc]
    return {"lines": len(lines), "exceptions": len(exc), "errors": len(err), "cc_inactive_warnings": len(cc),
            "cc67_locationentry": len(loc), "warnings_other": len(warn),
            "samples": [l.strip()[:200] for l in (exc + err)[:5]]}


# --- объекты игрока
def pigs():
    return connect().find_objects(By.NAME, "PigChef(Clone)", enabled=False)

def pig():
    l = pigs()
    return l[0] if l else None

def _retry(fn, n=6, pause=0.25):
    last = None
    for _ in range(n):
        try:
            return fn()
        except Exception as e:
            if type(e).__name__ not in ("NotFoundException", "ObjectNotFoundException"):
                raise
            last = e; time.sleep(pause)
    raise last

def ppos(o=None):
    def f():
        oo = o or pig()
        oo.update_object()
        return (oo.worldX, oo.worldY, oo.worldZ)
    return _retry(f)

def dxz(a, b): return math.hypot(a[0] - b[0], a[2] - b[2])
def dist3(a, b): return math.dist(a, b)

def grounded(o):
    return bool(o.get_component_property("UnityEngine.CharacterController", "isGrounded", PHYS))

def cc_enabled(o):
    return bool(o.get_component_property("UnityEngine.CharacterController", "enabled", PHYS))

def health(o=None):
    o = o or pig()
    return o.get_component_property("Damageable", "_currentHealthSO.CurrentHealth", ASM)

def scenes():
    return list(connect().get_all_loaded_scenes())

def shot(name):
    p = os.path.join(SHOTS, name + ".png")
    try:
        connect().get_png_screenshot(p)
    except Exception as e:
        return "ошибка скриншота: %s" % e
    return p


# --- телепорт
def _set_pos(o, x, y, z):
    o.set_component_property("UnityEngine.Transform", "position", CORE, {"x": x, "y": y, "z": z})

def teleport(method, x, y, z):
    o = pig()
    if method == "T1":
        _set_pos(o, x, y, z)
    elif method == "T2":
        o.set_component_property("UnityEngine.CharacterController", "enabled", PHYS, False)
        _set_pos(o, x, y, z)
        o.set_component_property("UnityEngine.CharacterController", "enabled", PHYS, True)
    elif method == "T3":
        cur = ppos(o)
        o.call_component_method("UnityEngine.Transform", "Translate", CORE,
                                [str(x - cur[0]), str(y - cur[1]), str(z - cur[2]), "World"],
                                ["System.Single", "System.Single", "System.Single", "UnityEngine.Space"])
    else:
        raise ValueError(method)


def tp_and_check(method, target, label="", ground_expected=True, y_tol=2.0, window=3.2):
    """Телепорт + проверки критерия 2.3: XZ<=2 м через 0,5 и 2 с, isGrounded и |dy|<=2 через 3 с, CC включён,
    PigChef один, в логе 0 исключений. Возвращает словарь с числами и флагом ok."""
    off = log_mark()
    t0 = time.perf_counter()
    r = {"target": target, "label": label, "method": method}
    try:
        teleport(method, *target)
    except Exception as e:
        r["error"] = "%s: %s" % (type(e).__name__, str(e)[:200]); r["ok"] = False; return r
    t_call = time.perf_counter() - t0
    r["call_s"] = round(t_call, 3)
    samples = []; first_g = None
    def at(ts):
        while time.perf_counter() - t0 < ts: time.sleep(0.02)
    try:
        at(0.5); o = pig(); p05 = ppos(o); r["xz_0_5"] = round(dxz(p05, target), 2)
        g = grounded(o);
        if g and first_g is None: first_g = round(time.perf_counter() - t0, 2)
        t = 0.75
        while t < 2.0:
            at(t); o = pig(); g = grounded(o)
            if g and first_g is None: first_g = round(time.perf_counter() - t0, 2)
            t += 0.25
        at(2.0); o = pig(); p2 = ppos(o); r["xz_2"] = round(dxz(p2, target), 2)
        at(window - 0.1); o = pig(); p3 = ppos(o); g3 = grounded(o)
        if g3 and first_g is None: first_g = round(time.perf_counter() - t0, 2)
        r["grounded_3s"] = g3; r["time_to_grounded_s"] = first_g
        r["y_3s"] = round(p3[1], 2); r["dy"] = round(abs(p3[1] - target[1]), 2)
        r["cc_enabled"] = cc_enabled(o); r["pig_count"] = len(pigs())
    except Exception as e:
        r["error"] = "%s: %s" % (type(e).__name__, str(e)[:200]); r["ok"] = False; return r
    r["log"] = log_since(off)
    ok = (r["xz_0_5"] <= 2.0 and r["xz_2"] <= 2.0 and r["cc_enabled"] and r["pig_count"] == 1 and r["log"]["exceptions"] == 0)
    if ground_expected:
        ok = ok and r["grounded_3s"] and r["dy"] <= y_tol
    r["ok"] = bool(ok)
    return r


# --- клавиши и шаги
def key(k, dur=0.1):
    return connect().press_key(getattr(AltKeyCode, k), power=1, duration=dur, wait=True)

def cam_pos():
    def f():
        o = connect().find_object(By.NAME, "Main Camera", enabled=False); o.update_object()
        return (o.worldX, o.worldY, o.worldZ)
    return _retry(f)

def choose_key(p, tgt):
    c = cam_pos()
    f = (p[0] - c[0], p[2] - c[2]); n = math.hypot(*f) or 1.0; f = (f[0] / n, f[1] / n)
    r = (f[1], -f[0])
    v = (tgt[0] - p[0], tgt[1] - p[1]) if False else (tgt[0] - p[0], tgt[2] - p[2]); n = math.hypot(*v) or 1.0; v = (v[0] / n, v[1] / n)
    sc = {"W": v[0] * f[0] + v[1] * f[1], "S": -(v[0] * f[0] + v[1] * f[1]), "D": v[0] * r[0] + v[1] * r[1], "A": -(v[0] * r[0] + v[1] * r[1])}
    return max(sc, key=sc.get)

def step_towards(tgt, dur=0.15):
    p = ppos(); k = choose_key(p, tgt); key(k, dur); time.sleep(0.15)
    return k, ppos()

def step_dir(vec_xz, dur=0.3):
    """шаг в сторону мирового вектора (x,z) (не к точке)"""
    p = ppos(); tgt = (p[0] + vec_xz[0] * 5, p[1], p[2] + vec_xz[1] * 5)
    k = choose_key(p, tgt); key(k, dur); time.sleep(0.2)
    return k


def ui_obj(component):
    l = connect().find_objects(By.COMPONENT, component, enabled=False)
    return l[0] if l else None

def comp_active(component):
    """GameObject с компонентом активен в иерархии (find с enabled=True возвращает только активные)"""
    return len(connect().find_objects(By.COMPONENT, component, enabled=True)) > 0


import guard   # страховки от паузы (CC-83)

def pstate():
    try:
        return pig().get_component_property("UOP1.StateMachine.StateMachine", "_currentState._originSO.name", "UOP1.StateMachine")
    except Exception:
        return None

def approach_step(k="W", dur=0.3, settle=0.5):
    """GUARD-01: шаг подхода. Нажать движение, измерить сдвиг XZ; параллельно наблюдать Sliding. Возвращает dict."""
    sw = guard.SlideWatch(); p0 = ppos(); sw.tick(pstate())
    key(k, dur); t0 = time.time()
    while time.time() - t0 < settle:
        sw.tick(pstate()); time.sleep(0.1)
    p1 = ppos(); sw.tick(pstate())
    return {"key": k, "moved_m": round(dxz(p0, p1), 2), "p0": tuple(round(v, 2) for v in p0), "p1": tuple(round(v, 2) for v in p1), "slide": sw}

def case(cid, fn, *a, approach=True, **kw):
    t0 = time.time()
    guard.before_case(cid)      # проба «живости»; если игра стоит, бросает guard.Paused с отчётом
    h_before = save_hashes()                      # SAVE-05: хеш до кейса
    ap = None
    try:
        if approach:                                                  # GUARD-01: шаг подхода перед любым вердиктом
            try: ap = approach_step()
            except Exception as e: ap = {"moved_m": None, "error": "%s: %s" % (type(e).__name__, str(e)[:80]), "slide": guard.SlideWatch()}
            if ap["moved_m"] is None or ap["moved_m"] < guard.MIN_APPROACH_M:
                g = guard.judge("Пройдено", ap["moved_m"], ap["slide"])
                r = {"verdict": "Invalid", "numbers": "GUARD-01: шаг подхода (%s 0,3 с) сдвинул игрока на %s м (< %.1f): игрок заморожен (диалог/меню/пауза?), кейс не выполнялся; %s" % (ap.get("key"), ap["moved_m"], guard.MIN_APPROACH_M, ap.get("error", ""))}
                r.update({"guard01": g})
                raise _Done(r)
        r = fn(*a, **kw)
        if ap is not None:
            g = guard.judge(r.get("verdict", ""), ap["moved_m"], ap["slide"]); r["guard01"] = g
            if g["verdict"] == "Invalid": r["verdict"] = "Invalid"
            if g["sliding_gt3s"]: r["numbers"] = str(r.get("numbers", "")) + " [ФЛАГ: Sliding > 3 с, %.1f с]" % g["sliding_max_s"]
    except _Done as dn:
        r = dn.r
    except (StopRun, guard.Paused):
        raise
    except Exception as e:
        name = type(e).__name__
        if name in ("CommandResponseTimeoutException", "NoAppConnected", "ConnectionError", "AppDisconnectedError", "ConnectionTimeoutError"):
            rep = guard.stall_report(cid, why="тайм-аут SDK внутри кейса: " + name)
            add_result({"id": cid, "verdict": "Не проверено", "numbers": "связь с игрой пропала: %s; классификатор: %s; %s" % (name, rep.get("klass"), rep.get("probable_cause")), "evidence": rep.get("log_tail_copy", "")})
            guard.after_case(cid, "BLOCKED", rep.get("probable_cause"))
            raise guard.Paused(rep)
        r = {"id": cid, "verdict": "Не проверено", "numbers": "ошибка скрипта: %s: %s" % (name, str(e)[:200]), "evidence": traceback.format_exc()[-500:]}
    h_after = save_hashes()
    r["save05"] = {"before": h_before, "after": h_after, "changed": h_before != h_after}
    r.setdefault("id", cid); r["seconds"] = round(time.time() - t0, 1); r["finished"] = now()
    add_result(r)
    guard.after_case(cid, r.get("verdict"), str(r.get("numbers", ""))[:150])
    return r


MD_F = os.path.join(REPO_RES, "new2_fast_20261123_rows.md")
def md_row(cid, verdict, numbers, evidence=""):
    """дописать строку таблицы в отчёт и в run5_results.json"""
    add_result({"id": cid, "verdict": verdict, "numbers": numbers, "evidence": evidence})
    with open(MD_F, "a", encoding="utf-8") as f:
        f.write("| %s | %s | %s | %s |\n" % (cid, verdict, str(numbers).replace("|", "/").replace("\n", " "), str(evidence).replace("|", "/")))

def md_note(text):
    with open(MD_F, "a", encoding="utf-8") as f:
        f.write("\n" + text + "\n\n")

