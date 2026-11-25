# -*- coding: utf-8 -*-
"""Этап 1: GUARD-01 (проверка на замороженном игроке в меню паузы) и PAUSE-01 (Beach)."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastlib import *
d = connect(); st = load_state()
pre = guard.preflight("stage1"); print("preflight", {k: pre[k] for k in ("consoleFlags","error_pause","play","alive")}, "iconic", pre["window"].get("iconic"))
if pre["window"].get("iconic"): raise SystemExit("окно Unity свёрнуто")
LOG0 = log_mark(); st["log0_stage1"] = LOG0
def menu_open(): return comp_active("UIPause") or any(True for o in d.find_objects(By.NAME, "Pause_Screen", enabled=True))
def tscale(): return d.get_static_property("UnityEngine.Time", "timeScale", CORE)
def close_menu_esc():
    key("Escape", 0.1); time.sleep(1.2); return not menu_open()
print("menu_open", menu_open(), "timeScale", tscale(), "scenes", scenes())
SAVE0 = save_hashes(); st["save_hashes_stage1_start"] = SAVE0

# ---------- GUARD-01: заведомо замороженный случай (меню паузы открыто) ----------
if not menu_open(): key("Escape", 0.1); time.sleep(1.5)
frozen_state = {"menu_open": menu_open(), "timeScale": tscale()}
called = {"n": 0}
def dummy(): called["n"] += 1; return {"verdict": "Пройдено", "numbers": "(заглушка: всегда Passed)"}
r1 = case("GUARD-01 frozen (меню паузы)", dummy)
shot("guard01_frozen")
ok_frozen = r1["verdict"] == "Invalid" and called["n"] == 0
closed = close_menu_esc()
print("меню закрыто Esc:", closed, "timeScale", tscale())
r2 = case("GUARD-01 control (свободное управление)", dummy)
ok_ctrl = r2["verdict"] == "Пройдено" and r2["guard01"]["approach_moved_m"] >= 0.3
# проверка флага Sliding на синтетической последовательности
sw = guard.SlideWatch()
for t, s in ((0, "Walking"), (1, "Sliding"), (2, "Sliding"), (3.5, "Sliding"), (4.6, "Sliding")): sw.tick(s, t)
sw2 = guard.SlideWatch()
for t, s in ((0, "Sliding"), (2, "Sliding"), (2.5, "Walking"), (3, "Sliding"), (5, "Sliding")): sw2.tick(s, t)
slide_ok = sw.flag and not sw2.flag
md_row("GUARD-01", "Пройдено" if (ok_frozen and ok_ctrl and slide_ok) else "Не пройдено",
  "замороженный случай (меню паузы «Hold on!» открыто, timeScale %s): шаг подхода W 0,3 с сдвинул на %s м (< 0,3), кейс-заглушка с вердиктом Passed получил «%s», заглушка не вызывалась (вызовов %d); контроль (меню закрыто Esc=%s): сдвиг %s м (≥ 0,3), вердикт «%s»; флаг Sliding > 3 с: непрерывные 3,6 с → флаг=%s, 2 + 2 с с перерывом → флаг=%s (ожидаются True/False)" %
  (frozen_state["timeScale"], r1.get("guard01", {}).get("approach_moved_m"), r1["verdict"], called["n"], closed, r2["guard01"]["approach_moved_m"], r2["verdict"], sw.flag, sw2.flag),
  "shots/guard01_frozen.png; встроено: scripts/fast_run3/guard.py (SlideWatch, judge), fastlib.py (approach_step, case)")

# ---------- PAUSE-01 ----------
def pause01():
    out = {}
    out["menu_before"] = menu_open(); out["ts_before"] = tscale()
    a = approach_step("W", 0.3, 0.6); out["free_step_m"] = a["moved_m"]
    shot("pause01_free")
    f0 = d.get_static_property("UnityEngine.Time", "frameCount", CORE); tm0 = d.get_static_property("UnityEngine.Time", "time", CORE)
    key("Escape", 0.1); time.sleep(1.5)
    out["menu_open"] = menu_open(); out["ts_open"] = tscale()
    tm1 = d.get_static_property("UnityEngine.Time", "time", CORE); time.sleep(1.5)
    tm2 = d.get_static_property("UnityEngine.Time", "time", CORE); f1 = d.get_static_property("UnityEngine.Time", "frameCount", CORE)
    out["game_time_delta_1_5s"] = round(tm2 - tm1, 4); out["frames_rendered"] = f1 - f0
    p0 = ppos(); key("W", 0.5); time.sleep(0.6); p1 = ppos(); out["w_in_menu_m"] = round(dxz(p0, p1), 3)
    shot("pause01_menu")
    out["closed_by_esc"] = close_menu_esc(); out["menu_after"] = menu_open(); out["ts_after"] = tscale()
    if menu_open():
        d.find_object(By.NAME, "ResumeButton", enabled=False).click(); time.sleep(1.2); out["closed_by_resume_button"] = not menu_open(); out["ts_after"] = tscale()
    b = approach_step("W", 0.3, 0.6); out["resumed_step_m"] = b["moved_m"]
    shot("pause01_resumed")
    ok = (out["menu_open"] and out["ts_open"] == 0 and abs(out["game_time_delta_1_5s"]) < 0.001 and out["w_in_menu_m"] < 0.05
          and not out["menu_after"] and out["ts_after"] == 1 and out["resumed_step_m"] >= 0.5)
    out["verdict"] = "Пройдено" if ok else "Не пройдено"
    out["numbers"] = ("Beach, свободно: шаг W до паузы %s м; Esc → меню открыто=%s, timeScale %s, игровое время за 1,5 с +%s (кадров отрисовано %s); W 0,5 с в меню сдвинул на %s м; закрыто Esc=%s (после: меню=%s, timeScale %s); шаг после закрытия %s м (≥ 0,5)" %
                      (out["free_step_m"], out["menu_open"], out["ts_open"], out["game_time_delta_1_5s"], out["frames_rendered"], out["w_in_menu_m"], out["closed_by_esc"], out["menu_after"], out["ts_after"], out["resumed_step_m"]))
    out["evidence"] = "shots/pause01_free.png, pause01_menu.png, pause01_resumed.png"
    return out
r = case("PAUSE-01", pause01, approach=False)
md_row("PAUSE-01", r["verdict"], r["numbers"], r.get("evidence", ""))
print("stage1 готов; save changed:", save_hashes() != SAVE0, "log:", log_since(LOG0))
