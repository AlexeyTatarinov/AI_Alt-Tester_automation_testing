# -*- coding: utf-8 -*-
"""stage8: статические данные уровней Chop Chop через AltTester Python SDK 2.4.1 (только чтение).

Запуск (интерпретатор scripts\\sdk_smoke\\.venv):
  python collect.py --probe                 # текущая сцена: каждый вызов API один раз, печать что работает
  python collect.py                         # все 10 локаций меню читов, с продолжением (resume)
  python collect.py --location Forest       # одна локация (можно через запятую)
  python collect.py --redo --location Beach # пересобрать локацию заново
Результат: Reports_2026-11-21\\results\\stage8_levels\\levels.json (пишется по ходу).

Правила: только чтение. Навигация только меню читов (elib.goto -> module_snapshot.cheat_go).
Нет set_component_property, нет телепорта, нет чтения больших массивов (vertices/triangles не читаются;
только triangles.Length внутри Unity для уникальных читаемых мешей, отключается --no-tris).
Все команды драйвера ограничены RATE вызовами в секунду (патч WebsocketConnection.send).
"""
import os, sys, json, time, math, re, argparse, statistics, traceback, collections

RES = r"Test_Ai\Reports_2026-11-21\results\stage8_levels"
OUT_F = os.path.join(RES, "levels.json")
PROBE_F = os.path.join(RES, "probe.json")
MODULES = r"Test_Ai\scripts\modules"
ASSETS = r"C:\Games\ChopChop\UOP1_Project\Assets"
GLOBAL_SCENE_FILES = (r"Scenes\Managers\PersistentManagers.unity", r"Scenes\Managers\Gameplay.unity")

CORE = "UnityEngine.CoreModule"; PHYS = "UnityEngine.PhysicsModule"; ED = "UnityEditor.CoreModule"
ORDER = ["Field_Hill", "Field_Farms", "Town_Market", "Town_Upper", "Town_Inner", "Forest",
         "Mountain_Path_bottom", "Mountain_Cave", "Mountain_Path_shaft", "Beach"]
GLOBAL_SCENES = ("PersistentManagers", "Gameplay", "DontDestroyOnLoad")
PLAYER_ROOTS = ("PigChef(Clone)",)
TOOL_ROOTS = ("AltTesterPrefab", "AltTester", "AltTesterPrefab(Clone)")
READ_CATS = ("location", "location_clone", "location_unverified", "unknown")   # для них читаем подробности
LOCAL_CATS = ("location", "location_clone", "location_unverified")              # входят в итоги локации

# слои из ProjectSettings/TagManager.asset: 2 Ignore Raycast, 4 Water, 5 UI, 7 Ground, 9 Characters
L_IGNORE, L_WATER, L_UI, L_GROUND, L_CHARS = 2, 4, 5, 7, 9
MASK_SOLID = ~((1 << L_IGNORE) | (1 << L_WATER) | (1 << L_UI) | (1 << L_CHARS))   # -569
MASK_GROUND = 1 << L_GROUND
MASK_WATER = 1 << L_WATER
V3 = "UnityEngine.Vector3, UnityEngine.CoreModule"
QTI = "UnityEngine.QueryTriggerInteraction, UnityEngine.PhysicsModule"

# компоненты для подсчёта: ключ -> (полное имя, сборка)
COMPS = collections.OrderedDict([
    ("MeshRenderer", ("UnityEngine.MeshRenderer", CORE)),
    ("SkinnedMeshRenderer", ("UnityEngine.SkinnedMeshRenderer", CORE)),
    ("MeshFilter", ("UnityEngine.MeshFilter", CORE)),
    ("BoxCollider", ("UnityEngine.BoxCollider", PHYS)),
    ("SphereCollider", ("UnityEngine.SphereCollider", PHYS)),
    ("CapsuleCollider", ("UnityEngine.CapsuleCollider", PHYS)),
    ("MeshCollider", ("UnityEngine.MeshCollider", PHYS)),
    ("CharacterController", ("UnityEngine.CharacterController", PHYS)),
    ("TerrainCollider", ("UnityEngine.TerrainCollider", "UnityEngine.TerrainPhysicsModule")),
    ("Terrain", ("UnityEngine.Terrain", "UnityEngine.TerrainModule")),
    ("Rigidbody", ("UnityEngine.Rigidbody", PHYS)),
    ("Light", ("UnityEngine.Light", CORE)),
    ("ReflectionProbe", ("UnityEngine.ReflectionProbe", CORE)),
    ("ParticleSystem", ("UnityEngine.ParticleSystem", "UnityEngine.ParticleSystemModule")),
    ("Animator", ("UnityEngine.Animator", "UnityEngine.AnimationModule")),
    ("LODGroup", ("UnityEngine.LODGroup", CORE)),
    ("Camera", ("UnityEngine.Camera", CORE)),
    ("AudioSource", ("UnityEngine.AudioSource", "UnityEngine.AudioModule")),
])
COLLIDER_KEYS = ("BoxCollider", "SphereCollider", "CapsuleCollider", "MeshCollider", "CharacterController", "TerrainCollider")


# ---------------------------------------------------------------- ограничение частоты
class Rate:
    def __init__(self, per_s):
        self.min_dt = 1.0 / per_s; self.last = 0.0; self.calls = 0; self.t0 = time.time()
        self.recent = collections.deque(maxlen=200)

    def wait(self):
        w = self.min_dt - (time.time() - self.last)
        if w > 0:
            time.sleep(w)
        self.last = time.time(); self.calls += 1; self.recent.append(self.last)

    def per_s(self):
        if len(self.recent) < 2:
            return None
        dt = self.recent[-1] - self.recent[0]
        return round((len(self.recent) - 1) / dt, 2) if dt > 0 else None


RATE = Rate(20)


def install_throttle(per_s):
    RATE.min_dt = 1.0 / min(20.0, float(per_s))
    from alttester import _websocket
    orig = _websocket.WebsocketConnection.send
    if getattr(orig, "_stage8", False):
        return

    def send(self, data):
        RATE.wait()
        return orig(self, data)
    send._stage8 = True
    _websocket.WebsocketConnection.send = send


# ---------------------------------------------------------------- файлы
def now():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def jsave(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, default=str)
    os.replace(tmp, path)


