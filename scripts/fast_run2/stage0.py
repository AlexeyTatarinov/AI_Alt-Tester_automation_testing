# -*- coding: utf-8 -*-
"""Прогон 2, этап 0: копия сохранений, пролог, возврат в меню (если игра в Beach), New Game до Beach.
Если после «Back to menu» связь пропала >20 с, останавливается и пишет, что видно."""
import os, sys, time, shutil, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastlib import *

d = connect()
st = load_state() or {}
REDO = "backup_dir" in st
st["run_started"] = datetime.datetime.now().isoformat(timespec="seconds")
st["orig_runInBackground"] = d.get_static_property("UnityEngine.Application", "runInBackground", CORE)
st["orig_autoSync"] = d.get_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS)
d.set_static_property("UnityEngine.Application", "runInBackground", CORE, True)
f1 = d.get_static_property("UnityEngine.Time", "frameCount", CORE); t1 = time.perf_counter(); time.sleep(1.0)
f2 = d.get_static_property("UnityEngine.Time", "frameCount", CORE); t2 = time.perf_counter()
st["prologue"] = {"runInBackground_now": d.get_static_property("UnityEngine.Application", "runInBackground", CORE),
                  "frames_per_s": round((f2 - f1) / (t2 - t1), 1), "ok": (f2 - f1) >= 30}
print("пролог:", st["prologue"], "исходные runInBackground/autoSync:", st["orig_runInBackground"], st["orig_autoSync"])
if not st["prologue"]["ok"]:
    save_state(st); print("STOP: Time.frameCount вырос меньше чем на 30 за 1 с"); sys.exit(2)
st["editor_log_offset0"] = log_mark()
with open(EDLOG, "rb") as f:
    f.seek(max(0, st["editor_log_offset0"] - 400)); st.setdefault("editor_log_last_line", None); st["editor_log_last_line"] = [l for l in f.read().decode("utf-8", "replace").split("\n") if l.strip()][-1][:200]
if not REDO:
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bk = os.path.join(TESTAI, "Reports_2026-11-21", "evidence", "save_backup", stamp)
    st["backup_dir"] = bk; st["saves_hash_before"] = save_hashes()
    for sd in SAVE_DIRS:
        sub = os.path.join(bk, os.path.basename(os.path.dirname(sd)).replace(" ", "_"))
        os.makedirs(sub, exist_ok=True)
        for f in ("save.chop", "save.chop.bak"):
            s = os.path.join(sd, f)
            if os.path.exists(s): shutil.copy2(s, os.path.join(sub, f))
print("копия сохранений:", st["backup_dir"], st["saves_hash_before"])
save_state(st)

sc = scenes()
if "MainMenu" not in sc:
    print("не MainMenu, возвращаюсь через паузу: сцены", sc)
    for _ in range(15):   # закрыть открытый диалог (иначе Escape не открывает паузу)
        if not comp_active("UIDialogueManager"): break
        key("Space", 0.1); time.sleep(0.8)
    key("Escape", 0.1); time.sleep(1.5)
    d.find_object(By.NAME, "BackToMenuButton", enabled=False).click(); time.sleep(1.5)
    d.find_object(By.NAME, "PopupButton - 1", enabled=False).click()
    t0 = time.time(); ok = False; last = None
    while time.time() - t0 < 25:
        try:
            sc = scenes(); last = sc
            if "MainMenu" in sc:
                ok = True; break
        except Exception as e:
            last = "%s" % type(e).__name__
        time.sleep(1.0)
    st["back_to_menu"] = {"ok": ok, "seconds": round(time.time() - t0, 1), "last": last}
    save_state(st)
    if not ok:
        print("STOP: после Back to menu связь/меню не вернулись за 25 с:", last); sys.exit(3)
    time.sleep(2.0)
t0 = time.time()
d.find_object(By.NAME, "Button New Game", enabled=False).click()
for _ in range(15):
    time.sleep(0.4)
    try:
        d.find_object(By.NAME, "PopupButton - 1", enabled=False).click(); break
    except Exception:
        pass
seen = {}; found = None
while time.time() - t0 < 60:
    sc = scenes()
    for n in ("PersistentManagers", "Gameplay", "Beach"):
        if n in sc and n not in seen: seen[n] = round(time.time() - t0, 1)
    if "Beach" in sc:
        try:
            o = pig()
        except Exception:
            o = None
        if o: found = round(time.time() - t0, 1); break
    time.sleep(0.3)
st["new_game"] = {"load_s": found, "scene_times": seen}
print("New Game: игрок найден через", found, "с", seen)
if found is None:
    save_state(st); print("STOP: игрок не появился за 60 с"); sys.exit(2)
time.sleep(3.0)
o = pig(); p = ppos(o)
st["spawn_found_pos"] = p; st["spawn_grounded"] = grounded(o); st["spawn_health"] = health(o)
st["tp_method"] = "T1"
print("позиция игрока:", p, "isGrounded", st["spawn_grounded"], "здоровье", st["spawn_health"], "сцены", scenes())
save_state(st)
