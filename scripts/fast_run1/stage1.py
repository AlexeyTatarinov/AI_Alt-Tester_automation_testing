# -*- coding: utf-8 -*-
"""Этап 1: TP-00. Микро-тест трёх способов телепорта (T1 -> T2 -> T3), до 2 попыток на способ, 3 повтора «туда и обратно»."""
import os, sys, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastlib import *

d = connect(); st = load_state()
OUT = (-185.6, -9.4, -376.9)
detail = {}
chosen = None
for method in ("T1", "T2", "T3"):
    if method == "T1":
        if "orig_autoSync" not in st:
            st["orig_autoSync"] = d.get_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS)
            save_state(st)
        try:
            d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, True)
            detail["T1_autoSync_set"] = d.get_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS)
        except Exception as e:
            detail["T1_autoSync_set"] = "ошибка: %s: %s" % (type(e).__name__, str(e)[:200])
    for attempt in (1, 2):
        reps = []
        for rep in range(1, 4):
            out = tp_and_check(method, OUT, "out")
            back = tp_and_check(method, SPAWN, "back")
            reps.append({"rep": rep, "out": out, "back": back, "ok": bool(out.get("ok") and back.get("ok"))})
            if not reps[-1]["ok"] and (out.get("error") or back.get("error")):
                break   # способ технически не работает, дальше смысла нет
        ok_n = sum(1 for r in reps if r["ok"])
        detail["%s_attempt%d" % (method, attempt)] = {"ok_reps": ok_n, "reps": reps}
        print("%s попытка %d: %d из 3" % (method, attempt, ok_n), flush=True)
        if ok_n == 3:
            chosen = method; break
        err = [r["out"].get("error") or r["back"].get("error") for r in reps if (r["out"].get("error") or r["back"].get("error"))]
        if err:
            detail["%s_errors" % method] = err[:2]; break
    if chosen: break
# вернуть игрока на спавн
try:
    teleport(chosen or "T2", *SPAWN) if chosen else None
except Exception:
    pass
st["tp_method"] = chosen; save_state(st)
json.dump(detail, open(os.path.join(REPO_RES, "run1_tp00_detail.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
if chosen:
    add_result({"id": "TP-00", "verdict": "Пройдено", "numbers": "выбран %s: критерий 2.3 выполнен 3 из 3 (туда и обратно); autoSyncTransforms исходно=%s" % (chosen, st.get("orig_autoSync")),
                "evidence": "run1_tp00_detail.json"})
else:
    errs = {k: v for k, v in detail.items() if k.endswith("_errors")}
    summ = {k: v["ok_reps"] for k, v in detail.items() if isinstance(v, dict) and "ok_reps" in v}
    add_result({"id": "TP-00", "verdict": "Не проверено", "numbers": "ни один способ не прошёл 3 из 3: %s; ошибки: %s" % (summ, errs), "evidence": "run1_tp00_detail.json"})
print("ВЫБРАН:", chosen)
