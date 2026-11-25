# -*- coding: utf-8 -*-
"""Этап 0: копия сохранений, пролог (runInBackground), метка Editor.log, New Game до Beach."""
import os, sys, time, shutil, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastlib import *

d = connect()
st = load_state() or {}
st["run_started"] = datetime.datetime.now().isoformat(timespec="seconds")
print("сцены:", scenes())

# пролог 2.4 (1): runInBackground = true и рост Time.frameCount
st["orig_runInBackground"] = d.get_static_property("UnityEngine.Application", "runInBackground", CORE)
d.set_static_property("UnityEngine.Application", "runInBackground", CORE, True)
f1 = d.get_static_property("UnityEngine.Time", "frameCount", CORE); t1 = time.perf_counter(); time.sleep(1.0)
f2 = d.get_static_property("UnityEngine.Time", "frameCount", CORE); t2 = time.perf_counter()
st["prologue"] = {"runInBackground_now": d.get_static_property("UnityEngine.Application", "runInBackground", CORE),
                  "frames_per_s": round((f2 - f1) / (t2 - t1), 1), "ok": (f2 - f1) >= 30}
print("пролог:", st["prologue"], "исходное runInBackground:", st["orig_runInBackground"])
if not st["prologue"]["ok"]:
    save_state(st); print("STOP: Time.frameCount вырос меньше чем на 30 за 1 с"); sys.exit(2)

# пролог 2.4 (2): метка Editor.log
st["editor_log_offset0"] = log_mark()
with open(EDLOG, "rb") as f:
    f.seek(max(0, st["editor_log_offset0"] - 400)); st["editor_log_last_line"] = [l for l in f.read().decode("utf-8", "replace").split("\n") if l.strip()][-1][:200]

# пролог 2.4 (3): копии обеих папок сразу перед New Game
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
bk = os.path.join(TESTAI, "Reports_2026-11-21", "evidence", "save_backup", stamp)
st["backup_dir"] = bk; st["saves_hash_before"] = save_hashes()
for i, sd in enumerate(SAVE_DIRS):
    sub = os.path.join(bk, os.path.basename(os.path.dirname(sd)).replace(" ", "_"))
    os.makedirs(sub, exist_ok=True)
    for f in ("save.chop", "save.chop.bak"):
        s = os.path.join(sd, f)
        if os.path.exists(s): shutil.copy2(s, os.path.join(sub, f))
print("копия сохранений:", bk, st["saves_hash_before"])
save_state(st)

# New Game
sc = scenes()
if "MainMenu" not in sc:
    print("STOP: не MainMenu:", sc); sys.exit(2)
t0 = time.time()
d.find_object(By.NAME, "Button New Game", enabled=False).tap()
for _ in range(15):
    time.sleep(0.4)
    try:
        d.find_object(By.NAME, "PopupButton - 1", enabled=False).tap(); break
    except Exception:
        pass
seen = {}; found = None
while time.time() - t0 < 60:
    sc = scenes()
    for n in ("PersistentManagers", "Gameplay", "Beach"):
        if n in sc and n not in seen: seen[n] = round(time.time() - t0, 1)
    if "Beach" in sc:
        o = pig()
        if o: found = round(time.time() - t0, 1); break
    time.sleep(0.3)
st["new_game"] = {"load_s": found, "scene_times": seen}
print("New Game: игрок найден через", found, "с", seen)
if found is None:
    save_state(st); print("STOP: игрок не появился за 60 с"); sys.exit(2)
# ждать управляемости: isGrounded и 3 с покоя
time.sleep(3.0)
o = pig(); p = ppos(o)
st["spawn_found_pos"] = p; st["spawn_grounded"] = grounded(o); st["spawn_health"] = health(o)
st["after_newgame_log"] = log_since(st["editor_log_offset0"])
print("позиция игрока:", p, "isGrounded", st["spawn_grounded"], "здоровье", st["spawn_health"], "сцены", scenes())
save_state(st)
