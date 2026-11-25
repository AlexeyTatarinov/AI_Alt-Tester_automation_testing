# -*- coding: utf-8 -*-
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inv_lib import *
pre = guard.preflight("inv13b"); print("preflight", {k: pre[k] for k in ("consoleFlags","error_pause","play","alive")}, "iconic", pre["window"].get("iconic"))
if pre["window"].get("iconic") or pre["error_pause"]: raise SystemExit("стоп")
d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, True)
if inv(): key("Tab", 0.1); time.sleep(1.0)
def inv13():
    teleport("T1", POT[0] - 3.0, POT[1] + 0.3, POT[2]); time.sleep(3.5)
    steps = 0; dist_hint = None
    for _ in range(14):
        k, p = step_towards(POT, 0.15); steps += 1
        if hint(): dist_hint = round(dxz(p, POT), 2); break
    key("E", 0.1); time.sleep(1.2)
    o = {"hint_dist": dist_hint, "steps": steps, "inv_open": inv(), "near_pot": INV().get_component_property("UIInventory", "_isNearPot", ASM), "tab": tab_type()}
    sl = slots(); o["recipes"] = [(n, a) for _, n, a, _ in sl]
    b, inter = action_button(); o["action_interactable_before"] = inter
    err_before = None
    try: err_before = INV().get_component_property("UIInventory", "_errorPotMessage.activeSelf", ASM)
    except Exception: pass
    shot("inv13_before_Q")
    guard.risky("INV-13 Q у котла")                       # чекпойнт: хеш save.chop, размер лога
    h0 = save_hashes(); off = log_mark()
    key("Q", 0.1); time.sleep(1.5)
    lg = log_since(off); h1 = save_hashes()
    alive_after = guard.alive()
    o.update({"exceptions": lg["exceptions"], "errors": lg["errors"], "samples": lg["samples"][:3], "save_changed": h0 != h1, "alive_after_Q": alive_after[0],
              "recipes_after": [(n, a) for _, n, a, _ in slots()], "inv_still_open": inv(), "tab_after": tab_type()})
    try: o["anim_flag_UIItemForAnimation"] = comp_active("UIItemForAnimation")
    except Exception: pass
    shot("inv13_after_Q")
    if inv(): key("Tab", 0.1); time.sleep(1.0)
    o["inv_closed"] = not inv()
    a = approach_step("W", 0.3, 0.6); o["control_back_step_m"] = a["moved_m"]
    nores = len(o["recipes"]) == 0
    if nores:
        ok = (o["action_interactable_before"] is False) and lg["exceptions"] == 0 and not o["save_changed"] and o["inv_closed"] and a["moved_m"] >= 0.5
        v = "Пройдено" if ok else "Не пройдено"
        num = ("у котла (подсказка на %s м, E → инвентарь открыт=%s, _isNearPot=%s, вкладка Recipe=%s): рецептов нет (вкладка пуста), кнопка действия interactable=%s (неактивна = норма); _errorPotMessage=%s; Q один раз: исключений %d, ошибок %d, save.chop изменился=%s, игра жива=%s; Tab закрыл=%s, шаг после %s м (≥0,5)" %
               (o["hint_dist"], o["inv_open"], o["near_pot"], o["tab"], o["action_interactable_before"], err_before, lg["exceptions"], lg["errors"], o["save_changed"], alive_after[0], o["inv_closed"], a["moved_m"]))
        if lg["samples"]: num += "; образцы лога: %s" % lg["samples"][:2]
    else:
        v = "Не проверено"; num = "рецепты есть: %s — сценарий готовки не реализован в скрипте" % o["recipes"]
    return {"verdict": v, "numbers": num, "evidence": "shots/inv13_*.png", "detail": o}
r = case("INV-13", inv13)
md_row("INV-13", r["verdict"], r["numbers"], r.get("evidence", ""))
print(json.dumps(r.get("detail"), ensure_ascii=False, default=str))
