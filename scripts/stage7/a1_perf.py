from g7 import *
F = os.path.join(R7, "perf.json")
R = {"note": "редактор Unity (Play in Editor), не сборка", "locations": []}
def dump(): jdump(F, R)
prestage("a1")
off = log_mark(); R["log_offset_playA"] = off
hyg_start("a1", R)
R["env_menu"] = env()
R["new_game_s"] = new_game()
print("new game", R["new_game_s"], "ready after", wait_ready(40), flush=True)
R["env"] = env(); print(R["env"], flush=True); dump()
ORDER = ["Field_Hill", "Field_Farms", "Town_Market", "Town_Upper", "Town_Inner", "Forest", "Mountain_Path_bottom", "Mountain_Cave", "Mountain_Path_shaft", "Beach"]
for name in ORDER:
    e = {"name": name, "scene": SCN[name]}
    try:
        hyg_tick(R, name)
        r, tries = goto_retry(name); e["load"] = r; e["load_tries"] = tries
        if not r["ok"]:
            e["error"] = "сцена не загрузилась"; R["locations"].append(e); dump(); continue
        if name == "Beach":
            e["wait_intro_s"] = wait_ready(40)
        time.sleep(10)
        f0, t0 = sg("UnityEngine.Time", "frameCount"), sg("UnityEngine.Time", "realtimeSinceStartup")
        time.sleep(10)
        f1, t1 = sg("UnityEngine.Time", "frameCount"), sg("UnityEngine.Time", "realtimeSinceStartup")
        e["frames"] = f1 - f0; e["seconds"] = round(t1 - t0, 3); e["avg_fps"] = round((f1 - f0) / (t1 - t0), 1)
        dts = []
        for i in range(10):
            dts.append(sg("UnityEngine.Time", "unscaledDeltaTime")); time.sleep(1.0)
        nums = [x for x in dts if isinstance(x, (int, float))]
        e["unscaledDeltaTime"] = dts
        if nums:
            e["dt_median_ms"] = round(statistics.median(nums) * 1000, 2); e["dt_max_ms"] = round(max(nums) * 1000, 2)
        st = {"probe_batches": sg("UnityEditor.UnityStats", "batches", ED)}
        for p in ("drawCalls", "setPassCalls", "triangles", "vertices"):
            st[p] = sg("UnityEditor.UnityStats", p, ED)
        e["render"] = st
        e["memory"] = memory()
        e["window"] = {"isFocused": sg("UnityEngine.Application", "isFocused"), "iconic": guard.unity_window().get("iconic")}
        e["pig_active"] = pig_active(); e["state"] = sname(gstate()); e["scenes"] = scenes()
        e["exceptions_total"] = exc_summary(off)["total"]
    except Exception as ex:
        e["error"] = "%s: %s" % (type(ex).__name__, str(ex)[:200])
    R["locations"].append(e); dump()
    print(json.dumps({k: e.get(k) for k in ("name", "avg_fps", "dt_median_ms", "dt_max_ms", "render", "memory", "window", "error", "exceptions_total")}, ensure_ascii=False), "load", e.get("load", {}).get("load_s"), flush=True)
R["exceptions"] = exc_summary(off); R["log_growth_bytes"] = log_len() - off; dump()
print("done", R["exceptions"]["by_type"], R["log_growth_bytes"])
