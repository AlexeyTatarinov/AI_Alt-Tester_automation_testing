# -*- coding: utf-8 -*-
"""Блок B, этап 2: INT-03 по исправленному критерию. Q не нажимается. Результат сразу в отчёт."""
import os, sys, time, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastlib import *

d = connect(); st = load_state()
d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, True)
R = 1.56   # радиус подсказки, INT-01 прогона 1
def hint(): return comp_active("UIInteraction")
def dlg(): return comp_active("UIDialogueManager")
def inv(): return comp_active("UIInventory")
def tp(t, wait=2.0):
    teleport("T1", t[0], t[1] + 0.3, t[2]); time.sleep(wait)

def yes_no_buttons():
    out = {}
    for o in d.find_objects(By.COMPONENT, "TMPro.TextMeshProUGUI", enabled=True):
        try:
            t = o.get_text().strip()
        except Exception:
            continue
        if t in ("Yes", "No"): out[t] = o
    return out

def int03():
    import guard; guard.risky("INT-03 Space в диалоге")
    if inv():
        key("Tab", 0.1); time.sleep(1.0)
    h0 = save_hashes(); off = log_mark()
    tp((HARE[0] - (R + 0.3), HARE[1], HARE[2]), 2.0)
    got = False
    for _ in range(8):
        step_towards(HARE, 0.15)
        if hint(): got = True; break
    if not got:
        return {"verdict": "Не проверено", "numbers": "подсказка у BardHare не появилась перед E (состояние не Gameplay или персонаж не повернут)", "screenshot": shot("INT-03_nohint")}
    key("E", 0.1)
    t0 = time.time(); opened = None
    while time.time() - t0 < 2.0:
        if dlg(): opened = round(time.time() - t0, 2); break
        time.sleep(0.05)
    if opened is None:
        return {"verdict": "Не пройдено", "numbers": "диалог не открылся за 2 с после E", "screenshot": shot("INT-03_nodlg")}
    n = 0; choice_at = None; clicked = None; texts = []
    for _ in range(40):
        if not dlg(): break
        if comp_active("UIDialogueChoicesManager"):
            yn = yes_no_buttons()
            if choice_at is None: choice_at = n
            if "Yes" in yn:
                yn["Yes"].click(); clicked = "Yes (клик мышью)"
            else:
                key("Return", 0.1); clicked = "Enter (кнопка Yes не найдена по тексту)"
            time.sleep(1.0)
            continue
        key("Space", 0.1); n += 1; time.sleep(0.7)
    closed = not dlg()
    # ждать возврата управления: диалог закрыт и подсказка у зайца видна, до 60 с
    t_close = time.time(); back = None; tl = []
    while time.time() - t_close < 60:
        h = hint(); dg = dlg()
        if len(tl) < 40: tl.append((round(time.time() - t_close, 1), h, dg))
        if h and not dg: back = round(time.time() - t_close, 1); break
        time.sleep(0.5)
    p0 = ppos(); step_dir((-1, 0), 0.3); moved = round(dxz(p0, ppos()), 2)
    h1 = save_hashes(); lg = log_since(off)
    ok = (opened <= 2.0 and closed and back is not None and moved >= 0.5)
    out = {"verdict": "Пройдено" if ok else "Не пройдено",
           "numbers": "диалог открылся за %s с; N = %d нажатий Space до закрытия (выбор Yes/No на нажатии %s, действие: %s); закрылся=%s; управление вернулось (подсказка у зайца, диалога нет) через %s с (до 60); шаг %s м; save.chop изменился=%s; исключений %d, ошибок %d. База N для DLG-10 от состояния после ручной игры владельца" % (
               opened, n, choice_at, clicked, closed, back, moved, h0 != h1, lg["exceptions"], lg["errors"]),
           "evidence": "run2_results.json"}
    if not ok: out["screenshot"] = shot("INT-03_fail")
    st["int03_N"] = n; save_state(st)
    return out

r = case("INT-03", int03); md_row("INT-03", r["verdict"], r["numbers"], r.get("screenshot", ""))
print("stage B2 готов")
