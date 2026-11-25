# -*- coding: utf-8 -*-
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inv_lib import *
pre = guard.preflight("inv10"); print("preflight", {k: pre[k] for k in ("consoleFlags","error_pause","play","alive")}, "iconic", pre["window"].get("iconic"))
if pre["window"].get("iconic") or pre["error_pause"]: raise SystemExit("стоп")
d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, True)
if inv(): key("Tab", 0.1); time.sleep(1.0)
def inv10():
    teleport("T1", SPAWN[0], SPAWN[1] + 0.3, SPAWN[2]); time.sleep(3.5)
    if not inv(): key("Tab", 0.1); time.sleep(1.2)
    o = {"inv_open": inv(), "tab": tab_type()}
    use = None; tabs = []
    for _ in range(4):
        sl = slots(); tabs.append((tab_type(), [(n, a, at) for _, n, a, at in sl]))
        cand = [x for x in sl if x[3] == 1 and x[2] >= 2]
        if cand: use = (cand[0], sl); break
        key("Y", 0.1); time.sleep(0.7)
    o["tabs"] = tabs
    if not use:
        if inv(): key("Tab", 0.1); time.sleep(0.8)
        return {"verdict": "Не проверено", "numbers": "нет предмета типа Use с количеством ≥ 2: %s" % tabs, "detail": o}
    (slot, name, amt0, at), sl = use
    others = [x for x in sl if x[0].id != slot.id]
    for _ in range(2):                      # выбор другого предмета и возврат (накопление подписок CC-81)
        if others: others[0][0].click(); time.sleep(0.5)
        slot.click(); time.sleep(0.5)
    before = next((x[2] for x in slots() if x[1] == name), None)
    o.update({"item": name, "amount_before": before, "tab_use": tab_type()})
    shot("inv10_before_Q")
    guard.risky("INV-10 Q (Seed x20)")
    h0 = save_hashes(); off = log_mark()
    key("Q", 0.1); time.sleep(1.0)
    after_1s = next((x[2] for x in slots() if x[1] == name), None)
    time.sleep(2.0)
    after_3s = next((x[2] for x in slots() if x[1] == name), None)
    lg = log_since(off); h1 = save_hashes(); al = guard.alive()
    shot("inv10_after_Q")
    o.update({"amount_after_1s": after_1s, "amount_after_3s": after_3s, "exceptions": lg["exceptions"], "errors": lg["errors"], "samples": lg["samples"][:3], "save_changed": h0 != h1, "alive_after_Q": al[0]})
    if inv(): key("Tab", 0.1); time.sleep(1.0)
    o["inv_closed"] = not inv()
    a = approach_step("W", 0.3, 0.6); o["control_back_step_m"] = a["moved_m"]
    delta = None if (before is None or after_3s is None) else before - after_3s
    ok = delta == 1 and lg["exceptions"] == 0
    v = "Пройдено" if ok else ("Не пройдено" if delta is not None else "Не подтверждено")
    num = ("предмет %s (Use), количество ДО Q %s, ПОСЛЕ Q: через 1 с %s, через 3 с %s (изменение %s, ожидается −1; больше −1 = накопившиеся подписки CC-81); перед Q 2 раза выбран другой предмет и возврат; исключений %d, ошибок %d, save.chop изменился=%s, игра жива=%s; инвентарь закрыт=%s, шаг после %s м" %
           (name, before, after_1s, after_3s, None if delta is None else -delta, lg["exceptions"], lg["errors"], o["save_changed"], al[0], o["inv_closed"], a["moved_m"]))
    if lg["samples"]: num += "; образцы лога: %s" % lg["samples"][:3]
    return {"verdict": v, "numbers": num, "evidence": "shots/inv10_*.png", "detail": o}
r = case("INV-10", inv10)
md_row("INV-10", r["verdict"], r["numbers"], r.get("evidence", ""))
print(json.dumps(r.get("detail"), ensure_ascii=False, default=str))
