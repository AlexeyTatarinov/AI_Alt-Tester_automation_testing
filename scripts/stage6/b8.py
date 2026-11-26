# M08-02: ToForestEntrance_FallDown, строго последним
from g6 import *
from pts import inside
R = {"after": []}
def dump(): jdump(os.path.join(R2, "b8.json"), R)
def st(label, off=None):
    s = {"label": label, "t": now(), "scenes": scenes()}
    for k, f in (("_isLoading", lambda: rd(first("SceneLoader"), "SceneLoader", "_isLoading", 1)), ("state", lambda: sname(gstate())),
                 ("pigs", lambda: len(pigs())), ("pigs_active", lambda: len(d.find_objects(By.NAME, "PigChef(Clone)", enabled=True))),
                 ("pig_pos", lambda: [round(v, 2) for v in (pigs()[0].worldX, pigs()[0].worldY, pigs()[0].worldZ)] if pigs() else None),
                 ("maps", lambda: {m: rd(first("Protagonist"), "Protagonist", "_inputReader._gameInput.%s.enabled" % m) for m in ("Gameplay", "Menus", "Dialogues")} if first("Protagonist") else None),
                 ("frame", lambda: d.get_static_property("UnityEngine.Time", "frameCount", CORE)),
                 ("timeScale", lambda: d.get_static_property("UnityEngine.Time", "timeScale", CORE))):
        try: s[k] = f()
        except Exception as e: s[k] = "ERR " + type(e).__name__
    if off is not None:
        e = exc_summary(off); s["exc"] = e["total"]; s["by_type"] = e["by_type"]
        if e["total"]: R["stack"] = e["first_stacks"]
    print(json.dumps(s, ensure_ascii=False), flush=True); return s
prestage("b8"); hyg_tick(R, "b8")
if "Town_Upper" not in scenes():
    for via in (None, "Town_Market", "Mountain_Cave"):
        try:
            if via: goto(via); time.sleep(3)
            print("goto", goto("Town_Upper"), flush=True); break
        except Exception as e: print("ERR", e, flush=True)
time.sleep(2); wait_play_ready()
EX = exits(); full = json.load(open(os.path.join(R2, "b3_Town_Upper.json"), encoding="utf-8"))["exits"]
x, y, z = -34.2, 21.04 + 3, 14.3; R["point"] = [x, y, z]
R["covers"] = [e["name"] for e in full if inside(e, x, z, 0.8)]; print("covers", R["covers"], flush=True)
assert R["covers"] == ["LocationExit_ToForestEntrance_FallDown"]
R["before"] = st("до"); R["log_len_before"] = off = log_mark(); dump()
autosync(True); teleport("T1", x, y, z); autosync(False); t0 = time.time()
try:
    for at in (5, 15, 30):
        while time.time() - t0 < at: time.sleep(0.2)
        R["after"].append(st("%d с" % at, off)); dump()
        d.get_png_screenshot(os.path.join(R2, "shots", "b8_%ds.png" % at))
    # одна попытка обычного выхода
    live = exits(); R["exits_loaded"] = [e["name"] for e in live]; print("exits loaded", R["exits_loaded"], flush=True)
    norm = [e for e in live if e["name"] == "LocationExit_ToInnerTown_Slope"]
    if norm and pigs():
        autosync(True)
        try: teleport("T1", 5.27, 21.9, 52.95); R["normal_try"] = "T1 в LocationExit_ToInnerTown_Slope"
        except Exception as e: R["normal_try"] = "T1 не прошёл: %s" % type(e).__name__
        autosync(False)
    else:
        R["normal_try"] = "обычных выходов нет в загруженных сценах (%d) или нет игрока; попытка: меню читов (C) -> Town_Market" % len(live)
        key("C", 0.1); time.sleep(1.5); R["cheat_opens"] = cheat_open()
        if R["cheat_opens"]:
            try: print(goto("Town_Market", 20))
            except Exception as e: R["cheat_goto_err"] = str(e)[:150]
        else: key("Escape", 0.1); time.sleep(1.5); R["pause_opens"] = pause_open()
    time.sleep(10); R["after_try"] = st("после попытки", off); print(R["normal_try"], R.get("cheat_opens"), R.get("pause_opens"), flush=True)
    d.get_png_screenshot(os.path.join(R2, "shots", "b8_after_try.png"))
    R["log"] = log_since(off); R["exc"] = exc_summary(off); print(R["log"], R["exc"]["by_type"], R["exc"]["first_stacks"], flush=True)
finally:
    autosync(False); dump()
