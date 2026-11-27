# -*- coding: utf-8 -*-
import os, sys, json, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from l10n_lib import *
d = connect(); R = {"cycles": []}
BK = r"Test_Ai\Reports_2026-11-21\evidence\save_backup\20261122_122526"
MAP = {"Unity_Technologies": SAVE_DIRS[0], "Unity_Open_Projects": SAVE_DIRS[1]}
def bk_hashes():
    out = {}
    for sub, dst in MAP.items():
        for f in ("save.chop", "save.chop.bak"): out[os.path.join(dst, f)] = sha(os.path.join(BK, sub, f))
    return out
def restore():
    for sub, dst in MAP.items():
        for f in ("save.chop", "save.chop.bak"):
            s = os.path.join(BK, sub, f)
            if os.path.exists(s): shutil.copy2(s, os.path.join(dst, f))
    return save_hashes() == bk_hashes()
pre = guard.preflight("menu08"); print("preflight", {k: pre[k] for k in ("consoleFlags","error_pause","play","alive")}, "iconic", pre["window"].get("iconic"))
if pre["window"].get("iconic") or pre["error_pause"]: raise SystemExit("стоп")
def counts():
    return {"EventSystem_comp": len(d.find_objects(By.COMPONENT, "UnityEngine.EventSystems.EventSystem", enabled=False)),
            "EventSystem_name": len(d.find_objects(By.NAME, "EventSystem", enabled=False)),
            "PersistentManagers_name": len(d.find_objects(By.NAME, "PersistentManagers", enabled=False)),
            "PigChef": len(pigs())}
base = counts(); R["baseline"] = base; R["baseline_scenes"] = scenes(); print("baseline", base, R["baseline_scenes"])
guard.risky("MENU-08: 3 круга Back to menu -> New Game")
R["checkpoint"] = {"save": save_hashes(), "log": log_mark()}
def pause_open(): return any(True for _ in d.find_objects(By.NAME, "Pause_Screen", enabled=True))
def to_menu():
    if not pause_open(): key("Escape", 0.1); time.sleep(1.5)
    d.find_object(By.NAME, "BackToMenuButton", enabled=False).click(); time.sleep(1.5)
    d.find_object(By.NAME, "PopupButton - 1", enabled=False).click()
    t0 = time.time()
    while time.time() - t0 < 40:
        try:
            if "MainMenu" in scenes(): return round(time.time() - t0, 1)
        except Exception: pass
        time.sleep(0.5)
    return None
def new_game():
    t0 = time.time(); d.find_object(By.NAME, "Button New Game", enabled=False).click()
    for _ in range(15):
        time.sleep(0.4)
        try: d.find_object(By.NAME, "PopupButton - 1", enabled=False).click(); break
        except Exception: pass
    seen = {}; found = None
    while time.time() - t0 < 60:
        try:
            sc = scenes()
            for n in ("PersistentManagers", "Gameplay", "Beach"):
                if n in sc and n not in seen: seen[n] = round(time.time() - t0, 1)
            if "Beach" in sc and pig(): found = round(time.time() - t0, 1); break
        except Exception: pass
        time.sleep(0.3)
    return found, seen
def probe_ph(i, secs=12.0):
    """следить за UI.Text с «PLACEHOLDER»: первое появление, исчезновение, родители, скриншот"""
    t0 = time.time(); first = None; last = None; info = None
    while time.time() - t0 < secs:
        hit = None
        try:
            for o in d.find_objects(By.COMPONENT, "UnityEngine.UI.Text", enabled=True):
                t = o.get_component_property("UnityEngine.UI.Text", "text", "UnityEngine.UI")
                if t and "PLACEHOLDER" in t: hit = o; break
        except Exception: pass
        if hit is not None:
            last = round(time.time() - t0, 1)
            if first is None:
                first = last; shot("menu08_c%d_placeholder" % i)
                try:
                    ch = []; p = hit.get_parent()
                    while p is not None and len(ch) < 8: ch.append(p.name); p = p.get_parent()
                    info = {"name": hit.name, "parents": ch, "xy": (round(hit.x), round(hit.y))}
                except Exception as e: info = {"name": hit.name, "err": type(e).__name__}
        time.sleep(0.5)
    return {"first_s": first, "last_s": last, "info": info}