def jload(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def global_names():
    """имена объектов из PersistentManagers.unity и Gameplay.unity (запасной способ, если scene.name не читается)"""
    names = set()
    for rel in GLOBAL_SCENE_FILES:
        try:
            txt = open(os.path.join(ASSETS, rel), encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        names |= set(re.findall(r"^\s*m_Name: (.+?)\s*$", txt, re.M))
        names |= set(re.findall(r"propertyPath: m_Name\s*\n\s*value: (.+?)\s*$", txt, re.M))
    names.discard("")
    return names


# ---------------------------------------------------------------- значения
def r3(v):
    return round(float(v), 3)


def as_vec(v):
    if isinstance(v, str):
        v = json.loads(v)
    return [r3(v["x"]), r3(v["y"]), r3(v["z"])]


def as_bounds(v):
    if isinstance(v, str):
        v = json.loads(v)
    return {"c": as_vec(v["center"]), "e": as_vec(v["extents"])}


def as_bool(v):
    if isinstance(v, bool):
        return v
    s = str(v).strip().strip('"').lower()
    if s in ("true", "false"):
        return s == "true"
    raise ValueError("не bool: %r" % (v,))


def as_int(v):
    if isinstance(v, bool):
        raise ValueError("bool вместо int")
    if isinstance(v, (int, float)):
        return int(v)
    return int(str(v).strip().strip('"'))


def as_len(v):
    if isinstance(v, str):
        v = json.loads(v)
    if not isinstance(v, list):
        raise ValueError("не список")
    return len(v)


def as_str(v):
    return None if v is None else str(v)


def short(v, n=200):
    s = json.dumps(v, ensure_ascii=False, default=str) if not isinstance(v, str) else v
    return s if len(s) <= n else s[:n] + "…(%d)" % len(s)


def is_err(v):
    return isinstance(v, str) and (v.startswith("ERR ") or v.startswith("OFF "))


class Reader:
    """адаптивное чтение: для поля берётся первый сработавший путь; если ни один путь не сработал на 3 объектах подряд
    (и ни разу не работал) — поле выключается до конца сцены. Ошибки возвращаются строкой 'ERR …'."""

    def __init__(self):
        self.mode = {}; self.fail = {}; self.last_err = {}; self.ok = collections.Counter()

    def get(self, o, comp, asm, field, alts, conv=None):
        key = comp + "." + field
        m = self.mode.get(key)
        if m == "off":
            return "OFF " + self.last_err.get(key, "")[:80]
        order = [m] if m is not None else range(len(alts))
        last = None
        for i in order:
            path, depth = alts[i]
            try:
                v = o.get_component_property(comp, path, asm, max_depth=depth)
                if conv is not None:
                    v = conv(v)
                self.mode[key] = i; self.fail[key] = 0; self.ok[key] += 1
                return v
            except Exception as e:
                last = "%s: %s" % (type(e).__name__, str(e)[:160])
        self.fail[key] = self.fail.get(key, 0) + 1; self.last_err[key] = last
        if m is None and self.fail[key] >= 3:
            self.mode[key] = "off"
        return "ERR " + str(last)

    def report(self, alts_of=None):
        out = {}
        for k in sorted(set(self.mode) | set(self.fail)):
            out[k] = {"mode": self.mode.get(k), "ok": self.ok.get(k, 0), "fail_streak": self.fail.get(k, 0), "last_err": self.last_err.get(k)}
        return out


F_BOUNDS = [("bounds", 2)]
F_CENTER = [("bounds.center", 1)]
F_EXTENTS = [("bounds.extents", 1)]
F_MATS = [("sharedMaterials.Length", 1), ("sharedMaterials", 1)]
F_SCENE = [("gameObject.scene.name", 1), ("gameObject.scene", 2)]


def conv_mats(v):
    if isinstance(v, list) or (isinstance(v, str) and v.strip().startswith("[")):
        return as_len(v)
    return as_int(v)


def ray(d, x, y, z, dist, mask):
    """Physics.Raycast(origin, down, dist, mask, Ignore) -> bool; вызов как в scripts\\stage6\\ray.py"""
    v = d.call_static_method("UnityEngine.Physics", "Raycast", PHYS,
                             [{"x": x, "y": y, "z": z}, {"x": 0, "y": -1, "z": 0}, dist, mask, "Ignore"],
                             [V3, V3, "System.Single", "System.Int32", QTI])
    return str(v).strip('"').lower() == "true"


def conv_scene(v):
    if isinstance(v, dict):
        return str(v["name"])
    if v is None:
        raise ValueError("None")
    return str(v)


def read_bounds(R, o, comp, asm):
    b = R.get(o, comp, asm, "bounds", F_BOUNDS, as_bounds)
    if not is_err(b):
        return b
    c = R.get(o, comp, asm, "bounds.center", F_CENTER, as_vec)
    e = R.get(o, comp, asm, "bounds.extents", F_EXTENTS, as_vec)
    if is_err(c) or is_err(e):
        return "ERR bounds: %s | %s" % (str(c)[:80], str(e)[:80])
    return {"c": c, "e": e}


def okey(o):
    return "%s|%.2f|%.2f|%.2f" % (o.name, o.worldX, o.worldY, o.worldZ)


# ---------------------------------------------------------------- состав сцены
class Membership:
    """категория объекта по корню иерархии: location / location_clone / player / global / tool / other:<scene> / unknown"""

    def __init__(self, scene, elems, R, gnames, log=print):
        self.scene = scene; self.by_tid = {}; self.root_cat = {}; self.root_scene = {}; self.cache = {}
        self.method = None; self.errors = 0
        for o in elems:
            self.by_tid[o.transformId] = o
        roots = [o for o in elems if not o.transformParentId or o.transformParentId not in self.by_tid]
        self.n_roots = len(roots)
        log("  корней иерархии: %d (объектов %d), читаю scene.name у корней" % (len(roots), len(elems)))
        for i, o in enumerate(roots):
            if o.name in PLAYER_ROOTS:
                self.root_cat[o.transformId] = "player"; continue
            if o.name in TOOL_ROOTS:
                self.root_cat[o.transformId] = "tool"; continue
            sn = R.get(o, "UnityEngine.Transform", CORE, "scene", F_SCENE, conv_scene)
            if not is_err(sn):
                self.method = "gameObject.scene.name"
                self.root_scene[o.transformId] = sn
                if sn in GLOBAL_SCENES:
                    cat = "global"
                elif sn == scene:
                    cat = "location_clone" if o.name.endswith("(Clone)") else "location"
                else:
                    cat = "other:" + sn
            else:
                self.errors += 1
                cat = "global_by_name" if o.name in gnames else "location_unverified"
                if self.method is None:
                    self.method = "names_from_unity_files"
            self.root_cat[o.transformId] = cat
            if i % 100 == 99:
                log("   … корней %d/%d, %s выз/с" % (i + 1, len(roots), RATE.per_s()))

    def root(self, o):
        t = o.transformId; hop = 0
        while hop < 128:
            p = self.by_tid.get(t)
            if p is None:
                return None
            if not p.transformParentId or p.transformParentId not in self.by_tid:
                return t
            t = p.transformParentId; hop += 1
        return None

    def cat(self, o):
        if o.transformId in self.cache:
            return self.cache[o.transformId]
        r = self.root(o)
        c = self.root_cat.get(r, "unknown") if r is not None else "unknown"
        self.cache[o.transformId] = c
        return c

    def counts(self):
        tot = collections.Counter(); act = collections.Counter()
        for o in self.by_tid.values():
            c = self.cat(o); tot[c] += 1
            if o.enabled:
                act[c] += 1
        return {"total": dict(tot), "active": dict(act)}

    def roots_summary(self):
        out = collections.defaultdict(list)
        for t, c in self.root_cat.items():
            o = self.by_tid.get(t)
            out[c].append(o.name if o else str(t))
        return {c: {"n": len(v), "names_first40": sorted(v)[:40]} for c, v in out.items()}


# ---------------------------------------------------------------- сборщик
class Collector:
    def __init__(self, E, args):
        self.E = E; self.d = E.d; self.By = E.By; self.args = args
        self.Rj = jload(OUT_F, None) if not args.fresh else None
        if self.Rj is None:
            if os.path.exists(OUT_F) and args.fresh:
                os.replace(OUT_F, OUT_F + ".bak_%s" % time.strftime("%Y%m%d_%H%M%S"))
            self.Rj = {"meta": {}, "scenes": {}, "locations": {}}
        m = self.Rj.setdefault("meta", {})
        m.setdefault("created", now())
        m.update({"script": os.path.abspath(__file__), "sdk": "AltTester-Driver 2.4.1 (Python)", "rate_limit_per_s": round(1 / RATE.min_dt, 1),
                  "note": "редактор Unity (Play in Editor), не сборка; только чтение; навигация меню читов",
                  "masks": {"solid": MASK_SOLID, "ground": MASK_GROUND, "water": MASK_WATER,
                            "solid_desc": "все слои, кроме Ignore Raycast(2), Water(4), UI(5), Characters(9); триггеры игнорируются"}})
        self.gnames = global_names()
        self.last_save = 0.0
        self.log_t0 = time.time(); self.log_b0 = self.loglen()

    # --- служебное
    def log(self, *a):
        print("[%s]" % time.strftime("%H:%M:%S"), *a, flush=True)

    def loglen(self):
        try:
            return os.path.getsize(self.E.EDLOG)
        except Exception:
            return 0

    def save(self, force=False):
        if force or time.time() - self.last_save > 15:
            self.Rj["meta"]["updated"] = now(); self.Rj["meta"]["calls_total"] = RATE.calls
            jsave(OUT_F, self.Rj); self.last_save = time.time()

    def check_log(self):
        el = time.time() - self.log_t0
        if el < 60:
            return
        rate = (self.loglen() - self.log_b0) / 1048576 / (el / 60)
        self.log_t0 = time.time(); self.log_b0 = self.loglen()
        if rate > self.args.max_log_mb_min:
            raise StopCollect("Editor.log растёт %.1f МБ/мин (> %.1f): остановка, продолжить потом тем же запуском" % (rate, self.args.max_log_mb_min))

    def find(self, key, enabled):
        full, _asm = COMPS[key]
        short_ = full.split(".")[-1]
        S = self.cur
        name = S.setdefault("component_find_names", {}).get(key)
        names = [name] if name else [short_, full]
        best = []; used = None
        for n in names:
            try:
                l = self.d.find_objects(self.By.COMPONENT, n, enabled=enabled)
            except Exception as e:
                S.setdefault("find_errors", {})["%s(%s)" % (n, enabled)] = "%s: %s" % (type(e).__name__, str(e)[:150])
                l = []
            if len(l) > len(best) or used is None:
                best, used = l, n
            if l:
                break
        if best and not name:
            S["component_find_names"][key] = used
        return best

    def sg(self, cls, prop, asm):
        try:
            return self.d.get_static_property(cls, prop, asm)
        except Exception as e:
            return "ERR %s: %s" % (type(e).__name__, str(e)[:160])

    def wait_ready(self, timeout=45):
        t0 = time.time()
        while time.time() - t0 < timeout:
            try:
                if self.d.find_objects(self.By.NAME, "PigChef(Clone)", enabled=True) and self.E.gstate() == 0:
                    return round(time.time() - t0, 1)
            except Exception:
                pass
            time.sleep(1.0)
        return None

    # --- навигация
    def go(self, loc):
        E = self.E
        same_scene = E.SCN[loc] in E.scenes()
        tries = []
        for via in (None, "Town_Market", "Mountain_Cave", "Forest"):
            if via is not None:
                if via == loc or E.SCN[via] == E.SCN[loc]:
                    continue
                try:
                    tries.append({"via": via, "r": list(E.goto(via))}); self.wait_ready(30); time.sleep(2)
                except Exception as e:
                    tries.append({"via": via, "err": "%s: %s" % (type(e).__name__, str(e)[:150])})
                same_scene = False
            try:
                r = E.goto(loc)
                tries.append({"to": loc, "r": list(r)})
                if same_scene:
                    time.sleep(8)   # та же .unity: cheat_go может вернуть успех до перезагрузки
                return {"ok": True, "tries": tries, "ready_s": self.wait_ready(45)}
            except SystemExit:
                raise
            except Exception as e:
                tries.append({"to": loc, "err": "%s: %s" % (type(e).__name__, str(e)[:150])})
        return {"ok": False, "tries": tries}

    # --- точка входа: статистика рендера
    def viewpoint(self):
        V = {"t": now()}
        time.sleep(self.args.settle)
        try:
            V["player_pos"] = [r3(x) for x in self.E.ppos()]
        except Exception as e:
            V["player_pos"] = "ERR %s" % type(e).__name__
        try:
            V["camera_pos"] = [r3(x) for x in self.E.cam_pos()]
        except Exception as e:
            V["camera_pos"] = "ERR %s" % type(e).__name__
        f0 = self.sg("UnityEngine.Time", "frameCount", CORE); t0 = self.sg("UnityEngine.Time", "realtimeSinceStartup", CORE)
        samples = []
        for i in range(3):
            samples.append({p: self.sg("UnityEditor.UnityStats", p, ED) for p in ("drawCalls", "setPassCalls", "triangles", "vertices", "batches")})
            time.sleep(1.0)
        f1 = self.sg("UnityEngine.Time", "frameCount", CORE); t1 = self.sg("UnityEngine.Time", "realtimeSinceStartup", CORE)
        st = {}
        for p in samples[0]:
            nums = [s[p] for s in samples if isinstance(s[p], (int, float)) and not isinstance(s[p], bool)]
            st[p] = statistics.median(nums) if nums else samples[0][p]
        V["unitystats_median3"] = st; V["unitystats_samples"] = samples
        try:
            V["avg_fps"] = round((f1 - f0) / (t1 - t0), 1)
        except Exception:
            V["avg_fps"] = None
        V["screen"] = [self.sg("UnityEngine.Screen", "width", CORE), self.sg("UnityEngine.Screen", "height", CORE)]
        V["isFocused"] = self.sg("UnityEngine.Application", "isFocused", CORE)
        V["game_state"] = self.E.gstate()
        V["scenes"] = self.E.scenes()
        return V

    # --- сцена целиком
    def collect_scene(self, scene, deadline):
        S = self.Rj["scenes"].setdefault(scene, {"scene": scene, "status": "partial", "phases": {}, "started": now()})
        self.cur = S
        R = Reader(); self.reader = R
        ph = S.setdefault("phases", {})
        S["loaded_scenes"] = self.E.scenes()
        # 1) состав: все объекты + корни (каждый запуск: id меняются после перезагрузки)
        self.log("  все объекты (get_all_elements enabled=False)…")
        t = time.time()
        try:
            old = self.d.get_command_response_timeout()
            self.d.set_command_response_timeout(180)
            elems = self.d.get_all_elements(enabled=False)
            self.d.set_command_response_timeout(old)
            S["all_elements_s"] = round(time.time() - t, 1)
        except Exception as e:
            elems = []; S["all_elements_error"] = "%s: %s" % (type(e).__name__, str(e)[:200])
        memb = Membership(scene, elems, R, self.gnames, self.log)
        S["membership"] = {"method": memb.method, "roots": memb.n_roots, "scene_name_errors": memb.errors,
                           "roots_by_cat": memb.roots_summary()}
        S["gameobjects"] = memb.counts()
        ph["membership"] = now(); self.save(True)
        self.log("  GameObject по категориям:", S["gameobjects"])
        # 2) подсчёт компонентов
        if "counts" not in ph or self.args.redo:
            C = {}
            for key in COMPS:
                allo = self.find(key, False); act = self.find(key, True)
                C[key] = {"total": dict(collections.Counter(memb.cat(o) for o in allo)),
                          "active": dict(collections.Counter(memb.cat(o) for o in act))}
            S["component_counts"] = C
            S["note_counts"] = "число GameObject с компонентом (find_objects By.COMPONENT); total = и неактивные, active = activeInHierarchy"
            ph["counts"] = now(); self.save(True)
            self.log("  компоненты (active, location):", {k: v["active"].get("location", 0) for k, v in C.items()})
        # 3) рендеры
        if not ph.get("renderers_done"):
            done = self.renderers(S, memb, R, deadline)
            S["reader_modes_renderers"] = R.report()
            if done:
                ph["renderers_done"] = now()
            self.save(True)
            if not done:
                return False
        # 4) MeshCollider
        if not ph.get("meshcolliders_done"):
            done = self.meshcolliders(S, memb, R, deadline)
            if done:
                ph["meshcolliders_done"] = now()
            self.save(True)
            if not done:
                return False
        # 5) свет, частицы, аниматоры, LOD
        if not ph.get("misc_done"):
            self.misc(S, memb, R)
            ph["misc_done"] = now(); self.save(True)
        # 6) площадь земли
        if not ph.get("ground_done") and not self.args.no_ground:
            done = self.ground(S)
            if done:
                ph["ground_done"] = now()
            self.save(True)
            if not done:
                return False
        S["reader_modes"] = R.report()
        S["summary"] = summarize(S)
        S["status"] = "done"; S["finished"] = now()
        self.save(True)
        return True

    def renderers(self, S, memb, R, deadline):
        rows = S.setdefault("renderers", {}); meshes = S.setdefault("meshes", {})
        skipped = collections.Counter(); seen = collections.Counter()
        plan = []
        for kind, comp, mesh_comp in (("MR", "UnityEngine.MeshRenderer", "UnityEngine.MeshFilter"), ("SMR", "UnityEngine.SkinnedMeshRenderer", "UnityEngine.SkinnedMeshRenderer")):
            objs = self.find("MeshRenderer" if kind == "MR" else "SkinnedMeshRenderer", True)
            for o in objs:
                k = kind + ":" + okey(o); seen[k] += 1
                if seen[k] > 1:
                    k += "#%d" % seen[k]
                c = memb.cat(o)
                if c not in READ_CATS:
                    skipped[c] += 1; continue
                if k in rows:
                    continue
                plan.append((kind, comp, mesh_comp, o, k, c))
        S["renderers_skipped_by_cat"] = dict(skipped)
        n0 = len(rows)
        self.log("  рендеры: уже %d, осталось %d (оценка %.0f мин при ~6 выз/с)" % (n0, len(plan), len(plan) * 7.5 / 6 / 60))
        t0 = time.time()
        for i, (kind, comp, mesh_comp, o, k, c) in enumerate(plan):
            row = {"kind": kind, "name": o.name, "id": o.id, "cat": c, "pos": [r3(o.worldX), r3(o.worldY), r3(o.worldZ)]}
            row["b"] = read_bounds(R, o, comp, CORE)
            row["en"] = R.get(o, comp, CORE, "enabled", [("enabled", 1)], as_bool)
            row["mat"] = R.get(o, comp, CORE, "materials", F_MATS, conv_mats)
            row["shadow"] = R.get(o, comp, CORE, "shadowCastingMode", [("shadowCastingMode", 1)], None)
            row["sb"] = R.get(o, comp, CORE, "isPartOfStaticBatch", [("isPartOfStaticBatch", 1)], as_bool)
            row["mesh"] = R.get(o, mesh_comp, CORE, "sharedMesh.name", [("sharedMesh.name", 1)], as_str)
            row["v"] = R.get(o, mesh_comp, CORE, "sharedMesh.vertexCount", [("sharedMesh.vertexCount", 1)], as_int)
            if row["sb"] is True:
                # кандидаты (internal Renderer) для разбора общего Combined Mesh; выключаются сами, если не читаются
                row["sbi"] = R.get(o, comp, CORE, "staticBatchIndex", [("staticBatchIndex", 1)], as_int)
                row["ssi"] = R.get(o, comp, CORE, "subMeshStartIndex", [("subMeshStartIndex", 1)], as_int)
            mk = "%s|%s|%s" % (kind, row["mesh"], row["v"])
            if isinstance(row["v"], int) and mk not in meshes:
                mi = {"kind": kind, "name": row["mesh"], "v": row["v"], "combined": bool(row["sb"] is True or str(row["mesh"]).startswith("Combined Mesh"))}
                mi["subMeshCount"] = R.get(o, mesh_comp, CORE, "sharedMesh.subMeshCount", [("sharedMesh.subMeshCount", 1)], as_int)
                if not self.args.no_tris:
                    rd = R.get(o, mesh_comp, CORE, "sharedMesh.isReadable", [("sharedMesh.isReadable", 1)], as_bool)
                    mi["readable"] = rd
                    if rd is True and row["v"] <= self.args.tris_max_vertices:
                        n = R.get(o, mesh_comp, CORE, "sharedMesh.triangles.Length", [("sharedMesh.triangles.Length", 1)], as_int)
                        mi["tris"] = n // 3 if isinstance(n, int) else n
                    else:
                        mi["tris"] = None
                meshes[mk] = mi
            row["mk"] = mk
            rows[k] = row
            if i % 25 == 24:
                el = time.time() - t0
                self.log("   рендеры %d/%d, %s выз/с, %.0f с" % (i + 1, len(plan), RATE.per_s(), el))
                self.save(); self.check_log()
            if deadline and time.time() > deadline:
                self.log("   лимит времени сцены: прочитано %d из %d, продолжу при следующем запуске" % (i + 1, len(plan)))
                S["stopped"] = "scene time limit"; return False
        return True

    def meshcolliders(self, S, memb, R, deadline):
        rows = S.setdefault("mesh_colliders", {}); seen = collections.Counter(); plan = []
        for o in self.find("MeshCollider", True):
            k = okey(o); seen[k] += 1
            if seen[k] > 1:
                k += "#%d" % seen[k]
            c = memb.cat(o)
            if c in READ_CATS and k not in rows:
                plan.append((o, k, c))
        self.log("  MeshCollider: осталось %d" % len(plan))
        comp = "UnityEngine.MeshCollider"
        for i, (o, k, c) in enumerate(plan):
            rows[k] = {"name": o.name, "cat": c, "pos": [r3(o.worldX), r3(o.worldY), r3(o.worldZ)],
                       "mesh": R.get(o, comp, PHYS, "sharedMesh.name", [("sharedMesh.name", 1)], as_str),
                       "v": R.get(o, comp, PHYS, "sharedMesh.vertexCount", [("sharedMesh.vertexCount", 1)], as_int),
                       "convex": R.get(o, comp, PHYS, "convex", [("convex", 1)], as_bool),
                       "en": R.get(o, comp, PHYS, "enabled", [("enabled", 1)], as_bool)}
            if i % 25 == 24:
                self.log("   MeshCollider %d/%d, %s выз/с" % (i + 1, len(plan), RATE.per_s()))
                self.save(); self.check_log()
            if deadline and time.time() > deadline:
                S["stopped"] = "scene time limit"; return False
        return True

    def misc(self, S, memb, R):
        def objs(key):
            return [o for o in self.find(key, True) if memb.cat(o) in READ_CATS]
        L = []
        for o in objs("Light"):
            c = "UnityEngine.Light"
            L.append({"name": o.name, "cat": memb.cat(o), "pos": [r3(o.worldX), r3(o.worldY), r3(o.worldZ)],
                      "type": R.get(o, c, CORE, "type", [("type", 1)]), "shadows": R.get(o, c, CORE, "shadows", [("shadows", 1)]),
                      "en": R.get(o, c, CORE, "enabled", [("enabled", 1)], as_bool), "intensity": R.get(o, c, CORE, "intensity", [("intensity", 1)]),
                      "range": R.get(o, c, CORE, "range", [("range", 1)])})
        S["lights"] = L
        P = []
        for o in objs("ParticleSystem")[: self.args.max_misc]:
            c, a = COMPS["ParticleSystem"]
            P.append({"name": o.name, "cat": memb.cat(o), "pos": [r3(o.worldX), r3(o.worldY), r3(o.worldZ)],
                      "playing": R.get(o, c, a, "isPlaying", [("isPlaying", 1)], as_bool),
                      "maxParticles": R.get(o, c, a, "main.maxParticles", [("main.maxParticles", 1)], as_int)})
        S["particle_systems"] = {"n_read": len(P), "by_name": dict(collections.Counter(re.sub(r" \(\d+\)$", "", p["name"]) for p in P)), "rows": P}
        A = []
        for o in objs("Animator")[: self.args.max_misc]:
            c, a = COMPS["Animator"]
            A.append({"name": o.name, "cat": memb.cat(o), "en": R.get(o, c, a, "enabled", [("enabled", 1)], as_bool),
                      "culling": R.get(o, c, a, "cullingMode", [("cullingMode", 1)])})
        S["animators"] = {"n_read": len(A), "by_name": dict(collections.Counter(re.sub(r" \(\d+\)$", "", x["name"]) for x in A)), "rows": A}
        G = []
        for o in objs("LODGroup"):
            c = "UnityEngine.LODGroup"
            G.append({"name": o.name, "cat": memb.cat(o), "lodCount": R.get(o, c, CORE, "lodCount", [("lodCount", 1)], as_int),
                      "en": R.get(o, c, CORE, "enabled", [("enabled", 1)], as_bool)})
        S["lodgroups"] = G
        self.log("  свет %d, частицы %d, аниматоры %d, LODGroup %d" % (len(L), len(P), len(A), len(G)))

    # --- Physics.Raycast вниз по сетке
    def ray(self, x, y, z, dist, mask):
        return ray(self.d, x, y, z, dist, mask)

    def ground(self, S):
        a = self.args
        G = S.get("ground") or {}
        rows = [r for r in S.get("renderers", {}).values() if r.get("cat") in LOCAL_CATS and isinstance(r.get("b"), dict)]
        if len(rows) < 5:
            S["ground"] = {"error": "мало рендеров с bounds (%d): сетку не строю" % len(rows)}; return True
        if not G.get("params"):
            xs = sorted(r["b"]["c"][0] for r in rows); zs = sorted(r["b"]["c"][2] for r in rows)
            ylo = sorted(r["b"]["c"][1] - r["b"]["e"][1] for r in rows); yhi = sorted(r["b"]["c"][1] + r["b"]["e"][1] for r in rows)

            def pct(l, q):
                return l[min(len(l) - 1, max(0, int(q * (len(l) - 1))))]
            x0, x1 = pct(xs, 0.02) - 5, pct(xs, 0.98) + 5; z0, z1 = pct(zs, 0.02) - 5, pct(zs, 0.98) + 5
            top = pct(yhi, 0.98) + 5; bottom = pct(ylo, 0.02) - 10
            area = (x1 - x0) * (z1 - z0)
            step = max(a.min_step, math.ceil(math.sqrt(area / a.ray_points) * 2) / 2.0)
            nx = int((x1 - x0) / step) + 1; nz = int((z1 - z0) / step) + 1
            dist = min(500.0, top - bottom)
            G = {"params": {"x0": round(x0, 2), "z0": round(z0, 2), "step": step, "nx": nx, "nz": nz, "top_y": round(top, 2), "dist": round(dist, 2),
                            "box_from": "центры bounds рендеров локации, перцентили 2–98 %, запас 5 м; верх = p98(max y)+5, низ = p2(min y)-10"},
                 "encoding": "строка на ряд z; символ = hex битов: 1 solid, 2 Ground-слой, 4 Water-слой; 'x' ошибка; '.' нет попаданий",
                 "rows": [], "heights": [], "done": False}
            S["ground"] = G
        p = G["params"]; x0, z0, step, nx, nz, top, dist = p["x0"], p["z0"], p["step"], p["nx"], p["nz"], p["top_y"], p["dist"]
        total = nx * nz
        h_every = max(1, int(total * 0.6 / max(1, a.ray_heights)))
        self.log("  сетка Raycast: %dx%d=%d точек, шаг %.1f м, расстояние %.0f м; начинаю с ряда %d" % (nx, nz, total, step, dist, len(G["rows"])))
        t0 = time.time(); idx = len(G["rows"]) * nx
        for j in range(len(G["rows"]), nz):
            z = z0 + j * step; line = []
            for i in range(nx):
                x = x0 + i * step
                try:
                    s = self.ray(x, top, z, dist, MASK_SOLID)
                    g = self.ray(x, top, z, dist, MASK_GROUND) if s else False
                    w = self.ray(x, top, z, dist, MASK_WATER)
                    bits = (1 if s else 0) | (2 if g else 0) | (4 if w else 0)
                    line.append("." if bits == 0 else "%x" % bits)
                    if s and idx % h_every == 0 and len(G["heights"]) < a.ray_heights:
                        lo, hi = 0.0, dist
                        while hi - lo > 0.5:
                            m = (lo + hi) / 2
                            if self.ray(x, top, z, m, MASK_SOLID):
                                hi = m
                            else:
                                lo = m
                        G["heights"].append([round(x, 2), round(z, 2), round(top - hi, 2)])
                except Exception as e:
                    line.append("x"); G["last_error"] = "%s: %s" % (type(e).__name__, str(e)[:150])
                idx += 1
            G["rows"].append("".join(line))
            if j % 3 == 2:
                self.log("   ряд %d/%d, %s выз/с, %.0f с" % (j + 1, nz, RATE.per_s(), time.time() - t0))
                self.save(); self.check_log()
            if time.time() - t0 > a.ray_seconds:
                G["stopped"] = "лимит %d с: продолжу при следующем запуске" % a.ray_seconds
                self.log("   " + G["stopped"]); return False
        G["done"] = True; G.pop("stopped", None)
        G.update(ground_stats(G))
        return True

    # --- основной цикл
    def run(self, locs):
        E = self.E
        self.Rj["meta"]["log_offset_start"] = E.log_mark()
        off = self.Rj["meta"]["log_offset_start"]
        for loc in locs:
            scn = E.SCN[loc]
            L = self.Rj["locations"].get(loc) or {}
            S = self.Rj["scenes"].get(scn) or {}
            if self.args.redo:
                L = {}; self.Rj["scenes"].pop(scn, None); S = {}
            need_view = L.get("status") != "done"
            need_static = S.get("status") != "done"
            if not need_view and not need_static:
                self.log(loc, "уже собрано, пропуск"); continue
            self.log("=== %s (сцена %s): точка входа %s, статика %s" % (loc, scn, need_view, need_static))
            L.update({"location": loc, "scene": scn, "button": E.LABEL[loc]})
            self.Rj["locations"][loc] = L
            nav = self.go(loc); L["goto"] = nav; self.save(True)
            if not nav["ok"]:
                L["status"] = "goto_failed"; self.save(True); self.log("  переход не удался", nav["tries"][-1:]); continue
            if need_view:
                L["viewpoint"] = self.viewpoint(); L["status"] = "done"; self.save(True)
                self.log("  UnityStats:", L["viewpoint"]["unitystats_median3"], "fps", L["viewpoint"]["avg_fps"])
            if need_static:
                deadline = time.time() + self.args.scene_seconds if self.args.scene_seconds else None
                t = time.time()
                ok = self.collect_scene(scn, deadline)
                sc = self.Rj["scenes"][scn]; sc["seconds_last_run"] = round(time.time() - t, 1)
                sc["collected_via"] = sc.get("collected_via") or loc
                if not ok:
                    self.log("  сцена %s собрана частично (продолжится при следующем запуске)" % scn)
                self.save(True)
            try:
                L["exceptions_since_start"] = E.exc_summary(off)["total"]
            except Exception:
                pass
            self.save(True)
        try:
            ex = E.exc_summary(off); self.Rj["meta"]["exceptions"] = {"total": ex["total"], "by_type": ex["by_type"]}
        except Exception as e:
            self.Rj["meta"]["exceptions"] = "ERR %s" % e
        self.save(True)


class StopCollect(Exception):
    pass


# ---------------------------------------------------------------- итоги
def ground_stats(G):
    st = G["params"]["step"]; c = collections.Counter()
    for row in G["rows"]:
        for ch in row:
            if ch == "x":
                c["error"] += 1; continue
            b = 0 if ch == "." else int(ch, 16)
            c["points"] += 1
            if b & 1: c["solid"] += 1
            if b & 2: c["ground_layer"] += 1
            if b & 4: c["water_layer"] += 1
            if (b & 4) and not (b & 1): c["water_only"] += 1
    a = st * st
    hs = [h[2] for h in G.get("heights", [])]
    return {"stats": dict(c), "area_m2": {"solid": round(c["solid"] * a, 1), "ground_layer": round(c["ground_layer"] * a, 1),
                                           "water_layer": round(c["water_layer"] * a, 1), "cell_m2": a},
            "height_quartiles": [round(statistics.quantiles(hs, n=4)[i], 2) for i in range(3)] if len(hs) >= 4 else hs}


def summarize(S):
    out = {}
    rows = [r for r in S.get("renderers", {}).values() if r.get("cat") in LOCAL_CATS]
    out["renderers"] = {"n": len(rows), "by_kind": dict(collections.Counter(r["kind"] for r in rows)),
                        "enabled_true": sum(1 for r in rows if r.get("en") is True),
                        "static_batched": sum(1 for r in rows if r.get("sb") is True),
                        "shadow_modes": dict(collections.Counter(str(r.get("shadow")) for r in rows)),
                        "materials_sum": sum(r["mat"] for r in rows if isinstance(r.get("mat"), int)),
                        "read_errors": sum(1 for r in rows if any(is_err(r.get(f)) for f in ("b", "en", "mat", "shadow", "sb", "mesh", "v")))}
    vrows = [r for r in rows if isinstance(r.get("v"), int)]
    meshes = S.get("meshes", {})
    naive = sum(r["v"] for r in vrows)
    nb = [r for r in vrows if not (r.get("sb") is True or str(r.get("mesh")).startswith("Combined Mesh"))]
    nb_ids = {id(r) for r in nb}
    bt = [r for r in vrows if id(r) not in nb_ids]
    bt_ids = {id(r) for r in bt}
    comb = {}
    for r in bt:
        c = comb.setdefault(r["mk"], {"mesh": r["mesh"], "v": r["v"], "renderers": 0, "tris": meshes.get(r["mk"], {}).get("tris")})
        c["renderers"] += 1
    # исходный меш у объекта со static batching иногда виден через MeshCollider того же объекта (тот же ключ)
    mc = S.get("mesh_colliders", {})
    via_col = []
    for k, r in S.get("renderers", {}).items():
        if id(r) in bt_ids:
            ck = k.split(":", 1)[1]
            c = mc.get(ck)
            if c and isinstance(c.get("v"), int):
                via_col.append(c["v"])
    out["vertices"] = {
        "naive_sum_DO_NOT_USE": naive,
        "non_batched_sum": sum(r["v"] for r in nb),
        "combined_meshes_unique": len(comb),
        "combined_meshes_sum_once": sum(c["v"] for c in comb.values()),
        "dedup_sum": sum(r["v"] for r in nb) + sum(c["v"] for c in comb.values()),
        "unique_meshes_sum": sum(m["v"] for m in meshes.values() if isinstance(m.get("v"), int)),
        "batched_renderers": len(bt),
        "batched_with_meshcollider_original": {"n": len(via_col), "sum_v": sum(via_col)},
        "note": "dedup_sum = рендеры без static batching (по объекту) + каждый Combined Mesh один раз. Вершины отдельного объекта внутри "
                "Combined Mesh через свойства SDK не получить (нужен Mesh.GetSubMesh — метод меша, не компонента); "
                "batched_with_meshcollider_original — исходный меш по MeshCollider того же объекта, если он есть.",
        "combined": sorted(comb.values(), key=lambda c: -c["v"])[:30]}
    tri_known = [r for r in nb if isinstance(meshes.get(r["mk"], {}).get("tris"), int)]
    out["triangles"] = {"non_batched_known_renderers": len(tri_known), "non_batched_known_sum": sum(meshes[r["mk"]]["tris"] for r in tri_known),
                        "combined_known_sum_once": sum(c["tris"] for c in comb.values() if isinstance(c["tris"], int)),
                        "unique_meshes_with_tris": sum(1 for m in meshes.values() if isinstance(m.get("tris"), int)), "unique_meshes": len(meshes)}
    agg = collections.Counter(); vv = {}
    for r in nb:
        agg[r["mk"]] += 1; vv[r["mk"]] = r["v"]
    out["top15_non_batched_by_total_vertices"] = [{"mesh": k.split("|")[1], "kind": k.split("|")[0], "v": vv[k], "copies": n, "total": vv[k] * n}
                                                  for k, n in sorted(agg.items(), key=lambda kv: -vv[kv[0]] * kv[1])[:15]]
    br = [r["b"] for r in rows if isinstance(r.get("b"), dict)]
    if br:
        out["bounds_union"] = {"min": [round(min(b["c"][i] - b["e"][i] for b in br), 2) for i in range(3)],
                               "max": [round(max(b["c"][i] + b["e"][i] for b in br), 2) for i in range(3)]}
    cc = S.get("component_counts", {})
    out["colliders_active_location"] = {k: cc.get(k, {}).get("active", {}).get("location", 0) for k in COLLIDER_KEYS}
    mcr = [c for c in mc.values() if c.get("cat") in LOCAL_CATS]
    out["mesh_colliders"] = {"n": len(mcr), "convex": sum(1 for c in mcr if c.get("convex") is True),
                             "v_sum": sum(c["v"] for c in mcr if isinstance(c.get("v"), int)),
                             "unique_meshes": len({(c.get("mesh"), c.get("v")) for c in mcr})}
    out["lights"] = dict(collections.Counter("%s/%s" % (l.get("type"), l.get("shadows")) for l in S.get("lights", [])))
    out["ground"] = {k: S.get("ground", {}).get(k) for k in ("area_m2", "stats")} if S.get("ground") else None
    return out


# ---------------------------------------------------------------- проба
def probe(E, args):
    d = E.d; By = E.By
    P = {"t": now(), "tests": []}

    def T(name, fn):
        t = time.time()
        try:
            v = fn(); ok = True
        except Exception as e:
            v = "%s: %s" % (type(e).__name__, str(e)[:200]); ok = False
        P["tests"].append({"name": name, "ok": ok, "s": round(time.time() - t, 2), "value": short(v, 300)})
        print("%s %-55s %5.2fs  %s" % ("OK " if ok else "ERR", name, time.time() - t, short(v, 140)), flush=True)
        return v if ok else None

    def prop(o, comp, path, asm, depth=1):
        return o.get_component_property(comp, path, asm, max_depth=depth)

    sc = T("get_all_loaded_scenes", E.scenes) or []
    loc = [s for s in sc if s not in GLOBAL_SCENES and s != "MainMenu"]
    scene = loc[0] if loc else None
    P["scene"] = scene
    old = d.get_command_response_timeout(); d.set_command_response_timeout(180)
    elems = T("get_all_elements(enabled=False)", lambda: d.get_all_elements(enabled=False)) or []
    d.set_command_response_timeout(old)
    tids = {o.transformId for o in elems}
    roots = [o for o in elems if not o.transformParentId or o.transformParentId not in tids]
    print("    объектов %d, корней %d, active по полю enabled: %d" % (len(elems), len(roots), sum(1 for o in elems if o.enabled)))
    P["elements"] = {"n": len(elems), "roots": len(roots), "active_field": sum(1 for o in elems if o.enabled),
                     "root_parent_ids_sample": [o.transformParentId for o in roots[:5]]}
    for o in roots[:3]:
        T("root %s Transform gameObject.scene.name" % o.name[:20], lambda o=o: prop(o, "UnityEngine.Transform", "gameObject.scene.name", CORE))
    if roots:
        T("root Transform gameObject.scene (depth 2)", lambda: prop(roots[0], "UnityEngine.Transform", "gameObject.scene", CORE, 2))
    found = {}
    for key, (full, asm) in COMPS.items():
        s = full.split(".")[-1]
        a = T("find COMPONENT %s enabled=False" % s, lambda s=s: len(d.find_objects(By.COMPONENT, s, enabled=False)))
        b = T("find COMPONENT %s enabled=True" % s, lambda s=s: d.find_objects(By.COMPONENT, s, enabled=True))
        if not a:
            T("find COMPONENT %s (full name) enabled=False" % full, lambda f=full: len(d.find_objects(By.COMPONENT, f, enabled=False)))
            b = T("find COMPONENT %s (full name) enabled=True" % full, lambda f=full: d.find_objects(By.COMPONENT, f, enabled=True)) or b
        found[key] = b or []
    mrs = [o for o in found["MeshRenderer"] if o.name not in PLAYER_ROOTS][:60]
    if mrs:
        o = mrs[0]; c = "UnityEngine.MeshRenderer"; f = "UnityEngine.MeshFilter"
        print("    MeshRenderer:", o.name)
        T("MR bounds (depth 2) -> as_bounds", lambda: as_bounds(prop(o, c, "bounds", CORE, 2)))
        T("MR bounds raw (depth 2)", lambda: prop(o, c, "bounds", CORE, 2))
        T("MR bounds.center", lambda: as_vec(prop(o, c, "bounds.center", CORE)))
        T("MR bounds.extents", lambda: as_vec(prop(o, c, "bounds.extents", CORE)))
        T("MR sharedMaterials.Length", lambda: prop(o, c, "sharedMaterials.Length", CORE))
        T("MR sharedMaterials (depth 1) len", lambda: as_len(prop(o, c, "sharedMaterials", CORE, 1)))
        T("MR shadowCastingMode", lambda: prop(o, c, "shadowCastingMode", CORE))
        T("MR isPartOfStaticBatch", lambda: prop(o, c, "isPartOfStaticBatch", CORE))
        T("MR enabled", lambda: prop(o, c, "enabled", CORE))
        T("MF sharedMesh.name", lambda: prop(o, f, "sharedMesh.name", CORE))
        v = T("MF sharedMesh.vertexCount", lambda: prop(o, f, "sharedMesh.vertexCount", CORE))
        T("MF sharedMesh.subMeshCount", lambda: prop(o, f, "sharedMesh.subMeshCount", CORE))
        rd = T("MF sharedMesh.isReadable", lambda: prop(o, f, "sharedMesh.isReadable", CORE))
        if str(rd).lower() == "true" and isinstance(v, int) and v <= 20000:
            T("MF sharedMesh.triangles.Length (/3 = tris)", lambda: prop(o, f, "sharedMesh.triangles.Length", CORE))
        else:
            print("    triangles.Length пропущен: isReadable=%s, vertexCount=%s" % (rd, v))
        sb = None
        for x in mrs:
            try:
                if as_bool(prop(x, c, "isPartOfStaticBatch", CORE)):
                    sb = x; break
            except Exception:
                pass
        if sb is not None:
            print("    static batch объект:", sb.name)
            for pth, dp in (("staticBatchIndex", 1), ("subMeshStartIndex", 1), ("staticBatchInfo", 2)):
                T("MR(static) %s" % pth, lambda p=pth, dp=dp: prop(sb, c, p, CORE, dp))
            T("MF(static) sharedMesh.name", lambda: prop(sb, f, "sharedMesh.name", CORE))
            T("MF(static) sharedMesh.vertexCount", lambda: prop(sb, f, "sharedMesh.vertexCount", CORE))
            T("MF(static) sharedMesh.subMeshCount", lambda: prop(sb, f, "sharedMesh.subMeshCount", CORE))
            T("MeshCollider того же объекта sharedMesh.name", lambda: prop(sb, "UnityEngine.MeshCollider", "sharedMesh.name", PHYS))
            T("MeshCollider того же объекта sharedMesh.vertexCount", lambda: prop(sb, "UnityEngine.MeshCollider", "sharedMesh.vertexCount", PHYS))
        else:
            print("    среди первых %d MeshRenderer нет isPartOfStaticBatch=True" % len(mrs))
    if found["SkinnedMeshRenderer"]:
        o = found["SkinnedMeshRenderer"][0]; c = "UnityEngine.SkinnedMeshRenderer"
        for pth, dp in (("bounds", 2), ("sharedMesh.name", 1), ("sharedMesh.vertexCount", 1), ("sharedMaterials.Length", 1), ("shadowCastingMode", 1), ("enabled", 1)):
            T("SMR %s" % pth, lambda p=pth, dp=dp: prop(o, c, p, CORE, dp))
    for key, paths in (("Light", ("type", "shadows", "intensity", "range", "enabled")), ("ParticleSystem", ("isPlaying", "main.maxParticles")),
                       ("Animator", ("enabled", "cullingMode")), ("LODGroup", ("lodCount", "enabled")),
                       ("MeshCollider", ("sharedMesh.name", "sharedMesh.vertexCount", "convex", "enabled"))):
        if found.get(key):
            o = found[key][0]; full, asm = COMPS[key]
            for pth in paths:
                T("%s %s" % (key, pth), lambda p=pth, o=o, full=full, asm=asm: prop(o, full, p, asm))
        else:
            print("    %s: активных нет, поля не проверены" % key)
    pp = T("player position (ppos)", E.ppos)
    T("camera position (cam_pos)", E.cam_pos)
    if pp:
        x, y, z = pp
        for nm, mk in (("solid", MASK_SOLID), ("ground", MASK_GROUND), ("water", MASK_WATER), ("all -1", -1)):
            T("Physics.Raycast down from player+30 m, mask %s" % nm, lambda mk=mk: ray(d, x, y + 30, z, 60.0, mk))

        def height():
            lo, hi = 0.0, 60.0; n = 0
            while hi - lo > 0.5:
                m = (lo + hi) / 2; n += 1
                if ray(d, x, y + 30, z, m, MASK_SOLID):
                    hi = m
                else:
                    lo = m
            return {"ground_y": round(y + 30 - hi, 2), "player_y": round(y, 2), "rays": n}
        T("Raycast binary search height (0.5 m)", height)
    for p in ("drawCalls", "setPassCalls", "triangles", "vertices", "batches"):
        T("UnityStats.%s" % p, lambda p=p: d.get_static_property("UnityEditor.UnityStats", p, ED))
    P["calls"] = RATE.calls; P["calls_per_s_recent"] = RATE.per_s()
    P["elapsed_s"] = round(time.time() - RATE.t0, 1)
    jsave(PROBE_F, P)
    bad = [t["name"] for t in P["tests"] if not t["ok"]]
    print("\nпроба: %d тестов, ошибок %d, вызовов %d, ~%s выз/с; файл %s" % (len(P["tests"]), len(bad), RATE.calls, RATE.per_s(), PROBE_F))
    for b in bad:
        print("  ERR", b)


# ---------------------------------------------------------------- запуск
def main():
    ap = argparse.ArgumentParser(description="stage8: статические данные локаций (только чтение)")
    ap.add_argument("--probe", action="store_true", help="проба API на текущей сцене, без навигации и без levels.json")
    ap.add_argument("--location", default="", help="локация(и) через запятую: " + ",".join(ORDER))
    ap.add_argument("--redo", action="store_true", help="пересобрать выбранные локации (иначе продолжение)")
    ap.add_argument("--fresh", action="store_true", help="начать levels.json заново (старый -> .bak_*)")
    ap.add_argument("--rate", type=float, default=20.0, help="вызовов драйвера в секунду, не больше 20")
    ap.add_argument("--scene-seconds", type=float, default=0, help="лимит секунд на сцену (0 = без лимита; недочитанное продолжится)")
    ap.add_argument("--ray-points", type=int, default=300, help="целевое число точек сетки Raycast (шаг подбирается)")
    ap.add_argument("--ray-heights", type=int, default=40, help="точек с высотой (двоичный поиск, ~8 лучей каждая)")
    ap.add_argument("--ray-seconds", type=float, default=300, help="лимит секунд на сетку одной сцены")
    ap.add_argument("--min-step", type=float, default=1.0, help="минимальный шаг сетки, м")
    ap.add_argument("--no-ground", action="store_true", help="без сетки Raycast")
    ap.add_argument("--no-tris", action="store_true", help="не читать sharedMesh.triangles.Length")
    ap.add_argument("--tris-max-vertices", type=int, default=300000)
    ap.add_argument("--max-misc", type=int, default=300, help="максимум ParticleSystem/Animator для чтения полей")
    ap.add_argument("--settle", type=float, default=5.0, help="пауза перед UnityStats в точке входа, с")
    ap.add_argument("--max-log-mb-min", type=float, default=8.0, help="стоп, если Editor.log растёт быстрее")
    args = ap.parse_args()
    locs = [s.strip() for s in args.location.split(",") if s.strip()] or list(ORDER)
    bad = [l for l in locs if l not in ORDER]
    if bad:
        ap.error("неизвестные локации: %s; есть: %s" % (bad, ", ".join(ORDER)))

    os.makedirs(RES, exist_ok=True)
    os.environ["MOD_OUT"] = RES           # mlib/guard пишут служебные файлы сюда
    install_throttle(args.rate)
    sys.path.insert(0, MODULES)
    import elib as E                      # подключение к 13000 происходит здесь (mlib.connect)
    E.prestage("stage8_probe" if args.probe else "stage8")
    if args.probe:
        probe(E, args); return
    C = Collector(E, args)
    try:
        C.run(locs)
    except StopCollect as e:
        C.Rj["meta"]["stopped"] = str(e); C.log("STOP:", e)
    except KeyboardInterrupt:
        C.Rj["meta"]["stopped"] = "KeyboardInterrupt"
    except BaseException as e:
        C.Rj["meta"]["stopped"] = "%s: %s" % (type(e).__name__, str(e)[:300]); C.Rj["meta"]["traceback"] = traceback.format_exc()[-2000:]
        raise
    finally:
        C.save(True)
        print("сохранено:", OUT_F, "вызовов", RATE.calls, flush=True)


if __name__ == "__main__":
    main()
