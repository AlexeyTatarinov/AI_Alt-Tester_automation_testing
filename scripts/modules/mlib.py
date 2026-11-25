# -*- coding: utf-8 -*-
"""Общая библиотека задания modules_stage1: перенаправляет файлы guard/fastlib в папку этого запуска (свежий счётчик восстановлений окна)."""
import os, sys, json, time, math
sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\fast_run7")
OUT = r"C:\Users\Aotat\Desktop\Test_Ai\Reports_2026-11-21\results\modules_stage1_20261125"
os.makedirs(OUT, exist_ok=True)
import fastlib, guard
guard.RES = OUT; guard.STATE_F = os.path.join(OUT, "run_state.json"); guard.STALL_F = os.path.join(OUT, "stall_report.json")
guard.TAILS = os.path.join(OUT, "log_tails"); guard.SHOTS = os.path.join(OUT, "shots"); guard.WIN_LOG = os.path.join(OUT, "window_restores.txt")
os.makedirs(guard.TAILS, exist_ok=True); os.makedirs(guard.SHOTS, exist_ok=True)
fastlib.REPO_RES = OUT; fastlib.STATE_F = guard.STATE_F; fastlib.RES_F = os.path.join(OUT, "results.json"); fastlib.SHOTS = guard.SHOTS
fastlib.MD_F = os.path.join(OUT, "rows.md")
from r4lib import *
import r4lib
from alttester import By, AltKeyCode
d = connect()

def prestage(label):
    """preflight перед этапом/сценой: Error Pause, жив, окно; при свёрнутом окне — restore (с повтором проверки)"""
    pre = guard.preflight(label)
    if pre["window"].get("iconic"):
        for _ in range(2):
            guard.restore_window("prestage " + label); time.sleep(1)
            w = guard.unity_window()
            if not w.get("iconic"): break
        pre["window"] = guard.unity_window()
    print("preflight", label, {k: pre[k] for k in ("consoleFlags", "error_pause", "alive")}, "iconic", pre["window"].get("iconic"), "pause_menu", pre.get("game_pause_menu"), flush=True)
    if pre["error_pause"]: raise SystemExit("STOP: Error Pause (7686)")
    if not pre["alive"]: raise SystemExit("STOP: игра не жива")
    return pre

def jdump(path, obj):
    json.dump(obj, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)

def sget(o, comp, prop, asm=ASM, depth=2):
    """безопасное чтение: (ok, value|error)"""
    t = time.time()
    try:
        v = o.get_component_property(comp, prop, asm, max_depth=depth)
        return {"call": f"{comp}.{prop} depth={depth}", "ok": True, "resp": str(v)[:300], "s": round(time.time()-t, 2), "raw": v}
    except Exception as e:
        return {"call": f"{comp}.{prop} depth={depth}", "ok": False, "resp": f"{type(e).__name__}: {str(e)[:250]}", "s": round(time.time()-t, 2)}