stopped = None
for i in (1, 2, 3):
    c = {"n": i}; off = log_mark()
    try:
        guard.before_case("MENU-08 круг %d" % i)
        c["to_menu_s"] = to_menu()
        if c["to_menu_s"] is None: c["fail"] = "MainMenu не загрузилось за 40 с"; R["cycles"].append(c); break
        time.sleep(4.0)
        c["menu_scenes"] = scenes(); c["menu_counts"] = counts(); c["menu_texts"] = read_texts(); c["menu_text_bad"] = audit(c["menu_texts"])
        shot("menu08_c%d_mainmenu" % i)
        if i == 1:   # язык в Settings главного меню
            try:
                d.find_object(By.NAME, "Button Settings ", enabled=False).click(); time.sleep(1.5)
                d.find_object(By.NAME, "Language_Tab", enabled=False).click(); time.sleep(1.0)
                c["menu_settings_lang"] = lang_cur(); c["menu_settings_texts"] = [t for n, t in read_texts()]; shot("menu08_menu_settings")
                d.find_object(By.NAME, "Button Close", enabled=True).click(); time.sleep(1.0)
            except Exception as e: c["menu_settings_err"] = type(e).__name__
        if i == 1:   # хеш против копии; при отличии вернуть из копии
            c["hash_before_ng"] = save_hashes(); c["hash_equal_backup"] = c["hash_before_ng"] == bk_hashes()
            if not c["hash_equal_backup"]: c["restored_ok"] = restore()
        else:
            c["hash_before_ng"] = save_hashes(); c["hash_equal_backup"] = c["hash_before_ng"] == bk_hashes()
        c["new_game_s"], c["scene_times"] = new_game()
        if c["new_game_s"] is None: c["fail"] = "игрок не найден за 60 с"; R["cycles"].append(c); break
        c["texts_1s"] = read_texts(); c["placeholder_probe"] = probe_ph(i); c["texts_5s"] = read_texts()
        c["scenes"] = scenes(); c["counts"] = counts()
        o = pig(); c["health"] = health(o); c["pos"] = tuple(round(v, 2) for v in ppos()); c["timeScale"] = d.get_static_property("UnityEngine.Time", "timeScale", CORE)
        c["pause_menu_open"] = pause_open()
        a = approach_step("W", 0.3, 0.6); c["approach_m"] = a["moved_m"]; c["sliding_flag"] = a["slide"].flag
        lg = log_since(off); c["log"] = {k: lg[k] for k in ("exceptions", "errors", "cc_inactive_warnings", "warnings_other")}; c["log_samples"] = lg["samples"][:3]
        shot("menu08_c%d_beach" % i)
        c["texts_bad"] = audit(c["texts_1s"]) + audit(c["texts_5s"])
        c["placeholder_seen"] = any("PLACEHOLDER" in (t or "") for t in [x[1] for x in c["texts_1s"] + c["texts_5s"]])
        c["ok"] = (sorted(c["scenes"]) == ["Beach", "Gameplay", "PersistentManagers"] and len(c["scenes"]) == 3 and c["counts"]["EventSystem_comp"] == base["EventSystem_comp"]
                   and c["counts"]["EventSystem_name"] == base["EventSystem_name"] and c["counts"]["PersistentManagers_name"] == base["PersistentManagers_name"]
                   and c["counts"]["PigChef"] == 1 and lg["exceptions"] == 0 and c["approach_m"] >= guard.MIN_APPROACH_M)
        print("круг", i, "ok:", c["ok"], {k: c[k] for k in ("to_menu_s", "new_game_s", "scenes", "counts", "log", "approach_m", "placeholder_seen")}, flush=True)
    except (guard.Paused, Exception) as e:
        c["fail"] = "%s: %s" % (type(e).__name__, str(e)[:160]); c["tb"] = __import__("traceback").format_exc()[-700:]; stopped = c["fail"]
        try: c["stall"] = guard.stall_report("MENU-08 круг %d" % i, why=c["fail"])
        except Exception: pass
    R["cycles"].append(c)
    json.dump(R, open(os.path.join(REPO_RES, "menu08.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    if stopped: break
print("итог:", [(c["n"], c.get("ok"), c.get("fail")) for c in R["cycles"]])
