from g7 import *
import shutil, glob, re
F = os.path.join(R7, "cc94_save.json")
R = {}
def dump(): jdump(F, R)
prestage("b3")
hyg_tick(R, "b3")
SF = os.path.join(SAVE_DIRS[0], "save.chop")
def guid_map():
    m = {}
    for f in glob.glob(r"C:\Games\ChopChop\UOP1_Project\Assets\ScriptableObjects\**\*.asset", recursive=True):
        try: g = re.search(r"_guid: (\w+)", open(f, encoding="utf-8-sig").read())
        except Exception: continue
        if g: m[g.group(1)] = f.split("Assets")[1].replace("\\", "/")
    return m
GM = guid_map()
def snap(tag):
    s = {"t": now(), "scenes": scenes()}
    for fn, out in (("save.chop", "save_%s.chop" % tag), ("save.chop.bak", "save_%s.chop.bak" % tag)):
        src = os.path.join(SAVE_DIRS[0], fn)
        if not os.path.exists(src):
            s[fn] = "нет файла"; continue
        dst = os.path.join(R7, out); shutil.copy2(src, dst)
        e = {"sha": sha(dst), "size": os.path.getsize(dst), "mtime": time.strftime("%H:%M:%S", time.localtime(os.path.getmtime(dst)))}
        try:
            j = json.load(open(dst, encoding="utf-8"))
            e["json_ok"] = True; e["locationId"] = j.get("_locationId"); e["location_asset"] = GM.get(j.get("_locationId"))
            e["inventory"] = {GM.get(x["itemGuid"], x["itemGuid"]).split("/")[-1]: x["amount"] for x in j.get("_itemStacks", [])}
            e["finished_steps"] = j.get("_finishedQuestlineItemsGUIds"); e["keys"] = sorted(j.keys())
        except Exception as ex:
            e["json_ok"] = False; e["json_error"] = str(ex)[:150]
        s[fn] = e
    print(tag, json.dumps(s, ensure_ascii=False), flush=True)
    return s
def game(off=None):
    s = {"t": now(), "scenes": scenes()}
    for k, f in (("_isLoading", lambda: rd(first("SceneLoader"), "SceneLoader", "_isLoading", 1)), ("state", lambda: sname(gstate())),
                 ("pigs", lambda: len(pigs())), ("memory_locationId", lambda: rd(first("StartGame"), "StartGame", "_saveSystem.saveData._locationId", 2) if first("StartGame") else None)):
        try: s[k] = f()
        except Exception as e: s[k] = "ERR " + type(e).__name__
    if off is not None:
        e = exc_summary(off); s["exc"] = e["total"]; s["by_type"] = e["by_type"]; s["stacks"] = e["first_stacks"]
    print(json.dumps(s, ensure_ascii=False)[:900], flush=True)
    return s
if "MainMenu" not in scenes():
    to_menu(); time.sleep(2)
guard.restore_window("b3 new game")
R["new_game_s"] = new_game(); R["ready_s"] = wait_ready(45); time.sleep(2)
r, tries = goto_retry("Town_Upper"); R["goto"] = tries
assert r["ok"], "Town_Upper не загрузился"
wait_ready(30); time.sleep(3)
R["game_before"] = game(); R["before"] = snap("before"); dump()
off = log_mark()
d.get_png_screenshot(os.path.join(R7, "shots", "cc94_before.png"))
try:
    autosync(True); teleport("T1", -34.2, 24.04, 14.3)
finally:
    autosync(False)
t0 = time.time()
while time.time() - t0 < 30: time.sleep(1.0)
R["game_after"] = game(off); R["after"] = snap("after")
R["autoSyncTransforms"] = sg("UnityEngine.Physics", "autoSyncTransforms", PHYS)
d.get_png_screenshot(os.path.join(R7, "shots", "cc94_after.png"))
a, b = R["before"]["save.chop"], R["after"]["save.chop"]
R["compare"] = {k: [a.get(k), b.get(k)] for k in ("sha", "size", "mtime", "json_ok", "locationId", "location_asset", "inventory", "finished_steps")}
R["compare_equal"] = {k: v[0] == v[1] for k, v in R["compare"].items()}
dump(); print(json.dumps(R["compare_equal"]), R["autoSyncTransforms"])
