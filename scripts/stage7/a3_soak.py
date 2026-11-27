from g7 import *
F = os.path.join(R7, "soak.json")
R = {"note": "редактор Unity", "transitions": [], "menu": []}
def dump(): jdump(F, R)
prestage("a3")
off = log_mark(); R["log_offset"] = off
hyg_tick(R, "a3")
MAN = {"AudioListener": "AudioListener", "Camera": "Camera", "EventSystem": None,
       "InventoryManager": "InventoryManager", "UIManager": "UIManager", "Protagonist": "Protagonist"}
def probe(label):
    s = {"label": label, "t": now(), "scenes": scenes(), "memory": memory()}
    c = {}
    for k, comp in MAN.items():
        try: c[k] = len(d.find_objects(By.COMPONENT, comp, enabled=False)) if comp else len(d.find_objects(By.NAME, k, enabled=False))
        except Exception as e: c[k] = "ERR " + type(e).__name__
    s["counts"] = c; s["editor_log_len"] = log_len(); s["exceptions"] = exc_summary(off)["total"]
    print(json.dumps({"label": label, "c": c, "mem": s["memory"], "log": s["editor_log_len"], "exc": s["exceptions"], "sc": s["scenes"]}, ensure_ascii=False), flush=True)
    return s
START = time.time()
if "Beach" not in scenes():
    goto_retry("Beach")
wait_ready(40); time.sleep(2)
R["baseline"] = probe("база Beach"); dump()
for i in range(1, 11):
    if time.time() - START > 11 * 60:
        R["transitions_stopped"] = "лимит времени после цикла %d" % (i - 1); break
    cyc = {"cycle": i, "legs": []}
    try:
        for name in ("Field_Hill", "Beach"):
            r = load_loc(name, settle=True)
            if not r["ok"]:
                time.sleep(3); r2 = load_loc(name, settle=True); r2["retry_after_fail"] = True; r = r2
            if not r["ok"]:
                _, tries = goto_retry(name); r = tries[-1]; r["via_intermediate"] = len(tries)
            cyc["legs"].append(r)
            assert r["ok"], "переход не удался: " + name
            time.sleep(2)
        cyc["wait_ready_s"] = wait_ready(40); time.sleep(1)
        cyc.update(probe("переход %d" % i))
    except Exception as e:
        cyc["error"] = "%s: %s" % (type(e).__name__, str(e)[:200]); print(cyc["error"], flush=True)
    R["transitions"].append(cyc); dump()
    hyg_tick(R, "t%d" % i)
R["menu_baseline"] = probe("база перед меню"); dump()
for i in range(1, 6):
    cyc = {"cycle": i}
    try:
        if cheat_open(): key("C", 0.1); time.sleep(1)
        cyc["to_menu_s"] = to_menu(); time.sleep(2)
        assert cyc["to_menu_s"] is not None, "MainMenu не появился"
        cyc["in_menu"] = probe("меню %d: MainMenu" % i)
        guard.restore_window("menu")
        cyc["new_game_s"] = new_game()
        assert cyc["new_game_s"] is not None, "New Game не загрузился"
        cyc["wait_ready_s"] = wait_ready(45); time.sleep(2)
        cyc.update(probe("меню %d: после New Game" % i))
    except Exception as e:
        cyc["error"] = "%s: %s" % (type(e).__name__, str(e)[:200]); print(cyc["error"], flush=True)
    R["menu"].append(cyc); dump()
    hyg_tick(R, "m%d" % i)
R["exc_summary"] = exc_summary(off); R["log_growth_bytes"] = log_len() - off; R["seconds"] = round(time.time() - START); dump()
print("done", R["exc_summary"]["by_type"], R["exc_summary"]["first_stacks"], R["seconds"])
