# -*- coding: utf-8 -*-
# общие функции stage7
import os, sys, json, time, statistics
os.environ["MOD_OUT"] = "Test_Ai/Reports_2026-11-21/results/modules_stage7_20261126"
sys.path.insert(0, r"Test_Ai\scripts\stage6")
from s3blib import *

R7 = OUT
ED = "UnityEditor.CoreModule"


def sg(cls, prop, asm=CORE):
    try:
        return d.get_static_property(cls, prop, asm)
    except Exception as e:
        return "ERR %s: %s" % (type(e).__name__, str(e)[:160])


def sm(cls, method, asm=CORE):
    try:
        return d.call_static_method(cls, method, asm, [])
    except Exception as e:
        return "ERR %s: %s" % (type(e).__name__, str(e)[:160])


def memory():
    P = "UnityEngine.Profiling.Profiler"
    return {"total_allocated": sm(P, "GetTotalAllocatedMemoryLong"), "mono_used": sm(P, "GetMonoUsedSizeLong")}


def env():
    return {"targetFrameRate": sg("UnityEngine.Application", "targetFrameRate"), "vSyncCount": sg("UnityEngine.QualitySettings", "vSyncCount"),
            "screen": [sg("UnityEngine.Screen", "width"), sg("UnityEngine.Screen", "height")],
            "isFocused": sg("UnityEngine.Application", "isFocused"), "iconic": guard.unity_window().get("iconic"),
            "runInBackground": sg("UnityEngine.Application", "runInBackground")}


def cheat_click(name):
    """открыть меню читов и кликнуть кнопку локации; возвращает (время клика, текст кнопки)"""
    for _ in range(3):
        if cheat_open():
            break
        key("C", 0.1); time.sleep(1.2)
    assert cheat_open(), "меню читов не открылось"
    label = LABEL[name]
    for t in d.find_objects(By.PATH, "//CheatMenu/*/Text", enabled=False):
        s = t.get_text()
        if s.startswith(label):
            b = t.get_parent()
            t0 = time.time(); b.click()
            return t0, s
    raise RuntimeError("нет кнопки " + label)


def load_loc(name, timeout=30, settle=True):
    """клик -> появление сцены (опрос 0,5 с). Возвращает dict; ok=False, если сцена не появилась"""
    want = SCN[name]
    before = locs()
    t0, txt = cheat_click(name)
    sec = None; errs = 0
    while time.time() - t0 < timeout:
        time.sleep(0.5)
        try:
            now_ = locs()
            if want in now_ and (want in before or not any(b in now_ for b in before)):
                sec = round(time.time() - t0, 2); break
        except Exception:
            errs += 1
    if settle:
        time.sleep(1.0)
        if cheat_open():
            key("C", 0.1); time.sleep(0.8)
    return {"from": before, "to": name, "ok": sec is not None, "load_s": sec, "poll_errors": errs, "button": txt}


def pig_active():
    return len(d.find_objects(By.NAME, "PigChef(Clone)", enabled=True)) > 0


def wait_ready(timeout=30):
    """игрок активен и Gameplay (интро в Beach скрывает PigChef)"""
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            if pig_active() and gstate() == 0:
                return round(time.time() - t0, 1)
        except Exception:
            pass
        time.sleep(1.0)
    return None


def goto_retry(name, vias=("Town_Market", "Mountain_Cave", "Forest")):
    """load_loc с обходом через промежуточную локацию (известная особенность меню читов)"""
    tries = []
    r = load_loc(name); tries.append(r)
    for via in vias:
        if r["ok"]:
            break
        if via == name:
            continue
        time.sleep(2)
        tries.append(load_loc(via)); time.sleep(3)
        r = load_loc(name); tries.append(r)
    return r, tries


def log_len():
    return os.path.getsize(EDLOG)


# s3blib перезаписывает MOD_OUT на папку stage6: вернуть все пути на stage7
R7 = "Test_Ai/Reports_2026-11-21/results/modules_stage7_20261126"
OUT = R7
guard.RES = R7; guard.STATE_F = os.path.join(R7, "run_state.json"); guard.STALL_F = os.path.join(R7, "stall_report.json")
guard.TAILS = os.path.join(R7, "log_tails"); guard.SHOTS = os.path.join(R7, "shots"); guard.WIN_LOG = os.path.join(R7, "window_restores.txt")
os.makedirs(guard.TAILS, exist_ok=True); os.makedirs(guard.SHOTS, exist_ok=True)
import fastlib
fastlib.REPO_RES = R7; fastlib.STATE_F = guard.STATE_F; fastlib.RES_F = os.path.join(R7, "results.json"); fastlib.SHOTS = guard.SHOTS
fastlib.MD_F = os.path.join(R7, "rows.md")
