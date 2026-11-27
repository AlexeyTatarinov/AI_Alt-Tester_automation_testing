from g7 import *
import random
CAP = 100
F = os.path.join(R7, "mesh.json")
R = {"note": "редактор Unity; обзор без вердикта", "scenes": {}}
try: R = json.load(open(F, encoding="utf-8"))
except Exception: pass
def dump(): jdump(F, R)
prestage("a2")
off = log_mark()
LIMIT = 1500
COMPS = {"MeshFilter": ("UnityEngine.MeshFilter", CORE), "SkinnedMeshRenderer": ("UnityEngine.SkinnedMeshRenderer", CORE),
         "MeshCollider": ("UnityEngine.MeshCollider", "UnityEngine.PhysicsModule"), "LODGroup": ("UnityEngine.LODGroup", CORE)}
_last = [0.0]
def throttle():
    # не больше 18 вызовов в секунду
    w = 0.056 - (time.time() - _last[0])
    if w > 0: time.sleep(w)
    _last[0] = time.time()
def rdm(o, comp, asm, prop):
    throttle()
    try: return o.get_component_property(comp, prop, asm)
    except Exception as e: return "ERR %s: %s" % (type(e).__name__, str(e)[:100])

START = time.time()
for name in (sys.argv[1:] or ["Town_Market", "Town_Upper", "Forest", "Beach"]):
    e = {"scene": name}
    hyg_tick(R, name)
    r, tries = goto_retry(name); e["load_ok"] = r["ok"]
    if not r["ok"]:
        R["scenes"][name] = e; dump(); print("нет сцены", name); continue
    e["wait_ready_s"] = wait_ready(40); time.sleep(3)
    e["loaded"] = scenes()
    found = {}
    for k, (comp, asm) in COMPS.items():
        try:
            found[k] = d.find_objects(By.COMPONENT, comp, enabled=True)
        except Exception as ex:
            found[k] = []; e.setdefault("find_errors", {})[k] = "%s: %s" % (type(ex).__name__, str(ex)[:150])
    e["counts"] = {k: len(v) for k, v in found.items()}
    print(name, e["counts"], flush=True)
    lod_ids = {o.id for o in found["LODGroup"]}
    items = [("MeshFilter", o) for o in found["MeshFilter"]] + [("SkinnedMeshRenderer", o) for o in found["SkinnedMeshRenderer"]]
    e["objects_total"] = len(items); e["skipped_over_limit"] = max(0, len(items) - LIMIT)
    random.Random(1).shuffle(items); items = items[:LIMIT]
    rows = []; errs = {}; err_sample = None
    random.Random(7).shuffle(items)  # случайный порядок: частичное чтение остаётся выборкой без смещения
    g0 = log_len(); t0 = time.time(); stopped = None; names = {}; ncalls = 0; done_n = 0
    for i, (kind, o) in enumerate(items):
        comp, asm = COMPS[kind]
        n = rdm(o, comp, asm, "sharedMesh.vertexCount"); ncalls += 1; done_n += 1
        if isinstance(n, int):
            if (kind, n) not in names:
                names[(kind, n)] = str(rdm(o, comp, asm, "sharedMesh.name")); ncalls += 1
            rows.append({"obj": o.name, "kind": kind, "mesh": names[(kind, n)], "vertices": n, "id": o.id})
        else:
            k = str(n)[:40]; errs[k] = errs.get(k, 0) + 1; err_sample = str(n)
        if i % 50 == 49 or time.time() - t0 > CAP:
            el = time.time() - t0; rate = (log_len() - g0) / 1048576 / (el / 60)
            jdump(os.path.join(R7, "mesh_partial.json"), {"scene": name, "done": done_n, "rows": rows, "errors": errs, "s": el, "calls": ncalls})
            print(" ", name, done_n, "/", len(items), "s", round(el), "calls/s", round(ncalls / el, 1), "log MB/min", round(rate, 2), flush=True)
            if rate > 5 and el > 20: stopped = "Editor.log растёт %.1f МБ/мин (после %d объектов)" % (rate, done_n); break
            if el > CAP: stopped = "лимит времени на сцену %d с (прочитано %d из %d, случайный порядок)" % (CAP, done_n, len(items)); break
    e["stopped"] = stopped; e["read_s"] = round(time.time() - t0, 1); e["calls"] = ncalls; e["objects_read"] = done_n; e["not_read"] = e["objects_total"] - done_n
    e["log_growth_bytes"] = log_len() - g0
    e["read_ok"] = len(rows); e["read_errors"] = errs; e["error_sample"] = err_sample
    e["sum_vertices"] = sum(r_["vertices"] for r_ in rows)
    e["sum_vertices_by_kind"] = {k: sum(r_["vertices"] for r_ in rows if r_["kind"] == k) for k in ("MeshFilter", "SkinnedMeshRenderer")}
    agg = {}
    for r_ in rows:
        a = agg.setdefault((r_["mesh"], r_["vertices"]), {"mesh": r_["mesh"], "vertices": r_["vertices"], "copies": 0})
        a["copies"] += 1
    e["unique_meshes"] = len(agg)
    e["top10_by_mesh_vertices"] = sorted(agg.values(), key=lambda a: -a["vertices"])[:10]
    e["top10_by_total_vertices"] = [dict(a, total=a["vertices"] * a["copies"]) for a in sorted(agg.values(), key=lambda a: -a["vertices"] * a["copies"])[:10]]
    # доля объектов с LODGroup: компонент на самом объекте или на любом предке
    mesh_objs = [o for _, o in items]
    parent_cache = {}
    same = sum(1 for o in mesh_objs if o.id in lod_ids)
    e["lod"] = {"lodgroups": len(lod_ids), "mesh_objects": len(mesh_objs), "mesh_objects_with_lodgroup_on_self": same,
                "share_self": round(same / len(mesh_objs), 3) if mesh_objs else None}
    # под LODGroup (потомки): по иерархии
    try:
        allo = {o.transformId: o for o in d.get_all_elements(enabled=True)}
        lod_tr = {o.transformId for o in found["LODGroup"]}
        under = 0
        for o in mesh_objs:
            t = o.transformId; hop = 0
            while t and hop < 40:
                if t in lod_tr: under += 1; break
                p = allo.get(t)
                if p is None: break
                t = p.transformParentId; hop += 1
        e["lod"]["mesh_objects_under_lodgroup"] = under
        e["lod"]["share_under"] = round(under / len(mesh_objs), 3) if mesh_objs else None
    except Exception as ex:
        e["lod"]["hierarchy_error"] = "%s: %s" % (type(ex).__name__, str(ex)[:150])
    e["rows"] = rows
    R["scenes"][name] = e; dump()
    print(json.dumps({k: e[k] for k in ("objects_total", "skipped_over_limit", "read_ok", "read_errors", "sum_vertices", "unique_meshes", "lod", "stopped", "read_s", "log_growth_bytes")}, ensure_ascii=False), flush=True)
    for a in e["top10_by_mesh_vertices"][:10]: print("   ", a)
    print("   error sample", err_sample)
R["exceptions"] = exc_summary(off); dump(); print("exc", R["exceptions"]["by_type"], "sec", round(time.time() - START))
